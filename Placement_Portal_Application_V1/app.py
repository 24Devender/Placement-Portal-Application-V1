from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Student, Company, Application, Drive
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key="placement_portal_secret_key"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER']='static/resumes'
os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['pre_email']
        password=request.form['pre_password']
        role=request.form['role']
        existing_user=User.query.filter_by(email=email,role=role).first()
        if existing_user and existing_user.password==password:
            session["id"]=existing_user.id
            session["role"]=existing_user.role
            session["email"]=existing_user.email
            if role=='admin':
                return redirect(url_for('admin_dashboard'))
            elif role=='student':
                return redirect(url_for('student_dashboard'))
            elif role=='company':
                return redirect(url_for('company_dashboard'))
        return render_template('login_page.html',error_message="Invalid login details")
    return render_template('login_page.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['username']
        email=request.form['email']
        password=request.form['password']
        role=request.form['role']
        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            return "User already exists"
        new_user=User(username=name,email=email,password=password,role=role)
        db.session.add(new_user)
        db.session.commit()
        if role=="student":
            new_student=Student(user_id=new_user.id,name=name,email=email)
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('student_dashboard'))
        elif role=="company":
            session["id"]=new_user.id
            session["role"]=new_user.role
            session["email"]=new_user.email
            return redirect(url_for('company_dashboard'))
        return redirect(url_for('login'))
    return render_template('register_page.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    search=request.args.get("search")
    if search:
        companies=Company.query.filter(Company.company_name.contains(search)).all()
        students=Student.query.filter(Student.name.contains(search)).all()
    else:
        companies=Company.query.all()
        students=Student.query.all()
    drives=Drive.query.all()
    applications=Application.query.all()
    return render_template("admin_page.html",companies=companies,students=students,drives=drives,applications=applications)

@app.route('/approve_company/<int:id>')
def approve_company(id):
    comp=Company.query.get(id)
    comp.approval_status="Approved"
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_company/<int:id>')
def reject_company(id):
    comp=Company.query.get(id)
    comp.approval_status="Rejected"
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/blacklist_company/<int:id>')
def blacklist_company(id):
    comp=Company.query.get(id)
    comp.blacklisted=True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/unblacklist_company/<int:id>')
def unblacklist_company(id):
    comp=Company.query.get(id)
    comp.blacklisted=False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/student_dashboard')
def student_dashboard():

    if "id" not in session:
        return redirect(url_for('login'))

    user_id = session.get("id")

    student = Student.query.filter_by(user_id=user_id).first()

    if not student:
        return "Student profile not found"

    if student.blacklisted:
        return "Your account has been blacklisted by the admin."

    drives = Drive.query.join(Company).filter(
        Company.approval_status == "Approved",
        Company.blacklisted == False,
        Drive.status == "Ongoing"
    ).all()

    applications = Application.query.filter_by(student_id=student.id).all()

    companies = Company.query.filter_by(
        approval_status="Approved",
        blacklisted=False
    ).all()

    company_dict = {c.id: c.company_name for c in companies}

    return render_template(
        "student_page.html",
        drives=drives,
        applications=applications,
        company_dict=company_dict
    )

@app.route('/apply_drive/<int:drive_id>', methods=['POST'])
def apply_drive(drive_id):

    if "id" not in session:
        return redirect(url_for("login"))

    user_id=session.get("id")
    student=Student.query.filter_by(user_id=user_id).first()

    if not student:
        return redirect(url_for('student_dashboard'))

    existing_application=Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if existing_application:
        return redirect(url_for('student_dashboard'))

    new_application=Application(
        student_id=student.id,
        drive_id=drive_id
    )

    db.session.add(new_application)
    db.session.commit()

    return redirect(url_for('student_dashboard'))

@app.route('/company_dashboard', methods=['GET','POST'])
def company_dashboard():

    if "id" not in session:
        return redirect(url_for("login"))

    user_id=session.get("id")
    company=Company.query.filter_by(user_id=user_id).first()

    if request.method=="POST":

        if not company:
            company=Company(user_id=user_id)

        company.company_name=request.form.get("company_name")
        company.GST_number=request.form.get("GST_number")
        company.email=request.form.get("email")
        company.HR_contact=request.form.get("HR_contact")
        company.website=request.form.get("website")

        if not company.id:
            company.approval_status="Pending"
            company.blacklisted=False
            db.session.add(company)

        db.session.commit()

        return redirect(url_for("company_dashboard"))

    if company:
        if company.blacklisted:
            return "Your company has been blacklisted by the admin."

        if company.approval_status=="Rejected":
            return "Your company registration has been rejected."

        if company.approval_status!="Approved":
            return "Your company registration is pending admin approval."

        drives=Drive.query.filter_by(company_id=company.id).all()
    else:
        drives=[]

    return render_template(
        "company_page.html",
        company=company,
        drives=drives
    )
@app.route('/create_drive',methods=['GET','POST'])
def create_drive():

    if "id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":

        title=request.form['job_title']
        description=request.form['job_description']
        eligibility=request.form['eligibility']
        deadline=request.form['deadline']

        deadline=datetime.strptime(deadline,"%Y-%m-%d").date()

        user_id=session.get("id")
        comp=Company.query.filter_by(user_id=user_id).first()

        drive=Drive(
            company_id=comp.id,
            job_title=title,
            job_description=description,
            eligibility_criteria=eligibility,
            application_deadline=deadline
        )

        db.session.add(drive)
        db.session.commit()

        return redirect(url_for("company_dashboard"))

    return render_template("create_drive.html")

@app.route('/view_applicants/<int:drive_id>')
def view_applicants(drive_id):
    applications=Application.query.filter_by(drive_id=drive_id).all()
    return render_template("view_applicants.html",applications=applications)
@app.route('/upload_resume',methods=['POST'])
def upload_resume():
    if "id" not in session:
        return redirect(url_for("login"))

    file=request.files.get("resume")

    if file:
        filename=secure_filename(file.filename)
        filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(filepath)

        user_id=session.get("id")
        student=Student.query.filter_by(user_id=user_id).first()

        if student:
            student.resume=filename
            db.session.commit()

    return redirect(url_for("student_dashboard"))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/view_company/<int:company_id>")
def view_company(company_id):

    if "id" not in session:
        return redirect(url_for("login"))

    company = Company.query.get_or_404(company_id)

    drives = Drive.query.filter_by(company_id=company.id).all()

    return render_template(
        "view_company.html",
        company=company,
        drives=drives
    )
@app.route('/blacklist_student/<int:id>')
def blacklist_student(id):

    student = Student.query.get_or_404(id)

    student.blacklisted = True

    db.session.commit()

    return redirect(url_for('admin_dashboard'))
@app.route('/unblacklist_student/<int:id>')
def unblacklist_student(id):

    student = Student.query.get_or_404(id)

    student.blacklisted = False

    db.session.commit()

    return redirect(url_for('admin_dashboard'))
@app.route('/complete_drive/<int:id>')
def complete_drive(id):

    drive = Drive.query.get_or_404(id)

    drive.status = "Completed"

    db.session.commit()

    return redirect(url_for('company_dashboard'))



if __name__=="__main__":
    with app.app_context():
        db.create_all()
        existing_admin=User.query.filter_by(username='admin').first()
        if not existing_admin:
            admin_user=User(username='admin',password='admin',email='admin@dg.com',role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)