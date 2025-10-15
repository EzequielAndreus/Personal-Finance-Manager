from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con expenses
    expenses = db.relationship(
        "Expense",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        """Establece el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)  # null = no es deuda
    element = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_debt(self):
        """Retorna True si el expense es una deuda (tiene due_date)"""
        return self.due_date is not None

    @property
    def is_overdue(self):
        """Retorna True si la deuda está vencida"""
        if not self.is_debt:
            return False
        return self.due_date < datetime.utcnow().date()

    @property
    def days_until_due(self):
        """Retorna días restantes hasta vencimiento (negativo si está vencido)"""
        if not self.is_debt:
            return None
        delta = self.due_date - datetime.utcnow().date()
        return delta.days

    def __repr__(self):
        return f"<Expense {self.name} - ${self.amount}>"
