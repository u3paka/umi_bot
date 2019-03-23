#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
from dealSQL import userDB, monStatus

def HPgager(restHP, fullHP):
	aHPgage = fullHP//5
	if restHP == 0:
		HPgage = '□□□□□'
	elif restHP < aHPgage:
		HPgage = '■□□□□'
	elif restHP < 2* aHPgage:
		HPgage = '■■□□□'
	elif restHP < 3* aHPgage:
		HPgage = '■■■□□'
	elif restHP < 4* aHPgage:
		HPgage = '■■■□□'
	elif restHP < 5* aHPgage:
		HPgage = '■■■■□'
	else:
		HPgage = '■■■■■'
	return HPgage

def readStatus(user = 'xxxx'):
		try:
			userDB.create_tables([monStatus], True)
			with userDB.transaction():
				try:
					status, created = monStatus.get_or_create(name = user)
					if created:
						print('newMON')
					return status
				except Exception as e:
					print(e)
				userDB.commit()
		except Exception as e:
			userDB.rollback()

def readUDB(user = 'xxxx'):
		try:
			with userDB.transaction():
				try:
					status= Users.select().where(Users.screen_name == user).get()
					return status
				except Exception as e:
					return ''
				userDB.commit()
		except Exception as e:
			userDB.rollback()

def init(name = 'xxxx', LV = 0):
	# userinfoデータよみだし
	status = {}
	try:
		userinfo = readUDB(name)
		lasttime = userinfo.time
		totalcnt = userinfo.totalcnt+1
		friends_cnt = userinfo.friends_cnt+1
		followers_cnt = userinfo.followers_cnt+1
		statuses_cnt = userinfo.statuses_cnt+1
		fav_cnt = userinfo.fav_cnt+1
		status['name'] = name
		status['nickname'] = userinfo.name[:5]
	except Exception as e:
		totalcnt = 1
		lasttime = 1
		friends_cnt = 100
		followers_cnt = 100
		statuses_cnt = 100
		fav_cnt = 100
		status['name'] = name
		status['nickname'] = name
	try:
		exp = userinfo.exp
		if exp == 0:
			exp = totalcnt *100
	except:
		exp = totalcnt *100
	# 計算式
	d = datetime.today()
	nowtime = d.strftime("%Y%m%d%H%M%S")
	difT = (int(nowtime)-int(lasttime) - 100) // 60
	Spe = 20-int(utiltools.sigmoid(difT)*10)
	status['exp'] = exp
	if LV == 0:
		status =  calcLv(status)
		LV = status['LV']
	else:
		status['LV'] = LV
		status['nextLVExp'] = 0
	status['damage'] = 0
	status['mode'] = 'encount'
	fullHP = int(np.log2(statuses_cnt)*10 * (LV/100) +(LV +10))
	restHP = fullHP
	status['HP'] = fullHP
	status['restHP'] =restHP
	status['HPgage'] = HPgager(restHP, fullHP)
	status['Atk'] = int(np.log2(friends_cnt)*10 * (LV/100) +(LV +5))
	status['Def'] = int(np.log2(followers_cnt)*10 * (LV/100) +(LV +5))
	status['SpA'] = int(np.log2(fav_cnt)*10 * (LV/100) +(LV +5))
	status['SpD'] = int(np.log2(totalcnt)*10 * (LV/100) +(LV +5))
	status['Spe'] = int(np.log2(Spe)*10 * (LV/100) +(LV +5))
	status['enemy_name'] = 'AlpkS'
	return status

def calcLv(status):
	exp = status['exp']
	if exp == None:
		exp = 1
	if exp != 0:
		nLv = 10
		LV = 0
		while exp > nLv:
			nLv = LV ** 3
			exp = exp - nLv
			LV = LV + 1
	else:
		LV = 10
	LvList = np.array([(lv) ** 3 for lv in range(LV+1)])
	print(LvList)
	nextLVExp = np.sum(LvList)
	status['nextLVExp'] = nextLVExp
	status['LV'] = LV
	return status

