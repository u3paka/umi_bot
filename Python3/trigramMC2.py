#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from collections import Counter
import NLP, utiltools
import TFIDF
import re
import random
import requests
import numpy as np
import dealSQL
DBPLACE = '/Users/xxxx'
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
database = SqliteExtDatabase(DBPLACE, autocommit=False, journal_mode='persist')
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

def getTrigram(startWith = '', Plist = ['<BOS>','名詞','名詞','名詞','助詞','動詞','助詞','助詞','名詞','名詞','名詞','助詞','動詞','助動詞','助動詞','<EOS>'], endWithList = ['。', '!', '！', '?', '？'], isDebug = False, n = 100):
  QuestionPhrase = '<KEY>...？'
  if startWith != '':
    ans = [startWith]
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
          cntArr = np.array([w.cnt for w in Ws])
          W = np.random.choice([w.W2 for w in Ws], p = cntArr/np.sum(cntArr))
        except Exception as e:
          W = ['...？\n','(•̀ᴗ•́)＜…']
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
          M.cnt += 1
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
        cntArr = np.array([m.cnt for m in Ms])
        return np.random.choice([m.framework for m in Ms], p = cntArr/np.sum(cntArr))
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

def formTrigram(word, isRandMetaS = True):
  if isRandMetaS:
    MetaFrame = getMetaSentence()
    MFs = [''.join([f, '助詞']) if not f[-1] == '>' else f for f in MetaFrame.split('助詞,')]
    cnt = len(MFs)
    try:
      ans = getTrigram(word, MFs[0])
    except Exception as e:
      if keys[0] == None:
        keys = ['']
      ansList = getTrigram(word[0])
    ans = ans.replace('<BOS>', '').replace('<EOS>', 'です。').replace('園田海未','私').replace('高坂穂乃果','穂乃果')
  else:
    ans = getTrigram(keys[0]).replace('<BOS>', '').replace('<EOS>', '')
  return ans


def dialog(s, isRandMetaS = True, isPrint = True, isLearn = False, n =5, tryCnt = 10, needs = set(['名詞', '固有名詞', '動詞', '形容詞'])):
  keys = TFIDF.getKWs(s, threshold = 50, n = n, length = 1, isPrint = isPrint, needs = needs, RandNum = 5)
  isAssociate = False
  if keys[0] == '':
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

def getSimilarWords(w = '淫夢', cnt = 3, dockerIP = '192.168.59.103'):
  g = requests.get("http://" + dockerIP + ":22670/distance?a1=" + w).json()
  return [g['items'][i]['term'] for i in range(cnt)]

def getAnalogy(w = ['かわいい', '最低'], cnt = 3, dockerIP = '192.168.59.103'):
  w.append('')
  w1 = w[0]
  w2 = w[1]
  w3 = w[2]
  if w[2] == '':
    w3 = w2
  g = requests.get(''.join(["http://",dockerIP,":22670/analogy?a1=", w1, "&a2=", w2, "&a3=", w3])).json()
  return [g['items'][i]['term'] for i in range(cnt)]

def associateAns(word):
  anal = getSimilarWords(w = word, cnt = 3, dockerIP = '192.168.59.103')
  ans = ''.join([word, 'といえば', anal[0], 'とか', anal[1], 'ですよね。'])
  return ans

if __name__ == '__main__':
  import sys
  import io
  import os
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

  try:
    argvs = sys.argv
    intext = argvs[1]
    command = argvs[2]
  except:
    command = ''
    intext = '''ちくしよおおおおおお💢💢'''
  # randnum = np.random.randint(10)
  ans = dialog(intext, isRandMetaS = 1, isPrint = True, isLearn = False, n =5, tryCnt = 10, needs = set(['名詞', '固有名詞', '動詞', '形容詞']))
  print(ans)

  # keys = TFIDF.getKWs(s, threshold = 50, n = n, length = 1, isPrint = isPrint, needs = needs, RandNum = 5)
  # isAssociate = False
  # try:
  # BA = dialog(intext, isRandMetaS = 1, isPrint = False, isLearn = 0)
  # print(BA[0].replace('<接尾>', 'さん').replace('<地域>', 'アキバ').replace('<数>', str(randnum)), BA[1])
  #   # getAnalogy(w = ['棒', '破廉恥', '高坂穂乃果'], cnt = 3, dockerIP = '192.168.59.103')
  #   # charAns = charaS.umiCharMain(ans)
  #   # if charAns!= "":
  #   #   print(charAns.replace('<接尾>', 'さん').replace('<地域>', 'アキバ').replace('<数>', str(randnum)))
  #   # else:
  #   #   print(ans)
  # except Exception as e:
  #   print(e)
  #   print('...なるほど。')

  # LIKE = [(tweet, 1) for tweet in dealSQL.getTweetList(n = 100,UserList = [], contains = '好き')]
  # umi =  dealSQL.getTweetList(n = 10000)
  # print(umi)
  # print(utiltools.f7(LIKE + HATE))
