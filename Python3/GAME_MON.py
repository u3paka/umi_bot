#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import subprocess
# import scipy as sp
import datetime # datetimeモジュールのインポート
import numpy as np
import random
import sqlite3
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
database = SqliteExtDatabase('../umiA.sqlite3', autocommit=False, journal_mode='persist')
database.connect()

class BaseModel(Model):
    class Meta:
        database = database

class Srtrtemps(BaseModel):
    kanasstream = CharField(db_column='kanasStream', null=True)
    lenrule = IntegerField(db_column='lenRule', null=True)
    losecnt = IntegerField(null=True)
    name = CharField(primary_key=True)
    totalcnt = IntegerField(null=True)
    wincnt = IntegerField(null=True)
    wordsstream = CharField(db_column='wordsStream', null=True)

    class Meta:
        db_table = 'srtrtemps'

class Tweets(BaseModel):
    createdat = DateTimeField(db_column='createdAt')
    name = CharField(null=True)
    screen_name = CharField(null=True)
    text = CharField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    user = CharField(db_column='user_id', null=True)

    class Meta:
        db_table = 'tweets'

class Users(BaseModel):
    auth = CharField(null=True)
    cnt = IntegerField(null=True)
    context = CharField(null=True)
    createdat = DateTimeField(db_column='createdAt')
    exp = IntegerField(null=True)
    fav_cnt = IntegerField(null=True)
    followers_cnt = IntegerField(null=True)
    friends_cnt = IntegerField(null=True)
    mode = CharField(null=True)
    name = CharField(null=True)
    other = CharField(null=True)
    recentid = CharField(db_column='recentID', null=True)
    reply = CharField(db_column='reply_id', null=True)
    reply_name = CharField(null=True)
    replycnt = IntegerField(null=True)
    screen_name = CharField(null=True, primary_key=True)
    status = CharField(db_column='status_id', null=True)
    statuses_cnt = IntegerField(null=True)
    time = CharField(null=True)
    totalcnt = IntegerField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    usr = CharField(db_column='usr_id', null=True)
    waiting = CharField(null=True)

    class Meta:
        db_table = 'users'

class Words(BaseModel):
    head = CharField()
    length = IntegerField()
    tail = CharField()
    word = CharField(primary_key=True)
    yomi = CharField()

    class Meta:
        db_table = 'words'

class monStatus(BaseModel):
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

toolNote = '''=ツール=
1.たたかう 2.ツール
3.かくにん 4.にげる
5.セーブ 6.リセット
7.あぷで 7.おわり
=設定=
1.リネーム XX
2.エンカウント @ XX
3.へるぷ
=道具=
1.ほむまん 2. 炭酸
3.リカバリ '''

helpNote = '''( •̀ ᴗ •́ )うみもん(海未っ)
<未編集場所...>
おとのきざかもんすたーず、略して「うみもん(仮)」
取説を読んでくださいね。
バグは多いです。レベル調整もまだです。
ごめんなさい、諦めてください。
コマンドを入力してください。
1.たたかう 2.つーる
3.かくにん 4.にげる'''

def sigmoid(z):
  return 1/(1+np.exp(-z)) if -100. < z else 0.

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
			database.create_tables([monStatus], True)
			with database.transaction():
				try:
					status, created = monStatus.get_or_create(name = user)
					if created:
						print('newMON')
					return status
				except Exception as e:
					print(e)
				database.commit()
		except Exception as e:
			database.rollback()

def readUDB(user = 'xxxx'):
		try:
			with database.transaction():
				try:
					status= Users.select().where(Users.screen_name == user).get()
					return status
				except Exception as e:
					return ''
				database.commit()
		except Exception as e:
			database.rollback()

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
	d = datetime.datetime.today()
	nowtime = d.strftime("%Y%m%d%H%M%S")
	difT = (int(nowtime)-int(lasttime) - 100) // 60
	Spe = 20-int(sigmoid(difT)*10)
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
	LvList = [(lv) ** 3 for lv in range(LV+1)]
	nextLVExp = sum(LvList)
	status['nextLVExp'] = nextLVExp
	status['LV'] = LV
	return status

