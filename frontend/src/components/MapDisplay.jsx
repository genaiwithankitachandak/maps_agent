import React, { useState, useEffect } from 'react';
import { APIProvider, Map, AdvancedMarker, Pin, InfoWindow, useMap, useMapsLibrary } from '@vis.gl/react-google-maps';
import './MapDisplay.css';

// We need a helper to geocode the string address into lat/lng since 
// the agent currently returns string addresses. We'll use the Maps Geocoding API implicitly
// or just rely on Advanced Marker taking string addresses if possible. 
// Vis.gl AdvancedMarker requires lat/lng. For a robust app, the backend should return lat/lng.
// For this prototype, we'll assume a rough center or add a simple geocoder.

const MapUpdater = ({ targetLocation, setCenter }) => {
  const map = useMap();
  const geocodingLibrary = useMapsLibrary('geocoding');
  const [geocoder, setGeocoder] = useState(null);

  useEffect(() => {
    if (!geocodingLibrary) return;
    setGeocoder(new geocodingLibrary.Geocoder());
  }, [geocodingLibrary]);

  useEffect(() => {
    if (!geocoder || !targetLocation) return;

    geocoder.geocode({ address: targetLocation }, (results, status) => {
      if (status === 'OK' && results && results[0]) {
        const newCenter = {
          lat: results[0].geometry.location.lat(),
          lng: results[0].geometry.location.lng()
        };
        setCenter(newCenter);
        if (map) {
          map.panTo(newCenter);
          map.setZoom(12);
        }
      } else {
        console.warn("Google Maps Geocoding failed for targetLocation:", targetLocation, "Status:", status);
      }
    });
  }, [geocoder, targetLocation, map, setCenter]);

  return null; // This is a logic-only component
};

const PlaceMarker = ({ place, onClick }) => {
  const geocodingLibrary = useMapsLibrary('geocoding');
  const [position, setPosition] = useState(null);

  useEffect(() => {
    if (!geocodingLibrary || !place.address) return;
    const geocoder = new geocodingLibrary.Geocoder();
    geocoder.geocode({ address: place.address }, (results, status) => {
      if (status === 'OK' && results && results[0]) {
        const newPos = {
          lat: results[0].geometry.location.lat(),
          lng: results[0].geometry.location.lng()
        };
        setPosition(newPos);
        // Store position on the place object so InfoWindow can use it later
        place.resolvedPosition = newPos;
      } else {
        console.warn("Google Maps Geocoding failed for place:", place.name, "Address:", place.address, "Status:", status);
      }
    });
  }, [geocodingLibrary, place]);

  if (!position) return null;

  return (
    <AdvancedMarker position={position} onClick={() => onClick(place)}>
      <Pin background={'#0f9d58'} borderColor={'#006425'} glyphColor={'#60d273'} />
    </AdvancedMarker>
  );
};

const MapInner = ({ places, targetLocation }) => {
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [center, setCenter] = useState({ lat: 47.6062, lng: -122.3321 }); // Default Seattle

  return (
    <Map
      defaultZoom={12}
      defaultCenter={{ lat: 47.6062, lng: -122.3321 }}
      mapId={import.meta.env.VITE_GOOGLE_MAPS_MAP_ID || "DEMO_MAP_ID"}
      gestureHandling={'greedy'}
    >
      <MapUpdater targetLocation={targetLocation} setCenter={setCenter} />

      {places && places.map((place, index) => (
        <PlaceMarker
          key={index}
          place={place}
          onClick={(p) => setSelectedPlace(p)}
        />
      ))}

      {selectedPlace && (
        <InfoWindow
          position={selectedPlace.resolvedPosition || center}
          onCloseClick={() => setSelectedPlace(null)}
        >
          <div className="info-window-content">
            <h3>{selectedPlace.name}</h3>
            <span className="category-badge">{selectedPlace.category}</span>
            <p className="address">{selectedPlace.address}</p>
            <p className="rating">⭐ {selectedPlace.rating}</p>
            <div className="match-reason-box">
              <strong>Why it matches your profile:</strong>
              <p>{selectedPlace.match_reason}</p>
            </div>
          </div>
        </InfoWindow>
      )}
    </Map>
  );
};

const MapDisplay = ({ places, targetLocation }) => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  if (!apiKey) {
    return <div style={{ color: 'red', marginTop: '2rem' }}>Error: VITE_GOOGLE_MAPS_API_KEY is missing from the .env file.</div>;
  }

  return (
    <div className="map-container">
      <APIProvider apiKey={apiKey}>
        <MapInner places={places} targetLocation={targetLocation} />
      </APIProvider>
    </div>
  );
};

export default MapDisplay;
