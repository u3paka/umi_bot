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

if __name__ == '__main__':
	# umi = getUserInfo('h_y_ok')
	# umi = getTweetList(n = 10)
	# umi = getPhrase(s_type = 'ぬるぽ', n = 1)
	status = {'favorite_count': 0, 'created_at': 'Wed Feb 17 14:54:01 +0000 2016', 'contributors': None, 'truncated': False, 'in_reply_to_user_id_str': None, 'retweet_count': 0, 'id': 699970059683414016, 'in_reply_to_status_id_str': None, 'geo': None, 'entities': {'hashtags': [], 'urls': [], 'symbols': [], 'user_mentions': []}, 'id_str': '691170059683414016', 'in_reply_to_screen_name': None, 'is_quote_status': False, 'timestamp_ms': '1455720841700', 'coordinates': None, 'in_reply_to_status_id': None, 'filter_level': 'low', 'retweeted': False, 'in_reply_to_user_id': None, 'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 'favorited': False, 'user': {'protected': False, 'created_at': 'Sun Mar 31 01:35:13 +0000 2013', 'utc_offset': 32400, 'favourites_count': 27, 'follow_request_sent': None, 'following': None, 'profile_image_url': 'http://pbs.twimg.com/profile_images/681463777951236096/SbnleYeJ_normal.jpg', 'profile_background_tile': False, 'description': '名前:つゆり きさめ/学生ラブライバー/絶叫勢/ぼっち勢/海未推し/善子推し(仮)/このすば/めぐみんはいいぞ/内田彩/詳細はツイプロ/+aで最近FFの比例がおかしい事に気がついたんでスパムを除く人に見つけ次第フォロー返してます。', 'profile_text_color': '333333', 'friends_count': 1481, 'time_zone': 'Tokyo', 'profile_sidebar_border_color': 'BDDCAD', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/681463777951236096/SbnleYeJ_normal.jpg', 'screen_name': 'tuyuri_kisame', 'default_profile_image': False, 'statuses_count': 40262, 'name': '栗花落 樹雨', 'is_translator': False, 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme16/bg.gif', 'followers_count': 1921, 'location': '神奈川県東部', 'geo_enabled': False, 'verified': False, 'notifications': None, 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/1317490188/1455626298', 'listed_count': 33, 'profile_background_color': '9AE4E8', 'profile_sidebar_fill_color': 'DDFFCC', 'profile_link_color': '0084B4', 'default_profile': False, 'url': 'http://twpf.jp/tuyuri_kisame', 'profile_use_background_image': True, 'contributors_enabled': False, 'id': 1317490188, 'lang': 'ja', 'id_str': '1317490188', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme16/bg.gif'}, 'place': None, 'text': 'トサカのないことりちゃん…( ˘ω˘ )', 'lang': 'ja'}
	# saveTweet(status)
	s = 'tweets'
	# PlotlyStream()
	# updateStream()
	# dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': 'tweet', 'to_whom':screen_name, 'when':setTime, 'tmptext': ans, 'tmpid': status_id, 'tmpfile': imgfile})
	# saveTask(taskdict = {'who':'_umiS', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow() + timedelta(hours=0, minutes=0, seconds = 10)})
	# updateTask(taskid = 1, taskdict = {'what': 'end'})
	# savePhrase(phrase = s, author = 'xxxx', status = 'mid', s_type = 'UserLearn')
	# print(getPhrase(s_type = 'trendword', n = 10))
	# initTasks()
	Timer(period = 10)
	# tmp = utiltools.getJSON()3
	# print(tmp)
	# print(utiltools.t2t(tmp['clocks']['imitationLimit']))

	# with open("tmpfile.json", "w") as tmpfile:
	# 	TEMP['test'] = 'あっs'
	# 	json.dump(TEMP,tmpfile, ensure_ascii=False,sort_keys=True, indent = 4)
