#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os, sys, io
import json
# Tweepyライブラリをインポート
import tweepy
from peewee import *
import re
from collections import deque
# import urllib
import urllib.request
import shutil
import time
from datetime import datetime
from playhouse.sqlite_ext import SqliteExtDatabase
import numpy as np
#MY MODULEs
import NLP
import TFIDF
import utiltools
import dealSQL
from dealSQL import twtrDB
import NNimg
import trigramMC2
import myGame
import Haiku


def get_oauth():
	# 各種キーをセット
	SECRETDIC = json.load(open("/Users/xxxx/Dropbox/Project/umiA/Data/secretDict.json"))
	twtrDictU = SECRETDIC['twtr']['Umi']
	CONSUMER_KEY = twtrDictU['consumer_key']
	CONSUMER_SECRET = twtrDictU['consumer_secret']
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	ACCESS_TOKEN = twtrDictU['access_token_key']
	ACCESS_SECRET =twtrDictU['access_token_secret']
	auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
	return auth


class myExeption(Exception): pass

def tweet(ans, screen_name = '', status_id = '', imgfile = '', bot_status = {'now': datetime.utcnow(), 'tweetStatus': {'isDebug':False, 'isSplitTweet': False, 'tempStop_since':0}}):
	tempStop_since = bot_status['tweetStatus']['tempStop_since']
	if tempStop_since != 0:
		delta = bot_status['now'] - datetime.strptime(tempStop_since, '%Y-%m-%d %H:%M:%S.%f')
		deltasec = delta.total_seconds()
		if deltasec < 300:
			return False, bot_status
		else:
			bot_status['tweetStatus']['tempStop_since'] = 0
	try:
		if screen_name != '':
			ans = ''.join(['@', screen_name,' ', ans])
		if len(ans) > 140:
			bot_status['tweetStatus']['isSplitTweet'] = True
			ans2 = ''.join([ans[0:139], '…'])
		else:
			bot_status['tweetStatus']['isSplitTweet'] = False
			ans2 = ans

		if imgfile != '':
			if bot_status['tweetStatus']['isDebug'] == False:
				tweetStatus = twtr.update_with_media(imgfile, status = ans2, in_reply_to_status_id = status_id)
				print('[Tweet.IMG.OK] @', screen_name, ' ', ans2)
			else:
				print('[Debug][Tweet.IMG.OK] @', screen_name, ' ', ans2)
		else:
			if bot_status['tweetStatus']['isDebug'] == False:
				tweetStatus = twtr.update_status(status = ans2, in_reply_to_status_id = status_id)
				print('[Tweet.OK] @', screen_name, ' ', ans2)
			else:
				print('[Debug][Tweet.OK] @', screen_name, ' ', ans2)

		if bot_status['tweetStatus']['isSplitTweet']:
			tweet(ans[139:], screen_name, status_id)
		else:
			return True, bot_status
	except tweepy.error.TweepError as e:
		print('[ERR][Tweet.TweepError] @', screen_name, ' ', ans)
		if e.response and e.response.status == 403:
			print('403')
			bot_status['tweetStatus']['tempStop_since'] = bot_status['now']
			return False, bot_status
		else:
			return True, bot_status
	except Exception as e:
		print('[Tweet.ERR] @', screen_name, ' ', ans)
		print(e)
		return False, bot_status

def quickResponse(status, bot_status):
	text = status['cleanText']
	if status['entities']['urls'] != []:
		ans = ''
	elif status['user']['screen_name'] in bot_status['BOTset']:
		ans = ''
	elif 'ぬるぽ' in text:
		ans = '■━⊂(   •̀ ᴗ •́) 彡 ｶﾞｯ☆`Д´)ﾉ'
	elif 'なんでも' in text:
		ans = '(  •̀ ᴗ •́)っ!! え、今何でもするって言いましたよね？では、一緒に山頂アタックですっ！！'
	elif 'おはよ' in text:
		ans = 'おはようございます。園田家の朝は、気合の入った剣道の朝稽古で始まります。今日も頑張りましょう。'
	elif 'おやすみ' in text:
		ans = 'おやすみなさい...'
	elif text in set(bot_status['tweetPool']['pool']):
		ans = ''.join([text,'(パクツイ便乗)'])
	else:
		mas = [w for w in NLP.MA.getMeCabList(text) if w[0] != '。']
		ans = Haiku.Haiku(mas)
	#ツイート
	if ans != '':
		try:
			return tweet(ans, status['user']['screen_name'], status_id = status['id_str'], imgfile = '', bot_status = bot_status)[0]
		except Exception as e:
			print(e)
			return False
	else:
		return False