#   s = ''' ヤァーー、メーーンッ！
#   ヤァーー、コテ、メン、ドォーー
# 園田家の朝は、気合の入った剣道の朝稽古で始まります。
# 跳躍素振り100回、正面素振り100回、蹲踞から立ち上がっての摺足と連続の3本抜き...。
# まだ白々とした陽光も儚い早朝のこの時間。
# 袴のひもをぎゅっと締め、広い道場で稽古をするのは、なかなか気持ちの良いものです。
# と、いう風に思えるようになったのは...いつの頃からだったでしょうか。
# 6月も末の初夏の候。
# 日の出も早いこの時期はこんな風に....暑い1日の中でも最も涼やかな気持ちのいい時間を過ごすことができます。が、これが冬ともなれば。午前5時くらいではまだ夜も明けきってはいない時刻。
# 暁暗の身を切るような冷たい空気の中を、身を縮ませながら道義に着替え、暖房のスイッチを入れてもほとんど聞いてこないいような、だだっ広い道場の空間を...冷たい海を切るように進むと。その裸足の足の一歩ごとに。

# 心底冷たい凍るような静けさが、私の身体を貫いて行きます。
# 小さい頃にはよく、そんな季節に...足の裏を縁どるような真っ赤なしもやけを作ってしまって。その痛みに涙する日もありました。

# 道場の床を踏みしめるたびに体に響くその痛みに泣きながら、足が痛いと訴えても。師範である父は「泣き言を言うな」「あとで薬を塗ればいい」と言うばかり。
# 朝の稽古が終わった後で、祖母が暮れる小さな肝油ドロップのやわらかな白い粒だけが....そんな時の私の心の支えでした。
# 朝のお稽古のご褒美にお婆上様がたった2粒だけくださる、とっておきの小さな白い甘いキャンディ。
# この季節にしかもらうことのできないそれが、しもやけを治すためのビタミン剤だった頃hあ、ずいぶん後になるまで知りませんでしたが、私にとっては今も懐かしく優しい思い出です。
# そして。そんな小さな涙の日々を過ぎて...。
# 今の私はもうそんなことでは泣きません。
# 足のうらだってすっかり強くなり、どんなに寒い冬が来ても、今ではしもやけだって少しもできなくなりました。
# こうしてすごす早朝の稽古は、対面のない基本稽古のみ。
# 段位をとったころからか、いつしか付き合う師範である父の姿も見えない日が増え...道場は私一人の自己鍛錬の場となりました。
# 手つかずの1日がこれから始まろうとする、朝のこの時間。
# まっさらな自分の心と体と向き合って...いつも。自分自身のその在り処を確かめるときです。
#   ヤァーー、メーーンッ！
# 稽古の最後は...今日も稽古で使わせてもらった道場への感謝を込めて、床の雑巾がけをして終わりにします。
# 袴の裾を少しだけたくし上げて、お寺の小坊主さんのように走り回る姿は少しおかしいかもしれませんが、これでなかなか、この動作が足腰の鍛錬になるのです。
# 本当はμ'sのメンバーにもこれでをやってもらったら、きっとすごくいいのではないかと思うのですが...学校の道場は他の部活動で完全に埋まってますから、やはり無理でしょうね。
# 残念です...。

# 母です。道場の後、軽くシャワーを浴びて汗を流した私を、廊下で見つけて言いました。
# 「はい、お願いします」
# 私は...礼儀正しく頭を下げて、お師匠様にお願いをさせていただきます。師匠の言葉にうむはなく、それに...再来週に実力試験を控えた今朝は、μ'sの朝の練習がないので、時間はまだありますから。
# 母は...優しい人ですが。やはりことお稽古のこととなれば敬うべき私の師匠。お師匠様のおっしゃることにはいつも「はい」と答え、叩頭するのが弟子のあるべき姿です。

# 流れてくる「梅の春」の唄を聴きながら、無心に待っていると。お稽古場の窓から入る陽射しがどんどん強くなっていくのを感じました。
# 少しだけ緩く着付けた浴衣の木綿の生地が、汗を流したあとの素肌に心地よく。この時期はお稽古着も楽で気分が軽くなりますね。などと....余計なことがつい頭の中に浮かんできたりして。いけない...叱られる。
# 舞台そでに座っている母の方をちらりと盗み見ると、いつの間にか母は目をつぶってユラユラと...曲に聞き入っていました。
# つい、笑いそうになって、必死で堪えます。母も陽に当たって思わず眠くなってしまったのでしょうか？
# いえ、きっと、私の踊りが、及第点をもらえたゆえのことだと....そう思うことにしましょう。
# もう目をつぶっていても安心していられるほどに...。

