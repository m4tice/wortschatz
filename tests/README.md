# Test Suite Documentation

## Overview

This comprehensive test suite provides unit and integration tests for the Wortschatz Flask application. The tests cover all major components including authentication, database operations, utility functions, and the wortschatz learning module.

## Test Structure

```
tests/
├── test_comprehensive.py      # Main comprehensive test suite
├── test_authentication.py     # Authentication module tests
├── test_database.py          # Database operations tests
├── test_utils.py             # Utility functions tests
├── test_authenticator.py     # Authenticator class tests
├── test_wortschatz.py        # Wortschatz module tests
├── test_integration.py       # Full application integration tests
└── test_responses.py         # Original response tests
```

## Test Categories

### 1. Authentication Tests (`test_authentication.py`)
- **Route Testing**: Login, registration, and password recovery pages
- **API Endpoints**: Authentication and registration API calls
- **Session Management**: Login/logout functionality
- **Security**: URL parameter handling and response headers

### 2. Database Tests (`test_database.py`)
- **User Model**: CRUD operations for user management
- **Database Interface**: Connection handling and query execution
- **SQL Injection Protection**: Parameterized query verification
- **Error Handling**: Database connection and query error scenarios

### 3. Utility Tests (`test_utils.py`)
- **Login Required Decorator**: Authentication enforcement
- **Session Management**: User login/logout functions
- **Git Integration**: Branch information retrieval
- **Security Considerations**: Session isolation and data validation

### 4. Authenticator Tests (`test_authenticator.py`)
- **Password Hashing**: BCrypt integration and security
- **Password Verification**: Correct/incorrect password handling
- **User Registration**: New user creation and duplicate handling
- **Security**: Timing attack resistance and hash strength

### 5. Wortschatz Tests (`test_wortschatz.py`)
- **Protected Routes**: Authentication requirement enforcement
- **Template Rendering**: Content verification for modes and session pages
- **Navigation**: Cross-route functionality and session persistence
- **Error Handling**: Invalid routes and method restrictions

### 6. Integration Tests (`test_integration.py`)
- **Full Workflows**: End-to-end user registration and login
- **Cross-Blueprint Navigation**: Multi-module application flow
- **Security Testing**: Comprehensive authentication and injection protection
- **Performance**: Multi-session handling and database operations

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_authentication.py

# Run specific test class
pytest tests/test_database.py::TestUserModel

# Run specific test method
pytest tests/test_utils.py::TestLoginRequired::test_login_required_with_authenticated_user
```

### Advanced Test Options

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html

# Run only unit tests (exclude integration)
pytest -m "not integration"

# Run only database-related tests
pytest -m database

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto

# Run tests with detailed output
pytest -v --tb=long

# Run tests and stop at first failure
pytest -x
```

### Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.database`: Tests requiring database access
- `@pytest.mark.authentication`: Authentication-related tests
- `@pytest.mark.slow`: Tests that take longer to execute

Example usage:
```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run authentication and database tests
pytest -m "authentication or database"
```

## Test Configuration

### pytest.ini
The test configuration is defined in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --tb=short --strict-markers --disable-warnings --color=yes
```

### Environment Setup

Tests use isolated environments with:
- Temporary databases for database tests
- Mock objects for external dependencies
- Test-specific Flask configurations
- Isolated session management

## Coverage Requirements

The test suite aims for comprehensive coverage:

### Current Coverage Areas:
- ✅ **Authentication Routes**: 100% route coverage
- ✅ **Database Operations**: All CRUD operations
- ✅ **User Management**: Registration, login, logout
- ✅ **Session Handling**: Login required decorator, session persistence
- ✅ **Template Rendering**: All HTML templates
- ✅ **Error Handling**: 404, 405, authentication failures
- ✅ **Security**: SQL injection, session isolation
- ✅ **Integration**: Full application workflows

### Key Test Scenarios:

1. **User Registration and Login**
   ```python
   # New user registration
   response = client.get('/auth/registration/newuser/password')
   assert response.status_code == 200
   
   # Immediate login after registration
   response = client.get('/auth/login/newuser/password')
   assert JSON response indicates success
   ```

2. **Protected Route Access**
   ```python
   # Without authentication - redirects
   response = client.get('/wortschatz/modes')
   assert response.status_code == 302
   
   # With authentication - succeeds
   with client.session_transaction() as sess:
       sess['user_id'] = 'testuser'
   response = client.get('/wortschatz/modes')
   assert response.status_code == 200
   ```

3. **Database Operations**
   ```python
   # User creation
   user = User(temp_db)
   result = user.create_user('testuser', 'hashedpass')
   assert result is True
   
   # User retrieval
   retrieved = user.get_user_by_username('testuser')
   assert retrieved[1] == 'testuser'
   ```

## Mock Usage

The test suite extensively uses mocking for:

### Database Mocking
```python
@pytest.fixture
def mock_user_db():
    return MagicMock(spec=User)

