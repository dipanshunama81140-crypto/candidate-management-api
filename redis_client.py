import redis
from config import settings

try:

    # Cloud Redis connection pool
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
except Exception as e:
    redis_client = None

def get_redis():
    return redis_client

# Candidate related saari cache keys clear karne ka helper
def invalidate_candidate_cache():
    if not redis_client:
       return
    try:
       keys = redis_client.keys("candidates:*")
       if keys:
           redis_client.delete(*keys)
           print(f"\n[REDIS] CACHE INVALIDATED: Purged {len(keys)} key(s)\n")
    except Exception as e:
        print(f"\n[REDIS WARNING] Cache invalidation skipped: {e}\n")