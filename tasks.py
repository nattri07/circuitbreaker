from flask import request, json, Blueprint, Flask, render_template, request, url_for,jsonify, redirect

from celery import Celery
from celery.utils.log import get_task_logger
import urllib
import requests
import redis
import logging

#########
#########

redisDB = redis.Redis('localhost')

if not (redisDB.exists("totalReq")):
	redisDB.set("totalReq",0)

if not (redisDB.exists("passedReq")):
	redisDB.set("passedReq",0)

##############
##############


AWS_ACCESS_KEY_ID = 'AKIAIT6YY7LWJ7HBWRIQ'
AWS_SECRET_ACCESS_KEY = '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'

BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe=''),
                               urllib.quote(AWS_SECRET_ACCESS_KEY, safe=''))

app = Celery('tasks',broker=BROKER_URL)


##############
##############






@app.task
def add(a,b):
	print "im here"
	return (a+b)








@app.task(bind=True)
def qFail(*args,**kwargs):

	logging.info("asdasdas")
	# print "I'm IN FAILED QUEUE"

	if int(redisDB.get("circuitStatus"))==1:
		return

	elif int(redisDB.get("circuitStatus"))==0:

		return



