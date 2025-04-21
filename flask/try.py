from app import db, Club, app  # Import db, Club model, and app from your Flask app

# Use the application context
with app.app_context():
    # Recreate tables with the new schema
    db.create_all()

    # Add clubs to the database
    club1 = Club(club_name="SerVe")
    club2 = Club(club_name="DiscO")

    # Add the clubs to the session
    db.session.add(club1)
    db.session.add(club2)

    # Commit the changes to the database
    db.session.commit()

    print("Clubs added successfully!")