"""Comprehensive tests for Mergington High School API endpoints"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Verify GET /activities returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Verify we have 9 activities
        assert len(activities) == 9
        
        # Verify specific activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Science Club" in activities
    
    def test_get_activities_returns_correct_structure(self, client):
        """Verify activities have correct data structure"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        
        # Verify all required fields
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
        # Verify data types
        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_participants_list(self, client):
        """Verify participants list contains correct initial data"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Verify GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]
    
    def test_root_redirect_with_follow(self, client):
        """Verify redirect destination is accessible"""
        response = client.get("/", follow_redirects=True)
        
        # Should get 200 from the redirected location
        assert response.status_code == 200


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client):
        """Verify successful signup of a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was actually added
        check_response = client.get("/activities")
        activities = check_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_multiple_participants(self, client):
        """Verify multiple participants can signup"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Art%20Studio/signup?email={email1}")
        response2 = client.post(f"/activities/Art%20Studio/signup?email={email2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        check_response = client.get("/activities")
        participants = check_response.json()["Art Studio"]["participants"]
        assert email1 in participants
        assert email2 in participants
    
    def test_signup_invalid_activity_not_found(self, client):
        """Verify signup fails for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Verify duplicate signup is rejected"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response1.status_code == 400
        data = response1.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_at_capacity(self, client):
        """Verify signup fails when activity is at max capacity"""
        # Basketball Club has max_participants=15, currently has 2
        # Add 13 more to reach capacity
        for i in range(13):
            response = client.post(
                f"/activities/Basketball%20Club/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Try to signup when at capacity
        response = client.post(
            "/activities/Basketball%20Club/signup?email=full@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "maximum capacity" in data["detail"]
    
    def test_signup_exactly_at_capacity(self, client):
        """Verify last spot in activity can be filled"""
        # Art Studio has max_participants=16, currently has 1
        # Fill remaining 15 spots
        for i in range(15):
            response = client.post(
                f"/activities/Art%20Studio/signup?email=artist{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Verify we're at capacity
        check_response = client.get("/activities")
        art_studio = check_response.json()["Art Studio"]
        assert len(art_studio["participants"]) == art_studio["max_participants"]
    
    def test_signup_various_activities(self, client):
        """Verify signup works for different activities"""
        test_email = "researcher@mergington.edu"
        activities_to_test = [
            "Chess Club",
            "Programming Class",
            "Science Club"
        ]
        
        for activity_name in activities_to_test:
            response = client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email={test_email}"
            )
            assert response.status_code == 200


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client):
        """Verify successful unregistration of a participant"""
        email = "michael@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        
        # Verify participant was actually removed
        check_response = client.get("/activities")
        activities = check_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_invalid_activity_not_found(self, client):
        """Verify unregister fails for non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Club/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_participant(self, client):
        """Verify unregister fails for participant not signed up"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notstudent@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_already_removed(self, client):
        """Verify unregister fails if already unregistered"""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_last_participant(self, client):
        """Verify can unregister the last participant from an activity"""
        activity = "Soccer Team"
        email = "alex@mergington.edu"  # Only participant
        
        # Get initial state
        check1 = client.get("/activities").json()
        assert len(check1[activity]["participants"]) == 1
        
        # Unregister
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify removed
        check2 = client.get("/activities").json()
        assert len(check2[activity]["participants"]) == 0
        assert email not in check2[activity]["participants"]


class TestIntegration:
    """Integration tests for complex scenarios"""
    
    def test_signup_and_unregister_roundtrip(self, client):
        """Verify signup followed by unregister works correctly"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Initially not signed up
        check1 = client.get("/activities").json()
        assert email not in check1[activity]["participants"]
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        check2 = client.get("/activities").json()
        assert email in check2[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        check3 = client.get("/activities").json()
        assert email not in check3[activity]["participants"]
    
    def test_capacity_lifecycle(self, client):
        """Verify capacity management through signup and unregister"""
        activity = "Debate Team"
        initial_response = client.get("/activities").json()
        initial_participants = len(initial_response[activity]["participants"])
        max_capacity = initial_response[activity]["max_participants"]
        slots_available = max_capacity - initial_participants
        
        # Fill remaining slots
        emails = []
        for i in range(slots_available):
            email = f"debater{i}@mergington.edu"
            emails.append(email)
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify at capacity
        check1 = client.get("/activities").json()
        assert len(check1[activity]["participants"]) == max_capacity
        
        # Try to add one more - should fail
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email=extra@mergington.edu"
        )
        assert response.status_code == 400
        
        # Unregister one
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={emails[0]}"
        )
        assert response.status_code == 200
        
        # Verify we can now signup again
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email=extra@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify at capacity again
        check2 = client.get("/activities").json()
        assert len(check2[activity]["participants"]) == max_capacity