def getStatus(name, LV = 0):
	try:
		status = {}
		mystatus = readStatus(name)
		if mystatus.exp == None:
			mystatus = init(name, LV)
		status = mystatus.__dict__['_data']
	except Exception as e:
		print(e)
		status = init(name)
	return status

def dealStatus(name, enemy):
	status = getStatus(name)
	try:
		LV = status['LV']
		if LV == None:
			LV = 0
		status = calcLv(status)
		altLV = status['LV']
		enemy_name = status['enemy_name']
		if altLV > LV:
			upLV = altLV - LV
			print('LVが'+str(upLV)+'上がりました！！！次エンカウント時にステータスが上昇します。')
	except:
		enemy_name = None
	enemyLV = status['LV'] - 1
	if enemy_name == None:
		enemy_name = enemy
		e_status = init(enemy, enemyLV)
	else:
		e_status = getStatus(enemy_name, LV)
	return status, e_status

def encount(me, enemy):
	ans = ''
	try:
		mystatus = getStatus(me)
		enemyLV = mystatus['LV'] - 1
	except Exception as e:
		print(e)
		mystatus = init(me)
		enemyLV = mystatus['LV'] - 1
		ans += 'データ新規作成'
	e_status = init(enemy, enemyLV)
	mystatus['mode'] = 'battle'
	return mystatus, e_status, ans

# def recover(name, amount = 1000):
# 	status, statusE = getStatus(name)
# 	maxHP = status['HP']
# 	restHP = status['restHP']

# 	if restHP + amount > maxHP:
# 		amount = maxHP - restHP
# 	twmonsDB.update_one({'_id': name},{'$inc': {'restHP': amount}}, upsert =True)
# 	status, statusE = getStatus(name)
# 	return status

# def getEXP(name, amount):
# 	twmonsDB.update_one({'_id': name},{'$inc': {'exp': amount}}, upsert =True)
# 	if amount > 0:
# 		print(str(amount) + 'exp獲得')
# 	else:
# 		print(str(-amount) + 'exp減少')
# 	status, statusE = getStatus(name)
# 	return status

def battle(status, statusE, waza = 100):
	ans = ''
	try:
		rnd = np.random.randint(100);
		rndDMG = int(np.random.randint(15)) + 60;
		restHP = status['restHP']
		Atk = status['Atk']
		damage = Atk- status['Def']
		Atker = statusE['nickname']
		kisoDMG = int(int((waza * int(statusE['LV'] * 2 / 5) + 2 ) * Atk / status['Def'])/ 50) + 2
		damage = int(kisoDMG * rndDMG / 100)
	except Exception as e:
		print(e)
	if damage < 0:
		damage = 0
		ans += Atker + 'の攻撃...' + 'こうかなしです'
	elif rnd < 16:
		damage = 0
		ans += Atker + 'の攻撃...' + 'はずれました'
	elif rnd < 12:
		damage = damage * 2
		ans += Atker + 'の攻撃 ' + 'きゅうしょ' + str(damage) + 'ダメ'
	else:
		ans += Atker + 'の攻撃 ' + str(damage) + 'ダメ'
	restHP = restHP - damage
	if restHP < 0:
		restHP = 0
	fullHP = status['HP']
	status['restHP'] = restHP
	status['damage'] = damage
	status['HPgage'] = HPgager(restHP, fullHP)
	return status, statusE, ans

