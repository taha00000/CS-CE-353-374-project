from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import io
import base64
import datetime
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
app.config['SQLALCHEMY_ECHO'] = True
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
    t_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # e.g., "13:00"
    end_time = db.Column(db.String(5), nullable=False)    # e.g., "14:00"
    booked = db.Column(db.Boolean, default=False)
    appointment_type = db.Column(db.String(20), nullable=False)  # "office_hours" or "student_scheduled"
    recurring_until = db.Column(db.Date, nullable=True)
    purpose = db.Column(db.String(200), nullable=True)  # Purpose of the meeting
    approved = db.Column(db.Boolean, default=False, nullable=False)  # Approval status

    ta = db.relationship('User', foreign_keys=[t_user_id], backref='ta_appointments')
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
    lent_out_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Foreign key to User table
    value = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='lent_resources')  # Relationship to User model

class ResourceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    due_date = db.Column(db.Date, nullable=False)
    approved = db.Column(db.Boolean, default=False)

    resource = db.relationship('Resource', backref='requests')
    student = db.relationship('User', backref='resource_requests')

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

    club = db.relationship('Club', backref='event_requests')  # Relationship to Club model

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
    error = None  # Initialize error message
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        # Query the user from the database
        user = User.query.filter_by(user_id=user_id).first()

        if not user:
            error = "User ID does not exist."  # Error for invalid username
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."  # Error for invalid password
        else:
            # Successful login
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))  # Redirect to the dashboard or home page

    return render_template('login.html', error=error)

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

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Get the current week (default to this week)
    today = datetime.today()
    start_of_week = request.args.get('start_of_week')
    if start_of_week:
        start_of_week = datetime.strptime(start_of_week, "%Y-%m-%d")
    else:
        start_of_week = today - timedelta(days=today.weekday())  # Start of the current week (Monday)

    end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)

    # Fetch filter criteria from the request
    major = request.args.get('major', '')
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')

    # Use aliases for the user table
    instructor_alias = aliased(User)  # Alias for the instructor
    student_alias = aliased(User)  # Alias for the student

    # Query appointments for the current week
    query = Appointment.query.filter(
        Appointment.day.between(start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d"))
    )

    # Apply filters if provided
    if major:
        query = query.filter(instructor_alias.major == major)
    if first_name:
        query = query.filter(instructor_alias.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(instructor_alias.last_name.ilike(f"%{last_name}%"))

    # Ensure the join is applied only once
    query = query.join(instructor_alias, Appointment.t_user_id == instructor_alias.id)

    appointments = query.all()

    # Map major abbreviations to full names
    MAJOR_FULL_NAMES = {
        "cs": "Computer Science",
        "ece": "Electrical/Computer Engineering",
        "sdp": "Social Development and Policy",
        "cnd": "Communication & Design",
        "ch": "Comparative Humanities",
        "iscim": "Science & Mathematics (iSciM)",
        "pg": "Playground",
    }

    return render_template(
        'appointments.html',
        appointments=appointments,
        start_of_week=start_of_week,
        end_of_week=end_of_week,
        timedelta=timedelta,
        user=user,
        majors=MAJOR_FULL_NAMES,
        filters={'major': major, 'first_name': first_name, 'last_name': last_name}  # Pass filters to the template
    )

@app.route('/reserve_appointment/<int:appointment_id>', methods=['POST'])
def reserve_appointment(appointment_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))  # Only students can reserve appointments

    # Get the appointment and the logged-in student
    appointment = Appointment.query.get(appointment_id)
    student = User.query.get(session['user_id'])

    if not appointment or appointment.booked:
        flash("This appointment is no longer available.", "danger")
        return redirect(url_for('appointments'))

    # Reserve the appointment
    appointment.booked = True
    appointment.student_user_id = student.id
    db.session.commit()

    flash("Appointment reserved successfully!", "success")
    return redirect(url_for('appointments'))

@app.route('/approve_appointment/<int:appointment_id>', methods=['POST'])
def approve_appointment(appointment_id):
    if 'user_id' not in session or session['role'] not in ['instructor', 'ta', 'ra']:
        return redirect(url_for('login'))  # Only instructors/TA/RA can approve appointments

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.t_user_id != session['user_id'] or appointment.appointment_type != "student_scheduled":
        flash("Unauthorized action.", "danger")
        return redirect(url_for('appointments'))

    # Approve the appointment
    appointment.approved = True
    appointment.booked = True
    db.session.commit()

    flash("Appointment approved successfully!", "success")
    return redirect(url_for('appointments'))

@app.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
def reject_appointment(appointment_id):
    if 'user_id' not in session or session['role'] not in ['instructor', 'ta', 'ra']:
        return redirect(url_for('login'))  # Only instructors/TA/RA can reject appointments

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.t_user_id != session['user_id'] or appointment.appointment_type != "student_scheduled":
        flash("Unauthorized action.", "danger")
        return redirect(url_for('appointments'))

    # Reject the appointment
    db.session.delete(appointment)
    db.session.commit()

    flash("Appointment rejected successfully!", "success")
    return redirect(url_for('appointments'))

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))  # Only students can book appointments

    # Fetch filter criteria
    search_name = request.args.get('search_name', '')
    filter_major = request.args.get('filter_major', '')

    # Query instructors
    query = User.query.filter(User.role.in_(['instructor', 'ta', 'ra']))
    if search_name:
        query = query.filter(
            (User.first_name.ilike(f"%{search_name}%")) | (User.last_name.ilike(f"%{search_name}%"))
        )
    if filter_major:
        query = query.filter(User.major == filter_major)

    instructors = query.all()

    if request.method == 'POST':
        instructor_id = request.form['instructor']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        purpose = request.form['purpose']

        # Validate the purpose length
        if len(purpose) > 200:
            flash("Purpose cannot exceed 200 characters.", "danger")
            return redirect(url_for('book_appointment'))

        # Validate the time constraints
        if not (start_time >= "08:30" and end_time <= "18:30"):
            flash("Appointments must be between 08:30 and 18:30.", "danger")
            return redirect(url_for('book_appointment'))

        # Validate the duration
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        duration = (end_hour - start_hour) * 60 + (end_minute - start_minute)
        if duration > 60:
            flash("Appointments cannot be longer than 1 hour.", "danger")
            return redirect(url_for('book_appointment'))

        # Create the appointment
        new_appointment = Appointment(
            t_user_id=instructor_id,
            student_user_id=session['user_id'],
            day=date,
            start_time=start_time,
            end_time=end_time,
            booked=False,  # Not booked until approved
            appointment_type="student_scheduled",
            purpose=purpose,
            approved=False  # Requires instructor approval
        )
        db.session.add(new_appointment)
        db.session.commit()

        flash("Appointment request submitted successfully! Waiting for instructor approval.", "success")
        return redirect(url_for('appointments'))

    # Map major abbreviations to full names
    MAJOR_FULL_NAMES = {
        "cs": "Computer Science",
        "ece": "Electrical/ Computer Engineering",
        "sdp": "Social Development and Policy",
        "cnd": "Communication & Design",
        "ch": "Comparative Humanities",
        "iscim": "Science & Mathematics (iSciM)",
        "pg": "Playground",
    }

    return render_template(
        'book_appointment.html',
        instructors=instructors,
        majors=MAJOR_FULL_NAMES,
        search_name=search_name,
        filter_major=filter_major
    )