def getStatus(name, LV = 0):
	try:
		status = {}
		mystatus = readStatus(name)
		if mystatus.exp == None:
			mystatus = init(name, LV)
		# convert sql2dict
		status['name'] = mystatus.name
		status['nickname'] = mystatus.nickname
		status['mode'] = mystatus.mode
		status['exp'] = mystatus.exp
		status['LV'] = mystatus.LV
		status['nextLVExp'] = mystatus.nextLVExp
		status['damage'] = mystatus.damage
		status['HP'] = mystatus.HP
		status['restHP'] = mystatus.restHP
		status['HPgage'] = mystatus.HPgage
		status['name'] = mystatus.name
		status['Atk'] = mystatus.Atk
		status['Def'] = mystatus.Def
		status['SpA'] = mystatus.SpA
		status['SpD'] = mystatus.SpD
		status['Spe'] = mystatus.Spe
		status['enemy_name'] = mystatus.enemy_name
	except Exception as e:
		# print(e)
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
	try:
		mystatus = getStatus(me)
		enemyLV = mystatus['LV'] - 1
	except Exception as e:
		# print(e)
		mystatus = init(me)
		enemyLV = mystatus['LV'] - 1
		print('データがないです。新しく作り直しますね。')
	e_status = init(enemy, enemyLV)
	mystatus['mode'] = 'battle'
	return mystatus, e_status

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
		print(Atker + 'の攻撃...' + 'こうかなしです')
	elif rnd < 16:
		damage = 0
		print(Atker + 'の攻撃...' + 'はずれました')
	elif rnd < 12:
		damage = damage * 2
		print(Atker + 'の攻撃 ' + 'きゅうしょ' + str(damage) + 'ダメ')
	else:
		print(Atker + 'の攻撃 ' + str(damage) + 'ダメ')
	restHP = restHP - damage
	if restHP < 0:
		restHP = 0
	fullHP = status['HP']
	status['restHP'] = restHP
	status['damage'] = damage
	status['HPgage'] = HPgager(restHP, fullHP)
	return status, statusE

