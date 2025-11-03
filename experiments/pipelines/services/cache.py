"""
Caching Service for MediVault
Redis-based caching for performance optimization
"""

import json
import redis
from typing import Optional, Any
from datetime import timedelta
from config import Config


class CacheService:
    """
    Redis caching service for improved performance
    """

    def __init__(self):
        self.enabled = Config.REDIS_ENABLED
        self.client = None

        if self.enabled:
            try:
                self.client = redis.from_url(
                    Config.REDIS_URL,
                    decode_responses=True
                )
                # Test connection
                self.client.ping()
                print("✓ Redis cache connected")
            except Exception as e:
                print(f"⚠ Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.client = None

    def _make_key(self, key: str) -> str:
        """Add prefix to cache key"""
        return f"medivault:{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(self._make_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = 300
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            expire_seconds: Expiration time in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            serialized = json.dumps(value)
            if expire_seconds:
                self.client.setex(
                    self._make_key(key),
                    expire_seconds,
                    serialized
                )
            else:
                self.client.set(self._make_key(key), serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(self._make_key(key))
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Pattern to match (e.g., "patient:123:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = self.client.keys(self._make_key(pattern))
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0

    def cache_patient_records(
        self,
        patient_id: str,
        records: list,
        expire_minutes: int = 5
    ):
        """Cache patient records"""
        key = f"patient:{patient_id}:records"
        self.set(key, records, expire_seconds=expire_minutes * 60)

    def get_patient_records(self, patient_id: str) -> Optional[list]:
        """Get cached patient records"""
        key = f"patient:{patient_id}:records"
        return self.get(key)

    def cache_search_results(
        self,
        query: str,
        patient_id: Optional[str],
        results: dict,
        expire_minutes: int = 10
    ):
        """Cache search results"""
        key = f"search:{query}"
        if patient_id:
            key += f":patient:{patient_id}"
        self.set(key, results, expire_seconds=expire_minutes * 60)

    def get_search_results(
        self,
        query: str,
        patient_id: Optional[str] = None
    ) -> Optional[dict]:
        """Get cached search results"""
        key = f"search:{query}"
        if patient_id:
            key += f":patient:{patient_id}"
        return self.get(key)

    def invalidate_patient_cache(self, patient_id: str):
        """Invalidate all cache for a patient"""
        self.clear_pattern(f"patient:{patient_id}:*")

    def cache_biomarker_trend(
        self,
        patient_id: str,
        biomarker_type: str,
        data: list,
        expire_minutes: int = 30
    ):
        """Cache biomarker trend data"""
        key = f"biomarker:trend:{patient_id}:{biomarker_type}"
        self.set(key, data, expire_seconds=expire_minutes * 60)

    def get_biomarker_trend(
        self,
        patient_id: str,
        biomarker_type: str
    ) -> Optional[list]:
        """Get cached biomarker trend"""
        key = f"biomarker:trend:{patient_id}:{biomarker_type}"
        return self.get(key)


# Singleton instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get or create cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
