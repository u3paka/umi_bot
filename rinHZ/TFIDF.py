#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
# MyModules
from dealSQL import langDB
import NLP
class langDBmodel(Model):
    class Meta:
        database = langDB

class managementInfos(langDBmodel):
	totaldoc = IntegerField(null=True)
	name = CharField(primary_key=True)
	class Meta:
		db_table = 'Infos'

class tfidf(langDBmodel):
    word = CharField()
    yomi = CharField(null=True)
    hinshi = CharField(null=True)
    hinshi2  = CharField(null=True)
    info3  = CharField(null=True)
    termcnt = IntegerField(null=True)
    tf = IntegerField(null=True)
    df = IntegerField(null=True)
    class Meta:
        db_table = 'df'

def incDocFreq(word):
	try:
		langDB.create_tables([managementInfos, tfidf], True)
		with langDB.transaction():
			try:
				wdb, created = tfidf.get_or_create(word = word)
				if created != True:
					try:
						wdb.df +=  1
					except:
						wdb.df = 1
					wdb.save()
			except Exception as e:
				print('')
			langDB.commit()
	except Exception as e:
		langDB.rollback()
		# print(e)

def upsertWord(ma, isLearn = False):
	genkei = ma[7]
	hinshi = ma[1]
	hinshi2 = ma[2]
	DF = 1;
	try:
		langDB.create_tables([managementInfos, tfidf], True)
		with langDB.transaction():
			try:
				wdb, created = tfidf.get_or_create(word = genkei, hinshi = hinshi, hinshi2 = hinshi2)
				if isLearn == False:
					DF = 1
				elif created == True:
					wdb.word = genkei
					wdb.yomi = ma[8]
					wdb.hinshi = ma[1]
					wdb.hinshi2  = ma[2]
					wdb.info3  = ma[3]
					wdb.termcnt = 1
					wdb.df = 1
					wdb.tf = 1
					wdb.save()
					DF = 1
				else:
					try:
						wdb.df +=  1
					except:
						wdb.df = 1
					wdb.save()
					DF = wdb.df
			except Exception as e:
				print('')
			langDB.commit()
	except Exception as e:
		langDB.rollback()
		# print(e)
	return DF

def calcTFIDF(w, TFdic, cnt = 5, totalDoc = 30000, isDebug = False):
	word = w[7]
	wordcnt = TFdic[word]
	TF =  wordcnt / cnt
	if word == '*':
		return ''
	else:
		DF = upsertWord(w)
	try:
		preIDF = totalDoc / DF
		IDF = 1 + np.log2(preIDF)
	except:
		IDF = 1
	TFIDF = TF * IDF
	w.append(TFIDF)
	if isDebug:
		print(word, str(round(TFIDF, 2)))
	return w

def TFIDF(s, totalDoc = 420000, isLearn = False, isDebug = False):
	s = s.replace('μ\'s','[{μ\'s').replace('海未ちゃん', '海未').replace('海未', '[{園田海未}]').replace('うみちゃん', '[{園田海未}]').replace('穂乃果', '[{高坂穂乃果}]').replace('ほのか', '[{高坂穂乃果}]').replace('かよちん', '[{小泉花陽}]').replace('ラブライブ', 'ラブライブ!').replace('真姫','[{西木野真姫}]').replace('まきちゃん','[{西木野真姫}]').replace('西木野[{西木野','西木野')
	# print(s)
	ma = NLP.MA.getMeCabCP(s)
	wordcnt = len(ma)
	wordList = [w[7] for w in ma]
	counter = Counter(wordList)
	TFdic = {}
	for word, cnt in counter.most_common():
		TFdic[word] = cnt
	result = [calcTFIDF(w, TFdic, cnt = 5, totalDoc = totalDoc, isDebug = isDebug) for w in ma]
	if isLearn:
		for key in TFdic.keys():
			incDocFreq(key)
	return result

def learnTFIDF(sList):
	# result = [Main(s, 1, True, True) for s in sList]
	# print(len(result))
	i = 1;
	for s in sList:
		print('++++++++++++++++++++++++++++++++++++++++++++++++++')
		print(i, s)
		try:
			mas = TFIDF(s, i, True, True)
		except Exception as e:
			print('')
		i += 1

