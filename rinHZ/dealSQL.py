#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *

class UserDBModel(Model):
    class Meta:
        database = userDB

class Srtrtemps(UserDBModel):
    kanasstream = CharField(db_column='kanasStream', null=True)
    lenrule = IntegerField(db_column='lenRule', null=True)
    losecnt = IntegerField(null=True)
    name = CharField(primary_key=True)
    totalcnt = IntegerField(null=True)
    wincnt = IntegerField(null=True)
    wordsstream = CharField(db_column='wordsStream', null=True)
    class Meta:
        db_table = 'srtrtemps'

class Users(UserDBModel):
	screen_name = CharField(primary_key=True)
	user_id = CharField(null=True)
	name = CharField(null=True)
	nickname = CharField(null=True)
	mode = CharField(null=True)
	cnt = IntegerField(null=True)
	reply_cnt = IntegerField(null=True)
	total_cnt = IntegerField(null=True)
	context = CharField(null=True)
	exp = IntegerField(null=True)
	reply_id = CharField(null=True)
	reply_name = CharField(null=True)
	status_id = CharField(null=True)
	time = DateTimeField(null=True, default = datetime.utcnow())
	tmp = CharField(null=True)
	tmpFile = CharField(null=True)
	tmpTime = DateTimeField(null=True)
	class Meta:
		db_table = 'users'

class Phrases(UserDBModel):
	phrase = CharField(primary_key=True)
	framework = CharField(null=True)
	s_type = CharField(null=True)
	status = CharField(null=True)
	ok_cnt = IntegerField(null=True)
	ng_cnt = IntegerField(null=True)
	author = CharField(null = True)
	createdAt = DateTimeField(null=True, default = datetime.utcnow())
	updatedAt = DateTimeField(null=True, default = datetime.utcnow())
	class Meta:
		db_table = 'phrases'


class Words(UserDBModel):
    head = CharField()
    length = IntegerField()
    tail = CharField()
    word = CharField(primary_key=True)
    yomi = CharField()
    class Meta:
        db_table = 'words'

class monStatus(UserDBModel):
	name = CharField(primary_key=True)
	nickname= CharField(null=True)
	mode = CharField(null=True)
	exp = IntegerField(null=True)
	LV = IntegerField(null=True)
	nextLVExp = IntegerField(null=True)
	damage = IntegerField(null=True)
	HP = IntegerField(null=True)
	restHP = IntegerField(null=True)
	HPgage= CharField(null=True)
	Atk = IntegerField(null=True)
	Def = IntegerField(null=True)
	SpA = IntegerField(null=True)
	SpD = IntegerField(null=True)
	Spe = IntegerField(null=True)
	enemy_name = CharField(null=True)
	class Meta:
		 db_table = 'mon_status'
#####twtrDB#######
class clockDBModel(Model):
	class Meta:
		database = clockDB
class Task(clockDBModel):
	# timer_id = IntegerField(primary_key=True)
	status = CharField(null=True, default = 'waiting')
	when = DateTimeField(null=True)
	who = CharField(null=True)
	what = CharField(null=True)
	to_whom = CharField(null=True)

	createdAt = DateTimeField(null=True, default = datetime.utcnow())
	updatedAt = DateTimeField(null=True, default = datetime.utcnow())
	tmptext = CharField(null=True, default = '')
	tmpfile = CharField(null=True, default = '')
	tmpcnt = IntegerField(null=True, default = 0)
	tmpid = CharField(null=True, default = '')
	bot_id = CharField(null=True, default = BOT_ID)
	class Meta:
		db_table = 'tasks'

def saveTask(taskdict = {'who':'_umiS', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow()}):
	try:
		clockDB.create_tables([Task], True)
		with clockDB.transaction():
			t = Task(**taskdict)
			t.save()
			clockDB.commit()
			print('TASK_SAVED]')
	except Exception as e:
		print(e)
		clockDB.rollback()

def searchTasks(when = datetime.utcnow(), who = '_umiS', n = 10):
	try:
		# clockDB.create_tables([Timer], True)
		with clockDB.transaction():
			active = Task.select().where(~Task.status == 'end')
			if who == '':
				tasks = active.where(Task.when < when).order_by(Task.id.desc()).limit(n)
			else:
				tasks = active.where(Task.when < when, Task.who == who).order_by(Task.id.desc()).limit(n)
			tasklist = [task.__dict__['_data'] for task in tasks]
			return tasklist
	except Exception as e:
		print(e)
		clockDB.rollback()

