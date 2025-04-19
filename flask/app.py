from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'ta', 'ra', 'instructor'
    major = db.Column(db.String(80), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ta_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Store TA user ID
    student_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Store student user ID
    day = db.Column(db.String(10), nullable=False)  # "Monday", "Tuesday", ...
    time = db.Column(db.String(10), nullable=False)  # "9:00", "10:00", ...
    booked = db.Column(db.Boolean, default=False)

    ta = db.relationship('User', foreign_keys=[ta_user_id], backref='ta_appointments')
    student = db.relationship('User', foreign_keys=[student_user_id], backref='student_appointments')

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(100), unique=True, nullable=False)

class ClubFundsTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(100), db.ForeignKey('club.club_name'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    club = db.relationship('Club', backref='funds_tracker')

# Define Resource model
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100), nullable=False)
    lent_out_to = db.Column(db.String(100), nullable=True)
    value = db.Column(db.Integer, nullable=False)

# Define ResourceRequest model
class ResourceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    due_date = db.Column(db.String(10), nullable=False)  # Date format: MM/DD/YYYY
    approved = db.Column(db.Boolean, default=False)

    resource = db.relationship('Resource', backref='requests')

class EventRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    event_description = db.Column(db.Text, nullable=False)
    approved = db.Column(db.Boolean, default=False)

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_id = request.form['user_id']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        major = request.form['major']
        new_user = User(first_name=first_name, last_name=last_name, user_id=user_id, password=password, role=role, major=major)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(user_id=request.form['user_id']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/ta')
def ta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('ta.html')

from sqlalchemy.orm import aliased

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        day = request.form['day']
        time = request.form['time']
        new_appointment = Appointment(ta_user_id=user.id, day=day, time=time, booked=False)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('appointments'))

    # Aliasing User table to differentiate TA and Student
    Student = aliased(User)

    # Fetch appointments with TA and Student names using LEFT JOIN
    appointments = db.session.query(
        Appointment.id,
        Appointment.day,
        Appointment.time,
        Appointment.booked,
        User.first_name.label('ta_first_name'),
        User.last_name.label('ta_last_name'),
        Student.first_name.label('student_first_name'),
        Student.last_name.label('student_last_name')
    ).join(User, Appointment.ta_user_id == User.id)\
     .outerjoin(Student, Appointment.student_user_id == Student.id)\
     .all()

    return render_template('appointments.html', appointments=appointments)


@app.route('/book/<int:appointment_id>')
def book_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get(appointment_id)
    student = User.query.get(session['user_id'])  # Get student user_id

    if appointment and not appointment.booked:
        appointment.student_user_id = student.id  # Store student ID
        appointment.booked = True
        db.session.commit()

    return redirect(url_for('appointments'))

@app.route('/promote')
def promote():
    if 'user_id' not in session or session['role'] not in ['instructor', 'ra']:
        return "Unauthorized", 403
    students = User.query.filter_by(role='student').all()
    return render_template('promote.html', students=students)

@app.route('/promote_to_ta/<int:user_id>', methods=['POST'])
def promote_to_ta(user_id):
    if 'user_id' not in session or session['role'] not in ['instructor', 'ra']:
        return "Unauthorized", 403
    
    user = User.query.get(user_id)
    if user and user.role == 'student':
        user.role = 'ta'
        db.session.commit()
    
    return redirect(url_for('promote'))

@app.route('/borrow_resource', methods=['GET', 'POST'])
def borrow_resource():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    resource_names = ["Resource 1", "Resource 2", "Resource 3"]
    message = ""

    if request.method == 'POST':
        selected_resource = request.form['resource']
        due_date_str = request.form['due_date']
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

        new_request = ResourceRequest(
            resource_name=selected_resource,
            student_user_id=session['user_id'],
            due_date=due_date,
            approved=False
        )
        db.session.add(new_request)
        db.session.commit()

        message = "Resource requested successfully!"

    student = User.query.get(session['user_id'])
    return render_template('borrow_resource.html', student=student, resource_names=resource_names, message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/clubs')
def clubs():
    if 'user_id' not in session or 'role' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])  # Get the current user from session
    return render_template('clubs.html', first_name=user.first_name, role=user.role)

