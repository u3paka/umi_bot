#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
from sql_models import *

import _
from _ import p, d, MyObject, MyException
import urllib
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import bs4
# MY PROGRAMs

def get_bs4soup_old(url):
	header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	html = urllib.request.urlopen(url)
	soup = bs4.BeautifulSoup(html, 'lxml')
	return soup
def get_bs4soup(url):
	USER_AGENT = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	# Selenium settings
	phantomjs_path = '/usr/local/bin/phantomjs'
	# phantomjs_args = [ '--proxy=proxy.server.no.basho:0000', '--cookie-file={}'.format("cookie.txt") ] service_args=phantomjs_args
	driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull, desired_capabilities={'phantomjs.page.settings.userAgent':USER_AGENT})
	# get a HTML response
	driver.get(url)
	html = driver.page_source.encode('utf-8')  # more sophisticated methods may be available
	soup = bs4.BeautifulSoup(html, 'lxml')
	# ss = driver.execute_script('return loadDisqus();')
	# p(ss)
	return soup
def get_googlemap(url = 'https://notendur.hi.is/~sfg6/google_maps_example/'):
	USER_AGENT = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	phantomjs_path = '/usr/local/bin/phantomjs'
	driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull, desired_capabilities={'phantomjs.page.settings.userAgent':USER_AGENT})
	# get a HTML response
	driver.set_window_size(1280, 800)
	driver.get(url)
	html = driver.page_source.encode('utf-8')  # more sophisticated methods may be available
	soup = bs4.BeautifulSoup(html, 'lxml')
	p(soup)
	time.sleep(5)
	driver.save_screenshot('test_google_maps_api_screenshot.png')

def extract_ss(url = 'http://www.lovelive-ss.com/?p={}'):
	soup = get_bs4soup(url)
	title = soup.find('h1', class_="entry-title")
	if title is None:
		return None
	else:
		p(title.get_text(), url)
	try:
		ss_contents = soup.find("div", class_ = "entry-content").find_all("dd", class_ ="t_b")
	except:
		return None
	def op_soup(content):
		a_conts = content.find_all('a')
		[a_cont.extract() for a_cont in a_conts if not a_cont is None]
		return content.get_text()
	s_ls = [op_soup(ss_content) for ss_content in ss_contents]
	return s_ls
def search_weblioEJJE(word = 'ask'):
	try:
		ans = CrawledData.select().where(CrawledData.title == word).get()
		return ans.data
	except DoesNotExist:
		try:
			converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
			ejje_url = ''.join(["http://ejje.weblio.jp/content/", converted_word])
			soup = get_bs4soup(ejje_url)
			text = str(soup.find("div", class_ = "summaryM"))
			ans = re.sub('([a-zA-Z!-/:-@¥[-`{-~\s]+)', '', text).replace('主な意味', '')
			if ans:
				CrawledData.create(tag = 'weblio', url = ejje_url, title = word, data = ans)
			return ans
		except:
			return ''

def search_wiki(word = 'クロマニョン人'):
	ans = ''
	try:
		converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
		wiki_url = ''.join(["https://ja.wikipedia.org/wiki/", converted_word])
		soup = get_bs4soup(wiki_url)
		ptext = soup.findAll("p")
		pstr =  ''.join([p.get_text() for p in ptext])
		ans = re.sub(re.compile('\<.+\>'), '' , pstr)
		ans = ans.replace('この記事には複数の問題があります。改善やノートページでの議論にご協力ください。', '').replace('■カテゴリ / ■テンプレート', '')
		anslist = [re.sub(re.compile('\[.+\]'), '' , s) for s in ans.split('。')]
		ans = ''.join(['。'.join(anslist[:8]), '。']).replace('。。', '。')
		return ans
	except Exception as e:
		d(e)
		return ''.join(['\'', word, '\'に一致する語は見つかりませんでした。'])