def updateTask(taskid = 0, kinds = [''], taskdict = {'who':'_umiS', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow()}):
	try:
		with clockDB.transaction():
			if kinds == ['']:
				task = Task.update(**taskdict).where(Task.id == taskid)
			elif taskid == 0:
				task = Task.update(**taskdict).where(Task.what << kinds)
			else:
				task = Task.update(**taskdict).where(Task.id == taskid, Task.what << kinds)
			task.execute()
	except Exception as e:
		print(e)
		clockDB.rollback()

#####twtrDB#######
class twtrDBModel(Model):
	class Meta:
		database = twtrDB
class Tweets(twtrDBModel):
	status_id = IntegerField(primary_key=True)
	screen_name = CharField(null=True)
	name = CharField(null=True)
	user_id = CharField(null=True)
	text = CharField(null=True)
	in_reply_to_status_id_str = CharField(null=True)
	bot_id = CharField(null=True)
	createdAt = DateTimeField(null=True)
	updatedAt = DateTimeField(null=True)
	class Meta:
		db_table = 'tweets'

def saveTweet(status):
	try:
		twtrDB.create_tables([Tweets], True)
		with twtrDB.transaction():
			Tweets.create(
				status_id = int(status['id_str']),
				screen_name = status['user']['screen_name'],
				name = status['user']['name'],
				text = status['text'],
				user_id = status['user']['id_str'],
				in_reply_to_status_id_str = status['in_reply_to_status_id_str'],
				bot_id = BOT_ID,
				createdAt = datetime.utcnow(),
				updatedAt = datetime.utcnow()
			)
			twtrDB.commit()
			# print('SAVED]')
	except Exception as e:
		print(e)
		twtrDB.rollback()
def getTweetList(n = 1000, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = ['hsw37', 'ry72321', 'MANI_CHO_8', 'HONO_HONOKA_1', 'MOEKYARA_SAIKOU', 'megmilk_0308'], contains = 'です'):
	try:
		# twtrDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with twtrDB.transaction():
			if UserList == []:
				tweets = Tweets.select().where(Tweets.text.contains(contains), ~Tweets.text.contains('RT'), ~Tweets.screen_name << BlackList, ~Tweets.text.contains('【')).order_by(Tweets.createdAt.desc()).limit(n)
			else:
			 	tweets = Tweets.select().where(Tweets.screen_name << UserList , ~Tweets.screen_name << BlackList, ~Tweets.text.contains('RT'), ~Tweets.text.contains('【')).order_by(Tweets.createdAt.desc()).limit(n)
		tweetslist = [utiltools.cleanText(tweet.text) for tweet in tweets]
		return tweetslist
	except Exception as e:
		print(e)
		twtrDB.rollback()

def getPhrase(s_type = '', status = '', n = 10):
	try:
		# UserDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			if status == '':
				Ps = Phrases.select().where(Phrases.s_type == s_type).limit(n)
			elif s_type == '':
				Ps = Phrases.select().where(Phrases.status == status).limit(n)
			else:
				Ps = Phrases.select().where(Phrases.s_type == s_type and Phrases.status == status).limit(n)
			if n == 1:
				return Ps.get().phrase
			else:
				cntArr = np.array([w.ok_cnt for w in Ps])
				P = np.random.choice([p.phrase for p in Ps], p = cntArr/np.sum(cntArr))
				return P
	except Exception as e:
		print(e)
		userDB.rollback()
		return '...'

def savePhrase(phrase, author = 'xxxx', status = 'mid', s_type = 'UserLearn'):
	try:
		# UserDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			P, iscreated = Phrases.get_or_create(phrase = phrase)
			if iscreated:
				P.phrase = phrase
				P.framework = phrase
				P.s_type = s_type
				P.status = status
				P.ok_cnt = 1
				P.ng_cnt = 0
				P.author = author
				P.createdAt
				P.save()
				userDB.commit()
	except Exception as e:
		print(e)
		userDB.rollback()

