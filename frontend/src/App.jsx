import { useState } from 'react'
import MapDisplay from './components/MapDisplay'
import UserProfile from './components/UserProfile'
import WeatherCard from './components/WeatherCard'
import FunFactCard from './components/FunFactCard'
import PlacesList from './components/PlacesList'
import './components/MapDisplay.css'

function App() {
  const [userId, setUserId] = useState('user_123')
  const [location, setLocation] = useState('Seattle, WA')
  const [searchLocation, setSearchLocation] = useState('Seattle, WA')
  const [recommendations, setRecommendations] = useState(null)
  const [userProfile, setUserProfile] = useState(null)
  const [weather, setWeather] = useState(null)
  const [funfact, setFunFact] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!userId || !location) return;

    setLoading(true);
    setError(null);
    setRecommendations(null);
    setWeather(null);
    setFunFact(null);
    setSearchLocation(location);

    try {
      // Fetch recommendations, profile, weather, and fun fact concurrently
      const [recResponse, profileResponse, weatherResponse, funfactResponse] = await Promise.all([
        fetch('/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId, location: location })
        }),
        fetch(`/profile/${userId}`),
        fetch('/weather', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ location: location, date: "today" })
        }),
        fetch('/funfact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ location: location })
        })
      ]);

      if (!recResponse.ok) throw new Error('Failed to fetch recommendations');

      const recData = await recResponse.json();
      setRecommendations(recData.recommendations || []);

      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        setUserProfile(profileData);
      } else {
        console.warn("Failed to fetch user profile data");
      }

      if (weatherResponse.ok) {
        const weatherData = await weatherResponse.json();
        if (!weatherData.error) {
          setWeather(weatherData);
        }
      } else {
        console.warn("Failed to fetch weather data");
      }

      if (funfactResponse.ok) {
        const funFactData = await funfactResponse.json();
        if (!funFactData.error) {
          setFunFact(funFactData);
        }
      } else {
        console.warn("Failed to fetch fun fact data");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Travel Concierge</h1>
        <p>Curated maps based on your unique travel profile.</p>
      </header>

      <form className="input-section" onSubmit={handleSearch}>
        <div className="input-group">
          <label>User ID</label>
          <input
            type="text"
            value={userId}
            onChange={e => setUserId(e.target.value)}
            placeholder="e.g. user_123"
          />
        </div>
        <div className="input-group">
          <label>Location</label>
          <input
            type="text"
            value={location}
            onChange={e => setLocation(e.target.value)}
            placeholder="e.g. Seattle, WA"
          />
        </div>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Searching...' : 'Find Places'}
        </button>
      </form>

      {error && <div style={{ color: 'red', textAlign: 'center', marginTop: '2rem' }}>{error}</div>}

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Analyzing profile and scanning {location}...</p>
        </div>
      )}

      {((userProfile || weather || funfact) && !loading) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          {userProfile && <UserProfile profile={userProfile} />}
          {weather && <WeatherCard weather={weather} />}
          {funfact && <FunFactCard funfact={funfact} location={searchLocation} />}
        </div>
      )}

      {recommendations && !loading && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(350px, 1fr) 2fr', // List gets 1fr (min 350px), Map gets 2fr
          gap: '1.5rem',
          marginTop: '1.5rem',
          height: '600px' // Give a fixed height to contain the map and scrolling lists
        }}>
          <PlacesList recommendations={recommendations} />

          <div style={{ height: '100%', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
            <MapDisplay places={recommendations} targetLocation={searchLocation} />
          </div>
        </div>
      )}
    </div>
  )
}

export default App
