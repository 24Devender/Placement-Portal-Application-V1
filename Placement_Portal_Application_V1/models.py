from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db=SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    role=db.Column(db.String(50),nullable=False)
    students=db.relationship("Student",backref="user",lazy=True)
    companies=db.relationship("Company",backref="user",lazy=True)

class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    name=db.Column(db.String(100))
    email=db.Column(db.String(200))
    resume=db.Column(db.String(300))
    blacklisted=db.Column(db.Boolean,default=False)
    applications=db.relationship("Application",backref="student",lazy=True)

class Company(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    company_name=db.Column(db.String(100))
    GST_number=db.Column(db.String(100))
    email=db.Column(db.String(200))
    HR_contact=db.Column(db.String(20))
    website=db.Column(db.String(200))
    approval_status=db.Column(db.String(60),default="Pending")
    blacklisted=db.Column(db.Boolean,default=False)
    drives=db.relationship("Drive",backref="company",lazy=True)

class Drive(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('company.id'),nullable=False)
    job_title=db.Column(db.String(100))
    job_description=db.Column(db.String(300))
    eligibility_criteria=db.Column(db.String(200))
    application_deadline=db.Column(db.Date)
    status=db.Column(db.String(60),default="Ongoing")
    applications=db.relationship("Application",backref="drive",lazy=True)

class Application(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False)
    drive_id=db.Column(db.Integer,db.ForeignKey('drive.id'),nullable=False)
    application_date=db.Column(db.DateTime,default=datetime.utcnow)
    status=db.Column(db.String(60),default="Applied")