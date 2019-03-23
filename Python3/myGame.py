#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime # datetimeモジュールのインポート
import numpy as np
import scipy as sp
import re

import json
from peewee import *
import sqlite3

# MY PROGRAMs
import NLP
import dealSQL
from dealSQL import userDB, Srtrtemps, Words

def Srtr(s = '', user = 'xxxx', lenrule = 1, cmd = 'normal'):
	if s == '':
		return '( •̀ ᴗ •́ )なにか、言ってくれないとしりとりできないです。\MISS'
	ans = ''
	answord = ''
	wordsList = []
	kanasList = []
	lenrule = lenrule
	srtrDB = {}
	try:
		# userDB.create_tables([Srtrtemps], True)
		with userDB.transaction():
			try:
				srtrdb, created = Srtrtemps.get_or_create(name = user)
				if created == True:
					srtrdb.name = user
					srtrdb.wordsstream = ''
					srtrdb.kanasstream = ''
					srtrdb.lenrule = lenrule
					srtrdb.save()
			except Exception as e:
				print(e)
			userDB.commit()
	except Exception as e:
		userDB.rollback()
		print(e)
		wordsList = []
		kanasList = []

	wordsList = srtrdb.wordsstream.split('<JOIN>')
	kanasList = srtrdb.kanasstream.split('<JOIN>')
	try:
		totalcnt = srtrdb.totalcnt
		wincnt = srtrdb.wincnt ## botの勝利数
		losecnt = srtrdb.losecnt ## botの敗北数
	except Exception as e:
		print(e)
		totalcnt = 1
		wincnt = 0
		losecnt = 0
	turncnt = len(wordsList)
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
				ans += '( •̀ ᴗ •́ )名詞の単語が見あたりません。他の単語はありませんか？\MISS'
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
			# userDB.create_tables([Words], True)
			with userDB.transaction():
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
				userDB.commit()
		except IntegrityError as ex:
			print (ex)
			userDB.rollback()

		try:
			lastgobi = kanasList[-1][-1]
			if lastgobi  == 'ー':
				lastgobi  = kanasList[-1].replace('ー','')[-1]
			lastgobi = lastgobi.replace('ャ','ヤ').replace('ュ','ユ').replace('ョ','ヨ').replace('ッ','ツ').replace('ィ','イ').replace('ァ','ア').replace('ェ','エ').replace('ゥ','ウ').replace('ォ','オ').replace('ヵ','カ').replace('ヶ','ケ').replace('ヮ','ワ')
		except Exception as e:
			# print(e)
			lastgobi = ''
		if cmd == 'showlist':
			return wordsList
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
			ans += 'いいですね。'+ruleNOTE+'しりとりしましょう。\nそれでは、「'+rawnoun+'」の「'+gobi+'」から開始です。'
		elif lenword < lenrule and rawnoun != 'しりとり':
				ans += '( •̀ ᴗ •́ )「'+rawnoun+'」ですね。'+ str(lenrule) +'字縛りですから、これでは字数が短いです。\n別の単語はないのですか？「しりとりおわり」で降参してもいいんですよ 〜♪。\MISS'
		else:
			kao = '( •̀ ᴗ •́ )'

		if lastgobi == '':
			wordsList.append(rawnoun)
			kanasList.append(kana)
		if cmd != 'restart':
			ans ='「'+rawnoun+'」ですね。'+gobi+'...\n'
			if lastgobi != gotou:
				ans += '( •̀ ᴗ •́ )その言葉ではだめです。\n' + lastgobi + 'から始まる別の単語でお願いします。「しりとりおわり」で終了してもOKです。\MISS'
			elif rawnoun in wordsList:
				ans += '( •̀ ᴗ •́ )たしか、その言葉は既に使われましたよ。私の勝利ですっ!! \END'
				wordsList = []
				kanasList = []
				wincnt += 1

			elif gobi == 'ン':
				ans +='( •̀ ᴗ •́ )いま、「ン」がつきましたね。私の勝利ですっ!!\END'
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
					ans += answord + ' です!! あっ、「ン」で負けてしまいました。もう一度です！！\END'
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
						ans += answord + ' ですッ!! あ、既に出ていた単語でした...。くっ、私の負けです。\END'
					else:
						ansgobi = answords.tail
						anskana = answords.yomi
						wordsList.append(answord)
						kanasList.append(anskana)
						ans += answord + ' ですっ!! 次の頭文字は「' + ansgobi +'」ですよ。'
	except Exception as e:
		print(e)
		ans += '( •̀ ᴗ •́ )思いつきませんでした。悔しいですけど、私の負けです。\END'
		wordsList = []
		kanasList = []
		losecnt =+ 1

	# メモリー
	try:
		# userDB.create_tables([Words], True)
		with userDB.transaction():
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
			userDB.commit()
	except IntegrityError as ex:
		print (ex)
		userDB.rollback()
	return ans

def SRTR(text, user):
	if 'しりとりおわり' in text:
		with userDB.transaction():
			try:
				word = Srtrtemps.select().where(Srtrtemps.name == user).limit(1).get()
				word.kanasstream = ''
				word.wordsstream = ''
				word.save()
				userDB.commit()
				return 'それでは、しりとりは終わりにしましょう。また遊んでくださいね。\END'
			except Exception as e:
				userDB.rollback()
				return'データの消去に失敗しました。とりあえず、しりとりは終わりにします。\END'
	elif 'しりとり' in text:
		try:
			num = re.match("\d*",cmdlist[1])
			extracted = num.group()
			lenrule = int(extracted)
		except:
			lenrule = 1
		return Srtr(text, user,lenrule,'restart')
	elif text == 'show':
		with userDB.transaction():
			wordscnt = Words.select().count()
			return '現在、SQLに'+ str(wordscnt)+'コの単語を覚えています。現在の単語の流れ↓\n' + str(Srtr(text, user, 1,'showlist'))
	elif text == 'showlist':
		return Srtr(text, user, 1,'showlist')
	elif text == 'check':
		try:
			checkword = cmdlist[1]
			with userDB.transaction():
				word = Words.select().where(Words.word == checkword).limit(1).get()
			return checkword + 'の結果...\nよみ:'+ word.yomi+'\n語頭:'+ word.head+'\n語尾:'+ word.tail+'\n長さ:'+ str(word.length)
		except Exception as e:
			userDB.rollback()
			print(e)
			return 'そのような単語は見当たりません。しりとりに戻りませんか？'
	else:
		return Srtr(text, user)
if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		text = argvs[1]
		user = argvs[2]
	except:
		user = 'pEEE'
		text = "しりとり"

	cmdlist = text.split(' ')
	text = cmdlist[0]
	ret = SRTR(text, user)
	print(ret)
	# userDB.close()