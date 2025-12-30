"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test cases for getting activities"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
    def test_get_activities_includes_expected_activities(self, client):
        """Test that the response includes expected activities"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", "Basketball Team"]
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"


class TestSignup:
    """Test cases for signing up for activities"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=student@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Chess Club" in data["message"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        response = client.post("/activities/Fake Activity/signup?email=student@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot signup twice for the same activity"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Attempt duplicate signup
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count"""
        email = "newstudent@mergington.edu"
        
        # Get initial participant count
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Soccer Club"]["participants"])
        
        # Sign up
        response = client.post(f"/activities/Soccer Club/signup?email={email}")
        assert response.status_code == 200
        
        # Get updated participant count
        response_after = client.get("/activities")
        count_after = len(response_after.json()["Soccer Club"]["participants"])
        
        assert count_after == count_before + 1


class TestUnregister:
    """Test cases for unregistering from activities"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        email = "unregister_test@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Art Studio/signup?email={email}")
        
        # Then unregister
        response = client.post(f"/activities/Art Studio/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from a non-existent activity"""
        response = client.post("/activities/Fake Activity/unregister?email=student@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister for a student not signed up"""
        response = client.post("/activities/Music Band/unregister?email=notsignup@mergington.edu")
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases the participant count"""
        email = "removestudent@mergington.edu"
        
        # Sign up first
        client.post(f"/activities/Debate Society/signup?email={email}")
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Debate Society"]["participants"])
        
        # Unregister
        response = client.post(f"/activities/Debate Society/unregister?email={email}")
        assert response.status_code == 200
        
        # Check participant count decreased
        response_after = client.get("/activities")
        count_after = len(response_after.json()["Debate Society"]["participants"])
        
        assert count_after == count_before - 1


class TestRoot:
    """Test cases for root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
