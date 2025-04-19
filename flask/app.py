from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "Student" or "SL"

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
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        role = "Student" if domain == "st" else "SL"

        # Look up the user in the database
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['role'] = role
            return redirect(url_for('welcome'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        if not username or not password or password != confirm_password:
            error = "Invalid input. Ensure passwords match and username is provided."
        elif User.query.filter_by(username=username).first():
            error = "username already exists. Please use a different one."
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role="Student")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/welcome')
def welcome():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))

    return render_template('welcome.html', username=session['username'], role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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