@app.route('/promote', methods=['GET', 'POST'])
def promote():
    # Fetch filter criteria from the request
    major = request.args.get('major', '')
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')

    # Query students
    query = User.query.filter_by(role='student')  # Only fetch students
    if major:
        query = query.filter(User.major == major)
    if first_name:
        query = query.filter(User.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(User.last_name.ilike(f"%{last_name}%"))

    students = query.all()

    # Map major abbreviations to full names
    MAJOR_FULL_NAMES = {
        "cs": "Computer Science",
        "ece": "Electrical/Computer Engineering",
        "sdp": "Social Development and Policy",
        "cnd": "Communication & Design",
        "ch": "Comparative Humanities",
        "iscim": "Science & Mathematics (iSciM)",
        "pg": "Playground",
    }

    return render_template(
        'promote.html',
        students=students,
        majors=MAJOR_FULL_NAMES,
        filters={'major': major, 'first_name': first_name, 'last_name': last_name}
    )

@app.route('/promote_to_ta/<int:user_id>', methods=['POST'])
def promote_to_ta(user_id):
    if 'user_id' not in session or session['role'] not in ['instructor', 'ra']:
        return "Unauthorized", 403
    
    user = User.query.get(user_id)
    if user and user.role == 'student':
        user.role = 'ta'
        db.session.commit()
    
    return redirect(url_for('promote'))

@app.route('/schedule_office_hours', methods=['GET', 'POST'])
def schedule_office_hours():
    if 'user_id' not in session or session['role'] not in ['ta', 'ra', 'instructor']:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        day = request.form['day']  # Day of the week
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        recurring_until = request.form.get('recurring_until')  # End date for recurring office hours

        # Convert recurring_until to a date object
        if recurring_until:
            recurring_until = datetime.strptime(recurring_until, "%Y-%m-%d").date()

        # Schedule office hours for each week until the recurring_until date
        current_date = datetime.today().date()
        while current_date <= recurring_until:
            if current_date.strftime('%A') == day:  # Match the selected day of the week
                new_appointment = Appointment(
                    t_user_id=user.id,
                    day=current_date.strftime("%Y-%m-%d"),
                    start_time=start_time,
                    end_time=end_time,
                    booked=False,
                    appointment_type="office_hours",  # Explicitly set as office hours
                    recurring_until=recurring_until
                )
                db.session.add(new_appointment)
            current_date += timedelta(days=1)  # Increment by one day

        db.session.commit()
        flash("Office hours scheduled successfully!", "success")  # Correct flash message
        return redirect(url_for('schedule_office_hours'))

    return render_template('schedule_office_hours.html')

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
    # Query the database for all resources
    resources = Resource.query.all()

    # Pass the resources to the template
    return render_template('view_resources.html', resources=resources, role=session.get('role'))

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
    # Query the database for approved events
    approved_events = EventRequest.query.filter_by(approved=True).all()

    # Pass the approved events to the template
    return render_template('view_events.html', events=approved_events)

@app.route('/resource_requests')
def resource_requests():
    requests = ResourceRequest.query.all()
    return render_template('resource_requests.html', requests=requests)

@app.route('/approve_resource_request/<int:request_id>', methods=['POST'])
def approve_resource_request(request_id):
    resource_request = ResourceRequest.query.get(request_id)
    if resource_request:
        # Mark the request as approved
        resource_request.approved = True

        # Update the `lent_out_to` field in the Resource table
        resource = Resource.query.get(resource_request.resource_id)
        if resource:
            resource.lent_out_to = resource_request.student_id  # Link the resource to the student ID
            db.session.commit()
            flash(f"Resource request {resource_request.id} approved successfully!", "success")
        else:
            flash("Resource not found!", "danger")
    else:
        flash("Resource request not found!", "danger")
    return redirect(url_for('resource_requests'))

@app.route('/reject_resource_request/<int:request_id>', methods=['POST'])
def reject_resource_request(request_id):
    resource_request = ResourceRequest.query.get(request_id)
    if resource_request:
        db.session.delete(resource_request)
        db.session.commit()
        flash(f"Resource request {resource_request.id} rejected and removed successfully!", "success")
    else:
        flash("Resource request not found!", "danger")
    return redirect(url_for('resource_requests'))

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

@app.route('/edit_club/<int:club_id>', methods=['POST'])
def edit_club(club_id):
    new_club_name = request.form['new_club_name']
    club = Club.query.get(club_id)
    if club:
        club.club_name = new_club_name
        db.session.commit()
        flash(f"Club '{club.club_name}' updated successfully!", "success")
    else:
        flash("Club not found!", "danger")
    return redirect(url_for('edit_clubs'))

@app.route('/delete_club/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    club = Club.query.get(club_id)
    if club:
        db.session.delete(club)
        db.session.commit()
        flash(f"Club '{club.club_name}' deleted successfully!", "success")
    else:
        flash("Club not found!", "danger")
    return redirect(url_for('edit_clubs'))

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
    # Fetch only resources that are not currently lent out
    available_resources = Resource.query.filter_by(lent_out_to=None).all()

    if request.method == 'POST':
        selected_resource_id = request.form.get('resource_id')  # Use resource ID for saving
        due_date_str = request.form.get('due_date')  # Get due date as a string
        student_id = session.get('user_id')  # Assume the logged-in user's ID is stored in the session

        if selected_resource_id and due_date_str and student_id:
            try:
                # Convert due_date_str to a Python date object
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

                # Check if the resource is still available
                resource = Resource.query.get(selected_resource_id)
                if resource and resource.lent_out_to is None:
                    # Save the resource request to the database
                    new_request = ResourceRequest(
                        resource_id=selected_resource_id,
                        student_id=student_id,
                        due_date=due_date,
                        approved=False
                    )
                    db.session.add(new_request)
                    db.session.commit()
                    flash("Resource request submitted successfully!", "success")
                    return redirect(url_for('request_resource'))
                else:
                    flash("The selected resource is no longer available.", "danger")
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
        else:
            flash("Please select a resource, provide a due date, and ensure you are logged in.", "danger")

    return render_template('request_resource.html', resources=available_resources)

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
# def view_attendance():
#     # Simulated data (replace with DB call)
#     event_name = "Sample Event Name"
#     attendance_data = [
#         {"name": "Member 1", "status": "Present"},
#         {"name": "Member 2", "status": "Absent"},
#         {"name": "Member 3", "status": "Present"},
#         {"name": "Member 4", "status": "Absent"},
#         {"name": "Member 5", "status": "Present"},
#     ]
#     return render_template('view_attendance.html', event_name=event_name, attendance=attendance_data)

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