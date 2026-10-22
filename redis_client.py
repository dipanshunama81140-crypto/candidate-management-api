import redis
from config import settings

# Cloud Redis connection pool
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client

# Candidate related saari cache keys clear karne ka helper
def invalidate_candidate_cache():
    # candidates:* pattern se match hone wali saari keys dhundein
    keys = redis_client.keys("canidates:*")
    if keys:
        redis_client.delete(*keys)
        print(f"\n[REDIS] CACHE INVALIDATED: Purged {len(keys)} key(s)\n")