def get_dl_links(url = "https://www.jstage.jst.go.jp/browse/jspa1962/-char/ja/", extention = 'pdf', except_str = 'pub', DIR = DATADIR, sleep_time = 1):
	abs_filename_ls = []
	try:
		soup = get_bs4soup(url)
		links = soup.findAll('a')
		download_urls = [href for href in [link.get('href') for link in links] if href and extention in href and not except_str in href]
		BASE_URL = '/'.join(url.split('/')[:3])
		downloads_cnt = len(download_urls)
		error_cnt = 0
		p(''.join([str(downloads_cnt), '件のファイルをダウンロードします。']))
		for i in range(downloads_cnt):
			time.sleep(sleep_time)
			try:
				target_url = ''.join([BASE_URL, download_urls[i]])
				p(target_url)
				filename = '.'.join([target_url.split('/')[-2], extention])
				abs_filename_ls.append(_.download_file(url = target_url, DIR = DIR, filename = filename))
			except:
				error_cnt += 1
				pass
			p(''.join(['COMPLETE:', str(i-error_cnt+1), '/', str(downloads_cnt), '\tERR:', str(error_cnt)]))
		return abs_filename_ls
	except Exception as e:
		p(e)
		return abs_filename_ls
def get_ss(word = 'クロマニョン人'):
	ans = ''
	try:
		converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
		wiki_url = ''.join(["https://ja.wikipedia.org/wiki/", converted_word])
		soup = get_bs4soup(wiki_url)
		ptext = soup.findAll("p")
		pstr =  ''.join([p.get_text() for p in ptext])
		ans = re.sub(re.compile('\<.+\>'), '' , pstr)
		ans = ans.replace('この記事には複数の問題があります。改善やノートページでの議論にご協力ください。', '').replace('■カテゴリ / ■テンプレート', '')
		anslist = [re.sub(re.compile('\[.+\]'), '' , s) for s in ans.split('。')]
		ans = ''.join(['。'.join(anslist[:8]), '。']).replace('。。', '。')
		return ans
	except Exception as e:
		d(e)
		return ''.join(['\'', word, '\'に一致する語は見つかりませんでした。'])
def analyse_sentiment_yahoo(word = ''):
	 # リアルタイム検索
	USER_AGENT = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	phantomjs_path = '/usr/local/bin/phantomjs'
	driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull, desired_capabilities={'phantomjs.page.settings.userAgent':USER_AGENT})
	driver.get("http://realtime.search.yahoo.co.jp/realtime")
	try:
		elem = driver.find_element_by_name('p')
	except:
		return False
	elem.clear()
	elem.send_keys(word)
	elem.send_keys(Keys.RETURN)
	time.sleep(1)
	html = driver.page_source.encode('utf-8')  # more sophisticated methods may be available
	soup = bs4.BeautifulSoup(html, 'lxml')
	ptext = soup.findAll('script')
	pstr = ''.join([p.get_text() for p in ptext])
	reg = 'YAHOO.JP.srch.rt.sentiment = (?P<json>.+)'
	compiled_reg = re.compile(reg, re.M)
	reg_ls = compiled_reg.search(pstr)
	if reg_ls:
		reg_ls_json = reg_ls.groupdict()
		senti_json = reg_ls_json['json']
		if senti_json:
			sentiment_dic = json.loads(senti_json)
			return sentiment_dic

class ShindanMaker(MyObject):
	def __init__(self):
		USER_AGENT = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
		phantomjs_path = '/usr/local/bin/phantomjs'
		self.driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull, desired_capabilities={'	phantomjs.page.settings.userAgent':USER_AGENT})

	def result(self, form = 'あるぱか', url = None):
		try:
			if not url is None:
				self.url = url
			self.driver.get(self.url)
			elem = self.driver.find_element_by_id('form')
			tag = self.driver.find_elements_by_class_name('input-lg')[0]
			tag.clear()
			tag.send_keys(form)
			tag.send_keys(Keys.RETURN)
			time.sleep(0.5)
			shindan_result = self.driver.find_element_by_id('copy_text_140').text
			self.driver.quit()
			return shindan_result
		except:
			return ''

	def get_hot_shindan(self, n = 10):
		try:
			hot_ranking_url = 'https://shindanmaker.com/c/list?mode=hot'
			url_base = 'https://shindanmaker.com/a'
			self.driver.get(hot_ranking_url)
			html = self.driver.page_source.encode('utf-8')  # more sophisticated methods may be available
			soup = bs4.BeautifulSoup(html, 'lxml')
			hots = soup.findAll('a', class_ = 'list_title')
			rand = np.random.randint(n)
			href = hots[rand].get('href')
			self.url = ''.join([url_base, href])
		except:
			return ''
