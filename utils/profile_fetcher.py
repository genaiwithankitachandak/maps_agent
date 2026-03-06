import logging
import json
from models.schemas import TravelProfile

logger = logging.getLogger(__name__)

# Mock database of profiles for initial testing
MOCK_DB = {
    "user_123": {
        "user_id": "user_123",
        "interests": ["science", "museums", "vegan food"],
        "preferred_budget": "$$",
        "accessibility_needs": [],
        "dietary_restrictions": ["vegan"],
        "party_size": 4
    },
    "user_456": {
        "user_id": "user_456",
        "interests": ["nightlife", "luxury dining", "art galleries"],
        "preferred_budget": "$$$$",
        "accessibility_needs": [],
        "dietary_restrictions": [],
        "party_size": 2
    }
}

class ProfileFetcher:
    """Fetches user travel profiles from a storage backend (e.g., BigQuery or Bucket)."""
    
    def __init__(self, mode: str = "mock"):
        self.mode = mode
        
    def get_profile(self, user_id: str) -> TravelProfile:
        """Fetch the profile for the given user_id."""
        logger.info(f"Fetching profile for user: {user_id} using mode {self.mode}")
        
        if self.mode == "mock":
            return self._get_mock_profile(user_id)
        elif self.mode == "bq":
            return self._get_bq_profile(user_id)
        else:
            raise ValueError(f"Unsupported ProfileFetcher mode: {self.mode}")
            
    def _get_mock_profile(self, user_id: str) -> TravelProfile:
        profile_data = MOCK_DB.get(user_id)
        if not profile_data:
            logger.warning(f"Profile not found for {user_id}. Using default generic profile.")
            return TravelProfile(
                user_id=user_id,
                interests=["general sightseeing"],
                preferred_budget="$$",
                party_size=1
            )
        return TravelProfile(**profile_data)
        
    def _get_bq_profile(self, user_id: str) -> TravelProfile:
        import os
        from google.cloud import bigquery
        
        try:
            client = bigquery.Client()
            dataset = os.environ.get("BQ_DATASET", "experiments-435323.marketing")
            table = os.environ.get("BQ_TABLE_PROFILES", "user_profiles")
            
            query = f"SELECT * FROM `{dataset}.{table}` WHERE user_id = @user_id LIMIT 1"
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
                ]
            )
            
            results = client.query(query, job_config=job_config).result()
            
            for row in results:
                profile_dict = dict(row.items())
                
                # BigQuery might return repeated fields as lists, or strings if they stored it that way.
                # Just to be safe, if we encounter a comma-separated string for our list fields, we parse it.
                for array_field in ['interests', 'accessibility_needs', 'dietary_restrictions']:
                    if array_field in profile_dict and isinstance(profile_dict[array_field], str):
                        try:
                            # if it looks like a JSON array string
                            if profile_dict[array_field].startswith('['):
                                import json
                                profile_dict[array_field] = json.loads(profile_dict[array_field])
                            else:
                                profile_dict[array_field] = [x.strip() for x in profile_dict[array_field].split(',') if x.strip()]
                        except:
                            profile_dict[array_field] = []

                return TravelProfile(**profile_dict)
                
        except Exception as e:
            logger.error(f"Error fetching from BigQuery for {user_id}: {e}")
            
        logger.warning(f"Profile not found for {user_id} in BigQuery. Using default generic profile.")
        return TravelProfile(
            user_id=user_id,
            interests=["general sightseeing"],
            preferred_budget="$$",
            party_size=1
        )
