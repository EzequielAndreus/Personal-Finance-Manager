# Testing Guide for Personal Finance Tracker

This document explains how to run and understand the tests for the expense tracking application.

## Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_models.py           # Tests for User and Expense models
├── test_auth.py             # Tests for authentication routes
├── test_routes.py           # Tests for Flask routes
└── test_utils.py            # Test utilities and helper functions
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual model methods and properties
- Test business logic in isolation
- Fast execution, no external dependencies

### Integration Tests (`@pytest.mark.integration`)
- Test Flask routes and HTTP requests
- Test database interactions
- Test authentication flows

## Running Tests

### Prerequisites
Make sure you have pytest installed:
```bash
uv add pytest
```

### Basic Test Commands

1. **Run all tests:**
   ```bash
   make test
   ```

2. **Run only unit tests:**
   ```bash
   make test-unit
   ```

3. **Run only integration tests:**
   ```bash
   make test-integration
   ```

4. **Run with coverage (requires pytest-cov):**
   ```bash
   make test-cov
   ```

5. **Run specific test file:**
   ```bash
   pytest tests/test_models.py -v
   ```

6. **Run specific test:**
   ```bash
   pytest tests/test_models.py::TestUser::test_user_creation -v
   ```

## Test Fixtures

The test suite includes several useful fixtures:

### Database Fixtures
- `test_app`: Flask application with test database
- `client`: Test client for making HTTP requests
- `db_session`: Database session for direct database operations

### User Fixtures
- `sample_user`: Regular test user
- `admin_user`: Admin test user
- `authenticated_client`: Test client with logged-in user
- `admin_client`: Test client with logged-in admin

### Data Fixtures
- `sample_expense`: Basic expense for testing
- `sample_debt`: Basic debt for testing
- `multiple_users`: Multiple test users
- `multiple_expenses`: Multiple test expenses
- `overdue_debts`: Overdue debts for testing
- `upcoming_debts`: Upcoming debts for testing

## Test Coverage

The test suite covers:

### Models (`test_models.py`)
- ✅ User creation and password hashing
- ✅ User-expense relationships
- ✅ Expense creation and validation
- ✅ Debt properties (is_debt, is_overdue, days_until_due)
- ✅ Model string representations

### Authentication (`test_auth.py`)
- ✅ Login/logout functionality
- ✅ Session management
- ✅ Protected route access
- ✅ Invalid credential handling

### Routes (`test_routes.py`)
- ✅ Index/dashboard route
- ✅ Expense CRUD operations
- ✅ Debt listing
- ✅ Summary page
- ✅ Error handling (404, unauthorized access)

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Structure
```python
import pytest

class TestMyFeature:
    """Test cases for MyFeature"""
    
    @pytest.mark.unit
    def test_my_feature_behavior(self, fixture_name):
        """Test description"""
        # Arrange
        # Act
        # Assert
        assert condition
```

### Using Fixtures
```python
def test_with_user_data(sample_user, db_session):
    """Test that uses sample user"""
    # Your test code here
    assert sample_user.username == "testuser"
```

### Marking Tests
```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.slow          # Slow running test
```

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -v -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Local Variables on Failure
```bash
pytest tests/ -l
```

### Debug Specific Test
```bash
pytest tests/test_models.py::TestUser::test_user_creation -v -s --pdb
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
pytest tests/ --tb=short --junitxml=test-results.xml
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what is being tested
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use Fixtures**: Leverage pytest fixtures for setup
5. **Mock External Dependencies**: Use mocks for external services
6. **Test Edge Cases**: Include boundary conditions and error cases

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root
2. **Database Issues**: Tests use in-memory SQLite, no setup required
3. **Session Issues**: Use the provided authenticated client fixtures

### Getting Help

- Check pytest documentation: https://docs.pytest.org/
- Review the test fixtures in `conftest.py`
- Look at existing tests for examples
