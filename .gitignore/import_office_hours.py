import pandas as pd
from datetime import datetime, timedelta
from app import app, db, Appointment, User, generate_password_hash # Import the Flask app

# Path to the Excel file
file_path = "data.xlsx"

# Read the Excel file
data = pd.read_excel(file_path)

# Define the target date for recurring_until
target_date = datetime.strptime("2025-08-19", "%Y-%m-%d").date()

# Use the Flask application context
with app.app_context():
    # Iterate through the rows and insert data into the database
    for index, row in data.iterrows():
        # Generate a unique user_id and password for the instructor
        user_id = row['first_name'].strip().lower() + row['last_name'].strip().lower()
        password = row['first_name'][0].lower() + row['last_name'][0].lower()

        # Check if the instructor exists in the User table
        instructor = User.query.filter_by(user_id=user_id).first()
        if not instructor:
            # Add the instructor as a user
            new_instructor = User(
                user_id=user_id,
                first_name=row['first_name'],
                last_name=row['last_name'],
                password=generate_password_hash(password),  # Set a default password (hashed in production)
                role="instructor",
                major=row['program']  # Use 'N/A' if the major column is missing
            )
            db.session.add(new_instructor)
            db.session.commit()  # Commit to get the new instructor's ID
            instructor = new_instructor

        # Schedule office hours for each week until the recurring_until date
        current_date = datetime.today().date()
        while current_date <= target_date:
            if current_date.strftime('%A') == row['day']:  # Match the day of the week
                new_appointment = Appointment(
                    t_user_id=instructor.id,
                    day=current_date.strftime("%Y-%m-%d"),
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    booked=False,
                    appointment_type="office_hours",
                    recurring_until=target_date
                )
                db.session.add(new_appointment)
            current_date += timedelta(days=1)  # Increment by one day

    # Commit the changes to the database
    db.session.commit()

print("Instructors and office hours data imported successfully!")