# def get_dm_image(self, n = 10):

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
		user = 'p_eval'
		text = "皇居"
	url = 'http://www.lovelive-ss.com/?p=8560'
	# soup = get_bs4soup(url)
	# p(soup)
	# import operate_sql
	# import natural_language_processing
	# site_url = 'http://www.lovelive-ss.com/?p={}'
	# import urllib
	# import urllib.request # opener
	# import urllib.parse # urlencode
	# import http
	# import http.cookiejar
	
	# opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
	USER_AGENT = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	phantomjs_path = '/usr/local/bin/phantomjs'
	login_url = 'https://mobile.twitter.com/session/new'
	# img_url = 'https://twitter.com/messages/media/772747782637563907'
	img_url = 'https://ton.twitter.com/1.1/ton/data/dm/772785678509760515/772785678547423232/iEUEceDa.jpg'
	driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull, desired_capabilities={'phantomjs.page.settings.userAgent':USER_AGENT})
	driver.get(img_url)
	try:
		loginid = driver.find_element_by_id('session[username_or_email]')
	except:
		p('log-in')
		tw_id, tw_pw = 'LiveAI_Rin','705216130'
		driver.get(login_url)  # ログインページを開く
		html = driver.page_source.encode('utf-8')
		loginid = driver.find_element_by_id('session[username_or_email]')
		password = driver.find_element_by_id('session[password]')
		loginid.send_keys(tw_id)
		password.send_keys(tw_pw)
		driver.find_element_by_name('commit').click()
		driver.get(img_url)
		time.sleep(1)
		driver.save_screenshot('DMimg.png')
		driver.quit()
	# p(search_weblioEJJE(word = 'some'))
	# range(4538, 8000):
	# reg = natural_language_processing.RegexTools()
	# filename = /XXXXXX'
	# url = 'https://www.google.co.jp/searchbyimage?image_url={}&encoded_image=&image_content=&filename=&hl=ja'.format(filename)
	# soup = get_bs4soup(url)
	# p(soup)
	# xkey = 'スクフェスのアイコン'
	# converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
	# g_url = 'https://www.google.co.jp/search?q={}&tbm=isch'.format(converted_word)
	# get_googlemap(url = g_url)
	# a = analyse_sentiment_yahoo(word = xkey)
	# p(a)



	# return sentiment_dic
	# import threading
	# threads = []
	#9061 2016/08/10
	# for ss_number in range(9061, 10000):
	# 	p(ss_number)
	# 	try:
	# 		url = site_url.format(ss_number)
	# 		# ss_ls = extract_ss(url = url)
	# 		# if ss_ls:
	# 		# 	operate_sql.save_ss(url, ss_ls)

	# 		datas = operate_sql.get_ss(url = url)
	# 		text = ''.join([data.text for data in datas])
	# 		# p(reg.extract_discorse(text))
	# 		operate_sql.save_ss_dialog(url)
	# 	except Exception as e:
	# 		d(e)
	# 	time.sleep(1+np.random.rand()*3)
	# for thread in threads:
	# 	if thread.is_alive():
	# 		thread.join()


	# p(1+np.random.rand()*3)
	# operate_sql.save_ss(url = url, texts = ['a', 'ss'])
	# extract_ss(url = 'http://www.lovelive-ss.com/?p=22')
	# p(os.environ['PATH'])
	# print(search_wiki(word = '官僚制'))
	# get_dl_links('http://www.fsa.go.jp/news/newsj/16/ginkou/f-20050629-3.html', extention = 'pdf', DIR = /XXXXXX', sleep_time = 1)
# 	while len(ans) > 130:
# 		ans = '。'.join(ans.split('。')[:-2])
# 	ans = ''.join([ans, '。'])
# 	print(ans)
# 	print(len(ans))
	# s = 'GIRLS und PANZER[注釈 1]は、'
	# face_char = re.compile('\[.+\]')
	# facelist = face_char.findall(s)
	# cleaned = re.sub(re.compile('\[.+\]'), '' , s)
	# print(cleaned)
	# cmdlist = text.split(' ')
	# text = cmdlist[0]
	# ret = SRTR(text, user)
	# print(ret)