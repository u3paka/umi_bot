#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import io
import os
import charaS
import requests
import urllib.parse
import urllib.request
import json
import random
import imghdr
import subprocess


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def flatten(nested_list):
    """2重のリストをフラットにする関数"""
    return [e for inner_list in nested_list for e in inner_list]

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

def dm2tweet(status):
  s= status['direct_message']
  s['user'] = {}
  s['user']['screen_name'] = s['sender_screen_name']
  s['user']['name'] = s['sender']['name']
  s['extended_entities'] = s['entities']
  return s

if __name__ == '__main__':
    # testword = ["猫"]
    # get_image(2, testword)
# if __name__ == '__main__':
# 	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	a = {}
# 	a['media'] = ['a']
# 	if 'media' in a:
	print(a)