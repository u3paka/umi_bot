#!/usr/bin/env python
# -*- coding:utf-8 -*-

#MY MODULEs
#variables
from setup import *
import NLP
import TFIDF
import NNimg
import trigramMC
import myGame
import GAME_MON
import Haiku
import dealSQL

def tweet(ans, screen_name = '', status_id = '', imgfile = '', tmp = tmp,  trycnt = 0):
	tempStop_since = tmp['tweetStatus']['tempStop_since']
	if tempStop_since != 0:
		delta = tmp['clocks']['now'] - datetime.strptime(tempStop_since, '%Y-%m-%d %H:%M:%S.%f')
		deltasec = delta.total_seconds()
		if deltasec < 300:
			return False, tmp
		else:
			tmp['tweetStatus']['tempStop_since'] = 0

	# 1時間あたりのツイート数が100を上回る場合、ツイートしない。
	if tmp['stats']['tweet_cnt_hour'] > 100:
		duration = trycnt + 1
		setTime = datetime.utcnow() + timedelta(hours=0, minutes = duration)
		dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': 'tweet', 'to_whom':screen_name, 'when':setTime, 'tmptext': ans, 'tmpid': status_id, 'tmpfile': imgfile, 'tmpcnt': trycnt +1})
		print('[Tweet.1minAfter] @', screen_name, ' ', ans)
		return False, tmp
	else:
		# ツイート数をtmpへ送りモニタする
		tmp['stats']['tweet_cnt_hour'] += 1
		tmp['stats']['tweet_cnt_today'] += 1

	try:
		if screen_name != '':
			ans = ''.join(['@', screen_name,' ', ans])
		if len(ans) > 140:
			tmp['tweetStatus']['isSplitTweet'] = True
			ans2 = ''.join([ans[0:139], '…'])
		else:
			tmp['tweetStatus']['isSplitTweet'] = False
			ans2 = ans

		if imgfile != '':
			if tmp['tweetStatus']['isDebug'] == False:
				tweetStatus = twtr.update_with_media(imgfile, status = ans2, in_reply_to_status_id = status_id)
				print('[Tweet.IMG.OK] @', screen_name, ' ', ans2)
			else:
				print('[Debug][Tweet.IMG.OK] @', screen_name, ' ', ans2)
		else:
			if tmp['tweetStatus']['isDebug'] == False:
				tweetStatus = twtr.update_status(status = ans2, in_reply_to_status_id = status_id)
				print('[Tweet.OK] @', screen_name, ' ', ans2)
			else:
				print('[Debug][Tweet.OK] @', screen_name, ' ', ans2)

		# 140字越えの際は、分割ツイート
		if tmp['tweetStatus']['isSplitTweet']:
			tweet(ans[139:], screen_name, status_id, tmp = tmp)
		else:
			return True, tmp
	except tweepy.error.TweepError as e:
		print('[ERR][Tweet.TweepError] @', screen_name, ' ', ans)
		if e.response and e.response.status == 403:
			print('403')
			tmp['tweetStatus']['tempStop_since'] = tmp["clocks"]['now']
			return False, tmp
		else:
			return True, tmp
	except Exception as e:
		print('[Tweet.ERR] @', screen_name, ' ', ans)
		print(e)
		return False, tmp

def sendDM(ans, screen_name = '', tmp = {'tweetStatus': {'isDebug':False, 'isSplitTweet': False, 'tempStop_since':0}}):
	try:
		if tmp['tweetStatus']['isDebug'] == False:
			tweetStatus = twtr.send_direct_message(screen_name = screen_name, text = ans)
			print('[DM.OK] @', screen_name, ' ', ans)
		else:
			print('[Debug][DM.OK] @', screen_name, ' ', ans2)
		return True, tmp
	except tweepy.error.TweepError as e:
		print('[ERR][DM.TweepError] @', screen_name, ' ', ans)
		if e.response and e.response.status == 403:
			print('403')
			tmp['tweetStatus']['tempStop_since'] = tmp['now']
			return False, tmp
		else:
			return True, tmp
	except Exception as e:
		print('[DM.ERR] @', screen_name, ' ', ans)
		print(e)
		return False, tmp

def send(ans, screen_name = '', status_id = '', imgfile = '', mode = 'dm', tmp = tmp,  trycnt = 0):
	if mode == 'dm':
		return sendDM(ans = ans, screen_name = screen_name, tmp = tmp)
	elif mode == 'open':
		return tweet(ans = ans, screen_name = '', status_id = '', imgfile = imgfile, tmp = tmp,  trycnt = trycnt)
	else:
		return tweet(ans = ans, screen_name = screen_name, status_id = status_id, imgfile = imgfile, tmp = tmp, trycnt = trycnt)


def getTrendwords(mode = 'withoutTag'):
	# 'locations': [{'woeid': 23424856, 'name': 'Japan'}]
	trends = twtr.trends_place(id = 23424856)[0]['trends']
	if mode == 'withoutTag':
		return [trend['name'] for trend in trends if not '#' in trend['name']]
	elif mode == 'withTag':
		trendtags = [trend['name'] for trend in trends if '#' in trend['name']]
		trendwords = [trend['name'] for trend in trends if not '#' in trend['name']]
		return trendwords, trendtags
	else:
		return [trend['name'] for trend in trends]

def defaultProfile():
	try:
		updateProfile(name = myPROFILE['NAME'], description = myPROFILE['DESCRIPTION'], location= myPROFILE['LOCATION'], url = myPROFILE['URL'], filename = myPROFILE['ICON'], BGfilename = myPROFILE['BG'], Bannerfilename = myPROFILE['Banner'] )
		return True
	except Exception as e:
		print(e)
		return False

def updateProfile(name, description, location, url = '', filename = '', BGfilename = '', Bannerfilename = ''):
	try:
		twtr.update_profile(name = name, url = url,  location = location, description = description)
		if filename != '':
			twtr.update_profile_image(filename)
		if BGfilename != '':
			twtr.update_profile_background_image(BGfilename)
		if Bannerfilename != '':
			twtr.update_profile_banner(Bannerfilename)
		return True
	except Exception as e:
		print(e)
		return False