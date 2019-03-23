#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from collections import Counter
import NLP
import TFIDF
import re
import random
import numpy as np
from itertools import chain
DBPLACE = '../LANGUAGE4.sqlite3'
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
db = SqliteExtDatabase('../twtrData.sqlite3', autocommit=False, journal_mode='persist')
db.connect()
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

class BaseModel(Model):
    class Meta:
        database = db
class Tweets(BaseModel):
    createdat = DateTimeField(db_column='createdAt')
    name = CharField(null=True)
    screen_name = CharField(null=True)
    text = CharField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    user = CharField(db_column='user_id', null=True)
    class Meta:
        database = db

def cleanText(text):
	text = re.sub(r'(@[^\s　]+)', '', text)
	text = re.sub(r'(#[^\s　]+)', '', text)
	text = re.sub(r'(http[^\s　]+)', '', text)
	text = re.sub(r'(^[\s　]+)', '', text)
	text = re.sub(r'([\s　]+$)', '', text)
	text = re.sub(r'(([\s　]+))', '', text)
	return text

database = SqliteExtDatabase(DBPLACE, autocommit=False, journal_mode='persist')
# database = SqliteExtDatabase('../trigram24000.sqlite3', autocommit=False, journal_mode='persist')
database.connect()
class BaseModel(Model):
    class Meta:
        database = database

class trigram(BaseModel):
    W1 = CharField(null=True)
    W2 = CharField(null=True)
    W3  = CharField(null=True)
    P1  = CharField(null=True)
    P2 = CharField(null=True)
    P3 = CharField(null=True)
    cnt = IntegerField(null=True)
    ok = IntegerField(null=True)
    ng = IntegerField(null=True)
    class Meta:
        db_table = 'trigram'

class mSentence(BaseModel):
	framework = CharField(null=True)
	cnt = IntegerField(null=True)
	ok = IntegerField(null=True)
	ng = IntegerField(null=True)
	class Meta:
		db_table = 'meta_sentence'

def getTweetList(n = 1000, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = ['hsw37', 'ry72321', 'MANI_CHO_8', 'HONO_HONOKA_1', 'MOEKYARA_SAIKOU', 'megmilk_0308']):
	try:
		db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():
			if UserList == []:
				tweets = Tweets.select().where(~Tweets.text.contains('RT'), ~Tweets.screen_name << BlackList, ~Tweets.text.contains('【')).order_by(Tweets.createdat.desc()).limit(n)
			else:
				tweets = Tweets.select().where(Tweets.screen_name << UserList , ~Tweets.screen_name << BlackList, ~Tweets.text.contains('RT'), ~Tweets.text.contains('【')).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [cleanText(tweet.text) for tweet in tweets  if 'RT' not in tweet.text]
			return tweetslist
	except Exception as e:
		db.rollback()
		# print(e)

def getTrigram(startWith = '', Plist = ['<BOS>','名詞','名詞','名詞','助詞','動詞','助詞','助詞','名詞','名詞','名詞','助詞','動詞','助動詞','助動詞','<EOS>'], endWithList = ['。', '!', '！', '?', '？'], isDebug = False, n = 100):
	QuestionPhrase = '<KEY>...？'
	if startWith != '':
		ans = ['<BOS>', startWith]
	else:
		ans = ['<BOS>']
	# print(Plist)
	lenP = len(Plist)
	i = 0
	isNext = True
	try:
		with database.transaction():
			if len(ans) == 1:
				try:
					Ws = trigram.select().where(trigram.W1 == ans[0], trigram.P2 == Plist[1]).order_by(trigram.cnt.desc())
					W = np.random.choice([w.W2 for w in Ws])
				except Exception as e:
					W = ''
				ans.append(W)
				# print(ans)
			while(True):
				isNext = True
				pre1 = ans[i]
				pre2 = ans[i+1]
				P3 = Plist[i+2]
				P2 = Plist[i+1]
				P1 = Plist[i]
				if isNext:
					# print('2単語一致前方2品詞一致', ans, i)
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3, trigram.P2 == P2, trigram.P1 == P1).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('2単語一致前方1品詞一致')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3, trigram.P2 == P2).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('2単語一致品詞一致')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('2単語一致')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('1単語一致')
					try:
						Ws = trigram.select().where(trigram.W2 == pre2).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('1単語一致2')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W2 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						if i == 0:
							return QuestionPhrase.replace('<KEY>', pre2)
						isNext = True
				ans.append(W)
				if isDebug:
					print(ans)
				i = i +1
				# if lenP < i+3:
				# 	break
				if W == '<EOS>':
					break
				if W in endWithList:
					break
				if i > 30:
					break
				W = ''
	except Exception as e:
		database.rollback()
		# print(e)
	return ''.join(ans)

def saveTrigram(tri):
	try:
		ma1 = tri[0]
		ma2 = tri[1]
		ma3 = tri[2]
		database.create_tables([trigram, mSentence], True)
		with database.transaction():
			try:
				T, created = trigram.get_or_create(W1 = ma1[0], W2 = ma2[0], W3 = ma3[0], P1 = ma1[1], P2 = ma2[1], P3 = ma1[1])
				if created == True:
					T.W1 = ma1[0]
					T.W2 = ma2[0]
					T.W3  = ma3[0]
					T.P1  = ma1[1]
					T.P2 = ma2[1]
					T.P3 = ma3[1]
					T.cnt = 1
					T.save()
				else:
					T.cnt = T.cnt +1
					T.save()
			except Exception as e:
				print('')
			database.commit()
	except Exception as e:
		database.rollback()
		# print(e)

