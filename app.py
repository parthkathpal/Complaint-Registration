from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# A secret key for flash messages. In production set securely.
app.config['SECRET_KEY'] = 'dev-secret-key'

db = SQLAlchemy(app)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Open')  # Open / In Progress / Resolved / Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Complaint {self.id} - {self.title}>'

# @app.before_first_request
# def create_tables():
#     db.create_all()

@app.route('/')
def index():
    # show list of complaints sorted newest first
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    return render_template('index.html', complaints=complaints)

@app.route('/complaint/new', methods=['GET', 'POST'])
def create_complaint():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        student_name = request.form.get('student_name', '').strip()
        student_email = request.form.get('student_email', '').strip()
        status = request.form.get('status', 'Open')

        if not title or not description or not student_name:
            flash('Title, Description and Student name are required.', 'danger')
            return redirect(url_for('create_complaint'))

        new = Complaint(
            title=title,
            description=description,
            student_name=student_name,
            student_email=student_email if student_email else None,
            status=status
        )
        db.session.add(new)
        db.session.commit()
        flash('Complaint created successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/complaint/<int:cid>')
def view_complaint(cid):
    c = Complaint.query.get_or_404(cid)
    return render_template('view.html', complaint=c)

@app.route('/complaint/<int:cid>/edit', methods=['GET', 'POST'])
def edit_complaint(cid):
    c = Complaint.query.get_or_404(cid)
    if request.method == 'POST':
        c.title = request.form.get('title', c.title).strip()
        c.description = request.form.get('description', c.description).strip()
        c.student_name = request.form.get('student_name', c.student_name).strip()
        c.student_email = request.form.get('student_email', c.student_email).strip()
        c.status = request.form.get('status', c.status)
        db.session.commit()
        flash('Complaint updated successfully.', 'success')
        return redirect(url_for('view_complaint', cid=c.id))
    return render_template('edit.html', complaint=c)

@app.route('/complaint/<int:cid>/delete', methods=['POST'])
def delete_complaint(cid):
    c = Complaint.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash('Complaint deleted.', 'info')
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     # ensure instance folder exists if used
#     os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)
#     app.run(debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
