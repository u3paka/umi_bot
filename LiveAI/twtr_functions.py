#!/usr/bin/env python
# -*- coding:utf-8 -*-

#MY MODULEs
#variables
from setup import *
import _
from _ import p, d, MyObject, MyException
import natural_language_processing
import operate_sql
import main
# @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
class StreamListener(tweepy.streaming.StreamListener):
	def __init__(self, srf = None, q = None, lock = None, events = None):
		super().__init__()
		self.srf = srf
		self.bot_id = srf.bot_id
		self.q = q
		self.lock = lock
		self.events = events
	def __del__(self):
		p(self.bot_id, 'stopping streaming...')
	# @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
	# def on_data(self, data):
		# p(self.events.stop.is_set(), self.events.ping.is_set())
	def on_connect(self):
		return True
	def on_friends(self, friends):
		bot_process = threading.Thread(target = self.srf.on_friends_main, args=(friends,), name = self.bot_id+ '_on_friends', daemon = True)
		bot_process.start()
		self.events.ping.set()
		return True
	def on_delete(self, status_id, user_id):
		self.events.ping.set()
		return True
	# @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
	def on_status(self, status):
		bot_process = threading.Thread(target = self.srf.on_status_main, args=(status._json,), name = self.bot_id+ '_on_status', daemon = True)
		bot_process.start()
		self.events.ping.set()
		return True
	@_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
	def on_direct_message(self,status):
		bot_process = threading.Thread(target = self.srf.on_direct_message_main, args=(status._json,), name = self.bot_id+ '_on_direct_message', daemon = True)
		bot_process.start()
		self.events.ping.set()
		return True
	@_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
	def on_event(self, status):
		bot_process = threading.Thread(target = self.srf.on_event_main, args=(status._json,), name = self.bot_id + '_on_event', daemon = True)
		bot_process.start()
		self.events.ping.set()
		return True
	def keep_alive(self):
		p(self.bot_id, 'keep_alive...')
		self.events.ping.set()
		return True
	def on_limit(self, track):
		p(self.bot_id, 'track', track)
		return True
	def on_warning(self, notice):
		p(notice, 'warning')
		return True
	def on_exception(self, exception):
		p(exception, self.bot_id, 'exception')
		return False
	def on_disconnect(self, notice):
		d(notice, 'disconnect')
		return False
	def on_error(self,status_code):
		p(status_code, 'cannot get')
		return False
	def on_timeout(self):
		p('timeout...')
		return False
	def on_closed(self, resp):
		return False
def get_twtr_auth(auth_dic):
	CONSUMER_KEY = auth_dic['consumer_key']
	CONSUMER_SECRET = auth_dic['consumer_secret']
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	ACCESS_TOKEN = auth_dic['access_token_key']
	ACCESS_SECRET = auth_dic['access_token_secret']
	auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
	return auth
