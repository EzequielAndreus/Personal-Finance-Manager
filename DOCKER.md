# Docker Setup

This project is fully dockerized with PostgreSQL database support.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start development environment:**
   ```bash
   make up
   ```

3. **Access the application:**
   - Flask app: http://localhost:5001
   - PostgreSQL: localhost:5432

## Available Commands

- `make build` - Build Docker images
- `make up` - Start development environment
- `make down` - Stop development environment
- `make logs` - View container logs
- `make shell` - Access Flask container shell
- `make db-shell` - Access PostgreSQL shell
- `make test` - Run tests in Docker
- `make clean` - Clean up containers and volumes
- `make prod-up` - Start production environment
- `make prod-down` - Stop production environment
- `make migrate` - Run database migrations

## Environment Variables

Edit `.env` file to configure:
- Database credentials
- Flask secret key
- Port settings
- Seed data options

## Production Deployment

For production, use:
```bash
make prod-up
```

Make sure to set proper environment variables in your `.env` file for production.
