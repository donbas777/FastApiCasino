import redis

redis_host = "redis"
redis_port = 6379

r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
