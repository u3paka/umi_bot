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
import twf

class myExeption(Exception): pass


def charconv(text, BOT_ID):
	if BOT_ID == '_rinHz':
		text = text.replace('です', 'だにゃ').replace('ます', 'にゃ')
	return text

def getKusoripu(tg1):
	ans = dealSQL.getPhrase(status = 'kusoripu', n = 20)
	if '{ID}' in ans:
		ans = ans.format(ID= ''.join(['@', tg1]))
	else:
		ans = ''.join(['@', tg1, ans])
	return ans


def monitorTL(status, tmp):
	text = status['cleanText']
	screen_name = status['user']['screen_name']
	if status['user']['screen_name'] == 'eewbot':
		eew, tmp = utiltools.eew(csv = text, standard = 0, tmp = tmp)
		if eew != '':
			ans = eew + '\n(通知実験中: データは本物です。)'
	elif tmp['stats']["tweet_cnt_hour"] > 100:
		ans = ''
	elif status['entities']['urls'] != []:
		ans = ''
	elif status['user']['screen_name'] in tmp['BOTset']:
		ans = ''
	elif 'ぬるぽ' in text:
		ans = dealSQL.getPhrase(s_type = 'ぬるぽ', n = 1)
	elif 'なんでも' in text:
		ans = dealSQL.getPhrase(s_type = 'なんでもって', n = 1)
		#テスト機能
	elif iscalledBOT(text):
		ans = dealSQL.getPhrase(s_type = 'よびだし', n = 1)
	elif 'ヌベヂョン' in text:
		ans = getKusoripu(tg1 = status['user']['screen_name'])
		screen_name = ''
	elif text in set(tmp['tweetPool']['pool']):
		ans = ''.join(['\n', text,'(パクツイ便乗)'])
		if len(ans) > 140:
			ans = text
	elif 'respon' in text:
		return False
	else:
		respSP = utiltools.crowlDic(text = text, dic = tmp["responseWord"])
		if respSP != '':
			ans = respSP
		else:
			text = utiltools.cleanText2(text)
			mas = [w for w in NLP.MA.getMeCabList(text) if w[0] != '。']
			ans = Haiku.Haiku(mas)
	#ツイート
	if ans != '':
		try:
			return twf.tweet(ans, screen_name, status_id = status['id_str'], imgfile = '', tmp = tmp)[0]
		except Exception as e:
			print(e)
			return False
	else:
		return False

def isAllowed(status, tmp = {'BOT_ID' : {}, 'BLACKset' : {}}):
	if status['retweeted'] or status['is_quote_status']:
		return False
	text = status['text']
	if 'RT' in text or 'QT' in text or '定期' in text or '【' in text or 'ポストに到達' in text or 'に入ってからリプライ数' in text:
		return False
	screen_name = status['user']['screen_name']
	if screen_name == tmp['BOT_ID']:
		return False
	if screen_name in tmp['BLACKset']:
		return False
	else:
		return True

def isReact(status , tmp):
	rand = np.random.rand()
	text = status['cleanText']
	if status['in_reply_to_screen_name'] == tmp['BOT_ID']: #リプライ全応答。
		return True
	elif status['in_reply_to_screen_name'] == None:
		if 'おはよ' in text or 'おやすみ' in text:
			return True

	if status['user']['screen_name'] in tmp['BOTset']:
		if rand < 0.001: #BOTに対する自発。0.1%
			return True
	elif status['user']['screen_name'] in tmp['myFriends']:
		if rand < 0.02: #2%
			return True
	elif rand < 0.008: #自発。0.5%
		return True
	else:
		return False

def imitate(screen_name, DIR = '/Users/xxxx'):
	try:
		user = twtr.get_user(screen_name = screen_name)._json
		Altname = user['name']
		Altdescription = user['description']
		isFollowing = user['following']
		if isFollowing == False:
			return False
		USERDIR = '/'.join([DIR, screen_name])
		if os.path.exists(USERDIR) == False:
			os.mkdir(USERDIR)
		if 'profile_image_url' in user:
			absIconfilename = utiltools.saveImg(media_url = user['profile_image_url'].replace('_normal', ''), DIR = USERDIR, filename = ''.join([screen_name, '_icon.jpg']))
		if 'profile_background_image_url' in user:
			absBGfilename = utiltools.saveImg(media_url = user['profile_background_image_url'], DIR = USERDIR, filename = ''.join([screen_name, '_BG.jpg']))
		if 'profile_banner_url' in user:
			absBannerfilename = utiltools.saveImg(media_url = user['profile_banner_url'], DIR = USERDIR, filename = ''.join([screen_name, '_Banner.jpg']))
		twf.updateProfile(name = Altname, description = Altdescription, location = ''.join(['まねっこ中@', screen_name]), url = '', filename = absIconfilename, 	BGfilename = absBGfilename, Bannerfilename = absBannerfilename)
		return True
	except Exception as e:
		print('[ERR]imitate')
		print(e)
		defaultProfile()
		return False