def getUserInfo(screen_name):
	try:
		# userDB.create_tables([Users], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			try:
				userinfo, iscreated = Users.get_or_create(screen_name = screen_name)
			except Exception as e:
				if screen_name == 'h_y_ok':
					screen_name = '例外h_y_ok'
					userinfo, iscreated = Users.get_or_create(screen_name = screen_name)
				else:
					print(e)
					iscreated = False
			if iscreated:
				userinfo.name = screen_name
				userinfo.nickname = screen_name
				userinfo.cnt = 0
				userinfo.total_cnt = 0
				userinfo.reply_cnt = 0
				userinfo.exp = 0
				userinfo.mode = 'dialog'
				userinfo.time = datetime.utcnow()
			try:
				userinfodata = userinfo.__dict__['_data']
			except:
				userinfodata = ''
			return userinfodata, iscreated
	except Exception as e:
		print(e)
		userDB.rollback()

def saveUserInfo(userstatus):
	try:
		# UserDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			try:
				userinfo = Users(**userstatus)
				userinfo.save()
			except Exception as e:
				print(e)
				return False, userstatus
			userDB.commit()
			return True, userstatus
	except Exception as e:
	  userDB.rollback()
	  return False, userstatus


if __name__ == '__main__':
	# umi = getUserInfo('h_y_ok')
	# umi = getTweetList(n = 10)
	# umi = getPhrase(s_type = 'ぬるぽ', n = 1)
	status = {'favorite_count': 0, 'created_at': 'Wed Feb 17 14:54:01 +0000 2016', 'contributors': None, 'truncated': False, 'in_reply_to_user_id_str': None, 'retweet_count': 0, 'id': 699970059683414016, 'in_reply_to_status_id_str': None, 'geo': None, 'entities': {'hashtags': [], 'urls': [], 'symbols': [], 'user_mentions': []}, 'id_str': '691170059683414016', 'in_reply_to_screen_name': None, 'is_quote_status': False, 'timestamp_ms': '1455720841700', 'coordinates': None, 'in_reply_to_status_id': None, 'filter_level': 'low', 'retweeted': False, 'in_reply_to_user_id': None, 'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 'favorited': False, 'user': {'protected': False, 'created_at': 'Sun Mar 31 01:35:13 +0000 2013', 'utc_offset': 32400, 'favourites_count': 27, 'follow_request_sent': None, 'following': None, 'profile_image_url': 'http://pbs.twimg.com/profile_images/681463777951236096/SbnleYeJ_normal.jpg', 'profile_background_tile': False, 'description': '名前:つゆり きさめ/学生ラブライバー/絶叫勢/ぼっち勢/海未推し/善子推し(仮)/このすば/めぐみんはいいぞ/内田彩/詳細はツイプロ/+aで最近FFの比例がおかしい事に気がついたんでスパムを除く人に見つけ次第フォロー返してます。', 'profile_text_color': '333333', 'friends_count': 1481, 'time_zone': 'Tokyo', 'profile_sidebar_border_color': 'BDDCAD', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/681463777951236096/SbnleYeJ_normal.jpg', 'screen_name': 'tuyuri_kisame', 'default_profile_image': False, 'statuses_count': 40262, 'name': '栗花落 樹雨', 'is_translator': False, 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme16/bg.gif', 'followers_count': 1921, 'location': '神奈川県東部', 'geo_enabled': False, 'verified': False, 'notifications': None, 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/1317490188/1455626298', 'listed_count': 33, 'profile_background_color': '9AE4E8', 'profile_sidebar_fill_color': 'DDFFCC', 'profile_link_color': '0084B4', 'default_profile': False, 'url': 'http://twpf.jp/tuyuri_kisame', 'profile_use_background_image': True, 'contributors_enabled': False, 'id': 1317490188, 'lang': 'ja', 'id_str': '1317490188', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme16/bg.gif'}, 'place': None, 'text': 'トサカのないことりちゃん…( ˘ω˘ )', 'lang': 'ja'}
	# saveTweet(status)
	s = 'tweets'
	# saveTask(taskdict = {'who':'_umiS', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow() + timedelta(hours=0, minutes=0, seconds = 10)})
	# updateTask(taskid = 1, taskdict = {'what': 'end'})
	# savePhrase(phrase = s, author = 'xxxx', status = 'mid', s_type = 'UserLearn')
	# print(getPhrase(s_type = 'trendword', n = 10))
	Timer(period = 2)