def isAllowed(status, bot_status):
	if 	status['retweeted'] or status['is_quote_status']:
		return False
	text = status['text']
	if 'RT' in text or 'QT' in text or '【' in text or 'ポストに到達' in text or 'に入ってからリプライ数' in text:
		return False
	screen_name = status['user']['screen_name']
	if screen_name == bot_status['BOT_ID']:
		return False
	if screen_name in bot_status['BLACKset']:
		return False
	else:
		return True

def isReact(text, screen_name, status_id, replyname , bot_status):
	rand = np.random.rand()
	if replyname == bot_status['BOT_ID']: #リプライには全受け。
		return True
	elif screen_name in bot_status['BOTset']:
		if rand < 0.001: #BOTに対する自発。0.1%
			return True
	elif rand < 0.005: #自発。0.5%
		return True
	else:
		return False

def saveMedias(status, ID, DIR = '/Users/xxxx'):
	def saveMedia(medias, ID, i, screen_name):
		m = medias[i]
		media_url = m['media_url']
		if ID == None:
			ID = datetime.utcnow().strftime("%Y%m%d%H%M%S")
		filename = ''.join([DIR,'/',ID,'_',str(i),'_',screen_name, '.jpg'])
		if os.path.exists(DIR) == False:
			os.mkdir(DIR)
		try:
			urllib.request.urlretrieve(media_url, filename)
			print(filename)
			return filename
		except IOError:
			print ("[ERR.SAVE.img]")
			return ''
	try:
		medias = status['extended_entities']['media']
		# print(status)
		return [filename for filename in [saveMedia(medias, ID, i, status['user']['screen_name']) for i in range(len(medias))] if filename != '']
	except Exception as e:
		print(e)

