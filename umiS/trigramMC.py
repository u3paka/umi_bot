#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import NLP
import TFIDF
import dealSQL

class BaseModel(Model):
    class Meta:
        database = talkDB

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

def getTrigram(startWith = '', Plist = ['<BOS>','名詞','名詞','名詞','助詞','動詞','助詞','助詞','名詞','名詞','名詞','助詞','動詞','助動詞','助動詞','<EOS>'], endWithList = ['。', '!', '！', '?', '？'], isDebug = False, n = 100):
  QuestionPhrase = '<KEY>...？'
  if startWith != '':
    ans = ['<BOS>',startWith]
  else:
    ans = ['<BOS>']
  # print(Plist)
  lenP = len(Plist)
  i = 0
  isNext = True
  try:
    with talkDB.transaction():
      if len(ans) == 1:
        try:
          Ws = trigram.select().where(trigram.W1 == ans[0], trigram.P2 == Plist[1]).order_by(trigram.cnt.desc())
          cntArr = np.array([w.cnt for w in Ws])
          W = np.random.choice([w.W2 for w in Ws], p = cntArr/np.sum(cntArr))
        except Exception as e:
          W = ['...？']
        ans += W
        i+= 1
        print(ans)
      while(True):
        isNext = True
        pre1 = ans[i]
        i1 = i+1
        pre2 = ans[i1]
        P3 = Plist[i+2]
        P2 = Plist[i1]
        P1 = Plist[i]
        if isNext:
          # print('2単語一致前方2品詞一致', ans, i)
          try:
            Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3, trigram.P2 == P2, trigram.P1 == P1).order_by(trigram.cnt.desc()).limit(n)
            cntArr = np.array([w.cnt for w in Ws])
            W = np.random.choice([w.W3 for w in Ws], p = cntArr/np.sum(cntArr))
            isNext = False
          except Exception as e:
            isNext = True
        if isNext:
          # print('2単語一致前方1品詞一致')
          try:
            Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3, trigram.P2 == P2).order_by(trigram.cnt.desc()).limit(n)
            cntArr = np.array([w.cnt for w in Ws])
            W = np.random.choice([w.W3 for w in Ws], p = cntArr/np.sum(cntArr))
            isNext = False
          except Exception as e:
            isNext = True
        if isNext:
          # print('2単語一致品詞一致')
          try:
            Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3).order_by(trigram.cnt.desc()).limit(n)
            cntArr = np.array([w.cnt for w in Ws])
            W = np.random.choice([w.W3 for w in Ws], p = cntArr/np.sum(cntArr))
            isNext = False
          except Exception as e:
            isNext = True
        if isNext:
          # print('2単語一致')
          try:
            Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2).order_by(trigram.cnt.desc()).limit(n)
            cntArr = np.array([w.cnt for w in Ws])
            W = np.random.choice([w.W3 for w in Ws], p = cntArr/np.sum(cntArr))
            isNext = False
          except Exception as e:
            isNext = True
        if isNext:
          # print('1単語一致')
          try:
            Ws = trigram.select().where(trigram.W2 == pre2).order_by(trigram.cnt.desc()).limit(n)
            cntArr = np.array([w.cnt for w in Ws])
            W = np.random.choice([w.W3 for w in Ws], p = cntArr/np.sum(cntArr))
            isNext = False
          except Exception as e:
            isNext = True
        if isNext:
          # print('1単語一致2')
          try:
            Ws = trigram.select().where(trigram.W1 == pre1).order_by(trigram.cnt.desc()).limit(n)
            cntArr = np.array([w.cnt for w in Ws])
            W = np.random.choice([w.W2 for w in Ws], p = cntArr/np.sum(cntArr))
            isNext = False
          except Exception as e:
            if i == 0:
              return QuestionPhrase.replace('<KEY>', pre2)
            isNext = True
        if ans[-1] != W:
          ans.append(W)
        else:
          break
        if isDebug:
          print(ans)
        i = i +1
        if lenP < i+3:
          break
        if W == '<EOS>':
          break
        if W in endWithList:
          break
        if i > 30:
          break
        W = ''
  except Exception as e:
    talkDB.rollback()
    # print(e)
  return ''.join(ans)

def saveTrigram(tri):
  try:
    ma1 = tri[0]
    ma2 = tri[1]
    ma3 = tri[2]
    talkDB.create_tables([trigram, mSentence], True)
    with talkDB.transaction():
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
      talkDB.commit()
  except Exception as e:
    talkDB.rollback()
    # print(e)

