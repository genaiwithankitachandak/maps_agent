import React from 'react';
import './UserProfile.css';

const UserProfile = ({ profile }) => {
  if (!profile) return null;

  return (
    <div className="profile-container">
      <h3>Travel Profile Dashboard</h3>
      <div className="profile-grid">
        <div className="profile-item">
          <span className="profile-label">User ID</span>
          <span className="profile-value">{profile.user_id}</span>
        </div>
        <div className="profile-item">
          <span className="profile-label">Party Size</span>
          <span className="profile-value">{profile.party_size}</span>
        </div>
        <div className="profile-item">
          <span className="profile-label">Budget</span>
          <span className="profile-value budget-badge">{profile.preferred_budget}</span>
        </div>

        <div className="profile-item full-width">
          <span className="profile-label">Top Interests</span>
          <div className="tags-container">
            {profile.interests && profile.interests.length > 0 ? (
              profile.interests.map((interest, i) => (
                <span key={i} className="tag tag-interest">{interest}</span>
              ))
            ) : (
              <span className="text-empty">None specified</span>
            )}
          </div>
        </div>

        <div className="profile-item full-width">
          <span className="profile-label">Dietary Restrictions</span>
          <div className="tags-container">
            {profile.dietary_restrictions && profile.dietary_restrictions.length > 0 ? (
              profile.dietary_restrictions.map((diet, i) => (
                <span key={i} className="tag tag-diet">{diet}</span>
              ))
            ) : (
              <span className="text-empty">None</span>
            )}
          </div>
        </div>

        <div className="profile-item full-width">
          <span className="profile-label">Accessibility Needs</span>
          <div className="tags-container">
            {profile.accessibility_needs && profile.accessibility_needs.length > 0 ? (
              profile.accessibility_needs.map((need, i) => (
                <span key={i} className="tag tag-access">{need}</span>
              ))
            ) : (
              <span className="text-empty">None</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
