import uuid

from django.core.cache import cache

CACHE_PREFIX = "pdf_export_scope"
TTL_SECONDS = 300


def store_export_scope(scope: dict) -> str:
    token = uuid.uuid4().hex
    cache.set(f"{CACHE_PREFIX}:{token}", scope, timeout=TTL_SECONDS)
    return token


def get_export_scope(token: str) -> dict | None:
    return cache.get(f"{CACHE_PREFIX}:{token}")
