# Milestone 1 - Personal Finance Management App

A Flask-based web application for managing personal expenses and debts with user authentication and a modern web interface.

## 🚀 Overview

This application provides a comprehensive solution for tracking personal finances, including:

- **User Authentication**: Secure login system with password hashing
- **Expense Management**: Create, edit, and track personal expenses
- **Debt Tracking**: Monitor debts with due dates and overdue notifications
- **Dashboard**: Visual overview of financial data
- **Category Management**: Organize expenses by categories
- **Responsive UI**: Modern web interface with Bootstrap styling

## 🏗️ Architecture

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML templates with Jinja2 templating
- **Containerization**: Docker with Docker Compose
- **Testing**: pytest for unit and integration tests

## 📋 Main Dependencies

### Core Dependencies

- **Flask 3.1.2** - Web framework
- **Flask-SQLAlchemy 3.1.1** - Database ORM
- **psycopg2-binary 2.9.11** - PostgreSQL adapter
- **Werkzeug 3.1.3** - WSGI utilities and password hashing

### Development Dependencies

- **pytest 8.4.2** - Testing framework
- **Docker & Docker Compose** - Containerization

## 🛠️ Installation & Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Quick Start with Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Milestone-1
   ```

2. **Build and start the application**

   ```bash
   make build
   make up
   ```

3. **Initialize the database**

   ```bash
   make migrate
   ```

4. **Access the application**
   - Web app: <http://localhost:5001>
   - Database: localhost:5432

## 📖 Makefile Commands

The project includes a comprehensive Makefile for easy development and deployment:

### Development Commands

```bash
make help          # Show all available commands
make build         # Build Docker images
make up            # Start development environment
make down          # Stop development environment
make logs          # View container logs
make restart       # Restart all services
make restart-web   # Restart only the web service
```

### Database Commands

```bash
make migrate       # Run database migrations and create tables
make db-shell      # Access PostgreSQL shell
```

### Testing Commands

```bash
make test          # Run tests in Docker container
```

### Production Commands

```bash
make prod-up       # Start production environment
make prod-down     # Stop production environment
```

### Maintenance Commands

```bash
make clean         # Clean up containers and volumes
make clean-all     # Clean up containers, volumes, and images
make status        # Show container status
```

### Development Helpers

```bash
make shell         # Access Flask container shell for debugging
```

## 🗄️ Database Schema

### Users Table

- `id` - Primary key
- `username` - Unique username
- `password_hash` - Hashed password
- `is_admin` - Admin privileges flag
- `created_at` - Account creation timestamp

### Expenses Table

- `id` - Primary key
- `name` - Expense description
- `amount` - Expense amount
- `category` - Expense category
- `date` - Expense date
- `due_date` - Due date (for debts)
- `element` - Additional element info
- `comment` - Optional comments
- `user_id` - Foreign key to users table
- `created_at` - Record creation timestamp

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key for sessions
- `PORT` - Application port (default: 5001)
- `SEED_PREDEFINED` - Seed database with sample data
- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_DEBUG` - Enable/disable debug mode

### Database Configuration

- **Host**: localhost (development) / db (Docker)
- **Port**: 5432
- **Database**: postgres
- **User**: postgres
- **Password**: password (change in production)

## 🧪 Testing

Run the test suite using:

```bash
make test
```

The project includes comprehensive tests for:

- Authentication routes
- Expense management
- Database models
- Utility functions

## 🚀 Deployment

### Development Deployment

```bash
make up
```

### Production Deployment

```bash
make prod-up
```

### Environment Setup

1. Set environment variables in `.env` file
2. Update `SECRET_KEY` for production
3. Configure proper database credentials
4. Set `FLASK_ENV=production`

## 📁 Project Structure

```
Milestone-1/
├── src/
│   ├── app.py                 # Main Flask application
│   ├── main.py               # Entry point
│   ├── controllers/          # Route handlers
│   │   ├── auth_route.py     # Authentication routes
│   │   ├── expense_route.py  # Expense management routes
│   │   └── dashboard_route.py # Dashboard routes
│   ├── models/               # Database models
│   │   ├── user.py          # User model
│   │   └── expense.py       # Expense model
│   ├── templates/            # HTML templates
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── docker-compose.yml       # Development Docker setup
├── docker-compose.prod.yml  # Production Docker setup
├── Dockerfile              # Docker image configuration
├── Makefile               # Development commands
└── requirements.txt       # Python dependencies
```

## 🔐 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- SQL injection protection via SQLAlchemy ORM
- CSRF protection (Flask-WTF recommended for production)
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## 📝 License

This project is part of a milestone assignment. Please refer to your course guidelines for usage terms.

## 🆘 Troubleshooting

### Common Issues

**Database connection errors:**

```bash
make down
make up
make migrate
```

**Port conflicts:**

- Change the port in `docker-compose.yml` if 5001 is occupied

**Permission issues:**

```bash
sudo make clean
make build
make up
```

**View logs for debugging:**

```bash
make logs
```

For more help, check the container status:

```bash
make status
```
