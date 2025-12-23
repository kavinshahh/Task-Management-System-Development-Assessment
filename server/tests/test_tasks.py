import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import Users, Tasks

# PostgreSQL test database configuration
TEST_DATABASE_URL = "postgresql://kavin:kavin%40123@localhost:5432/test_db"

# Create engine for test database
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
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
    # Drop all tables after all tests are done
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database():
    """Clean all data from tables before each test"""
    db = TestingSessionLocal()
    try:
        # Delete in correct order (tasks before users due to foreign key)
        db.query(Tasks).delete()
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


@pytest.fixture
def auth_token(sample_user_data):
    """Create a user and return authentication token"""
    # Register user
    client.post("/register", json=sample_user_data)
    
    # Login and get token
    login_response = client.post(
        "/login",
        data={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    return login_response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": 1
    }


class TestCreateTask:
    """Test cases for creating tasks"""
    
    def test_create_task_success(self, auth_headers, sample_task_data):
        """Test successful task creation"""
        response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["priority"] == sample_task_data["priority"]
        assert data["complete"] == False
        assert "id" in data
    
    def test_create_task_without_auth(self, sample_task_data):
        """Test task creation without authentication token"""
        response = client.post("/tasks/", json=sample_task_data)
        
        assert response.status_code == 401
    
    def test_create_task_invalid_token(self, sample_task_data):
        """Test task creation with invalid token"""
        response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_create_task_without_description(self, auth_headers):
        """Test task creation without optional description"""
        task_data = {
            "title": "Task without description",
            "priority": 2
        }
        response = client.post(
            "/tasks/",
            json=task_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] is None
        assert data["priority"] == task_data["priority"]
    
    def test_create_task_missing_required_fields(self, auth_headers):
        """Test task creation with missing required fields"""
        incomplete_data = {"title": "Incomplete Task"}
        response = client.post(
            "/tasks/",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_create_multiple_tasks(self, auth_headers):
        """Test creating multiple tasks for same user"""
        tasks = [
            {"title": "Task 1", "description": "First task", "priority": 1},
            {"title": "Task 2", "description": "Second task", "priority": 2},
            {"title": "Task 3", "description": "Third task", "priority": 3}
        ]
        
        created_ids = []
        for task in tasks:
            response = client.post("/tasks/", json=task, headers=auth_headers)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])
        
        # All IDs should be unique
        assert len(created_ids) == len(set(created_ids))


