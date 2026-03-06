import React from 'react';
import './WeatherCard.css';

const WeatherCard = ({ weather }) => {
  if (!weather) return null;

  return (
    <div className="weather-card">
      <div className="weather-header">
        <h3>Weather Forecast</h3>
        <span className="weather-date">{weather.date}</span>
      </div>
      <div className="weather-content">
        <div className="weather-main">
          <span className="weather-temp">{weather.temperature}</span>
          <span className="weather-cond">{weather.conditions}</span>
        </div>
        <div className="weather-suggestion">
          <strong>Tip:</strong> {weather.dressing_suggestions}
        </div>
      </div>
    </div>
  );
};

export default WeatherCard;
