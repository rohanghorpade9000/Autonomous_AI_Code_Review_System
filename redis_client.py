import redis

# Initialize Redis client
redis_client = redis.StrictRedis(
    host="localhost",
    port=6379,
    decode_responses=True  # Ensures results are returned as strings
)
