from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import io
import base64
import datetime

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
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    club = db.relationship('Club', backref='funds_tracker')

# Define Resource model
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100), nullable=False)
    lent_out_to = db.Column(db.String(100), nullable=True)
    value = db.Column(db.Integer, nullable=False)

class ResourceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    student_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.String(10), nullable=False)  # Date format: MM/DD/YYYY
    approved = db.Column(db.Boolean, default=False)

    resource = db.relationship('Resource', backref='requests')
    student = db.relationship('User')

class EventRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    event_name = db.Column(db.String(100))
    event_description = db.Column(db.Text)
    event_date = db.Column(db.Date)
    event_time = db.Column(db.Time)
    location = db.Column(db.String(100))
    budget = db.Column(db.Integer)
    approved = db.Column(db.Boolean, default=False)

    club = db.relationship('Club', backref='event_requests')

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
    return render_template('dashboard.html', user=user, role=user.role)

@app.route('/ta')
def ta():
    if 'user_id' not in session or 'role' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])  # Get the current user from session
    return render_template('ta.html', name=user.first_name+" "+user.last_name,  role=user.role)

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

    # Fetch resource names from database
    resources = Resource.query.all()
    resource_names = [r.resource_name for r in resources]
    message = ""

    if request.method == 'POST':
        selected_resource = request.form['resource']
        due_date_str = request.form['due_date']
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").strftime("%m/%d/%Y")

        resource = Resource.query.filter_by(resource_name=selected_resource).first()
        if resource:
            new_request = ResourceRequest(
                resource_id=resource.id,
                due_date=due_date,
                approved=False
            )
            db.session.add(new_request)
            db.session.commit()
            message = "Resource requested successfully!"
        else:
            message = "Selected resource not found!"

    student = User.query.get(session['user_id'])
    return render_template('borrow_resource.html', student=student, resource_names=resource_names, message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/clubs_sl')
def clubs_sl():
    if 'user_id' not in session or 'role' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])  # Get the current user from session
    return render_template('clubs_sl.html', name=user.first_name+" "+user.last_name,  role=user.role)

@app.route('/view_resources')
def view_resources():
    return render_template('view_resources.html')

@app.route('/edit_resources', methods=['GET', 'POST'])
def edit_resources():
    if 'user_id' not in session or session['role'] != 'sl':
        return redirect(url_for('login'))  # Restrict access to Student Life users

    if request.method == 'POST':
        # Handle adding a new resource
        if 'add_resource' in request.form:
            resource_name = request.form['resource_name']
            value = request.form['value']
            if Resource.query.filter_by(resource_name=resource_name).first():
                flash("Resource already exists!", "danger")
            else:
                new_resource = Resource(resource_name=resource_name, value=value)
                db.session.add(new_resource)
                db.session.commit()
                flash("Resource added successfully!", "success")

        # Handle editing an existing resource
        elif 'edit_resource' in request.form:
            resource_id = request.form['resource_id']
            new_name = request.form['new_resource_name']
            new_value = request.form['new_value']
            resource = Resource.query.get(resource_id)
            if resource:
                resource.resource_name = new_name
                resource.value = new_value
                db.session.commit()
                flash("Resource updated successfully!", "success")
            else:
                flash("Resource not found!", "danger")

        # Handle deleting a resource
        elif 'delete_resource' in request.form:
            resource_id = request.form['resource_id']
            resource = Resource.query.get(resource_id)
            if resource:
                db.session.delete(resource)
                db.session.commit()
                flash("Resource deleted successfully!", "success")
            else:
                flash("Resource not found!", "danger")

    # Fetch all resources to display
    resources = Resource.query.all()
    return render_template('edit_resources.html', resources=resources)

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
    clubs = Club.query.all()  # Fetch all clubs
    selected_club = None
    total_funds = None

    if request.method == 'POST':
        selected_club_id = request.form['club_id']  # This is a string (from dropdown value)
        selected_club = Club.query.get(int(selected_club_id))  # Convert to Club object

        if selected_club:
            total_funds = db.session.query(db.func.sum(ClubFundsTracker.amount))\
                .filter_by(club_id=selected_club.id).scalar()
            total_funds = total_funds if total_funds else 0

    return render_template('view_clubs.html', clubs=clubs, selected_club=selected_club, total_funds=total_funds)

@app.route('/resource_requests')
def resource_requests():
    requests = ResourceRequest.query.all()
    return render_template('resource_requests.html', requests=requests)

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

@app.route('/club_finances', methods=['GET', 'POST'])
def club_finances():
    clubs = Club.query.all()
    selected_club = request.form.get('club_name') if request.method == 'POST' else clubs[0].club_name if clubs else None
    finances = []
    graph_url = None

    if selected_club:
        data = ClubFundsTracker.query.filter_by(club_name=selected_club).order_by(ClubFundsTracker.date).all()
        final_balance = 0
        for entry in data:
            final_balance += entry.amount
            finances.append({
                'purpose': entry.purpose,
                'amount': entry.amount,
                'date': entry.date,
                'final_balance': final_balance
            })

        # Graph generation
        x_labels = [f["date"] + "\n" + f["purpose"] for f in finances]
        y_values = [f['final_balance'] for f in finances]

        fig, ax = plt.subplots()
        ax.plot(x_labels, y_values, marker='o', linestyle='-', color='skyblue')
        ax.set_title(f'{selected_club} Financials')
        ax.set_xlabel('Date / Purpose')
        ax.set_ylabel('Final Balance (PKR)')
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        graph_url = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

    return render_template('club_finances.html', clubs=clubs, selected_club=selected_club, finances=finances, graph_url=graph_url)

