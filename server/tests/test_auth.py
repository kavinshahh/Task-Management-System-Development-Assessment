import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import Users

TEST_DATABASE_URL = "postgresql://kavin:kavin%40123@localhost:5432/test_db"


engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables before all tests"""
    Base.metadata.create_all(bind=engine)
    yield
   
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database():
    """Clean all data from tables before each test"""
    db = TestingSessionLocal()
    try:
     
        db.query(Users).delete()
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123",
        "phone_number": 1234567890
    }


class TestRegister:
    """Test cases for user registration"""
    
    def test_register_success(self, sample_user_data):
        """Test successful user registration"""
        response = client.post("/register", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert data["is_active"] == True
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_register_duplicate_username(self, sample_user_data):
        """Test registration with duplicate username"""
        # Register first user
        client.post("/register", json=sample_user_data)
        
        # Try to register with same username but different email
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "Username or email already exists" in response.json()["detail"]
    
    def test_register_duplicate_email(self, sample_user_data):
        """Test registration with duplicate email"""
     
        client.post("/register", json=sample_user_data)
        
        # Try to register with same email but different username
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"
        response = client.post("/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "Username or email already exists" in response.json()["detail"]
    
    def test_register_invalid_email(self, sample_user_data):
        """Test registration with invalid email format"""
        invalid_data = sample_user_data.copy()
        invalid_data["email"] = "notanemail"
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            "email": "test@example.com",
            "username": "testuser"
            # Missing other required fields
        }
        response = client.post("/register", json=incomplete_data)
        
        assert response.status_code == 422


class TestLogin:
    """Test cases for user login"""
    
    def test_login_success(self, sample_user_data):
        """Test successful login"""
        # Register user first
        client.post("/register", json=sample_user_data)
        
        # Login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = client.post(
            "/login",
            data=login_data,  # OAuth2PasswordRequestForm expects form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_username(self, sample_user_data):
        """Test login with non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "somepassword"
        }
        response = client.post(
            "/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_wrong_password(self, sample_user_data):
        """Test login with incorrect password"""
        # Register user first
        client.post("/register", json=sample_user_data)
        
        # Try to login with wrong password
        login_data = {
            "username": sample_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post(
            "/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        response = client.post(
            "/login",
            data={},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
    
    def test_token_can_be_used(self, sample_user_data):
        """Test that the token received from login can be used for authentication"""
        # Register and login
        client.post("/register", json=sample_user_data)
        login_response = client.post(
            "/login",
            data={
                "username": sample_user_data["username"],
                "password": sample_user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        
        # Try to access protected endpoint with token
        response = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200  # Should be able to access protected route
    
    def test_password_is_hashed(self, sample_user_data):
        """Test that passwords are properly hashed in database"""
        # Register user
        client.post("/register", json=sample_user_data)
        
        # Check database directly
        db = TestingSessionLocal()
        try:
            user = db.query(Users).filter(
                Users.username == sample_user_data["username"]
            ).first()
            
            assert user is not None
            # Password should be hashed, not plain text
            assert user.hashed_password != sample_user_data["password"]
            # Bcrypt hashes start with $2b$
            assert user.hashed_password.startswith("$2b$")
        finally:
            db.close()
    
    def test_multiple_logins_generate_valid_tokens(self, sample_user_data):
        """Test that multiple logins generate different valid tokens"""
        # Register user
        client.post("/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        # First login
        response1 = client.post(
            "/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = response1.json()["access_token"]
        
        # Second login
        response2 = client.post(
            "/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token2 = response2.json()["access_token"]
        
        # Tokens should be different (due to timestamp in exp claim)
        assert token1 != token2
        
        # Both tokens should work
        tasks_response1 = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token1}"}
        )
        tasks_response2 = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert tasks_response1.status_code == 200
        assert tasks_response2.status_code == 200