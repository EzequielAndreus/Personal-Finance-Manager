from models import Expense, db, User
from datetime import datetime, timedelta

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

def seed_predefined_data(app):
    """Create 5 users with predefined expenses."""
    with app.app_context():
        # Check if data already exists
        if User.query.count() > 1:  # More than just admin
            print("Users already exist; skipping predefined data seeding.")
            return

        # Define the 5 users
        users_data = [
            {"username": "Javier", "password": "password", "is_admin": True},
            {"username": "Rodrigo", "password": "password", "is_admin": False},
            {"username": "Charlie", "password": "Charlie123", "is_admin": False},
            {"username": "Diana", "password": "Diana123", "is_admin": False},
            {"username": "Eve", "password": "Eve123", "is_admin": True},
        ]

        # Create users
        created_users = {}
        for user_data in users_data:
            user = User(username=user_data["username"], is_admin=user_data["is_admin"])
            user.set_password(user_data["password"])
            db.session.add(user)
            created_users[user_data["username"]] = user

        db.session.commit()
        print(f"Created {len(users_data)} users: {', '.join(u['username'] for u in users_data)}")

        # Define predefined expenses for each user
        expenses_data = {
            "Javier": [
                {"name": "Grocery Shopping", "amount": 85.50, "category": "Food", "date": "2025-01-15", "element": "Supermarket", "comment": "Weekly groceries"},
                {"name": "Gas Bill", "amount": 120.00, "category": "Utilities", "date": "2025-01-10", "element": "Gas Company", "comment": "Monthly bill", "due_date": "2025-10-31"},
                {"name": "Netflix Subscription", "amount": 15.99, "category": "Leisure", "date": "2025-01-01", "element": "Netflix", "comment": "Monthly subscription"},
            ],
            "Rodrigo": [
                {"name": "Uber Ride", "amount": 12.50, "category": "Transport", "date": "2024-01-20", "element": "Uber", "comment": "Airport ride"},
                {"name": "Restaurant Dinner", "amount": 45.00, "category": "Food", "date": "2024-01-18", "element": "Restaurant", "comment": "Date night"},
                {"name": "Gym Membership", "amount": 50.00, "category": "Health", "date": "2024-01-01", "element": "Fitness Center", "comment": "Monthly fee", "due_date": "2024-02-01"},
            ],
            "Charlie": [
                {"name": "Electricity Bill", "amount": 95.75, "category": "Utilities", "date": "2024-01-12", "element": "Power Company", "comment": "Monthly bill"},
                {"name": "Coffee Shop", "amount": 4.50, "category": "Food", "date": "2024-01-22", "element": "Starbucks", "comment": "Morning coffee"},
                {"name": "Phone Bill", "amount": 65.00, "category": "Utilities", "date": "2024-01-05", "element": "Mobile Carrier", "comment": "Monthly plan", "due_date": "2024-02-05"},
            ],
            "Diana": [
                {"name": "Rent Payment", "amount": 1200.00, "category": "Rent", "date": "2024-01-01", "element": "Landlord", "comment": "Monthly rent", "due_date": "2024-02-01"},
                {"name": "Book Purchase", "amount": 25.99, "category": "Leisure", "date": "2024-01-16", "element": "Bookstore", "comment": "Programming book"},
                {"name": "Doctor Visit", "amount": 150.00, "category": "Health", "date": "2024-01-14", "element": "Medical Center", "comment": "Annual checkup"},
            ],
            "Eve": [
                {"name": "Office Supplies", "amount": 35.00, "category": "Work", "date": "2024-01-19", "element": "Office Depot", "comment": "Notebooks and pens"},
                {"name": "Team Lunch", "amount": 75.00, "category": "Food", "date": "2024-01-17", "element": "Restaurant", "comment": "Team building"},
                {"name": "Software License", "amount": 99.00, "category": "Work", "date": "2024-01-01", "element": "Software Co", "comment": "Annual license", "due_date": "2024-02-01"},
            ],
        }

        # Create expenses for each user
        total_expenses = 0
        for username, user_expenses in expenses_data.items():
            user = created_users[username]
            for exp_data in user_expenses:
                expense = Expense(
                    name=exp_data["name"],
                    amount=exp_data["amount"],
                    category=exp_data["category"],
                    date=datetime.strptime(exp_data["date"], "%Y-%m-%d").date(),
                    element=exp_data["element"],
                    comment=exp_data["comment"],
                    user_id=user.id,
                )
                
                # Add due_date if specified (makes it a debt)
                if "due_date" in exp_data:
                    expense.due_date = datetime.strptime(exp_data["due_date"], "%Y-%m-%d").date()
                
                db.session.add(expense)
                total_expenses += 1

        db.session.commit()
        print(f"Created {total_expenses} predefined expenses across all users.")