@app.route('/edit_clubs', methods=['GET', 'POST'])
def edit_clubs():
    if 'user_id' not in session or session['role'] != 'sl':
        return redirect(url_for('login'))  # Restrict access to Student Life users

    if request.method == 'POST':
        # Handle adding a new club
        if 'add_club' in request.form:
            club_name = request.form['club_name']
            if Club.query.filter_by(club_name=club_name).first():
                flash("Club already exists!", "danger")
            else:
                new_club = Club(club_name=club_name)
                db.session.add(new_club)
                db.session.commit()
                flash("Club added successfully!", "success")

        # Handle editing an existing club
        elif 'edit_club' in request.form:
            club_id = request.form['club_id']
            new_name = request.form['new_club_name']
            club = Club.query.get(club_id)
            if club:
                club.club_name = new_name
                db.session.commit()
                flash("Club updated successfully!", "success")
            else:
                flash("Club not found!", "danger")

        # Handle deleting a club
        elif 'delete_club' in request.form:
            club_id = request.form['club_id']
            club = Club.query.get(club_id)
            if club:
                db.session.delete(club)
                db.session.commit()
                flash("Club deleted successfully!", "success")
            else:
                flash("Club not found!", "danger")

    # Fetch all clubs to display
    clubs = Club.query.all()
    return render_template('edit_clubs.html', clubs=clubs)

@app.route('/clubs_st')
def clubs_st():
    if 'user_id' not in session or 'role' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])  # Get the current user from session
    return render_template('clubs_st.html', name=user.first_name+" "+user.last_name,  role=user.role)

@app.route('/borrowed_resources')
def borrowed_resources():
    # Sample data for demonstration; replace with DB query
    resource = {
        "id": "MIC001",
        "name": "Microphone",
        "lent_out_to": "SerVe",
        "event": "DiscO"
    }
    return render_template('borrowed_resources.html', resource=resource)

@app.route('/request_resource', methods=['GET', 'POST'])
def request_resource():
    resources = Resource.query.all()  # Fetch all resources from the database
    if request.method == 'POST':
        selected_resource_id = request.form.get('resource_id')  # Use resource ID for saving
        due_date = request.form.get('due_date')
        student_user_id = session.get('user_id')  # Assume the logged-in user's ID is stored in the session

        if selected_resource_id and due_date and student_user_id:
            # Save the resource request to the database
            new_request = ResourceRequest(
                resource_id=selected_resource_id,
                student_user_id=student_user_id,
                due_date=due_date,
                approved=False
            )
            db.session.add(new_request)
            db.session.commit()
            flash("Resource request submitted successfully!", "success")
            return redirect(url_for('request_resource'))
        else:
            flash("Please select a resource, provide a due date, and ensure you are logged in.", "danger")

    return render_template('request_resource.html', resources=resources)

from flask import render_template, request, redirect, flash
from datetime import datetime

@app.route('/request_event', methods=['GET', 'POST'])
def request_event():
    if request.method == 'POST':
        try:
            club_name = request.form['club_name']
            club = Club.query.filter_by(club_name=club_name).first()

            if not club:
                flash("Selected club does not exist.", "danger")
                return redirect(url_for('request_event'))

            new_request = EventRequest(
                club_id=club.id,
                event_name=request.form['event_name'],
                event_description=request.form['event_description'],
                event_date=datetime.strptime(request.form['event_date'], "%d-%m-%Y").date(),
                event_time=datetime.strptime(request.form['event_time'], "%H:%M").time(),
                location=request.form['location'],
                budget=int(request.form['budget']),
                approved=False
            )

            db.session.add(new_request)
            db.session.commit()
            flash("Event request submitted successfully!", "success")
            return redirect(url_for('request_event'))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    clubs = [club.club_name for club in Club.query.all()]
    locations = ["Auditorium", "Lab 1", "Room A101", "Courtyard"]
    return render_template('request_event.html', clubs=clubs, locations=locations)

@app.route('/view_attendance')
def view_attendance():
    # Simulated data (replace with DB call)
    event_name = "Sample Event Name"
    attendance_data = [
        {"name": "Member 1", "status": "Present"},
        {"name": "Member 2", "status": "Absent"},
        {"name": "Member 3", "status": "Present"},
        {"name": "Member 4", "status": "Absent"},
        {"name": "Member 5", "status": "Present"},
    ]
    return render_template('view_attendance.html', event_name=event_name, attendance=attendance_data)

@app.route('/event_feedback')
def event_feedback():
    student_id = "S1223"  # You can replace this with session-based logic if needed
    events = ["DiscO", "Event 2", "Event 3"]

    if request.method == 'POST':
        selected_event = request.form['event']
        feedback = request.form['feedback']
        
        # For now, just print it (replace with DB insertion if needed)
        print(f"Student ID: {student_id}")
        print(f"Selected Event: {selected_event}")
        print(f"Feedback: {feedback}")

        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('feedback.event_feedback'))

    return render_template('event_feedback.html', student_id=student_id, events=events)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)