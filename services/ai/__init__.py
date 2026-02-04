"""
LLM & Embedding işlemleri
"""


class EmbeddingService:
    """Embedding servisi"""
    
    def __init__(self, model_name: str = "all-minilm-l6-v2"):
        self.model_name = model_name
    
    def embed_text(self, text: str):
        """Metni vektöre dönüştür"""
        return {
            "text": text,
            "embedding": [],
            "model": self.model_name
        }


class LLMService:
    """LLM servisi"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
    
    async def generate(self, prompt: str, **kwargs):
        """LLM ile yanıt oluştur"""
        return {
            "prompt": prompt,
            "response": "",
            "model": self.model_name
        }
