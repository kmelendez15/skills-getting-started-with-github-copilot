"""Tests for the Mergington High School Activities API."""

import pytest


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Verify expected activities exist
        assert "Basketball" in activities
        assert "Soccer" in activities
        assert "Art Club" in activities
        assert "Programming Class" in activities
    
    def test_get_activities_contains_activity_details(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_participant_count(self, client):
        """Test that activities contain correct participant information."""
        response = client.get("/activities")
        activities = response.json()
        
        # Basketball should have at least one participant
        assert len(activities["Basketball"]["participants"]) > 0
        assert activities["Basketball"]["max_participants"] == 15


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant for an activity."""
        email = "newstudent@mergington.edu"
        activity = "Science Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email in response.json()["message"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signups are rejected."""
        email = "alex@mergington.edu"  # Already signed up for Basketball
        activity = "Basketball"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a non-existent activity."""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_updates_participant_list(self, client, reset_activities):
        """Test that signup updates the activity's participant list."""
        email = "newstudent@mergington.edu"
        activity = "Debate Team"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up new participant
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify participant count increased
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity]["participants"])
        assert updated_count == initial_count + 1
        assert email in updated_response.json()[activity]["participants"]


class TestUnsignupEndpoint:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_unsignup_existing_participant(self, client, reset_activities):
        """Test removing an existing participant from an activity."""
        email = "alex@mergington.edu"
        activity = "Basketball"
        
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
    
    def test_unsignup_nonexistent_participant(self, client, reset_activities):
        """Test removing a participant who is not signed up."""
        email = "notregistered@mergington.edu"
        activity = "Basketball"
        
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unsignup_from_nonexistent_activity(self, client, reset_activities):
        """Test removing a participant from a non-existent activity."""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unsignup_updates_participant_list(self, client, reset_activities):
        """Test that unsignup updates the activity's participant list."""
        email = "alex@mergington.edu"
        activity = "Basketball"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Remove participant
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify participant count decreased
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity]["participants"])
        assert updated_count == initial_count - 1
        assert email not in updated_response.json()[activity]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_signup_then_unsignup(self, client, reset_activities):
        """Test signing up and then unregistering a participant."""
        email = "integration@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify sign up
        check_response = client.get("/activities")
        assert email in check_response.json()[activity]["participants"]
        
        # Unsign up
        unsignup_response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert unsignup_response.status_code == 200
        
        # Verify unsign up
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple different participants signing up for the same activity."""
        activity = "Music Ensemble"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up multiple participants
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signed up
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity]["participants"])
        assert final_count == initial_count + len(emails)
        
        for email in emails:
            assert email in final_response.json()[activity]["participants"]
