from models import db, User


def init_db(app):
    """Create the tables and the initial admin user"""
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", is_admin=True)
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
        else:
            print("Database already initialized")