def saveMetaS(P):
  Pstr = ','.join(P)
  try:
    talkDB.create_tables([trigram, mSentence], True)
    with talkDB.transaction():
      try:
        M, created = mSentence.get_or_create(framework = Pstr)
        if created == True:
          M.framework = Pstr
          M.cnt = 1
          M.ok = 1
          M.ng = 0
          M.save()
        else:
          M.cnt += 1
          M.save()
      except Exception as e:
        print('')
      talkDB.commit()
  except Exception as e:
    talkDB.rollback()

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
    # talkDB.create_tables([trigram, mSentence], True)
    with talkDB.transaction():
      try:
        Ms = mSentence.select().where(mSentence.framework.contains('<BOS>,名詞,')).order_by(mSentence.cnt.desc()).limit(n)
        cntArr = np.array([m.cnt for m in Ms])
        return np.random.choice([m.framework for m in Ms], p = cntArr/np.sum(cntArr))
      except Exception as e:
        print('')
      talkDB.commit()
  except Exception as e:
    talkDB.rollback()
    # print(e)

def addRelateKW(KWdict):
  KWdict['名詞'] = ['']
  KWdict['<BOS>'] = [KWdict['名詞'].pop()]
  KWdict['形容詞'] = ['危ない', '嬉しい', '汚い']
  KWdict['格助詞'] = ['は']
  KWdict['記号'] = ['！']
  return KWdict



def formTrigram(word, isRandMetaS = True):
  if isRandMetaS:
    MetaFrame = getMetaSentence()
    MFs = [''.join([f, '助詞']) if not f[-1] == '>' else f for f in MetaFrame.split('助詞,')]
    cnt = len(MFs)
    try:
      ans = getTrigram(word, MFs[0])
    except Exception as e:
      ans = getTrigram(word)
    ans = ans.replace('<BOS>', '').replace('<EOS>', 'です。').replace('園田海未','私').replace('高坂穂乃果','穂乃果')
  else:
    ans = getTrigram(word).replace('<BOS>', '').replace('<EOS>', '')
  return ans


def dialog(s, isRandMetaS = True, isPrint = True, isLearn = False, n =5, tryCnt = 10, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
  keys = TFIDF.getKWs(s, threshold = 50, n = n, length = 1, isPrint = isPrint, needs = needs, RandNum = 5)
  isAssociate = False
  if keys[0] == '':
    try:
      return dealSQL.getPhrase(status = 'nod', n = 20)
    except:
      return '...そうなんですね'
  if isAssociate:
    BA = associateAns(keys[0])
  else:
    # wordset = getSimilarWords(w = keys[0], cnt = tryCnt)
    BA = formTrigram(word = keys[0], isRandMetaS = isRandMetaS)
    # ansSims = {ans: TFIDF.cosSimilarity(ans, s) for ans in ANSs}
    # BA = sorted(ansSims.items(), reverse = True, key=lambda x:x[1])[0]

  if isLearn:
    TrigramCore(s, isLearn = True, isDebug = False)
  if isPrint:
    print('=> 自動生成した応答文は以下のとおりです。')
    print(BA)
  randnum = np.random.randint(10)
  BA = BA.replace('<接尾>', 'さん').replace('<地域>', 'アキバ').replace('<数>', str(randnum))
  return BA

def getSimilarWords(w = '', cnt = 3, dockerIP = '192.168.XX.XX'):
  g = requests.get("http://" + dockerIP + ":22670/distance?a1=" + w).json()
  return [g['items'][i]['term'] for i in range(cnt)]

def getAnalogy(w = ['かわいい', '最低'], cnt = 3, dockerIP = '192.168.XX.XX'):
  w.append('')
  w1 = w[0]
  w2 = w[1]
  w3 = w[2]
  if w[2] == '':
    w3 = w2
  g = requests.get(''.join(["http://",dockerIP,":22670/analogy?a1=", w1, "&a2=", w2, "&a3=", w3])).json()
  return [g['items'][i]['term'] for i in range(cnt)]

def associateAns(word):
  anal = getSimilarWords(w = word, cnt = 3, dockerIP = '192.168.XX.XX')
  ans = ''.join([word, 'といえば', anal[0], 'とか', anal[1], 'ですよね。'])
  return ans


