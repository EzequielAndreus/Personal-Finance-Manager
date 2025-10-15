import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/postgres'
    # name = postgres, password = password, host = localhost, dbname = postgres
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
db = SQLAlchemy(app)

# Model of Expense
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Double, nullable=False)
    categoy = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    element = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(300), nullable=False)

# Model of Debt
class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Double, nullable=False)
    categoy = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    dueDate = db.Column(db.DateTime, nullable=False)
    element = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(300), nullable=False)

def main():
    print("Hello from milestone-1!")

if __name__ == "__main__":
    main()