def Main(status, bot_status):
	text = status['cleanText']
	status_id = status['id_str']
	screen_name = status['user']['screen_name']
	userinfo, isNewUser = dealSQL.getUserInfo(screen_name)
	now = datetime.utcnow()
	if isNewUser:
		welcomeTweet = 'はじめまして。よろしくお願いしますね。\n[新規ユーザー名検出...ユーザー情報登録完了]'
		tweetStatus, Altbot_status =  tweet(welcomeTweet, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	try:
		delta = now - datetime.strptime(userinfo['time'], '%Y-%m-%d %H:%M:%S.%f')
		deltasec = delta.total_seconds()
	except:
		deltasec = 50

	if deltasec > 1000:
		userinfo['cnt'] = 0
		userinfo['mode'] = 'dialog'
		if userinfo['mode'] == 'confirm.tag.img':
			src = userinfo['tmpFile']
			drc = ''.join(['/Users/xxxx'])
			if os.path.exists(drc) == False:
				os.mkdir(drc)
			shutil.copy(src, drc)

	if userinfo['mode'] == 'ignore':
		userinfo['cnt'] = 0
		userinfo['mode'] = 'dialog'
		Altbot_status = bot_status
		tweetStatus = False
	elif deltasec < 3:
		ans = dealSQL.getPhrase(s_type = 'tooFreq', n = 20)
		userinfo['mode'] = 'ignore'
		tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif 'userinfo' in text:
		ans = str(userinfo)
		tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif userinfo['cnt'] > 5:
		ans = dealSQL.getPhrase(s_type = 'cntOver', n = 20)
		userinfo['mode'] = 'ignore'
		tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif 'media' in status['entities']:
		userinfo['cnt'] = 0
		fileID = now.strftime("%Y%m%d%H%M%S")
		if status['entities']['hashtags'] != []:
			imgtag = status['entities']['hashtags'][0]['text']
			try:
				filenames = saveMedias(status, ID = fileID, DIR = '/Users/xxxx' + imgtag)
				ans = ''.join(['画像を「', imgtag, '」として学習対象に登録しました。ご協力ありがとうございます。'])
			except Exception as e:
				print(e)
				ans = '画像を読み取れませんでした。'
			tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
		else:
			try:
				filenames = saveMedias(status, ID = fileID, DIR = '/Users/xxxx')
				filename = filenames[0]
				label, FACEflag, altfilename = NNimg.predictAns(filename  = filename, isShow = False, model = "/Users/xxxx')
				if FACEflag == False:
					ans = '顔認識に失敗しています。 精度は下がりますが...\n' + label + 'ですか？正しかったら、「正解」と言ってください。'
				else:
					ans = label + 'ですか？正しかったら、「正解」と言ってください。'
				tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, imgfile = altfilename, bot_status = bot_status)
				drc = ''.join(['/Users/xxxx', label])
				if os.path.exists(drc) == False:
					os.mkdir(drc)
				shutil.copy(filename, drc)

				userinfo['mode'] = 'confirm.tag.img'
				print('/'.join([drc, filename.split('/')[-1]]))
				userinfo['tmpFile'] = '/'.join([drc, filename.split('/')[-1]])
			except Exception as e:
				print(e)
				ans = '画像を読み取れませんでした。'
				tweetStatus, Altbot_status = tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif userinfo['mode'] == 'confirm.tag.img':
		userinfo['cnt'] = 0
		if status['entities']['hashtags'] != []:
			imgtag = status['entities']['hashtags'][0]['text']
			isMoveDIR = True
		elif not 'ない' in text and ('正解' in text or '正し' in text):
			ans = 'やりました！正解ですね。'
			userinfo['mode'] = 'dialog'
			isMoveDIR = False
		else:
			try:
				imgtag = TFIDF.calcKWs(text, length = 1, needs = set(['固有名詞', '名詞']))[0][0]
			except Exception as e:
				print(e)
				imgtag = 'undefined'
			isMoveDIR = True
		if isMoveDIR:
			src = userinfo['tmpFile']
			drc = ''.join(['/Users/xxxx', imgtag])
			if os.path.exists(drc) == False:
				os.mkdir(drc)
			shutil.copy(src, drc)
			if imgtag != 'undefined':
				ans = ''.join(['...成る程...「', imgtag, '」なのですね。ありがとうございます。\n(フィードバックしました。学習反映にまでは時間がかかります。)'])
				userinfo['mode'] = 'dialog'
			else:
				ans = '...一体、これは何なのですか？(好奇心)'
		##送信
		tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif 'しりとり' in text or userinfo['mode'] == 'srtr':
		userinfo['mode'] = 'srtr'
		ans = myGame.SRTR(text, screen_name)
		if '\END' in ans:
			ans = ans.replace('\END', '')
			userinfo['mode'] = 'dialog'
		if '\MISS' in ans:
			ans = ans.replace('\MISS', '')
			if userinfo['cnt'] > 3:
				ans = 'しりとりは終わりにしましょう'
				userinfo['mode'] = 'dialog'
				userinfo['cnt'] = 0
		else:
			userinfo['cnt'] = 0
		tweetStatus, Altbot_status = tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif 'おみくじ' in text or '占い' in text:
		ans = dealSQL.getPhrase(s_type = 'おみくじ', n = 20)
		tweetStatus, Altbot_status = tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	elif deltasec > 259200: #3日
		ans = 'ご無沙汰しております...おかえりなさい。'
		tweetStatus, Altbot_status =  tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)
	else:
		ans = trigramMC2.dialog(text, isRandMetaS = True, isPrint = True, isLearn = False, n =5, tryCnt = 10, needs = set(['名詞', '固有名詞', '動詞', '形容詞']))
		ans = ans.replace('<人名>', status['user']['name'])
		tweetStatus, Altbot_status = tweet(ans, screen_name = screen_name, status_id = status_id, bot_status = bot_status)

	userinfo['time'] = now
	userinfo['cnt'] += 1
	dealSQL.saveUserInfo(userinfo)
	return tweetStatus, Altbot_status



