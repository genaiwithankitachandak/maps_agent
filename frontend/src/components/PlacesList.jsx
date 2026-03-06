import React from 'react';
import './PlacesList.css';

const PlaceListCard = ({ title, icon, places, emptyMessage }) => {
  return (
    <div className="places-list-card">
      <div className="places-list-header">
        <h3>{icon} {title}</h3>
        <span className="places-count">{places.length}</span>
      </div>
      
      {places.length === 0 ? (
        <p className="empty-message">{emptyMessage}</p>
      ) : (
        <ul className="places-list">
          {places.map((place, index) => (
            <li key={index} className="place-item">
              <div className="place-item-header">
                <span className="place-name">{place.name}</span>
                {place.rating && <span className="place-rating">⭐ {place.rating}</span>}
              </div>
              <span className="place-category">{place.category}</span>
              <p className="place-address">📍 {place.address}</p>
              <p className="place-match-reason"><strong>Why:</strong> {place.match_reason}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const PlacesList = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) return null;

  // Simple heuristic: if category contains 'Restaurant', 'Cafe', 'Food', 'Bar', 'Dining' it's food.
  // Otherwise it's an activity/sights
  const foodKeywords = ['restaurant', 'cafe', 'food', 'bar', 'dining', 'eatery', 'coffee', 'bakery'];
  
  const foodPlaces = recommendations.filter(place => {
    const cat = place.category.toLowerCase();
    return foodKeywords.some(keyword => cat.includes(keyword));
  });

  const activityPlaces = recommendations.filter(place => {
    const cat = place.category.toLowerCase();
    return !foodKeywords.some(keyword => cat.includes(keyword));
  });

  return (
    <div className="places-list-container">
      <PlaceListCard 
        title="Food & Dining" 
        icon="🍽️" 
        places={foodPlaces} 
        emptyMessage="No specific food recommendations found for this profile." 
      />
      
      <PlaceListCard 
        title="Sights & Activities" 
        icon="📸" 
        places={activityPlaces} 
        emptyMessage="No specific activity recommendations found for this profile." 
      />
    </div>
  );
};

export default PlacesList;
