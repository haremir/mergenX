"""
Dış API entegrasyonları (Amadeus, THY vb.)
"""


class ProviderClient:
    """Harici sağlayıcı istemcisi"""
    
    def __init__(self, provider_name: str, api_key: str):
        self.provider_name = provider_name
        self.api_key = api_key
    
    async def fetch_data(self, endpoint: str, params: dict):
        """Harici API'den veri al"""
        return {
            "provider": self.provider_name,
            "status": "success",
            "data": []
        }