@app.route('/view_resources')
def view_resources():
    return render_template('view_resources.html')

@app.route('/view_events')
def view_events():
    # Dummy data for past events (replace with data from your database or other sources)
    past_events = [
        {
            "club_name": "Science Club",
            "location": "Auditorium",
            "date": "2023-11-10",
            "time": "10:00 AM",
            "budget": "$500",
            "feedback": "Good",
        },
        {
            "club_name": "Literature Club",
            "location": "Library",
            "date": "2023-11-15",
            "time": "2:00 PM",
            "budget": "$300",
            "feedback": "Excellent",
        },
        {
            "club_name": "Music Club",
            "location": "Open Ground",
            "date": "2023-11-20",
            "time": "5:00 PM",
            "budget": "$700",
            "feedback": "Satisfactory",
        },
    ]

    return render_template('view_events.html', events=past_events)

@app.route('/view_clubs', methods=['GET', 'POST'])
def view_clubs():
    clubs = Club.query.all()  # Fetch all clubs from the database
    clubs_list = [club.club_name for club in clubs]

    club_name = None
    total_funds = None

    if request.method == 'POST':
        # Get selected club
        club_name = request.form['club_name']
        
        # Get total funds for the selected club
        total_funds_record = db.session.query(db.func.sum(ClubFundsTracker.amount)).filter(ClubFundsTracker.club_name == club_name).scalar()
        total_funds = total_funds_record if total_funds_record else 0

    return render_template('view_clubs.html', clubs=clubs_list, club_name=club_name, total_funds=total_funds)

@app.route('/resource_requests')
def resource_requests():
    return render_template('resource_requests.html')

@app.route('/add_request', methods=['GET', 'POST'])
def add_request():
    if request.method == 'POST':
        resource_name = request.form['resource_name']
        due_date = request.form['due_date']
        
        # Check if resource is valid
        resource = Resource.query.filter_by(resource_name=resource_name).first()
        
        if resource:
            new_request = ResourceRequest(resource_id=resource.id, due_date=due_date)
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('view_requests'))
        else:
            return 'Resource not found', 404

    return render_template('add_request.html')

@app.route('/view_requests')
def view_requests():
    requests = ResourceRequest.query.all()  # Fetch all requests
    return render_template('view_requests.html', requests=requests)

@app.route('/approve_request/<int:id>')
def approve_request(id):
    request_to_approve = ResourceRequest.query.get(id)
    request_to_approve.approved = True
    db.session.commit()
    return redirect(url_for('view_requests'))

@app.route('/reject_request/<int:id>')
def reject_request(id):
    request_to_reject = ResourceRequest.query.get(id)
    db.session.delete(request_to_reject)
    db.session.commit()
    return redirect(url_for('view_requests'))

@app.route('/event_requests', methods=['GET', 'POST'])
def event_requests():
    if request.method == 'POST':
        club_name = request.form['club_name']
        event_name = request.form['event_name']
        event_description = request.form['event_description']

        new_request = EventRequest(
            club_name=club_name,
            event_name=event_name,
            event_description=event_description
        )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('event_requests'))

    all_requests = EventRequest.query.all()
    return render_template('event_requests.html', requests=all_requests)

@app.route('/approve_event/<int:id>')
def approve_event(id):
    event = EventRequest.query.get_or_404(id)
    event.approved = True
    db.session.commit()
    return redirect(url_for('event_requests'))

@app.route('/reject_event/<int:id>')
def reject_event(id):
    event = EventRequest.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('event_requests'))

@app.route('/club_finances')
def club_finances():
    return render_template('club_finances.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
