#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import subprocess
# PROJECT_PATH='/Users/xxxx'
# sys.path.append(PROJECT_PATH+'/modules')
# sys.path.append(PROJECT_PATH+'/Data')
# DATABASE_NAME = os.path.join(os.path.dirname(__file__),"db","xxx.db")

import datetime # datetimeモジュールのインポート
import random
import numpy as np
import scipy as sp

import NLP
import re

import json
import sqlite3
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

def Srtr(s = '', user = 'xxxx', lenrule = 1, cmd = 'normal'):
	if s == '':
		print('( •̀ ᴗ •́ )なにか、言ってくれないとしりとりできないです。#MISS')
		return
	answord = ''
	wordsList = []
	kanasList = []
	lenrule = lenrule
	srtrDB = {}
	try:
		database.create_tables([Srtrtemps], True)
		with database.transaction():
			try:
				srtrdb, created = Srtrtemps.get_or_create(name = user)
				if created == True:
					srtrdb.name = user
					srtrdb.wordsstream = ''
					srtrdb.kanasstream = ''
					srtrdb.lenrule = lenrule
					srtrdb.save()
				wordsList = srtrdb.wordsstream.split('<JOIN>')
				kanasList = srtrdb.kanasstream.split('<JOIN>')
			except Exception as e:
				print(e)
			database.commit()
	except Exception as e:
		database.rollback()
		print(e)
		wordsList = []
		kanasList = []

	try:
		totalcnt = srtrdb['totalcnt']
		wincnt = srtrdb['wincnt'] ## botの勝利数
		losecnt = srtrdb['losecnt'] ## botの敗北数
	except Exception as e:
		# print(e)
		totalcnt = 1
		wincnt = 0
		losecnt = 0
	turncnt = len(wordsList)
	# print(turncnt)
	try:
		# アポストロフィに無理やり対応(すごい例外)
		s = s.replace('海未', '園田海未')
		if "μ's" in s:
			rawnoun = "μ's"
			kana = 'ミューズ'
		else:
			rawNouns = NLP.MA.getMeCab(s, form=['名詞'], exception = ['数', '接尾', '非自立', '接続助詞', '格助詞', '代名詞'])
			kanaNouns = NLP.MA.getMeCab(s, mode = 8, form = ['名詞'], exception = ['数', '接尾', '非自立', '接続助詞', '格助詞', '代名詞'])
			if rawNouns == ():
				print('( •̀ ᴗ •́ )名詞の単語が見あたりません。他の単語はありませんか？#MISS')
				return
			rawnoun = rawNouns[0]
			kana = kanaNouns[0]
		p = re.compile("[!-@[-`{-~]")    # 半角記号+半角数字
		cleanednoun = re.sub(p, '', kana)
		gobi = cleanednoun[-1:]
		if gobi == 'ー':
			gobi = cleanednoun.replace('ー','')[-1:]
		gotou = cleanednoun[:1]
		gobi = gobi.replace('ャ','ヤ').replace('ュ','ユ').replace('ョ','ヨ').replace('ッ','ツ').replace('ィ','イ').replace('ァ','ア').replace('ェ','エ').replace('ゥ','ウ').replace('ォ','オ').replace('ヵ','カ').replace('ヶ','ケ').replace('ヮ','ワ')

		word = {}
		lenword = len(kana)
		try:
			# database.create_tables([Words], True)
			with database.transaction():
				try:
					w, created = Words.create_or_get(word = rawnoun, yomi = kana, head = gotou, tail = gobi, length = lenword)
					if created == False:
						w.word = rawnoun
						w.yomi = kana
						w.head = gotou
						w.tail = gobi
						w.length = lenword
						w.save()
				except Exception as e:
					print(e)
				database.commit()
		except IntegrityError as ex:
			print (ex)
			database.rollback()

		try:
			lastgobi = kanasList[-1][-1]
			if lastgobi  == 'ー':
				lastgobi  = kanasList[-1].replace('ー','')[-1]
			lastgobi = lastgobi.replace('ャ','ヤ').replace('ュ','ユ').replace('ョ','ヨ').replace('ッ','ツ').replace('ィ','イ').replace('ァ','ア').replace('ェ','エ').replace('ゥ','ウ').replace('ォ','オ').replace('ヵ','カ').replace('ヶ','ケ').replace('ヮ','ワ')
		except Exception as e:
			# print(e)
			lastgobi = ''
		if cmd == 'showlist':
			print(wordsList)
			return
		elif cmd == 'restart':
			wordsList = []
			kanasList = []
			if lenrule > 1:
				ruleNOTE = 'では、'+ str(lenrule) + '字以上で'
			else:
				ruleNOTE = ''
			if gobi == 'ン':
				rawnoun = 'しりとり'
				gobi = 'リ'
			wordsList.append(rawnoun)
			kanasList.append(kana)
			print('いいですね。'+ruleNOTE+'しりとりしましょう。\nそれでは、「'+rawnoun+'」の「'+gobi+'」から開始です。')
		elif lenword < lenrule and rawnoun != 'しりとり':
				print('( •̀ ᴗ •́ )「'+rawnoun+'」ですね。'+ str(lenrule) +'字縛りですから、これでは字数が短いです。\n別の単語はないのですか？「しりとりおわり」で降参してもいいんですよ 〜♪。#MISS')
				return
		else:
			kao = '( •̀ ᴗ •́ )'

		if lastgobi == '':
			wordsList.append(rawnoun)
			kanasList.append(kana)
		if cmd != 'restart':
			print('「'+rawnoun+'」ですね。'+gobi+'...')
			if lastgobi != gotou:
				print('( •̀ ᴗ •́ )その言葉ではだめです。\n' + lastgobi + 'から始まる別の単語でお願いします。「しりとりおわり」で終了してもOKです。#MISS'	)
			elif rawnoun in wordsList:
				print('( •̀ ᴗ •́ )たしか、その言葉は既に使われましたよ。私の勝利ですっ!! #END')
				wordsList = []
				kanasList = []
				wincnt += 1

			elif gobi == 'ン':
				print('( •̀ ᴗ •́ )いま、「ン」がつきましたね。私の勝利ですっ!! #END')
				wincnt += 1
				wordsList = []
				kanasList = []

			else:
				wordsList.append(rawnoun)
				kanasList.append(kana)
				LoseFlag = False
				# LoseFLAGについて
				if turncnt > 25:
					LoseFlag = True

				if LoseFlag == True:
					wordscnt = wordsDB.count({'gotou': gobi,'gobi': 'ン','length':{'$gte' :lenrule}})
					rndcnt = np.random.randint(wordscnt)
					answord = wordsDB.find({'gotou': gobi, 'gobi': 'ン','length':{'$gte' :lenrule}})[rndcnt]
					print(answord + ' です!! あっ、「ン」で負けてしまいました。もう一度です！！#END')
					losecnt +=1
					wordsList = []
					kanasList = []
				else:
					# try:
					answords = Words.select().where((Words.head == gobi)&(Words.tail != 'ン')&(Words.length > lenrule)).order_by(fn.Random()).limit(1).get()
					answord = answords.word
					if answord in wordsList:
						wordsList = []
						kanasList = []
						losecnt =+ 1
						print(answord + ' ですッ!! あ、既に出ていた単語でした...。くっ、私の負けです。#END')
						return
					else:
						ansgobi = answords.tail
						anskana = answords.yomi
						wordsList.append(answord)
						kanasList.append(anskana)
						print(answord + ' ですっ!! 次の頭文字は「' + ansgobi +'」ですよ。')
	except Exception as e:
		# print(e)
		print('( •̀ ᴗ •́ )思いつきませんでした。悔しいですけど、私の負けです。#END')
		wordsList = []
		kanasList = []
		losecnt =+ 1
	# メモリー
	try:
		# database.create_tables([Words], True)
		with database.transaction():
			try:
				srtrdb = Srtrtemps.get(name = user)
				srtrdb.name = user
				wstream = '<JOIN>'.join(wordsList)
				srtrdb.wordsstream = wstream
				srtrdb.kanasstream = '<JOIN>'.join(kanasList)
				srtrdb.lenrule = lenrule
				srtrdb.save()
			except Exception as e:
				print(e)
			database.commit()
	except IntegrityError as ex:
		print (ex)
		database.rollback()

