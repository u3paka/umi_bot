#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, io
import subprocess
import multiprocessing
cpu_count = multiprocessing.cpu_count()
if cpu_count == 2:
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import json
import re
import urllib.request
import shutil
import time
from datetime import datetime, timedelta
from collections import Counter, deque
from itertools import chain
#math
import random
import math
import numpy as np
import cv2
import tensorflow as tf
import tensorflow.python.platform
from sklearn import cross_validation, metrics, preprocessing
from sklearn.externals import joblib
import skflow
import requests
# Tweepyライブラリをインポート
import tweepy

import plotly


def support_datetime_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(repr(o) + " is not JSON serializable")

THISPATH = os.path.abspath(os.path.dirname(__file__))
PROJECTPATH = '/'.join(THISPATH.split('/')[:-1])
DATADIR = '{PROJECTPATH}/Data'.format(PROJECTPATH = PROJECTPATH)

#configurationを読み込み or 生成
cfgPLACE = THISPATH + '/config.json'
cfg = {}
try:
	with open(cfgPLACE, "r", encoding='utf-8') as cfgjson:
		cfg = json.load(cfgjson)
except Exception as e:
	print(e)
	with open(cfgPLACE, "w", encoding='utf-8') as cfgjson:
		json.dump(cfg,cfgjson, ensure_ascii=False, sort_keys=True, indent = 4, default = support_datetime_default)
if 'BOT_ID' in cfg:
	BOT_ID = cfg['BOT_ID']
else:
	BOT_ID = input('BOTs screen name is ...')
	with open(cfgPLACE, "w", encoding='utf-8') as cfgjson:
		json.dump(cfg,cfgjson, ensure_ascii=False, sort_keys=True, indent = 4, default = support_datetime_default)

CONSUMER_KEY = cfg['twtr']['consumer_key']
CONSUMER_SECRET = cfg['twtr']['consumer_secret']
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
ACCESS_TOKEN = cfg['twtr']['access_token_key']
ACCESS_SECRET = cfg['twtr']['access_token_secret']
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
twtr = tweepy.API(auth, wait_on_rate_limit=True)

plotly.plotly.sign_in(username="xxxx", api_key=cfg["plotlyAPIKEY"])

#tempFileを読み込み or 生成
TEMPJSONPLACE = THISPATH + '/' + BOT_ID+".tmp.json"
tmp = {}
try:
	with open(TEMPJSONPLACE, "r", encoding='utf-8') as tmpjson:
		tmp = json.load(tmpjson)
except Exception as e:
	print(e)
	with open(TEMPJSONPLACE, "w", encoding='utf-8') as tmpjson:
		json.dump(tmp,tmpjson, ensure_ascii=False, sort_keys=True, indent = 4, default = support_datetime_default)

# 各種キーをセット
# SECRETJSON = '{PROJECTPATH}/Data/secretDict.json'.format(PROJECTPATH = PROJECTPATH)
# SECRETDIC = json.load(open(SECRETJSON))



myPROFILE = {}
myPROFILE['NAME'] = cfg['BOT_name']
myPROFILE['nicknames'] = cfg['BOT_nicknames'].replace(' ', '').split(',')
myPROFILE['ICON'] = DATADIR + '/user/' + BOT_ID + '/' + BOT_ID + '_icon.jpg'
myPROFILE['Banner'] = DATADIR + '/user/' + BOT_ID + '/' + BOT_ID + '_Banner.jpg'
myPROFILE['BG'] = DATADIR + '/user/' + BOT_ID + '/' + BOT_ID + '_BG.jpg'
myPROFILE['DESCRIPTION'] = cfg['DESCRIPTION']
myPROFILE['URL'] = cfg['githubURL']
myPROFILE['LOCATION'] = '状態: ◯'

DIRIMGtmp = '{PROJECTPATH}/Data/tmp'.format(PROJECTPATH = PROJECTPATH)
DIRIMGfeedback = '{PROJECTPATH}/Data/imgsfeedback'.format(PROJECTPATH = PROJECTPATH)
DIRIMGundefined = '{PROJECTPATH}/Data/imgsfeedback/undefined'.format(PROJECTPATH = PROJECTPATH)

#DBs
twtrSQLPLACE = '{PROJECTPATH}/Data/twtrData.sqlite3'.format(PROJECTPATH = PROJECTPATH)
langDBPLACE = DATADIR + '/' + 'tfidf.sqlite3'
userDBPLACE = DATADIR + '/' + BOT_ID + '.base'
talkDBPLACE = DATADIR + '/' + BOT_ID + '.talk'
clockDBPLACE = DATADIR + '/' + BOT_ID + '.clock'
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
userDB = SqliteExtDatabase(userDBPLACE, autocommit=False, journal_mode='persist')
langDB = SqliteExtDatabase(langDBPLACE, autocommit=False, journal_mode='persist')
talkDB = SqliteExtDatabase(talkDBPLACE, autocommit=False, journal_mode='persist')
twtrDB = SqliteExtDatabase(twtrSQLPLACE, autocommit=False, journal_mode='persist')
clockDB = SqliteExtDatabase(clockDBPLACE, autocommit=False, journal_mode='persist')

modelNNimg = DATADIR + '/ML_Brain/DNN_1-3_8'
testpic = DATADIR + '/imgs/maki/sr-maki-cool-shoki-go.jpg'

cv2CascadeClassifier = DATADIR + '/lib/lbpcascade_animeface.xml'


def iscalledBOT(text):
	if True in [botname in text for botname in myPROFILE['nicknames']]:
		return True
	else:
		return False

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

# MyModules
import utiltools











