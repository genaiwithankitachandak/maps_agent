import React, { useState, useEffect } from 'react';
import './FunFactCard.css';

const FunFactCard = ({ funfact, location }) => {
  const [currentFact, setCurrentFact] = useState(funfact);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setCurrentFact(funfact);
  }, [funfact]);

  const handleMore = async () => {
    if (!location) return;
    setLoading(true);
    try {
      const response = await fetch('/funfact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location })
      });
      if (response.ok) {
        const data = await response.json();
        if (!data.error) {
          setCurrentFact(data);
        }
      }
    } catch (err) {
      console.error("Failed to fetch more fun facts:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!currentFact) return null;

  return (
    <div className="funfact-card">
      <div className="funfact-header">
        <h3>✨ Fun Fact</h3>
        <button
          className="btn-more-fun-fact"
          onClick={handleMore}
          disabled={loading}
        >
          {loading ? 'Thinking...' : 'More!'}
        </button>
      </div>
      <div className="funfact-content">
        <h4 className="funfact-title">{currentFact.title}</h4>
        <p className="funfact-description">{currentFact.description}</p>
      </div>
    </div>
  );
};

export default FunFactCard;