def Main(status, tmp, mode = 'dm'):
	ans = ''
	IMGfile = ''
	tweetStatus = ''
	filename = ''
	text = status['cleanText']
	status_id = status['id_str']
	screen_name = status['user']['screen_name']
	userinfo, isNewUser = dealSQL.getUserInfo(screen_name)
	now = status['now']

	BOT_ID = tmp['BOT_ID']

	#時間計測(秒)
	try:
		try:
			delta = now - userinfo['time']
		except: #文字列対策
			print('convert str into datetime')
			delta = now - datetime.strptime(userinfo['time'], '%Y-%m-%d %H:%M:%S.%f')
		deltasec = delta.total_seconds()
	except Exception as e:
		print(e)
		deltasec = 50

	#返答タイムアウト処理
	if deltasec > 1000:
		userinfo['cnt'] = 0
		userinfo['mode'] = 'dialog'
		if userinfo['mode'] == 'confirm.tag.img':
			src = userinfo['tmpFile']
			drc = DIRIMGundefined
			if os.path.exists(drc) == False:
				os.mkdir(drc)
			shutil.copy(src, drc)

	# 応答
	if 'ping' in text:
		ans = ''.join(['Δsec : ', str(deltasec)])
	elif userinfo['mode'] == 'ignore':
		userinfo['cnt'] = 0
		userinfo['mode'] = 'dialog'
	elif deltasec < 3:
		ans = dealSQL.getPhrase(s_type = 'tooFreq', n = 20)
		userinfo['mode'] = 'ignore'
	elif 'userinfo' in text:
		ans = str(userinfo)
	elif userinfo['mode'] == 'learn.text':
		if status['in_reply_to_screen_name'] in {BOT_ID}:
			text = status['text'].replace('@'+BOT_ID, '')
			text = re.sub(r'(@[^\s　]+)', '{ID}', text)
			if 'end' in text:
				userinfo['mode'] = 'dialog'
				userinfo['tmp'] = ''
				ans = 'learningモードをクローズしました。この結果は開発にフィードバックされます。ご協力感謝します。'
			else:
				labelstatus = userinfo['tmp']
				userinfo['cnt'] = 0
				dealSQL.savePhrase(phrase = text, author = screen_name, status = labelstatus, s_type = 'UserLearn')
				ans = '[learning]saved!!... 続けて覚えさせるテキストをリプライしてください。\nendと入力するまでモードは続きます。'
		else:
			ans = 'learningモードの途中です。覚えさせるテキストをリプライしてください。\nendと入力するまでモードは続きます。'
	elif userinfo['mode'] == 'sleeping' and deltasec > 3600:
		ans = dealSQL.getPhrase(s_type = 'goodmorning', n = 1)
		ans += '\n' + dealSQL.getPhrase(s_type = 'sleep.span', n = 1).format(utiltools.sec2HMSstr(deltasec))
		userinfo['mode'] = 'dialog'

	elif 'media' in status['entities'] and status['in_reply_to_screen_name'] in {BOT_ID}:
		userinfo['cnt'] = 0
		fileID = now.strftime("%Y%m%d%H%M%S")
		if status['entities']['hashtags'] != []:
			imgtag = status['entities']['hashtags'][0]['text']
			try:
				filenames = utiltools.saveMedias(status, ID = fileID, DIR = '/'.join([DIRIMGfeedback, imgtag]))
				ans = dealSQL.getPhrase(s_type = 'appreciate.giveme.img', n = 1).format(imgtag)
			except Exception as e:
				print(e)
				ans = dealSQL.getPhrase(s_type = 'err.get.img', n = 1)
		else:
			try:
				filenames = utiltools.saveMedias(status, ID = fileID, DIR = DIRIMGtmp)
				filename = filenames[0]
				label, FACEflag, IMGfile = NNimg.predictAns(filename  = filename, isShow = False, model = modelNNimg, workDIR = '')
				if FACEflag == False:
					ans = dealSQL.getPhrase(s_type = 'confirm.detect.img.noface', n = 1).format(label)
				else:
					ans = dealSQL.getPhrase(s_type = 'confirm.detect.img', n = 1).format(label)

				drc = '/'.join([DIRIMGfeedback, label])
				if os.path.exists(drc) == False:
					os.mkdir(drc)
				shutil.copy(filename, drc)

				userinfo['mode'] = 'confirm.tag.img'
				print('/'.join([drc, filename.split('/')[-1]]))
				userinfo['tmpFile'] = '/'.join([drc, filename.split('/')[-1]])
				filename = IMGfile
			except Exception as e:
				print(e)
				ans = dealSQL.getPhrase(s_type = 'err.get.img', n = 1)

	elif userinfo['mode'] == 'confirm.tag.img':
		userinfo['cnt'] = 0
		if status['entities']['hashtags'] != []:
			imgtag = status['entities']['hashtags'][0]['text']
			isMoveDIR = True
		elif not 'ない' in text and ('正解' in text or '正し' in text):
			ans = dealSQL.getPhrase(s_type = 'success.detect.img', n = 1)
			userinfo['mode'] = 'dialog'
			isMoveDIR = False
		else:
			try:
				imgtag = TFIDF.calcKWs(text, length = 1, needs = {'固有名詞', '名詞'})[0][0]
			except Exception as e:
				print(e)
				imgtag = 'undefined'
			isMoveDIR = True
		if isMoveDIR:
			src = userinfo['tmpFile']
			drc = '/'.join([DIRIMGfeedback, imgtag])
			if os.path.exists(drc) == False:
				os.mkdir(drc)
			shutil.copy(src, drc)
			if imgtag != 'undefined':
				ans = dealSQL.getPhrase(s_type = 'appreciate.feedback.img', n = 1).format(imgtag)
				userinfo['mode'] = 'dialog'
			else:
				ans = dealSQL.getPhrase(s_type = 'ask.feedback.img', n = 1)
	elif userinfo['cnt'] > 6:
		ans = dealSQL.getPhrase(s_type = 'cntOver', n = 20)
		userinfo['mode'] = 'ignore'
	elif '海未face' in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		umipicDIR = '/Users/xxxx'
		filename = utiltools.getRandIMG(umipicDIR)
		ans = '...'
	elif 'timer' in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		cmds = text.split(' ')
		try:
			timersec = cmds[1]
		except:
			timersec = 300
		try:
			tmptext = cmds[2]
		except:
			tmptext = ''
		setTime = datetime.utcnow() + timedelta(hours=0, minutes=0, seconds = int(timersec))
		dealSQL.saveTask(taskdict = {'who':screen_name, 'what': 'timer', 'to_whom': screen_name, 'when':setTime, 'tmptext': tmptext})
		setTimeJ = setTime + timedelta(hours=9)
		ans = datetime.strftime(setTimeJ, '%m月%d日 %H時%M分%S秒') + 'にタイマーをセットしました。'
	elif 'learn' in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		userinfo['mode'] = 'learn.text'
		cmds = text.split(' ')
		tmplabel = cmds[1]
		userinfo['tmp'] = tmplabel
		userinfo['cnt'] = 0
		ans = '[Learningモード]\n' + tmplabel+ 'として覚えさせるテキストをリプライしてください。\nendと入力するまでモードは続きます。'

	elif 'respon' in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		if 'clear' in text:
			try:
				tmp['responseWord'] = {}
				ans = '全てのTL監視を停止しました。by @' + screen_name + '\n 監視ワードを追加するには半角スペース区切りで、\n response [監視ワード] [応答文]'
				screen_name = ''
			except:
				ans = '設定失敗。半角スペースで区切ってオーダーしてください。'
		else:
			try:
				cmds = text.split(' ')
				tgword = cmds[1]
				response = cmds[2]
				if len(tgword) > 3:
					tmp['responseWord'][tgword] = response
					ans = '「' + tgword + '」を監視して\n「' + response + '」と5分間反応します。by @' + screen_name + '\n 監視ワードを追加するには半角スペース区切りで、\n response [監視ワード] [応答文]'
					setTime = datetime.utcnow() + timedelta(hours=0, minutes=5)
					dealSQL.saveTask(taskdict = {'who':screen_name, 'what': 'erase.tmp.responseWord', 'to_whom': screen_name, 'when':setTime, 'tmptext': tgword})
					screen_name = ''
				else:
					ans = '監視ワードは4文字以上である必要があります。'
			except:
				ans = '設定失敗。半角スペースで区切ってオーダーしてください。'
	elif 'kusoripu' in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		try:
			cmds = text.split(' ')
			tgname = cmds[1]
			user = twtr.get_user(screen_name = tgname)._json
			isFollowing = user['following']
			if isFollowing:
				screen_name = ''
				status_id = ''
				ans = getKusoripu(tg1 = tgname)
			else:
				ans = 'そのユーザーはFF外です。クソリプは制限されます。'
		except:
			ans = 'クソリプ失敗。半角スペースで区切ってオーダーしてください。送信先はアットマークなしで記述してください。'

	elif 'su modsys'  in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		cmds = text.split(' ')
		tmp[cmds[2]] = cmds[3]
		ans = 'mod '+ cmds[2] + ' into ' + cmds[3]

	elif tmp['imitating'] != '' and 'default' in text:
		if twf.defaultProfile():
			ans = 'デフォルトに戻りました'
			tmp['imitating'] = ''
		else:
			ans = 'デフォルトに戻るのに失敗 @_apkX'

	elif 'imitat' in text and status['in_reply_to_screen_name'] in {BOT_ID}:
		try:
			cmds = text.split(' ')
			tgname = cmds[1].replace('@', '').replace('.', '')
			ans = 'imitateErr'
			print(cmds, tgname)
			# imitation中
			print(tmp['imitating'])
			##TODO check whether ff or not
			if imitate(tgname):
				ans = tgname + 'さんのまねっこ5分間開始 defaultリプで元に戻ります。'
				mode = 'open'
				tmp['imitating'] = tgname
				# tmp['clocks']['imitationLimit'] = now + timedelta(hours=0, minutes=30)
				# tmp['clocks']['imitationTimer'] = now + timedelta(hours=0, minutes=5)
				setTime = now + timedelta(hours=0, minutes=5)
				dealSQL.saveTask(taskdict = {'who':BOT_ID, 'what': 'imitate.default', 'to_whom':screen_name, 'when':setTime, 'tmptext': ''})
			else:
				ans = tgname + 'さんのまねっこ失敗 FF外の場合はまねっこできません。'
		except Exception as e:
			print('[ERR][Main.imitation]')
			print(e)
			ans = 'まねっこがどこか失敗です...'

	elif 'しりとり' in text or userinfo['mode'] == 'srtr':
		userinfo['mode'] = 'srtr'
		ans = myGame.SRTR(text, screen_name)
		if '\END' in ans:
			ans = ans.replace('\END', '')
			userinfo['mode'] = 'dialog'
		if '\MISS' in ans:
			ans = ans.replace('\MISS', '')
			if userinfo['cnt'] > 3:
				ans = dealSQL.getPhrase(s_type = 'shiritori.end', n = 1)
				userinfo['mode'] = 'dialog'
				userinfo['cnt'] = 0
		else:
			userinfo['cnt'] = 0

	elif 'おてもん' in text or userinfo['mode'] == 'mon':
		userinfo['mode'] = 'mon'
		userinfo['cnt'] = 0
		try:
			ans = GAME_MON.Main(text, screen_name, 'アルパカさん')
			if '\END' in ans:
				ans = ans.replace('\END', '')
				userinfo['mode'] = 'dialog'
			if '\MISS' in ans:
				ans = ans.replace('\MISS', '')
		except:
			ans = '工事中...'
			userinfo['mode'] = 'dialog'
	elif 'おみくじ' in text or '占い' in text:
		ans = dealSQL.getPhrase(s_type = 'おみくじ', n = 20)
	elif 'おはよ' in text and status['in_reply_to_screen_name'] in set([None, BOT_ID]):
		ans = dealSQL.getPhrase(s_type = 'goodmorning', n = 1)
	elif 'おやすみ' in text and status['in_reply_to_screen_name'] in set([None, BOT_ID]):
		ans = dealSQL.getPhrase(s_type = 'goodnight', n = 1)
		userinfo['mode'] = 'sleeping'
	elif 'トレンドワード' in text:
		ans = '\n- '.join(['[現在のトレンドワード]']+tmp['trendwordsList'][:10])
	elif deltasec > 600000: #3日
		ans = dealSQL.getPhrase(s_type = 'longtimenosee', n = 1)
	else:
		ans = trigramMC.dialog(text, isRandMetaS = True, isPrint = True, isLearn = False, n =5, tryCnt = 10, needs = set(['名詞', '固有名詞'])).replace('<人名>', status['user']['name'])
		ans = charconv(ans, BOT_ID)

	# if isNewUser:
	# 	ans = dealSQL.getPhrase(s_type = 'welcomeNewUser', n = 20)

	if ans != '':
		tweetStatus, tmp = twf.send(ans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = mode, tmp = tmp)
	userinfo['time'] = now
	userinfo['cnt'] += 1
	dealSQL.saveUserInfo(userinfo)
	return tweetStatus, tmp