class TestGetTasks:
    """Test cases for retrieving tasks"""
    
    def test_get_tasks_empty(self, auth_headers):
        """Test getting tasks when user has no tasks"""
        response = client.get("/tasks/", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_tasks_with_data(self, auth_headers, sample_task_data):
        """Test getting tasks when user has tasks"""
        # Create multiple tasks
        task1 = sample_task_data.copy()
        task2 = sample_task_data.copy()
        task2["title"] = "Second Task"
        task2["priority"] = 2
        
        client.post("/tasks/", json=task1, headers=auth_headers)
        client.post("/tasks/", json=task2, headers=auth_headers)
        
        # Get all tasks
        response = client.get("/tasks/", headers=auth_headers)
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        assert tasks[0]["title"] == task1["title"]
        assert tasks[1]["title"] == task2["title"]
    
    def test_get_tasks_without_auth(self):
        """Test getting tasks without authentication"""
        response = client.get("/tasks/")
        
        assert response.status_code == 401
    
    def test_user_only_sees_own_tasks(self, sample_task_data):
        """Test that users only see their own tasks"""
        # Create first user and task
        user1_data = {
            "email": "user1@example.com",
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
            "password": "password123",
            "phone_number": 1111111111
        }
        client.post("/register", json=user1_data)
        login1 = client.post(
            "/login",
            data={"username": "user1", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = login1.json()["access_token"]
        
        # Create second user and task
        user2_data = {
            "email": "user2@example.com",
            "username": "user2",
            "first_name": "User",
            "last_name": "Two",
            "password": "password456",
            "phone_number": 2222222222
        }
        client.post("/register", json=user2_data)
        login2 = client.post(
            "/login",
            data={"username": "user2", "password": "password456"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token2 = login2.json()["access_token"]
        
        # User 1 creates a task
        task1 = sample_task_data.copy()
        task1["title"] = "User 1 Task"
        client.post(
            "/tasks/",
            json=task1,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # User 2 creates a task
        task2 = sample_task_data.copy()
        task2["title"] = "User 2 Task"
        client.post(
            "/tasks/",
            json=task2,
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # User 1 should only see their task
        response1 = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token1}"}
        )
        tasks1 = response1.json()
        assert len(tasks1) == 1
        assert tasks1[0]["title"] == "User 1 Task"
        
        # User 2 should only see their task
        response2 = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token2}"}
        )
        tasks2 = response2.json()
        assert len(tasks2) == 1
        assert tasks2[0]["title"] == "User 2 Task"
    
    def test_get_tasks_includes_complete_status(self, auth_headers, sample_task_data):
        """Test that retrieved tasks include complete status"""
        # Create task
        client.post("/tasks/", json=sample_task_data, headers=auth_headers)
        
        # Get tasks
        response = client.get("/tasks/", headers=auth_headers)
        tasks = response.json()
        
        assert len(tasks) == 1
        assert "complete" in tasks[0]
        assert tasks[0]["complete"] == False


class TestMarkTaskComplete:
    """Test cases for marking tasks as complete"""
    
    def test_mark_complete_success(self, auth_headers, sample_task_data):
        """Test successfully marking a task as complete"""
        # Create a task
        create_response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Mark as complete
        response = client.put(
            f"/tasks/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["complete"] == True
    
    def test_mark_complete_nonexistent_task(self, auth_headers):
        """Test marking non-existent task as complete"""
        response = client.put(
            "/tasks/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]
    
    def test_mark_complete_without_auth(self, sample_task_data):
        """Test marking task as complete without authentication"""
        response = client.put("/tasks/1")
        
        assert response.status_code == 401
    
    def test_mark_complete_other_user_task(self, sample_task_data):
        """Test that user cannot mark another user's task as complete"""
        # Create first user and task
        user1_data = {
            "email": "user1@example.com",
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
            "password": "password123",
            "phone_number": 1111111111
        }
        client.post("/register", json=user1_data)
        login1 = client.post(
            "/login",
            data={"username": "user1", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = login1.json()["access_token"]
        
        # User 1 creates a task
        create_response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        task_id = create_response.json()["id"]
        
        # Create second user
        user2_data = {
            "email": "user2@example.com",
            "username": "user2",
            "first_name": "User",
            "last_name": "Two",
            "password": "password456",
            "phone_number": 2222222222
        }
        client.post("/register", json=user2_data)
        login2 = client.post(
            "/login",
            data={"username": "user2", "password": "password456"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token2 = login2.json()["access_token"]
        
        # User 2 tries to mark User 1's task as complete
        response = client.put(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 404  # Should not find task
    
    def test_mark_already_complete_task(self, auth_headers, sample_task_data):
        """Test marking an already complete task as complete again"""
        # Create and mark task as complete
        create_response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Mark as complete first time
        client.put(f"/tasks/{task_id}", headers=auth_headers)
        
        # Mark as complete second time
        response = client.put(f"/tasks/{task_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["complete"] == True


class TestDeleteTask:
    """Test cases for deleting tasks"""
    
    def test_delete_task_success(self, auth_headers, sample_task_data):
        """Test successfully deleting a task"""
        # Create a task
        create_response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Delete the task
        response = client.delete(
            f"/tasks/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "Task deleted successfully" in response.json()["message"]
        
        # Verify task is deleted
        get_response = client.get("/tasks/", headers=auth_headers)
        assert len(get_response.json()) == 0
    
    def test_delete_nonexistent_task(self, auth_headers):
        """Test deleting non-existent task"""
        response = client.delete(
            "/tasks/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]
    
    def test_delete_without_auth(self):
        """Test deleting task without authentication"""
        response = client.delete("/tasks/1")
        
        assert response.status_code == 401
    
    def test_delete_other_user_task(self, sample_task_data):
        """Test that user cannot delete another user's task"""
        # Create first user and task
        user1_data = {
            "email": "user1@example.com",
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
            "password": "password123",
            "phone_number": 1111111111
        }
        client.post("/register", json=user1_data)
        login1 = client.post(
            "/login",
            data={"username": "user1", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = login1.json()["access_token"]
        
        # User 1 creates a task
        create_response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        task_id = create_response.json()["id"]
        
        # Create second user
        user2_data = {
            "email": "user2@example.com",
            "username": "user2",
            "first_name": "User",
            "last_name": "Two",
            "password": "password456",
            "phone_number": 2222222222
        }
        client.post("/register", json=user2_data)
        login2 = client.post(
            "/login",
            data={"username": "user2", "password": "password456"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token2 = login2.json()["access_token"]
        
        # User 2 tries to delete User 1's task
        response = client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 404  # Should not find task
        
        # Verify task still exists for User 1
        get_response = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert len(get_response.json()) == 1
    
    def test_delete_complete_task(self, auth_headers, sample_task_data):
        """Test deleting a completed task"""
        # Create task
        create_response = client.post(
            "/tasks/",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Mark as complete
        client.put(f"/tasks/{task_id}", headers=auth_headers)
        
        # Delete the task
        response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "Task deleted successfully" in response.json()["message"]
    
    def test_delete_multiple_tasks(self, auth_headers):
        """Test deleting multiple tasks sequentially"""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            response = client.post(
                "/tasks/",
                json={
                    "title": f"Task {i+1}",
                    "description": f"Description {i+1}",
                    "priority": i+1
                },
                headers=auth_headers
            )
            task_ids.append(response.json()["id"])
        
        # Delete all tasks
        for task_id in task_ids:
            response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
            assert response.status_code == 200
        
        # Verify all tasks are deleted
        get_response = client.get("/tasks/", headers=auth_headers)
        assert len(get_response.json()) == 0