class TwtrTools(MyObject):
	def __init__(self, bot_id = 'LiveAIs'):
		self.bot_id = bot_id
		api_keys = cfg['twtr']
		twtr_auths = {key: get_twtr_auth(value) for key, value in api_keys.items()}
		twtr_apis = {key: tweepy.API(value, wait_on_rate_limit = True) for key, value in twtr_auths.items()}
		self.twtr_auth = twtr_auths[bot_id]
		self.twtr_api = twtr_apis[bot_id]
	#ベータ版
	# @_.retry(Exception, tries=30, delay=30, max_delay=240, jitter=0.25)
	# @_.retry(tweepy.TweepError, tries=30, delay=0.3, max_delay=16, jitter=0.25)
	def user_stream(self, srf, q, lock, events):
		# _.reconnect_wifi()
		p('start user_stream')
		auth = self.twtr_auth
		stream = tweepy.Stream(auth = auth, listener = StreamListener(srf, q, lock, events), async=False, timeout = 180)
		stream.userstream(stall_warnings=True, _with=None, replies=None, track=None, locations=None, encoding='utf8', async=True)
		p('waiting stop event')
		events.stop.wait()
		p('stopping user_stream')
		stream.running = False
	@_.retry(tweepy.TweepError, tries=30, delay=0.3, max_delay=16, jitter=0.25)
	def filter_stream(self, twq = None, track=['python']):
		auth = self.twtr_auth
		stream = tweepy.Stream(auth = auth, listener = FilterStreamListener(twq), timeout = 60, async = 1, secure=True)
		stream.filter(async=True, languages=['ja'],track=['#'])
	def get_status(self, status_id):
		try:
			return self.twtr_api.get_status(id = status_id)
		except tweepy.error.TweepError as e:
			return None

	def send(self, ans, screen_name = '', status_id = '', imgfile = '', mode = 'dm', try_cnt = 0):
		if mode == 'dm':
			return self.send_direct_message(ans = ans, screen_name = screen_name)
		elif mode == 'open':
			return self.send_tweet(ans = ans, screen_name = '', status_id = '', imgfile = imgfile, try_cnt = try_cnt)
		else:
			return self.send_tweet(ans = ans, screen_name = screen_name, status_id = status_id, imgfile = imgfile, try_cnt = try_cnt)
	def send_tweet(self, ans, screen_name = '', status_id = '', imgfile = '',  try_cnt = 0):
		if screen_name:
			ans1 = ''.join(['@', screen_name,' ', ans]).replace('@@', '@')
		else:
			ans1 = ans
		if len(ans1) > 140:
			is_split = True
			ans2 = ''.join([ans1[0:139], '…'])
		else:
			is_split = False
			ans2 = ans1
		if imgfile:
			tweet_status = self.twtr_api.update_with_media(imgfile, status = ans2, in_reply_to_status_id = status_id)
			print(self.bot_id, '[Tweet.IMG.OK] @', screen_name, ' ', ans2)
		else:
			tweet_status = self.twtr_api.update_status(status = ans2, in_reply_to_status_id = status_id)
			print(self.bot_id, '[Tweet.OK] @', screen_name, ' ', ans2)
		# 140字越えの際は、分割ツイート
		if is_split:
			if screen_name:
				try_cnt += 1
				return self.send_tweet(''.join(['...', ans[139:]]), screen_name = screen_name, status_id = status_id, try_cnt = try_cnt)
			else:
				return tweet_status
		else:
			return tweet_status

	def send_direct_message(self, ans, screen_name = '', try_cnt = 0):
		tweet_status = self.twtr_api.send_direct_message(screen_name = screen_name, text = ans)
		print('[DM.OK] @', screen_name, ' ', ans)
		return tweet_status

	def getTrendwords(self, mode = 'withoutTag'):
		# 'locations': [{'woeid': 23424856, 'name': 'Japan'}]
		trends = self.twtr_api.trends_place(id = 23424856)[0]['trends']
		if mode == 'withoutTag':
			return [trend['name'] for trend in trends if not '#' in trend['name']]
		elif mode == 'withTag':
			trendtags = [trend['name'] for trend in trends if '#' in trend['name']]
			trendwords = [trend['name'] for trend in trends if not '#' in trend['name']]
			return trendwords, trendtags
		else:
			return [trend['name'] for trend in trends]
	def update_profile(self, name, description, location, url = '', filename = '', BGfilename = '', Bannerfilename = ''):
		try:
			self.twtr_api.update_profile(name = name, url = url,  location = location, description = description)
			if filename:
				self.twtr_api.update_profile_image(filename)
			if BGfilename:
				self.twtr_api.update_profile_background_image(BGfilename)
			if Bannerfilename:
				self.twtr_api.update_profile_banner(Bannerfilename)
			return True
		except Exception as e:
			print(e)
			return False
	def is_create_list_success(self, name, mode = 'private', description = ''):
		try:
			self.twtr_api.create_list(name = name, mode = mode, description = description)
			return True
		except:
			return False
	def get_listmembers_all(self, username, listname):
		try:
			return [UserObject.screen_name for UserObject in tweepy.Cursor(self.twtr_api.list_members, username, listname).items()]
		except tweepy.error.TweepError as e:
			if e.api_code == '34':
				if username == self.bot_id:
					p(listname, 'MAKE the LIST!!')
			# 		self.is_create_list_success(name = listname)
			return []
		except:
			return []
	def get_followers_all(self, screen_name):
		return self.twtr_api.followers(screen_name = screen_name)
	def give_fav(self, status_id):
		try:
			self.twtr_api.create_favorite(id = status_id)
		except :
			return False
		else:
			return True
	def get_userinfo(self, screen_name):
		try:
			return self.twtr_api.get_user(screen_name = screen_name)._json
		except :
			pass
	def is_destroy_friendship_success(self, screen_name):
		try:
			self.twtr_api.destroy_friendship(screen_name = screen_name)
			return True
		except:
			return False
	def is_create_friendship_success(self, screen_name):
		try:
			self.twtr_api.create_friendship(screen_name = screen_name)
			return True
		except:
			return False
	def convert_direct_message_to_tweet_status(self, status):
  		s = status['direct_message']
  		s['user'] = {}
  		s['user']['screen_name'] = s['sender_screen_name']
  		s['user']['name'] = s['sender']['name']
  		s['user']['id_str'] = s['sender']['id_str']
  		s['in_reply_to_status_id_str'] = None
  		s['in_reply_to_screen_name'] = self.bot_id
  		s['extended_entities'] = s['entities']
  		s['retweeted'] = False
  		s['is_quote_status'] = False
  		return s
	def download_userobject_urls(self, userobject, target_object, DIR = DIRusers):
		screen_name = userobject.screen_name
		if target_object is None:
			target_object = operate_sql.BotProfile(screen_name)
		USERDIR = '/'.join([DIR, screen_name])
		if not os.path.exists(USERDIR):
			os.mkdir(USERDIR)
		target_object.name = userobject.name.replace(' ' , '')
		target_object.description = userobject.description
		target_object.abs_icon_filename = ''
		target_object.abs_background_filename = ''
		target_object.abs_banner_filename = ''
		try:
			# if not userobject.profile_image_url is None:
			if hasattr(userobject, 'profile_image_url'):
				target_object.abs_icon_filename = _.saveImg(media_url = userobject.profile_image_url.replace('_normal', ''), DIR = USERDIR, filename = ''.join([screen_name, '_icon.jpg']))
		except Exception as e:
			_.log_err()
		try:
			# if not userobject.profile_banner_url is None:
			if hasattr(userobject, 'profile_banner_url'):
				target_object.abs_banner_filename = _.saveImg(media_url = userobject.profile_banner_url, DIR = USERDIR, filename = ''.join([screen_name, '_banner.jpg']))
		except Exception as e:
			_.log_err()
		return target_object
	def imitate(self, screen_name, DIR = DIRusers):
		try:
			userobj = self.twtr_api.get_user(screen_name = screen_name)
			if not userobj.following:
				return False
			user = self.download_userobject_urls(userobj, target_object = None, DIR = DIR)
			set_time = datetime.utcnow() + timedelta(hours=9, minutes=10)
			self.update_profile(name = user.name, description = user.description, location = ''.join([set_time.strftime('%m月%d日%H:%M'), 'までモノマネ中@', screen_name]), url = '', filename = user.abs_icon_filename, BGfilename = user.abs_background_filename, Bannerfilename = user.abs_banner_filename)
			return True
		except Exception as e:
			_.log_err()
			return False




