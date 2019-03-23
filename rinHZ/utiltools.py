#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *

def getJSON(place = TEMPJSONPLACE):
  with open(place, "r", encoding='utf-8') as tmpjson:
    return json.load(tmpjson)

def saveJSON(tmp, place = TEMPJSONPLACE):
  with open(place, "w", encoding='utf-8') as tmpjson:
    # shutil.copy2(place, ''.join([place, '.bkup']))
    try:
      json.dump(tmp, tmpjson, ensure_ascii=False, sort_keys=True, indent = 4,  default = support_datetime_default)
      return True
    except:
      return False

def t2t(strtime):
  return datetime.strptime(strtime, '%Y-%m-%dT%H:%M:%S.%f')


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def flatten(nested_list):
    """2重のリストをフラットにする関数"""
    return [e for inner_list in nested_list for e in inner_list]

def getDeepPathDic(DIR):
  def filebool(jpg):
    if jpg in {'.DS_Store'}:
      return False
    elif '.' in jpg:
      return True
    else:
      return False
  clsdirs = os.listdir(DIR)
  clsdirs = [clsdir for clsdir in clsdirs if not clsdir in {'.DS_Store'}]
  imgdics = list(chain.from_iterable([[(''.join([clsdirs[i],'/', jpg]), i)  for jpg in os.listdir(DIR + clsdirs[i]) if filebool(jpg)] for i in range(len(clsdirs))]))
  return imgdics

def crowlDic(text = 'test', dic = tmp["responseWord"]):
  def func(A):
    if A in text:
      return dic[A]
  anss =  [react for react in [func(atg) for atg in dic] if react != None]
  if anss != []:
    return anss[0]
  else:
    return ''

def cleanText(text, isKaigyouOFF = False):
  text = re.sub(r'(@[^\s　]+)', '', text)
  text = re.sub(r'(#[^\s　]+)', '', text)
  # text = re.sub(r'(http[^\s　]+)', '', text)
  text = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', text)
  text = re.sub(r'(^[\s　]+)', '', text)
  text = re.sub(r'([\s　]+$)', '', text)
  text = text.replace('&lt;', '<').replace('&gt;', '>')
  if isKaigyouOFF:
    text = re.sub(r'(([\s　]+))', '', text)
  return text

def cleanText2(text):
   text = re.sub(r'[!-/:-@[-`{-~]', '', text)
   text = re.sub(r'(([\s　]+))', '', text)
   text = text.replace('w', '')
   return text

def dm2tweet(status):
  s= status['direct_message']
  s['user'] = {}
  s['user']['screen_name'] = s['sender_screen_name']
  s['user']['name'] = s['sender']['name']
  s['extended_entities'] = s['entities']
  s['retweeted'] = False
  s['is_quote_status'] = False
  return s

def sigmoid(z):
  return 1/(1+np.exp(-z)) if -100. < z else 0.

def adjustSize(DIR):
  clsdirs = os.listdir(DIR)
  clsdirs = [clsdir for clsdir in clsdirs if not clsdir in {'.DS_Store'}]
  dics = [(clsdir, os.listdir(DIR + clsdir)) for clsdir in clsdirs]
  lendic = [len(adds) for clsdir, adds in dics]
  maxsize = np.max(lendic)
  per = np.around(maxsize/lendic)
  [[[shutil.copy2(DIR+dics[i][0]+'/'+add, DIR+dics[i][0]+'/'+'copy'+str(k)+'_'+add) for add in dics[i][1] if not add in {'.DS_Store'} ] for k in range(int(per[i])) if k != 0 ] for i in range(len(clsdirs))]

def sec2HMSstr(sec):
  hours = 0
  minutes = 0
  if sec>3600:
    hours = int(round(sec/3600,1))
    sec -= hours*3600
  if sec > 60:
    minutes = int(round(sec/60,1))
    sec -= minutes*60
  return ''.join([str(hours),'時間',str(minutes),'分', str(sec),'秒'])