def Main(intext, user):
	if 'しりとりおわり' in intext:
		try:
			context['srtr']['wordsList'] = []
			context['srtr']['kanasList'] = []
			print('それでは、しりとりは終わりにしましょう。また遊んでくださいね。#END')
		except Exception as e:
			print(e)
			print('データの消去に失敗しました。とりあえず、しりとりは終わりにします。#END')
	elif 'しりとり' in intext:
		try:
			num = re.match("\d*",cmdlist[1])
			extracted = num.group()
			lenrule = int(extracted)
		except:
			lenrule = 1
		Srtr(intext, user,lenrule,'restart')
	elif text == 'show':
		print('現在、SQLに'+ str(Words.select().count())+'コの単語を覚えています。現在の単語の流れ↓')
		Srtr(intext, user, 1,'showlist')
	elif text == 'showlist':
		Srtr(intext, user, 1,'showlist')
	elif text == 'check':
		try:
			checkword = cmdlist[1]
			with database.transaction():
				word = Words.select().where(Words.word == checkword).limit(1).get()
			print(checkword + 'の結果...\nよみ:'+ word.yomi+'\n語頭:'+ word.head+'\n語尾:'+ word.tail+'\n長さ:'+ str(word.length))
		except Exception as e:
			database.rollback()
			print(e)
			print('そのような単語は見当たりません。しりとりに戻りませんか？')
	else:
		Srtr(intext, user)
if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		intext = argvs[1]
		user = argvs[2]
	except:
		user = 'pEEE'
		intext = "しりとりおわり"

	cmdlist = intext.split(' ')
	text = cmdlist[0]
	Main(intext, user)
	# database.close()