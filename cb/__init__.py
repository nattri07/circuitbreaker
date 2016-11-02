import redis


redisDB = redis.Redis('localhost')

if not redisDB.exists("failedReq"):
	redisDB.set("failedReq", 0)

if not redisDB.exists("successReq"):
	redisDB.set("successReq", 0)