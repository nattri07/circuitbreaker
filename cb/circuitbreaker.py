
import requests
import redis
import pickle

########################################
# INITIALIZE REDIS and SET CONSTANTS
########################################

TOLERANCE_THRESHOLD = 20
PASS_CODES = {200,201}
FAIL_CODES = {502,503,504}
IGNORE_CODES = {410}

redisDB = redis.Redis('localhost')



###########################

class circuitBreaker(object):

	def __init__(self):
		self.instance = ""


	def createHashEntry(self,*args):
		if not redisDB.hexists("circuitStatus", args):
			redisDB.hset("circuitStatus", args, 1)
		return




	###################

	#function to handle post requests

	def postreq(self,*args, **kwargs):

															#make hash entry for service if it
		self.createHashEntry(*args)								#doesnt exist in circuit

		if int(redisDB.hget("circuitStatus", args)) == 1:	#check if circuit is live
			print "CIRCUIT IS LIVE"
			servResp = requests.post(*args, **kwargs)		#actual post request
			code = servResp.status_code

			if code in FAIL_CODES:							#code block to push 500 error series
				pass 										#into queue
				#push to queue

			#if code in IGNORE_CODES:						#custom responses will be handled here
				#do something													

			isLive = self.updateStatus(code,*args)				#update service metrics and issue trip
			if not isLive:
				print ""
				self.restore(*args)

			return servResp									#return control to user

		else:
			print "CIRCUIT NOT LIVE"
			return requests.post("http://127.0.0.1:5000/serviceDown", **kwargs)

			### post req to servicedown to be replaced with live queue implementation for scaling



	#function to handle get requests

	def getreq(self,*args, **kwargs):
		
		self.createHashEntry(*args)

		if int(redisDB.hget("circuitStatus", args)) == 1:
			print "CIRCUIT IS LIVE"
			servResp = requests.get(*args, **kwargs)
			code = servResp.status_code							#SAME CODE BLOCK AS ABOVE
																#KILL ME BUT NO WORK AROUND
																#different args and kwargs so cant
			print args											#parse in same function to extract
			if code in FAIL_CODES:								#get / post.

				pickleParams = pickle.dumps(kwargs['params'])

				serviceList = args[0]+"firstFail"
				print serviceList
				redisDB.lpush(serviceList,pickleParams)
				print "KWARGS ABOVE"
				#push to queue

			isLive = self.updateStatus(code,*args)
			
			print isLive

			if not isLive:
				print ""
				self.getRestore(*args)
				print "I RESTORED"

			return servResp

		else:
			print "CIRCUIT NOT LIVE"
			return requests.post("http://127.0.0.1:5000/serviceDown", **kwargs)




	def trip(self,*args):
		print "Ooops I tripped"
		redisDB.hset("circuitStatus", args, 0)				#trip the circuit for that service
		redisDB.set("failedReq", 0)							#reset counters
		redisDB.set("successReq", 0)						#rolling timed counters to be used to scale
		return 0




	def updateStatus(self,result,*args):

		if result in FAIL_CODES:
			redisDB.incr("failedReq")						#increment respective counters
		elif result in PASS_CODES:
			redisDB.incr("successReq")


		numSuccess = int(redisDB.get("successReq"))
		numFail = int(redisDB.get("failedReq"))


		if numFail == 0 and numSuccess == 0:
			print "ALWAYS HERE"
			successRate = 100
		else:
			successRate = 100*(numSuccess/(numSuccess+numFail))	#calculate successrate


		if successRate > TOLERANCE_THRESHOLD:				#WOOHOO still not failing
			return 1

		else:
			return self.trip(*args)								#shucks trip me





	def restore(self,*args):
		#execute restore logic based upon queue implementation
		#trigger queue ----> iterate incrementally till threshold comes down
		#check for status
		#proceed to next chunk if failure rate comes down.
		#if not send an email to the service or something 
		print "Restoring"
		redisDB.hset("circuitStatus", args, 1)				#everything is rosey so restore
		return

	def getRestore(self,*args):
		print "Restoring GET"
		
		firstQueue = args[0]+'firstFail'
		secondQueue = args[0]+'secondFail'
		thirdQueue = args[0]+'ThirdFail'

		lenFail_1 = redisDB.llen(firstQueue)
		for i in range (0, lenFail_1):
			params = pickle.loads(redisDB.lpop(firstQueue))
			servResp = requests.get(args[0], params)
			code = servResp.status_code
			if code in FAIL_CODES:
				redisDB.lpush(secondQueue,pickle.dumps(params))


		redisDB.hset("circuitStatus", args, 1)				#everything is rosey so restore
		return