def display(status, statusE):
	try:
		restHPe = statusE['restHP']
		me = status['name']
		mynickname = status['nickname']
		ans = 'ー\n'
		ans += statusE['nickname']+ 'Lv'+str(statusE['LV']) + '\n'
		ans += statusE['HPgage']+ '['+str(statusE['damage'])+'↓\n'
		ans += 'HP'+ str(restHPe)+'/'+str(statusE['HP'])+ '\n'
		ans += '↑ー↓'+ '\n'
		ans += status['nickname'] + 'Lv'+str(status['LV'])+ '\n'
		ans += status['HPgage']+'['+str(status['damage'])+'↓'+ '\n'
		restHP = str(status['restHP'])
		ans += 'HP'+ str(restHP)+'/'+str(status['HP'])+ '\n'
		
		if restHPe <= 0:
			kotaichi = 50
			addexp = int(kotaichi * statusE['LV'])
			ans += statusE['name'] + 'をたおした( •̀ ᴗ •́ )#END'
			statusE['restHP'] = statusE['HP']
			status['enemy_name'] = 'アルパカさん'
			status['mode'] = 'encount'
		elif restHP != 0:
			ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'+ '\n'
			status['enemy_name'] = statusE['name']
		else:
			ans += mynickname + 'はたおれた\nめのまえがまっくらになった\n( •̀ ᴗ •́ ) #END'
			status['enemy_name'] = statusE['name']
			status['mode'] = 'encount'
			maxHP = status['HP']
			status['restHP'] = maxHP
		return status, ans
	except Exception as e:
		print('ERR.display', e)
		return status, ans

def selectMode(text):
	if 'たたかう' in text:
		p2 = 'battle'
	elif '1' in text:
		p2 = 'battle'
	elif 'へるぷ' in text:
		p2 = 'help'
	elif '2' in text:
		p2 = 'help'
	elif 'かくにん' in text:
		p2 = 'status'
	elif '3' in text:
		p2 = 'status'
	elif 'にげる' in text:
		p2 = 'にげる'
	elif '4' in text:
		p2 = 'にげる'
	elif 'リカバリ' in text:
		p2 = 'recovery'
	elif 'ほむまん' in text:
		p2 = 'ほむまん'
	elif '炭酸' in text:
		p2 = '炭酸'
	elif 'はじめから' in text:
		p2 = 'リセット'
	elif 'リセット' in text:
		p2 = 'リセット'
	elif 'エンカウント' in text:
		p2 = 'encount'
	elif 'リネーム' in text:
		p2 = 'rename'
	elif 'セーブ' in text:
		p2 = 'セーブ'
	elif 'アプデ' in text:
		p2 = 'update'
	elif 'あぷで' in text:
		p2 = 'update'
	elif 'update' in text:
		p2 = 'update'
	elif 'へるぷ' in text:
		p2 = 'help'
	elif 'ツール' in text:
		p2 = 'tool'
	elif 'どうぐ' in text:
		p2 = 'tool'
	elif 'つーる' in text:
		p2 = 'tool'
	else:
		 p2 = 'back'
	return p2

def sendEXP(status):
	try:
		status['mode'] = 'battle' ## back
		print('( •̀ ᴗ •́ )データのセーブが完了しました。#END' + '#exp' + str(status['exp']))
	except Exception as e:
		print(e)
		print('( •̀ ᴗ •́ )データのセーブに失敗しました。そんなこともありますよね。#END' + '#exp' + str(status['exp']))
	return status

def showStatus(status):
	try:
		nextLVExp = status['nextLVExp']
		exp = status['exp']
		difexp = nextLVExp - exp
		print('( •̀ ᴗ •́ )',status['name'])
		print('の能力値は...')
		print('LV',status['LV'])
		# print('exp',status['exp'])
		print('次Lvまで'+str(difexp)+'exp')
		print('HP', status['HP'])
		print('Atk', status['Atk'])
		print('Def', status['Def'])
		print('SpA', status['SpA'])
		print('SpD', status['SpD'])
		print('Spe', status['Spe'])
		print('ーーです。\n1.たたかう 2.つーる\n3.かくにん 4.にげる')
	except:
		print('測定できません。フォローされていないか、データーベースが構築されていないかだと思います...')

