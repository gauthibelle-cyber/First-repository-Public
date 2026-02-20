"""Pytest configuration and fixtures for API tests"""
import pytest
from fastapi.testclient import TestClient
from src.app import app
import copy


@pytest.fixture
def test_activities():
    """Provide a clean copy of test activities data"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer training and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Basketball practice and tournament participation",
            "schedule": "Mondays, Wednesdays, 5:00 PM - 6:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 24,
            "participants": ["aiden@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu", "zoe@mergington.edu"]
        }
    }


@pytest.fixture
def client(test_activities):
    """Provide a test client with clean app state"""
    # Import here to get the actual activities dict from app
    from src import app as app_module
    
    # Store original activities
    original_activities = copy.deepcopy(app_module.activities)
    
    # Replace with test data
    app_module.activities.clear()
    app_module.activities.update(test_activities)
    
    # Create test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Restore original activities after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)
