"""
Oteller verilerini senkronize et
"""
import logging

logger = logging.getLogger(__name__)


def sync_hotels():
    """Otel verilerini senkronize et"""
    logger.info("Oteller senkronizasyonu başlıyor...")
    
    # Senkronizasyon mantığı
    
    logger.info("Oteller senkronizasyonu tamamlandı")