def saveMetaS(P):
	Pstr = ','.join(P)
	try:
		database.create_tables([trigram, mSentence], True)
		with database.transaction():
			try:
				M, created = mSentence.get_or_create(framework = Pstr)
				if created == True:
					M.framework = Pstr
					M.cnt = 1
					M.ok = 1
					M.ng = 0
					M.save()
				else:
					M.cnt = M.cnt +1
					M.save()
			except Exception as e:
				print('')
			database.commit()
	except Exception as e:
		database.rollback()

def TrigramCore(s, isLearn = False, isDebug = False):
	s = s.replace('海未', '園田海未').replace('うみちゃん', '園田海未').replace('穂乃果', '高坂穂乃果').replace('ほのか', '高坂穂乃果').replace('かよちん', '小泉花陽')
	ma = NLP.MA.getMeCabCP(s)
	ma = [[w[0], w[1]] for w in ma]
	ma = [['<BOS>', '<BOS>']] + ma + [['<EOS>', '<EOS>']]
	Plist = [w[1] for w in ma]
	saveMetaS(Plist)
	wcnt = len(ma)
	triMA = [[ma[i], ma[i+1], ma[i+2]] for i in range(wcnt-2)]
	if isLearn:
		[saveTrigram(ma) for ma in triMA]
	if isDebug:
		print(triMA)

def learnTrigram(sList):
	i = 1;
	for s in sList:
		print('++++++++++++++++++++++++++++++++++++++++++++++++++')
		print(i, s)
		try:
			mas = TrigramCore(s, 1, 1)
		except Exception as e:
			print('')
		i += 1

def learnLang(sList):
	i = 1;
	for s in sList:
		print('++++++++++++++++++++++++++++++++++++++++++++++++++')
		print(i, s)
		try:
			trigram = TrigramCore(s, 1, 0)
			tfidf = TFIDF.TFIDF(s, i, True, 0)
		except Exception as e:
			print('')
		i += 1

def extractKeywords(ma, exp = ['助詞', '助動詞', '記号', '接続詞', '数']):
	def isKeyword(x, exp = ['助詞', '助動詞', '記号', '接続詞', '数']):
		if x[1] in exp:
			return False
		elif x[2] in exp:
			return False
		else:
			return True
	return [x for x in sorted(ma, key = lambda x: x[10], reverse = True) if isKeyword(x, exp)]

def getMetaSentence(n = 50):
	try:
		# database.create_tables([trigram, mSentence], True)
		with database.transaction():
			try:
				Ms = mSentence.select().where(mSentence.framework.contains('<BOS>,名詞,')).order_by(mSentence.cnt.desc()).limit(n)
				return np.random.choice([m.framework for m in Ms])#, p = [m.cnt for m in Ms])
			except Exception as e:
				print('')
			database.commit()
	except Exception as e:
		database.rollback()
		# print(e)

def addRelateKW(KWdict):
	KWdict['名詞'] = ['']
	KWdict['<BOS>'] = [KWdict['名詞'].pop()]
	KWdict['形容詞'] = ['危ない', '嬉しい', '汚い']
	KWdict['格助詞'] = ['は']
	KWdict['記号'] = ['！']
	return KWdict

def getRelateW(w):
	return



def dialog(intext, isRandMetaS = True, isPrint = True, isLearn = False, n =5, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
	keys = TFIDF.getKWs(intext, threshold = 50, n = n, length = 1, isPrint = isPrint, needs = needs, RandNum = 5)
	if isRandMetaS:
		MetaFrame = getMetaSentence()
		MFs = [''.join([f, '助詞']) if not f[-1] == '>' else f for f in MetaFrame.split('助詞,')]
		cnt = len(MFs)
		try:
			ansList = [getTrigram(keys[i], MFs[i]) for i in range(cnt)] ###ここのkey部修正のために話題連想データベースを作る必要がある。
		except Exception as e:
			# print(e)
			if keys[0] == None:
				keys = ['']
			ansList = [getTrigram(keys[0])]
		ans = ''.join(ansList).replace('<BOS>', '').replace('<EOS>', 'です。')
	else:
		ans = getTrigram(keys[0]).replace('<BOS>', '').replace('<EOS>', '')
	if isLearn:
		TrigramCore(intext, isLearn = True, isDebug = False)
	if isPrint:
		print('=> 自動生成した応答文は以下のとおりです。')
		print(ans)
	return ans

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	import charaS
	try:
		argvs = sys.argv
		intext = argvs[1]
		command = argvs[2]
	except:
		command = ''
		intext = '''埼玉県'''
	randnum = np.random.randint(10)
	try:
		ans = dialog(intext, isRandMetaS = 1, isPrint = False, isLearn = 0).replace('<接尾>', 'さん').replace('<地域>', 'アキバ').replace('<数>', str(randnum))
		charAns = charaS.umiCharMain(ans)
		if charAns!= "":
			print(charAns.replace('<接尾>', 'さん').replace('<地域>', 'アキバ').replace('<数>', str(randnum)))
		else:
			print(ans)
	except Exception as e:
		print('...なるほど。')

	# jobs = []
	# for i in range(5):
	# 	p = multiprocessing.Process(target=dialog, args=(intext, 1, True, 0))
	# 	jobs.append(p)
	# 	p.start()
	# for job in jobs:
	# 	job.join()

