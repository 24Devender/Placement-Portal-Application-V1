from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from datetime import datetime
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),unique = True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable = False)
class student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable = False)
    gender =db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    department = db.Column(db.String(100))
    email = db.Column(db.String(200), unique = True)
    resume = db.Column(db.String(300))
class company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100), nullable = False)
    GST_number = db.Column(db.String(100), unique = True)
    email = db.Column(db.String(200), unique = True)
    HR_contact = db.Column(db.Integer)
    website = db.Column(db.String(200), unique = True)
    approval_status = db.Column(db.String(60), default = "Pending")
class drive(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    Job_Title = db.Column(db.String(100))
    Job_description = db.Column(db.String(200))
    eligibility_criteria = db.column(db.String(100))
    application_deadline = db.column(db.Date)
    status = db.Column(db.String(60), default = "Pending")
class Application(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))
    application_date = db.Column(db.DateTime, default = datetime.utcnow)
    status = db.Column(db.String(60), default = "Applied")



        