# 母は...この道場に生まれた一人娘で、日舞・園田流の家元です。
# つまり、正確にいえば、園田家の現在の当主は母であり、武道家である父は入り婿ということになります。園田家はもとは武家ではありますが、女流の家系で、なかなか男子が生まれることがなく、たびたび親戚より婿養子をとっての家督相続があったそうです。しかし今はもうそんな時代でもなく、単に母が1人で継ぐことになっていたところに...ですから、もともとここは日舞のお家元の道場だったのが....偶然出会った父との結婚により、父のする武道場も併設することになり、離れをつぶして大きな道場を立てることになったそうです。
# 板張りの武道場には、片側に舞台が作られていて、いざという時はそこが日舞の舞台になりさらにふだんはその舞台の奥の壁が開くと、その先に広がる庭の向こうには的場が作られていて、舞台を射場として使い、弓道の練習をすることができるようになっています。
# 父は武道家、母は舞踊家。よく私は...父の跡取りのように思われるのですが。そんなわけで、本来は日舞の舞踊家としての跡取りが期待されていると言えます。
# もちろん、こんな立派な舞踊場兼武道場があるわけですから、父からも跡取りが欲されているのは間違いないと思いますが。
# といっても、あんな風に...居眠りしている母の様子を見ていると、まあ本当にそんなに期待されているのかどうかもわかりませんけれど...ね。フフフ。
# 曲が終わると同時に目を開けた母が言いました。

# なるほど。そういうことでしたか。
# 言いにくそうに言って少し照れた様子の母を見ながら考えました。
# そういえば、父の誕生日が近いです。
# 私はなんだか急に...嬉しくなりました。
# それに。そういうことなら、今日は放課後のμ'sの練習のあとも、少しみんなと一緒に過ごす時間がとれそうです。
#   わかりました。それなら、今日も私も穂乃果たちと一緒に夕食を取ってきてもかまわないでしょうか？
# 嬉しそうに笑いながら言ういつもの母のお気に入りの昔話に、少しだけうんざりし...私と穂乃果は母たちとは違います...でも、そう言いたくても、堂々と否定できないところがなぜか悔しくて。私は、もう学校の時間なので支度をしてきますと、早々に母の前を去りました。
# 私は...結婚とか、子どもとか。そんなことは全く考えられません!  そんな遠い遠い未来のことを言われても...困ります。それどころか、今、私たちは、私たちが一緒に居られるための場所を。私たちの母校・音ノ木坂学院をこの世から失わないために...そのために毎日一生懸命頑張っているのに。
# 全く呑気な母親です。
# 子の心、親知らず。
# ああ。ことりがよく言うように。私は少し...苦労性なのでしょうか？


# その日の練習を終えた...帰り道。
# そう言いながら穂乃果がおなかをさすりあげる様子を見ていたら、思わず笑ってしまいました。
#   そんな風におなかを突き出していたら、まるでタヌキのように見えますよ？
# 夕食の時間も過ぎて、もうすっかり暗くなった夜空に浮かぶ、少したれ目な丸顔の穂乃果タヌキ。
# プッ...クスクス。そう思ったらますますタヌキに見てきて、笑いが止まらなくなりました。似てる...穂乃果のうちの裏庭においてある信楽焼の大きなおタヌキ様。小さい頃はよくおままごとの相手にして一緒に遊びましたっけ。
#   す、すみません...クスクス
# 今日のμ'sの練習を終えて、みんなで立ち寄ったファミリーレストラン。一人だけ追加でポテトフライまで頼んで嬉しそうに食べていた穂乃果の顔が目に浮かぶと...やっぱりなぜか笑顔になってしまいます。
# ピョンとひとつ跳ねて、髪を揺らした穂乃果が言いました。にっこり、真ん丸なお月様のような大きな笑顔。
#   な、何をいきなり...
#   そ、それは...
# 別にそんなことは気にしてないですよ、と言おうとして。少しだけ、寂しそうな穂乃果の顔に気がつきました。
# 全員徒歩通学のμ'sメンバーが、駅近くのファミレスから、それぞれ自宅のある方向へと別れて散り、最後に残ったのは...昔から家が一番の近所の幼なじみのこの2人。
# 私と...穂乃果でした。
# しょんぼりと肩を落とす穂乃果に。
#   そんなことないです。穂乃果だって、お店の手伝いがあるじゃないですか。
# 少し照れた顔でポリポリと頭をかいて言う穂乃果に...私は再び笑顔になってしまって。
#   私ももう、当たり前ですから。お互い...自営業の娘は大変ですよね。
# 私はそう言って笑いながら、ふと前を見上げると。
# 急に周囲の暗さが増していました。
# いつのまにか私たちの住む...家の近くまで歩いてきていました。
# '''
  # umi = s.split('\n')
  # learnTrigram(umi)