class StreamListener(tweepy.streaming.StreamListener):
	def __init__(self):
		super(StreamListener,self).__init__()
		print('loading initialData...')
		self.tmp = {'users':{'EX_SCREEN_NAME': {'cnt':0, 'tweets':[]}}, 'tweets': {}, 'bot_status':{}}
		self.bot_status = {}
		self.bot_status['start_time'] = datetime.utcnow()
		self.bot_status['BOT_ID'] = '_umiA'
		self.bot_status['BOTset'] = set([UserObject.screen_name for UserObject in twtr.list_members('_umiA', 'BOT',  -1)])
		self.bot_status['BLACKset'] = set([UserObject.screen_name for UserObject in twtr.list_members('_umiA', 'BLACKLIST',  -1)])
		self.bot_status['tweetStatus'] =  {'isDebug':0, 'isSplitTweet': False, 'tempStop_since':0}
		self.bot_status['tweetPool'] = {'cnt': 0, 'pool':[]}
		print('setupData has loaded! starting Streaming...')
	def __del__(self):
		print('stopping Streaming...')
		print(self.bot_status)
	def on_status(self,status):
		status = status._json
		# dealSQL.saveTweet(status)
		if isAllowed(status, self.bot_status):
			now = datetime.utcnow()
			status_id = status['id_str']
			screen_name = status['user']['screen_name']
			replyname = status['in_reply_to_screen_name']
			text = utiltools.cleanText(status['text'])
			print(status['user']['name'], replyname, text)
			status['cleanText'] = text
			#直近ツイート処理
			#TL監視クイックレスポンス
			if quickResponse(status, bot_status = self.bot_status):
				return True

			#Tweetプーリング
			if not screen_name in self.bot_status['BOTset'] and status['entities']['urls'] == [] and len(text)>5:
				self.bot_status['tweetPool']['pool'].append(text)
				if self.bot_status['tweetPool']['cnt'] > 10:
					self.bot_status['tweetPool']['pool'].pop(0)
				else:
					self.bot_status['tweetPool']['cnt'] += 1
				# print(self.bot_status['tweetPool']['pool'])

			# リアクション
			if isReact(text, screen_name, status_id, replyname , bot_status = self.bot_status):
				tweetStatus, self.bot_status = Main(status, bot_status = self.bot_status)
				return True
			else:
				return True
		return True
	def on_direct_message(self,status):
		print(status._json)
		status = utiltools.dm2tweet(status._json)
		text = utiltools.cleanText(status['text'])
		status['cleanText'] = text
		print(status['user']['name'], text)
		Main(status, self.bot_status)
		return True
	def on_error(self,status):
		print ("can't get")
	def on_timeout(self):
		raise myExeption


def Stream(autth):
	stream = tweepy.Stream(auth = auth, listener = StreamListener(), async = True, secure=True)
	while True :
		try:
			stream.userstream()
		except Exception as e:
			print(e)
			time.sleep(100)
			stream = tweepy.Stream(auth,StreamListener())
if __name__ == '__main__':
	import multiprocessing
	cpu_count = multiprocessing.cpu_count()
	if cpu_count == 2:
		sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	auth = get_oauth()
	twtr = tweepy.API(auth)
	Stream(auth)
	NNimg.predictAns(filename  = filenames[0], isShow = False, model = "/Users/xxxx')
	# EXbot_status = {'BOT_ID': '_umiA', 'BLACKset': {'Rin_Hoshizora'}, 'tweetStatus': {'isSplitTweet': False, 'tempStop_since': 0, 'isDebug': True}, 'tweetPool': {'cnt': 79}, 'BOTset': {'Mecha_ZORARU', 'haijin_rijicho', 'umikiti_kotori', 'kanan_h_bot_', 'anju_wh_bot', 'yandekotori_bot', 'sports_Rin', 'best_gnist_eri', 'hanamaru_h_bot', 'FFgai_bot', 'Rin_Hoshizora', 'rin_rice_bot', 'srg_honoka', 'rin_bell1101', 'hanayo0117bot', 'haijin_honoka_', 'lovery_rin'}}
	# s = 'テスト投稿]'
	# Main(s, 'screen_name', EXbot_status)
	# tweet(s, status_id = '', imgfile = '')
	# print(len(s))
	# tweet(s, 'xxxx', imgfile = '')
# print(api.user_timeline(screen_name = 'xxxx'))
# print(twtr.get_status())
	# print(twtr.list_members('_umiA', 'BOT',  -1)[0].screen_name)