def extractKeywords(ma, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
	def isKeyword(x, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
		try:
			if x[1] in needs:
				return True
			elif x[2] in needs:
				return True
			else:
				return False
		except Exception as e:
				return False
	return [x for x in sorted(ma, key = lambda x: x[10], reverse = True) if isKeyword(x, needs)]

def extractTFIDF(s, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
	ma = TFIDF(s, totalDoc = 420000, isLearn = False, isDebug = False)
	result = extractKeywords(ma, needs)
	return result

def calcKWs(s, length = 1, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
	impMA = extractTFIDF(s, needs)
	seen = set()
	seen_add = seen.add
	KWs = [(x[7], x[1], x[10]) for x in impMA if len(x[0])>length]
	KWtfidf = np.array([x for x in KWs if x[0] not in seen and not seen_add(x[0])])
	return KWtfidf

def getRandKWs(KWs, RandNum = 1):
	kwcnt = len(KWs)
	tfidf = np.array([float(x[2]) for x in KWs])
	per = np.sum(tfidf)
	p = tfidf / per
	if RandNum > kwcnt:
		RandNum = kwcnt
	try:
		return np.random.choice([x[0] for x in KWs], RandNum, replace=False, p = p)
	except:
		return ['']
def KWfilter(datas):
	BLACKset = set(['ちゃん'])
	return [data for data in datas if not data[0] in BLACKset]
def getKWs(s, threshold = 50, n = 5, length = 1, isPrint = True, needs = set(['名詞', '固有名詞', '動詞', '形容詞']), RandNum = 1):
	KWtfidf = calcKWs(s, length = length, needs = needs)
	kwcnt = len(KWtfidf)
	KWtfidf = KWfilter(KWtfidf)

	if RandNum > 0 and s != '':
		# KWdict = {KW[1]: [key[0] for key in KWtfidf if key[1] == KW[1]] for KW  in KWtfidf}
		return getRandKWs(KWtfidf, RandNum = RandNum)
	if kwcnt == 0:
		if isPrint:
			print('=> キーワードは見つかりませんでした。')
		return ['']
	else:
		if isPrint:
			if kwcnt < n:
				print('=> ' + str(kwcnt) + '個の文章の重要キーワードを抽出しました。')
			else:
				print('=> ' + str(n) + '個の文章の重要キーワードを抽出しました。')
		mostImpTFIDF = KWtfidf[0][2]
		print(mostImpTFIDF)
		convImpRate = 100 / float(mostImpTFIDF)

		return impkey

def setKWtoTweet(n = 1000):
	try:
		db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():
			tweets = Tweets.select().where(Tweets.screen_name != '_umiA' and ~Tweets.text.contains('RT')).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [utiltools.cleanText(tweet.text) for tweet in tweets  if 'RT' not in tweet.text]
			return tweetslist
	except Exception as e:
		langDB.rollback()
		# print(e)

# def cosine_similarity(v1, v2):
#     return sum([a*b for a, b in zip(v1, v2)])/(sum(map(lambda x: x*x, v1))**0.5 * sum(map(lambda x: x*x, v2))**0.5)

def cosSimilarity(s1, s2):
	try:
		intexts = [s1, s2]
		tfidflist = [{ma[7]: ma[10] for ma in extractTFIDF(text) if ma[1] in set(['動詞', '名詞', '固有名詞', '形容詞', '助詞', '副詞', '助動詞'])} for text in intexts]
		vecF = set(utils.f7(list(chain.from_iterable([tfidflist[0].keys()] + [tfidflist[1].keys()]))))
		tfidflist0 = tfidflist[0]
		tfidflist1 = tfidflist[1]
		v1 = np.array([tfidflist0[w] if w in set(tfidflist0) else 0 for w in vecF])
		v2 = np.array([tfidflist1[w] if w in set(tfidflist1) else 0 for w in vecF])
		# return np.sum(np.dot(v1,v2))/(np.sum(np.sqrt(np.dot(v1,v1)))*np.sum(np.sqrt(np.dot(v2,v2))))
		bunbo = (np.linalg.norm(v1) * np.linalg.norm(v2))
		if bunbo != 0:
			return np.dot(v1, v2) / bunbo
		else:
			return 0
	except:
		return 0
if __name__ == '__main__':
	command = 'getsim'
	intext = '''逆に軽快なアコースティックギター'''
	# intext2 = 'dd\nd'
	key = calcKWs(intext, length = 1, needs = set(['固有名詞', '名詞']))
	print(key[0])
	# if command == 'learn':
	# 	print('学習しました。')
	# 	ma = TFIDF(intext, 420000, 1, 1)
	# elif command == 'showKey':
	# 	imp = getKWs(intext, threshold = 0, n = 5, length = 0, isPrint = True, RandNum = 1)
	# 	print(imp)
	# elif command == 'learnTFIDF':
	# 	tweetslist = getTweetList(420000)
	# 	learnTFIDF(tweetslist)
	# # elif command == 'getsim':
	# else:
		# imp = getKWs(intext, threshold = 50, n = 5, length = 0, isPrint = False)
		# print('<JOIN>'.join(imp))
	# tweetslist = getTweetList(80000)
	# learnTFIDF(tweetslist)

