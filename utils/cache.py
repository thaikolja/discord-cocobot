"""
Caching utilities for the cocobot application.

This module provides caching functionality using Redis for performance optimization
and reduced API calls.
"""

import asyncio
import json
import time
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import logging
import redis
from redis.asyncio import Redis
from utils.logger import get_logger


class CacheManager:
	"""Manages caching using Redis with fallback to in-memory cache."""

	def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
		self.logger = get_logger(__name__)
		self.default_ttl = default_ttl

		# Initialize Redis connection if URL is provided
		if redis_url:
			try:
				self.redis_client = Redis.from_url(redis_url, decode_responses=True)
				self.use_redis = True
				self.logger.info("Redis cache initialized successfully")
			except Exception as e:
				self.logger.error(f"Failed to connect to Redis: {e}, falling back to in-memory cache")
				self.redis_client = None
				self.use_redis = False
		else:
			self.redis_client = None
			self.use_redis = False

		# In-memory fallback cache
		self.memory_cache = {}

	async def get(self, key: str) -> Optional[Any]:
		"""Get a value from cache."""
		try:
			if self.use_redis and self.redis_client:
				value = await self.redis_client.get(key)
				if value is not None:
					try:
						return json.loads(value)
					except json.JSONDecodeError:
						return value
				return None
			else:
				# Check in-memory cache
				if key in self.memory_cache:
					cached_item = self.memory_cache[key]
					if cached_item['expires_at'] > time.time():
						return cached_item['value']
					else:
						# Remove expired item
						del self.memory_cache[key]
						return None
				return None
		except Exception as e:
			self.logger.error(f"Cache get error for key {key}: {e}")
			return None

	async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
		"""Set a value in cache with optional TTL."""
		if ttl is None:
			ttl = self.default_ttl

		try:
			if self.use_redis and self.redis_client:
				# Serialize the value to JSON for Redis storage
				try:
					serialized_value = json.dumps(value, default=str)
				except TypeError:
					# If value can't be JSON serialized, convert to string
					serialized_value = str(value)

				await self.redis_client.setex(key, ttl, serialized_value)
				return True
			else:
				# Store in memory cache
				self.memory_cache[key] = {
					'value': value,
					'expires_at': time.time() + ttl
				}
				return True
		except Exception as e:
			self.logger.error(f"Cache set error for key {key}: {e}")
			return False

	async def delete(self, key: str) -> bool:
		"""Delete a key from cache."""
		try:
			if self.use_redis and self.redis_client:
				result = await self.redis_client.delete(key)
				return result > 0
			else:
				if key in self.memory_cache:
					del self.memory_cache[key]
					return True
				return False
		except Exception as e:
			self.logger.error(f"Cache delete error for key {key}: {e}")
			return False

	async def exists(self, key: str) -> bool:
		"""Check if a key exists in cache."""
		try:
			if self.use_redis and self.redis_client:
				return await self.redis_client.exists(key) > 0
			else:
				if key in self.memory_cache:
					# Check if not expired
					if self.memory_cache[key]['expires_at'] > time.time():
						return True
					else:
						del self.memory_cache[key]
						return False
				return False
		except Exception as e:
			self.logger.error(f"Cache exists error for key {key}: {e}")
			return False

	async def clear(self) -> bool:
		"""Clear all cache."""
		try:
			if self.use_redis and self.redis_client:
				await self.redis_client.flushdb()
				return True
			else:
				self.memory_cache.clear()
				return True
		except Exception as e:
			self.logger.error(f"Cache clear error: {e}")
			return False

	async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
		"""Increment a counter in cache."""
		if ttl is None:
			ttl = self.default_ttl

		try:
			if self.use_redis and self.redis_client:
				result = await self.redis_client.incrby(key, amount)
				if ttl > 0:
					await self.redis_client.expire(key, ttl)
				return result
			else:
				# In-memory increment
				if key in self.memory_cache:
					current_value = self.memory_cache[key]['value']
					if isinstance(current_value, (int, float)):
						new_value = current_value + amount
					else:
						new_value = amount
				else:
					new_value = amount

				self.memory_cache[key] = {
					'value': new_value,
					'expires_at': time.time() + ttl
				}
				return new_value
		except Exception as e:
			self.logger.error(f"Cache increment error for key {key}: {e}")
			return None

	async def get_ttl(self, key: str) -> int:
		"""Get the time-to-live for a cached key."""
		try:
			if self.use_redis and self.redis_client:
				ttl = await self.redis_client.ttl(key)
				return ttl if ttl > 0 else 0
			else:
				if key in self.memory_cache:
					expires_at = self.memory_cache[key]['expires_at']
					remaining = int(expires_at - time.time())
					return max(0, remaining)
				return 0
		except Exception as e:
			self.logger.error(f"Cache TTL error for key {key}: {e}")
			return 0


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
	"""Get the global cache manager instance."""
	global _cache_manager
	if _cache_manager is None:
		from config.config import get_global_config
		config = get_global_config()
		_cache_manager = CacheManager(
			redis_url=config.cache.redis_url,
			default_ttl=config.cache.default_ttl
		)
	return _cache_manager


# Convenience functions
async def cache_get(key: str) -> Optional[Any]:
	"""Get a value from cache."""
	return await get_cache_manager().get(key)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
	"""Set a value in cache."""
	return await get_cache_manager().set(key, value, ttl)


async def cache_delete(key: str) -> bool:
	"""Delete a key from cache."""
	return await get_cache_manager().delete(key)


async def cache_exists(key: str) -> bool:
	"""Check if a key exists in cache."""
	return await get_cache_manager().exists(key)


async def cache_clear() -> bool:
	"""Clear all cache."""
	return await get_cache_manager().clear()


async def cache_increment(key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
	"""Increment a counter in cache."""
	return await get_cache_manager().increment(key, amount, ttl)


def cache_key(*parts) -> str:
	"""Create a cache key from parts."""
	return ":".join(str(part) for part in parts)


# Decorator for function result caching
def cached(ttl: int = 3600, key_prefix: str = "func"):
	"""Decorator to cache function results."""

	def decorator(func):
		async def wrapper(*args, **kwargs):
			# Create cache key based on function name and arguments
			cache_key_str = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

			# Try to get from cache first
			result = await cache_get(cache_key_str)
			if result is not None:
				return result

			# Execute function and cache result
			result = await func(*args, **kwargs)
			await cache_set(cache_key_str, result, ttl)
			return result

		return wrapper

	return decorator


# Decorator for API response caching
def api_cached(ttl: int = 300, key_prefix: str = "api"):
	"""Decorator to cache API responses."""

	def decorator(func):
		async def wrapper(*args, **kwargs):
			# Create cache key based on function name and parameters
			params_hash = hash(str(args) + str(kwargs))
			cache_key_str = f"{key_prefix}:{func.__name__}:{params_hash}"

			# Try to get from cache first
			result = await cache_get(cache_key_str)
			if result is not None:
				return result

			# Execute API call and cache result
			result = await func(*args, **kwargs)
			await cache_set(cache_key_str, result, ttl)
			return result

		return wrapper

	return decorator


# Initialize cache at module level
async def init_cache():
	"""Initialize the cache system."""
	cache = get_cache_manager()
	# Test the cache connection
	test_key = "cocobot:cache:test"
	await cache_set(test_key, "test_value", 60)
	if await cache_get(test_key) == "test_value":
		logging.getLogger(__name__).info("Cache system initialized successfully")
	else:
		logging.getLogger(__name__).warning("Cache system may not be working properly")


# Run initialization if module is loaded
asyncio.create_task(init_cache())