def selectModebyStatus(p2, status, statusE):
	mode = status['mode']
	if mode == 'encount':
		p2 = 'encount'
	elif mode == 'battle':
		if status['Spe'] > statusE['Spe']:
			p2 = 'battle.attack'
		else:
			p2 = 'battle.attacked'
	elif mode == 'battle.attacked':
		p2 = 'battle.attacked'
	elif mode == 'battle.attack':
		p2 = 'battle.attack'
	else:
		p2 = 'back'
	return p2

def Main(text, me, enemy = 'アルパカ'):
	ans = ''

	p2 = selectMode(text)
	isSaveOK = True
	try:
		status, statusE = dealStatus(me, enemy)
		p2 = selectModebyStatus(p2, status, statusE)
	except Exception as e:
		print(e)
		ans += '( •̀ ᴗ •́ )おとのきざかモンスター`s[海未](通称:うみもん)のせかいへようこそ。[β版]\n 進行役の園田海未です。私となかよくしたり、ふぁぼったり、ツイートしたり、ゲームであそんだりすると強くなれますよ。\n「たたかう」と返信して、さぁ修行ですっ！！'
		status = init(me)
		e_status = init(enemy)
		status['mode'] = 'encount'
		save(status)
		return ans

	try:
		if p2 == 'status':
			showStatus(status)
		elif p2 == 'リセット':
			isSaveOK = reset(me)
		elif p2 == 'セーブ':
			status = sendEXP(status)
			status['mode'] = 'battle'
		# elif p2 == 'rename':
		# 	try:
		# 		newname = cmdlist[1].replace('@', '')
		# 		if len(newname)>5:
		# 			ans += '文字数が長いです。5文字まででお願いします。'
		# 		else:
		# 			oldname = status['nickname']
		# 			status['nickname'] = newname
		# 			ans += '( •̀ ᴗ •́ )'+oldname+ 'から'+ newname +'にニックネームの変更が完了しました。'
		# 		ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
		# 	except:
		# 		ans +='( •̀ ᴗ •́ )その名前ではリネームできません'
		# 		ans +='1.たたかう 2.つーる\n3.かくにん 4.にげる'
		elif p2 == 'encount':
			try:
				status, statusE, ansENCOUNT = encount(me, enemy)
				ans += ansENCOUNT
				ans += ''.join(['( •̀ ᴗ •́ )あ、やせいの\n',statusE['name'],'\nがあらわれました'])
			except Exception as e:
				print(e)
				status, statusE, ansENCOUNT = encount(me, enemy)
				ans += ansENCOUNT
				ans +=''.join(['( •̀ ᴗ •́ )あ、やせいの\n',statusE['name'],'\nがあらわれました'])
			status['HPgage'] =  '■■■■■'
			status, ans = display(status, statusE)
			status['mode'] = 'battle'

		elif p2 == 'recovery':
			restHP = status['restHP']
			maxHP = status['HP']
			status = recover(me)
			ans += '( •̀ ᴗ •́ )HPが全回復しました\n' + str(restHP) +'->' + str(maxHP)
			ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'

		elif p2 == 'ほむまん':
			restHPB = status['restHP']
			status = recover(me, 10)
			restHPA = status['restHP']
			maxHP = status['HP']
			ans += '( •̀ ᴗ •́ )HPが10回復しました。('+ str(restHPB) +'->' + str(restHPA) +')/'+ str(maxHP) +'\代償として20経験値下げておきますね'
			status = getEXP(me, -20)
			ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'

		elif p2 == '炭酸':
			status = recover(status, -10)
			ans += '( •̀ ᴗ •́ )怒 HPを10減らしました。炭酸はきらいです。'
			ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
		elif p2 == 'update':
			status = init(me)
			ans += '( •̀ ᴗ •́ )ステータスをアップデートしました。'
			ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
		elif p2 == 'battle.attacked':
			random.seed(text)
			waza = random.randint(0, 150)
			status, statusE, ansB = battle(status, statusE, waza)
			status, ansD = display(status, statusE)
			ans += ansB +'\n'+ ansD
			status['mode'] = 'battle.attack'
		elif p2 == 'battle.attack':
			random.seed(text)
			waza = random.randint(0, 150)
			statusE, status, ansB = battle(statusE, status, waza)
			status, ansD = display(status, statusE)
			ans += ansB +'\n'+ ansD
			status['mode'] = 'battle.attacked'
		elif p2 == 'tool':
			ans += toolNote

		elif p2 == 'help':
			ans += helpNote
	
		elif p2 == 'back':
			ans += '( •̀ ᴗ •́ )行動を選択してください'
			status, ans = display(status, statusE)
			status['mode'] = 'back'
	
		elif p2 == 'にげる':
			rnd = np.random.randint(100);
			if rnd < 80:
				ans += 'うまくにげられました。\n( •̀ ᴗ •́ )またあそんでくださいね。#END'
				status['enemy'] = ''
				status['mode'] = 'encount'
			else:
				ans += '( •̀ ᴗ •́ ) にげられないです'
				status, ans = display(status, statusE)
		else:
			if status['Spe'] > statusE['Spe']:
				status, statusE = battle(status, statusE)
				status, ans = display(status, statusE)
				status['mode'] = 'battle.attacked'
			else:
				status, statusE = battle(statusE, status)
				status, ans = display(status, statusE)
				status['mode'] = 'battle.attack'
	except Exception as e:
		print(e)
		try:
			try:
				ans += '( •̀ ᴗ •́ )あ、敵は逃げてしまいました。また今度にしましょう。とりあえず、オートセーブしておきました。再開する場合は「うみもん」で。バグったら「リセット」#END' + '#exp' + str(status['exp'])
			except Exception as e:
				print(e)
				ans += '( •̀ ᴗ •́ )あ、敵は困って逃げてしまいました。また今度にしましょう。 再開する場合は「うみもん」で。バグったら「リセット」#END'
			status = init(me)
			statusE = init(enemy)
		except Exception as e:
			print(e)
			ans +='( •̀ ᴗ •́ )バグ発生です。\n そんなこともありますよね。そのうち直しておきますね #END'
	
	if isSaveOK == True:
		save(status)
		save(statusE)
	return ans

