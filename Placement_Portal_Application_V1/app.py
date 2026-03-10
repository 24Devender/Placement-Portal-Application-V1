from flask import Flask, render_template    
from models import db, user, student, company, Application, drive
app = Flask(__name__) #Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_admin = user.query.filter_by(username='admin').first()
        if not existing_admin:
            admin_user = user(username='admin', password='admin',email='admin@dg.com', role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)