def display(status, statusE):
	restHPe = statusE['restHP']
	me = status['name']
	mynickname = status['nickname']
	print('ー')
	print(statusE['nickname'], 'Lv'+str(statusE['LV']))
	print(statusE['HPgage'], '['+str(statusE['damage'])+'↓')
	print('HP', str(restHPe)+'/'+str(statusE['HP']))
	print('↑ー↓')
	print(status['nickname'], 'Lv'+str(status['LV']))
	print(status['HPgage'],'['+str(status['damage'])+'↓')
	restHP = status['restHP']
	print('HP', str(restHP)+'/'+str(status['HP']))
	
	if restHPe <= 0:
		kotaichi = 50
		addexp = int(kotaichi * statusE['LV'])
		print(statusE['name'] + 'をたおした( •̀ ᴗ •́ )')
		# status = getEXP(me, addexp)
		status['enemy_name'] = 'AlpkS'
		status['mode'] = 'encount'
	elif restHP != 0:
		print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		status['enemy_name'] = statusE['name']
	else:
		print(mynickname,'はたおれた\nめのまえがまっくらになった\n( •̀ ᴗ •́ ) #END')
		status['enemy_name'] = statusE['name']
		status['mode'] = 'encount'
		maxHP = status['HP']
		status['restHP'] = maxHP
	return status

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
		# print(e)
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
	p2 = selectMode(text)
	isSaveOK = True
	try:
		status, statusE = dealStatus(me, enemy)
		p2 = selectModebyStatus(p2, status, statusE)
	except Exception as e:
		print(e)
		print('( •̀ ᴗ •́ )おとのきざかモンスター`s[海未](通称:うみもん)のせかいへようこそ。[β版]\n 進行役の園田海未です。私となかよくしたり、ふぁぼったり、ツイートしたり、ゲームであそんだりすると強くなれますよ。\n「たたかう」と返信して、さぁ修行ですっ！！')
		status = init(me)
		e_status = init(enemy)
		status['mode'] = 'encount'
		save(status)
		return

	try:
		if p2 == 'status':
			showStatus(status)
		elif p2 == 'リセット':
			isSaveOK = reset(me)
		elif p2 == 'セーブ':
			status = sendEXP(status)
			status['mode'] = 'battle'
		elif p2 == 'rename':
			try:
				newname = cmdlist[1].replace('@', '')
				if len(newname)>5:
					print('文字数が長いです。5文字まででお願いします。')
				else:
					oldname = status['nickname']
					status['nickname'] = newname
					print('( •̀ ᴗ •́ )'+oldname+ 'から'+ newname +'にニックネームの変更が完了しました。')
				print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
			except:
				print('( •̀ ᴗ •́ )その名前ではリネームできません')
				print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		elif p2 == 'encount':
			try:
				enemy = cmdlist[1].replace('@', '')
				status, statusE = encount(me, enemy)
				print('( •̀ ᴗ •́ )あ、やせいの\n',statusE['name'],'\nがあらわれました')
			except Exception as e:
				status, statusE = encount(me, enemy)
				print('( •̀ ᴗ •́ )あ、やせいの\n',statusE['name'],'\nがあらわれました')
			status['HPgage'] =  '■■■■■'
			status = display(status, statusE)
			status['mode'] = 'battle'

		elif p2 == 'recovery':
			restHP = status['restHP']
			maxHP = status['HP']
			status = recover(me)
			print('( •̀ ᴗ •́ )HPが全回復しました\n' + str(restHP) +'->' + str(maxHP))
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')

		elif p2 == 'ほむまん':
			restHPB = status['restHP']
			status = recover(me, 10)
			restHPA = status['restHP']
			maxHP = status['HP']
			print('( •̀ ᴗ •́ )HPが10回復しました。('+ str(restHPB) +'->' + str(restHPA) +')/'+ str(maxHP) +'\代償として20経験値下げておきますね')
			status = getEXP(me, -20)
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')

		elif p2 == '炭酸':
			status = recover(status, -10)
			print('( •̀ ᴗ •́ )怒 HPを10減らしました。炭酸はきらいです。')
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		elif p2 == 'update':
			status = init(me)
			print('( •̀ ᴗ •́ )ステータスをアップデートしました。')
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		elif p2 == 'battle.attacked':
			random.seed(text)
			waza = random.randint(0, 150)
			status, statusE = battle(status, statusE, waza)
			status = display(status, statusE)
			status['mode'] = 'battle.attack'
		elif p2 == 'battle.attack':
			random.seed(text)
			waza = random.randint(0, 150)
			statusE, status = battle(statusE, status, waza)
			status = display(status, statusE)
			status['mode'] = 'battle.attacked'
		elif p2 == 'tool':
			print(toolNote)

		elif p2 == 'help':
			print(helpNote)
	
		elif p2 == 'back':
			print('( •̀ ᴗ •́ )行動を選択してください')
			status = display(status, statusE)
			status['mode'] = 'back'
	
		elif p2 == 'にげる':
			rnd = np.random.randint(100);
			if rnd < 80:
				print('うまくにげられました。\n( •̀ ᴗ •́ )またあそんでくださいね。#END')
				status['enemy'] = ''
				status['mode'] = 'encount'
			else:
				print('( •̀ ᴗ •́ ) にげられないです')
				status = display(status, statusE)
		else:
			if status['Spe'] > statusE['Spe']:
				status, statusE = battle(status, statusE)
				status = display(status, statusE)
				status['mode'] = 'battle.attacked'
			else:
				status, statusE = battle(statusE, status)
				status = display(status, statusE)
				status['mode'] = 'battle.attack'
	except Exception as e:
		try:
			try:
				print('( •̀ ᴗ •́ )あ、敵は逃げてしまいました。また今度にしましょう。とりあえず、オートセーブしておきました。再開する場合は「うみもん」で。バグったら「リセット」#END' + '#exp' + str(status['exp']))
			except Exception as e:
				# print(e)
				print('( •̀ ᴗ •́ )あ、敵は困って逃げてしまいました。また今度にしましょう。 再開する場合は「うみもん」で。バグったら「リセット」#END')
			status = init(me)
			statusE = init(enemy)
		except Exception as e:
			print('( •̀ ᴗ •́ )バグ発生です。\n そんなこともありますよね。そのうち直しておきますね #END')
	
	if isSaveOK == True:
		save(status)
		save(statusE)

def save(status):
	try:
		database.create_tables([monStatus], True)
		with database.transaction():
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
			database.commit()
	except IntegrityError as ex:
		print (ex)
		database.rollback()

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
	Main(text, me, enemy)
	# getEXP('xxxx', 1000000)
	print(len('''どのような表現が差別なのであろうか。ひいては、本当の差別とは何であろうか。 身近な日常のなかで無意識に用いている差別表現を考えさせる。
生徒らが考える「模範的な」差別表現は果たして本当に差別表現なのであろうか。
一方で、差別表現を使っていないつもりでも差別の意味を込めた発言をしてことがあるのではないだろうか。
たとえば、差別をしまいとして被差別者を待遇して扱うことは本当に差別の回避であろうか。学校現場では、身体障碍者に対して手助けを行うべしと教えることが多いが、それは果たして身体障碍者が望んでいることであろうか。健常者による率先した積極的な対応は暗に障碍者を見下した上での行動、すなわちパターナリズムではなかろうか。
同様の構造は女性に対する差別でも見られる。イスラム圏では、一夫多妻制が採用されており、キリスト教圏は女性差別であるとして圧力をかけている。しかし、一夫一妻制になり実際に路頭に迷うのは女性たちではないだろうか。つまり、この手の差別をめぐる議論には被差別者の意思を聞かないで一方的に行われることが多い。そもそも、そうした対応方法自体が差別なのではなかろうか。'''))
	