def eew(csv, standard = 0, bot_status = {'eewIDset' : {'ND20160216143311'}}):
  eew = csv.split(',')
  eewDic = {}
  if eew[1] != '01':
    eewDic['title'] = '【緊急地震速報'
  else:
    eewDic['title'] = '(訓練)【緊急地震速報'
  eewDic['date'] = eew[2]
  # eewDic['ID'] = eew[5]
  isLAST = False
  if eew[5] in bot_status['eewIDset']:
    if eew[3] in set(['8', '9']):
      eewDic['title'] = ''.join(['(最終)', eewDic['title']])
      bot_status['eewIDset'].discard(eew[5])
    else:
      return ''
  else:
    bot_status['eewIDset'].add(eew[5])

  eewDic['time'] = eew[6].split(' ')[1]
  eewDic['area'] = eew[9]
  eewDic['depth'] = ''.join([eew[10], 'km'])
  eewDic['magnitude'] = eew[11]
  eewDic['seismic_intensity'] = eew[12]
  if eew[13] == '1':
    eewDic['eqType'] = '海洋'
  else:
    eewDic['eqType'] = '内陸'
  eewDic['alert'] = eew[14]
  eewAlert = ''
  if int(eewDic['seismic_intensity']) >= standard:
    if eew[0] != '35':
      eewAlert = ''.join([eewDic['title'], '<震度', eewDic['seismic_intensity'], '> M', eewDic['magnitude'], '】\n震源:', eewDic['area'], ' (', eewDic['eqType'], ')\n', eewDic['time'], '発生', ' 深さ', eewDic['depth']])
    else:
      eewAlert = ''.join([eewDic['title'], '<震度', eewDic['seismic_intensity'], '>】\n震源:', eewDic['area'], ' (', eewDic['eqType'], ')\n', eewDic['time'], '発生', '深さ', eewDic['depth']])
  return eewAlert, bot_status

def saveMedias(status, ID, DIR = '/Users/xxxx'):
  def saveMedia(medias, ID, i, screen_name):
    m = medias[i]
    media_url = m['media_url']
    if ID == None:
      ID = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = ''.join([DIR,'/',ID,'_',str(i),'_',screen_name, '.jpg'])
    if os.path.exists(DIR) == False:
      os.mkdir(DIR)
    try:
      urllib.request.urlretrieve(media_url, filename)
      print(filename)
      return filename
    except IOError:
      print ("[ERR.SAVE.img]")
      return ''
  try:
    medias = status['extended_entities']['media']
    # print(status)
    return [filename for filename in [saveMedia(medias, ID, i, status['user']['screen_name']) for i in range(len(medias))] if filename != '']
  except Exception as e:
    print(e)

def saveImg(media_url, DIR, filename):
  if os.path.exists(DIR) == False:
    os.mkdir(DIR)
  try:
    absfilename = '/'.join([DIR,filename])
    if os.path.exists(absfilename):
      os.remove(absfilename)
    urllib.request.urlretrieve(media_url, absfilename)
    print(absfilename)
    return absfilename
  except IOError:
    print ("[ERR.SAVE.img]")
    return ''


def getRandIMG(DIR):
  pics = [fn for fn in os.listdir(DIR) if not fn == '.DS_Store']
  pic = np.random.choice(pics)
  return '/'.join([DIR, pic])

if __name__ == '__main__':
  # adjustSize(DIR)
  s = '[████▓▒に▒▓████'
  print(crowlDic(text = 'ためし', dic = tmp["reactWord"]))
  # print(cleanText2(s))

  # print(TEMP)
  # TEMP['test2'] = {'a':22}
  # print(TEMP)
  # saveTEMP(TEMP)
  # print(getRandIMG('/Users/xxxx'))
  # print(sec2HMSstr(50))
  # csv = '37,00,2016/02/16 14:34:00,9,3,ND20160216143311,2016/02/16 12:33:01,40.4,142.2,岩手県沖,50,3.6,2,1,0'
  # al = eew(csv, standard = 2)
  # print(al)