def save(status):
	try:
		userDB.create_tables([monStatus], True)
		with userDB.transaction():
			try:
				mstatus, created = monStatus.get_or_create(name = status['name'])
				# print(created)
				mstatus.name = status['name']
				mstatus.nickname = status['nickname']
				mstatus.mode = status['mode']
				mstatus.exp = status['exp']
				mstatus.LV = status['LV']
				mstatus.nextLVExp = status['nextLVExp']
				mstatus.damage = status['damage']
				mstatus.HP = status['HP']
				mstatus.restHP = status['restHP']
				mstatus.HPgage = status['HPgage']
				mstatus.name = status['name']
				mstatus.Atk = status['Atk']
				mstatus.Def = status['Def']
				mstatus.SpA = status['SpA']
				mstatus.SpD = status['SpD']
				mstatus.Spe = status['Spe']
				mstatus.enemy_name = status['enemy_name']
				mstatus.save()
			except Exception as e:
				print(e)
			userDB.commit()
	except IntegrityError as ex:
		print (ex)
		userDB.rollback()

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		me = argvs[1]
		intext = argvs[2]
	except:
		me = 'xxxx'
		intext = 'リセット'
		intext = 'エンカウント KOTORI'
		intext = 'セーブ'
		intext = 'たたかう'
	cmdlist = intext.split(' ')
	text = cmdlist[0]
	enemy = 'アルパカ'
	# init('xxxx')
	# メイン
	ans = Main(text, me, enemy)
	print(ans)
	# getEXP('xxxx', 1000000)
	
