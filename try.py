from app import app, db, Resource, ResourceRequest  # Import your database instance and models

with app.app_context():  # Ensure the Flask application context is active
    # Drop the ResourceRequest and Resource tables
    ResourceRequest.__table__.drop(db.engine)
    Resource.__table__.drop(db.engine)
    print("ResourceRequest and Resource tables have been deleted.")