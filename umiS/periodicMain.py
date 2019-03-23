#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import NLP
import TFIDF
import NNimg
import trigramMC
import myGame
import GAME_MON
import Haiku
import dealSQL
import twf

def loopMain(task):
	ans = ''
	tmp = utiltools.getJSON()
	print(task)
	taskid = task['id']
	todo = task['what']
	screen_name = task['to_whom']
	filename = task['tmpfile']
	status_id = task['tmpid']
	setTime = task['when']
	setTimeJ = setTime + timedelta(hours=9)
	trycnt = 0
	if todo == 'timer':
		ans = datetime.strftime(setTimeJ, '%m月%d日 %H時%M分%S秒') + 'です。タイマーの時刻を経過しました。\n' + task['tmptext']
	elif todo == 'teiki.trendword':
		trendwords = twf.getTrendwords()
		trendword = np.random.choice(trendwords)
		ans = dealSQL.getPhrase(s_type = 'trendword', n = 2).format(trendword)
		post30min = setTime + timedelta(hours=0, minutes=30)
		dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': todo, 'to_whom': '', 'when':post30min})
		tmp['trendwordsList'] = trendwords
	elif todo == 'imitate.default':
		if twf.defaultProfile():
			ans = 'デフォルトに戻りました'
			screen_name = ''
			tmp['imitating'] = ''
		else:
			ans = 'デフォルトに戻るのに失敗 サポートにお問い合わせください。'
	elif todo == 'erase.tmp.responseWord':
		try:
			del tmp['responseWord'][task['tmptext']]
		except:
			print('del err')
	elif todo == 'erase.tmp.stats.tweet_cnt_hour':
		tmp['stats']['tweet_cnt_hour'] = 0
		post1hour = setTime + timedelta(hours=1)
		dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': todo, 'to_whom': '', 'when':post1hour})

	elif todo == 'tweet':
		ans = task['tmptext']
		trycnt = task['tmpcnt']

	if ans != '':
		twf.send(ans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = 'tweet', tmp = tmp, trycnt = trycnt)
	dealSQL.updateTask(taskid = taskid, taskdict = {'status': 'end'})
	utiltools.saveJSON(tmp)
	return True

def initTasks():
	dealSQL.updateTask(kinds = ['tweet', 'teiki.trendword', 'erase.tmp.stats.tweet_cnt_hour'], taskdict = {'status': 'end'})
	utcnow = datetime.utcnow()
	setTime = utcnow  + timedelta(hours=0, minutes=5)
	dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': 'teiki.trendword', 'to_whom':'', 'when':setTime, 'tmptext': ''})
	dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': 'erase.tmp.stats.tweet_cnt_hour', 'to_whom': '', 'when':utcnow})

def Timer(period = 2):
	initTasks()
	while True:
		now = datetime.utcnow()
		print(now)
		tasks = dealSQL.searchTasks(when = now, who = '', n = 10)
		[loopMain(task) for task in tasks if task != '']
		time.sleep(period)