class StreamListener(tweepy.streaming.StreamListener):
	def __init__(self):
		print('loading initialData...')
		super(StreamListener,self).__init__()
		tmp['clocks'] = {}
		tmp['clocks']['start_time'] = datetime.utcnow()
		# tmp['clocks']['future30'] = tmp['clocks']['start_time'] + timedelta(hours=0, minutes=1)
		# tmp['clocks']['imitationLimit'] = tmp['clocks']['start_time']
		# tmp['clocks']['imitationTimer'] = tmp['clocks']['start_time']
		tmp['imitating'] = BOT_ID

		tmp['BOT_ID'] = BOT_ID
		tmp['BOTset'] = [UserObject.screen_name for UserObject in twtr.list_members('_umiS', 'BOT',  -1)]
		tmp['myFriends'] = [UserObject.screen_name for UserObject in twtr.list_members(BOT_ID, 'myFriends',  -1)]
		tmp['BLACKset'] = [UserObject.screen_name for UserObject in twtr.list_members(BOT_ID, 'BLACKLIST',  -1)]
		tmp['trendwordsList'] = twf.getTrendwords()
		tmp['tweetStatus'] =  {'isDebug':0, 'isSplitTweet': False, 'tempStop_since':0}
		tmp['tweetPool'] = {'cnt': 0, 'pool':[]}
		tmp['eewIDset'] = {}
		utiltools.saveJSON(tmp)
		print('setupData has loaded! starting Streaming...')
	def __del__(self):
		print('stopping Streaming...')
	def on_status(self,status):
		tmp = utiltools.getJSON()
		tmp['stats']["TL_cnt"] += 1
		status = status._json
		# print(status)
		dealSQL.saveTweet(status)
		if isAllowed(status, tmp):
			status_id = status['id_str']
			screen_name = status['user']['screen_name']
			replyname = status['in_reply_to_screen_name']
			text = utiltools.cleanText(status['text'])
			print(status['user']['name'], ']@', replyname, text)

			now = datetime.utcnow()
			tmp['clocks']['now'] = now
			#ツイートステータス情報追加処理
			status['now'] = now
			status['cleanText'] = text

			#直近ツイート処理
			#TL監視クイックレスポンス
			if monitorTL(status, tmp):
				return True

			#Tweetプーリング
			if not screen_name in tmp['BOTset'] and status['entities']['urls'] == [] and len(text)>5 and not '便乗' in text and not 'imitate' in text and not 'learn' in text and not 'img' in text and not 'kusoripu' in text:
				tmp['tweetPool']['pool'].append(text)
				if tmp['tweetPool']['cnt'] > 10:
					tmp['tweetPool']['pool'].pop(0)
				else:
					tmp['tweetPool']['cnt'] += 1

			# リアクション
			if isReact(status, tmp):
				tweetStatus, tmp = Main(status, tmp = tmp, mode = 'tweet')
		utiltools.saveJSON(tmp)
		return True
	def on_direct_message(self,status):
		# status = utiltools.dm2tweet(status._json)
		# text = utiltools.cleanText(status['text'])
		# status['cleanText'] = text
		# if isAllowed(status, tmp):
		# 	status_id = status['id_str']
		# 	screen_name = status['user']['screen_name']
		# 	text = utiltools.cleanText(status['text'])
		# 	status['cleanText'] = text
		# 	now = datetime.utcnow()
		# 	tmp['clocks']['now'] = now
		# 	print(status['user']['name'], text)
		# 	#TL監視クイックレスポンス
		# 	if monitorTL(status, tmp = tmp):
		# 		return True
		# 	tweetStatus, tmp = Main(status, mode = 'dm', tmp = tmp)
		return True
	def on_error(self,status):
		print ("can't get")
	def on_timeout(self):
		raise myExeption

def Stream(auth):
	stream = tweepy.Stream(auth = auth, listener = StreamListener(), async = True, secure=True)
	while True :
		try:
			stream.userstream()
		except Exception as e:
			print(e)
			time.sleep(100)
			stream = tweepy.Stream(auth,StreamListener())