def test_authenticate_success(self, authenticator, mock_user_db):
    mock_user_db.get_user_by_username.return_value = ('user', 'user', 'hash')
    result = authenticator.authenticate('user', 'pass')
```

### External Service Mocking
```python
@patch('app.util.Repo')
def test_get_git_branch(self, mock_repo):
    mock_repo.return_value.active_branch.name = 'main'
    result = get_git_branch()
    assert result == 'main'
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

### GitHub Actions Integration
```yaml
- name: Run tests
  run: |
    python -m pytest tests/ --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
```

### Local Development
```bash
# Pre-commit test run
pytest tests/ --cov=app --cov-report=term-missing

# Quick test run during development
pytest tests/test_authentication.py -v
```

## Best Practices

### Test Organization
1. **Arrange-Act-Assert**: Clear test structure
2. **Descriptive Names**: Test names describe the scenario
3. **Single Responsibility**: Each test verifies one behavior
4. **Fixture Reuse**: Common setup shared via fixtures

### Test Data Management
1. **Temporary Databases**: Isolated test databases
2. **Mock Objects**: External dependencies mocked
3. **Test Cleanup**: Automatic cleanup of test artifacts
4. **Data Isolation**: Tests don't affect each other

### Error Testing
1. **Exception Handling**: Verify error conditions
2. **Edge Cases**: Boundary conditions tested
3. **Invalid Input**: Malformed data handling
4. **Security**: Injection and authentication bypass attempts

## Troubleshooting

### Common Issues

1. **Database Lock Errors**
   ```bash
   # Solution: Ensure proper cleanup in fixtures
   pytest tests/test_database.py -v
   ```

2. **Import Errors**
   ```bash
   # Solution: Check PYTHONPATH includes project root
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest
   ```

3. **Session Conflicts**
   ```bash
   # Solution: Use session_transaction() context manager
   with client.session_transaction() as sess:
       sess['user_id'] = 'testuser'
   ```

### Debug Mode

Enable debug output for troubleshooting:
```bash
# Run with debug output
pytest -s --log-cli-level=DEBUG

# Run specific test with debugging
pytest tests/test_authentication.py::TestAuthenticationAPI::test_authenticate_valid_credentials -s -v
```

## Performance Considerations

### Test Execution Time
- **Unit Tests**: < 0.1s per test
- **Integration Tests**: < 1s per test
- **Database Tests**: < 0.5s per test

### Optimization Strategies
1. **Parallel Execution**: Use pytest-xdist for parallel runs
2. **Test Selection**: Use markers to run specific test subsets
3. **Mock Usage**: Reduce external dependencies
4. **Database Fixtures**: Reuse database setup where possible

## Future Enhancements

### Planned Additions
1. **Performance Tests**: Load testing for critical paths
2. **API Testing**: REST API endpoint validation
3. **Browser Testing**: Selenium integration for UI tests
4. **Security Testing**: Automated security vulnerability scanning

### Test Metrics
- **Code Coverage**: Target 95%+ coverage
- **Test Count**: 100+ individual test cases
- **Execution Time**: < 30 seconds for full suite
- **Reliability**: 99%+ success rate in CI/CD

## Contributing

When adding new tests:

1. **Follow Naming Convention**: `test_feature_scenario`
2. **Add Docstrings**: Describe test purpose
3. **Use Appropriate Markers**: Categorize tests correctly
4. **Maintain Coverage**: Ensure new code is tested
5. **Update Documentation**: Document new test scenarios

Example new test:
```python
def test_new_feature_success_case(self, client):
    """Test that new feature works in success scenario."""
    # Arrange
    setup_test_data()
    
    # Act
    response = client.get('/new-feature/endpoint')
    
    # Assert
    assert response.status_code == 200
    assert b'expected_content' in response.data
```

## Miscellaneous
**Test Runner Script**
```
python run_tests.py --suite auth --coverage --verbose
```