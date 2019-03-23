#!/usr/bin/env python
# -*- coding: utf-8 -*-
import natural_language_processing
from sql_models import *
import _
from _ import p, d, MyObject, MyException
import operate_sql
import queue
# import concurrent.futures
import random

# from sklearn.cluster import KMeans
# def kmeans(features, k=10):
#         km = KMeans(n_clusters=k, init='k-means++', n_init=1, verbose=True)
#         km.fit(features)
#         return km.labels_
# def plot(features, labels):
#         import matplotlib.pyplot as plt
#         plt.scatter(features[:, 0], features[:, 1], c=labels, cmap=plt.cm.jet)
#         plt.show()

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# from sklearn.decomposition import TruncatedSVD
# from sklearn.preprocessing import Normalizer
# def main(items, isPlot =False):
#         vectorizer = TfidfVectorizer(
#                 use_idf=True
#         )
#         X = vectorizer.fit_transform(items)
#         lsa = TruncatedSVD(10)
#         X = lsa.fit_transform(X)
#         X = Normalizer(copy=False).fit_transform(X)
#         km = KMeans(init='k-means++',)
#         km.fit(X)
#         kmlabel = km.labels_
#         print(kmlabel)
#         labeled_items = [(kmlabel[i], items[i]) for i in range(len(kmlabel))]
#         labelcnt = len(kmlabel)
#         i =0
#         while(True):
#             print('++++++++++++++++++')
#             print('クラスタNo.', i)
#             [print('・', item[1]) for item in labeled_items if item[0] == i]
#             i += 1
#             if i > labelcnt:
#                 break
#         if isPlot:
#             plot(X, km.labels_)
def extract_haiku(mas):
        mas = [ma for ma in mas if not ma[1] in {'記号', '顔文字'}]
        yomi = [ma[9] for ma in mas]
        if '*' in yomi:
                return ''
        else:
                origin = [ma[0] for ma in mas]
                metaS = [ma[1] for ma in mas]
                yomi = [y.replace('ー', '').replace('ャ', '').replace('ュ', '').replace('ョ', '') for y in yomi]
        wlens = [len(w) for w in yomi]
        word_total_len = np.sum(wlens)
        if not word_total_len in {17, 18}:
                return ''
        else:
                wlenArr = [np.sum(wlens[0:i+1]) for i in range(len(wlens))]
                if 5 in wlenArr and 12 in wlenArr and 17 in wlenArr:
                        index1 = wlenArr.index(5)+1
                        index2 = wlenArr.index(12)+1
                        comment =    '[5-7-5]'
                elif 5 in wlenArr and 13 in wlenArr and 18 in wlenArr:
                        index1 = wlenArr.index(5)+1
                        index2 = wlenArr.index(13)+1
                        comment = '[5-8-5]'
                else:
                        return ''
                ExSets = {'助詞', '助動詞', '記号'}
                if mas[index1][1] in ExSets or mas[index2][1] in ExSets:
                        return ''
                ExSets2 = {'非自立', '接尾'}
                if mas[index1][2] in ExSets2 or mas[index2][2] in ExSets2:
                        return ''
                return ''.join(['\n',''.join(origin[0:index1]), '\n    ', ''.join(origin[index1:index2]), '\n        ', ''.join(origin[index2:]), '...', comment])

def getBoomWords(username = '_umiA', n = 400):
        try:
                with twlog_sql.transaction():
                        tweets = Tweets.select().where((operateTweets.screen_name == username) & (~Tweets.text.contains('RT'))).order_by(Tweets.createdat.desc()).limit(n)
                        tweetslist = [clean_text(tweet.text) for tweet in tweets]#    if 'RT' not in tweet.text]
                        # print([tweet.text for tweet in tweets])
                        tweetslist = [Kaomoji(tweet) for tweet in tweetslist]
                        nouns = [natural_language_processing.MA.get_mecab(s[0], form='名詞', exception="数,接尾,非自立,接続助詞,格助詞,代名詞",returnstyle = 'list',Debug=0) for s in tweetslist]
                        # nounslist = list(set(chain.from_iterable(nouns)))
                        nounslist = list(chain.from_iterable(nouns))
                        # print(nounslist)
                        noun2list = [noun for noun in nounslist if len(noun) > 2]
                        # # print(noun2list)
                        # randn = random.choice(noun2list)
                        if noun2list == []:
                                print(user + 'さんのデータが足りません。もう少し経ってから再試行してみてください。')
                        else:
                                print(user + 'さんが最近よくつかう言葉は...')
                                counter = Counter(noun2list)
                                for word, cnt in counter.most_common(5):
                                        print('☆ ', word)
                                print('です。')
        except IntegrityError as ex:
                print(ex)
                db.rollback()

class TFIDF(MyObject):
        def __init__(self, option = ''):
                self.option = option
                self.fix_s1_tfidf = None

        @_.retry(OperationalError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
        @db.atomic()
        def upsert_word(self, ma, is_learn = False):
                genkei = ma[7]
                hinshi = ma[1]
                hinshi2 = ma[2]
                document_frequency = 1
                is_created = False
                try:
                    wdb = TFIDFModel.get(word = genkei, hinshi = hinshi)
                    wdb.df +=  1
                except DoesNotExist as e:
                    wdb = TFIDFModel(**{'word': genkei, 'hinshi': hinshi, 'hinshi2': hinshi2, 'info3' : ma[3], 'yomi' : ma[8], 'df': 1})
                    is_created = True
                except:
                    raise
                document_frequency = wdb.df
                if is_learn:
                    wdb.save()
                return document_frequency, is_created

        def calc_tf_idf(self, w, term_frequency_dic, total_documents = 30000, is_debug = False, is_learn = False):
                word = w[7]
                term_frequency = term_frequency_dic[word]
                if word == '*':
                        return ''
                else:
                        document_frequency, is_created = self.upsert_word(w, is_learn)
                try:
                        base_inversed_document_frequency = total_documents / document_frequency
                        inversed_document_frequency = 1 + np.log2(base_inversed_document_frequency)
                except:
                        inversed_document_frequency = 1
                tf_idf = term_frequency * inversed_document_frequency
                w.append(tf_idf)
                w.append(is_created)
                if is_debug:
                        p(word, str(round(tf_idf, 2)))
                return w

        def append_tf_idf_on_ma_result(self, ma, total_documents = 420000, is_learn = False, is_debug = False):
                word_ls = [w[7] for w in ma]
                counter = Counter(word_ls)
                term_frequency_dic = {}
                def word_counter(word, cnt):
                    term_frequency_dic[word] = cnt
                [word_counter(word, cnt) for word, cnt in counter.most_common()]
                result = [self.calc_tf_idf(w, term_frequency_dic, total_documents = total_documents, is_debug = is_debug, is_learn = is_learn) for w in ma]
                return result

        def learn_tf_idf(self, sList):
                i = 1;
                for s in sList:
                        p('++++++++++++++++++++++++++++++++++++++++++++++++++')
                        p(i, s)
                        try:
                                ma = natural_language_processing.MA.get_mecab_coupled(s, couple_target = {'記号', '助動詞', '助詞' ,'名詞'}, cp_kakoi = '{}', cp_splitter = '', masking_format = '{original}',    is_mask_on = 1)
                                self.append_tf_idf_on_ma_result(ma, total_documents = i, is_learn = True, is_debug = False)
                        except Exception as e:
                                print(e)
                        i += 1
        def extract_tf_idf(self, ma, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, exception = {'数'}):
                def is_keyword(x, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, exceptions = {'数'}):
                        try:
                                if x[1] in needs:
                                        if not x[2] in exceptions:
                                                return True
                                elif x[2] in needs:
                                        if not x[2] in exceptions:
                                                return True
                                return False
                        except Exception as e:
                                return False
                def sort_tf_idf_ma(tf_idf_ma, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, exceptions = {'数'}):
                        return [x for x in sorted(tf_idf_ma, key = lambda x: x[10], reverse = True) if is_keyword(x, needs, exceptions)]
                ##
                tf_idf_ma = self.append_tf_idf_on_ma_result(ma, total_documents = 420000, is_learn = False, is_debug = False)
                result = sort_tf_idf_ma(tf_idf_ma, needs)
                return result

        def calc_keywords_tf_idf(self, ma, length = 1, needs = {'名詞', '固有名詞', '動詞', '形容詞'}):
                extracted_keywords_ma = self.extract_tf_idf(ma, needs)
                seen = set()
                seen_add = seen.add
                keywords = [(x[7], x[1], x[10], x[11]) for x in extracted_keywords_ma if len(x[0])>length]
                keyword_tf_idf = np.array([x for x in keywords if x[0] not in seen and not seen_add(x[0])])
                return keyword_tf_idf
        def get_random_keywords(self, keywords, random_cnt = 1):
                kwcnt = len(keywords)
                tf_idf = np.array([float(x[2]) for x in keywords])
                per = np.sum(tf_idf)
                p = tf_idf / per
                if random_cnt > kwcnt:
                        random_cnt = kwcnt
                try:
                        return np.random.choice([x[0] for x in keywords], random_cnt, replace=False, p = p)
                except:
                        return []
        def extract_keywords_from_text(self, s, threshold = 50, n = 5, length = 1, is_print = True, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, random_cnt = 1):
                ma = natural_language_processing.MA.get_mecab_coupled(s)
                return self.extract_keywords_from_ma(ma = ma, threshold = threshold, n = n, length = length, is_print = is_print, needs = needs, random_cnt = random_cnt)
        def extract_keywords_from_ma(self, ma, threshold = 50, n = 5, length = 1, is_print = True, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, random_cnt = 1):
                def keyword_filter(datas):
                        exception_set = {'ちゃん', 'こと'}
                        return [data for data in datas if not data[0] in exception_set]
                keyword_tf_idf = self.calc_keywords_tf_idf(ma, length = length, needs = needs)
                kwcnt = len(keyword_tf_idf)
                keyword_tf_idf = keyword_filter(keyword_tf_idf)
                if random_cnt > 0:
                        return self.get_random_keywords(keyword_tf_idf, random_cnt = random_cnt)
                if kwcnt == 0:
                        if is_print:
                                p('=> キーワードは見つかりませんでした。')
                        return []
                else:
                        if is_print:
                                if kwcnt < n:
                                        p('=> ' + str(kwcnt) + '個の文章の重要キーワードを抽出しました。')
                                else:
                                        print('=> ' + str(n) + '個の文章の重要キーワードを抽出しました。')
                        mostImptf_idf = keyword_tf_idf[0][2]
                        print(mostImptf_idf)
                        convImpRate = 100 / float(mostImptf_idf)
                        return impkey
        def precalc_s1_tfidf(self, s):
                self.fix_s1_tfidf =  {ma[7]: ma[10] for ma in self.extract_tf_idf(natural_language_processing.MA.get_mecab_coupled(s)) if ma[1] in {'動詞', '名詞', '固有名詞', '形容詞', '助詞', '副詞', '助動詞'}}
        @_.retry(OperationalError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
        def calc_cosine_similarity(self, s1, s2):
                if not s1 or not s2:
                        return 0
                if not self.fix_s1_tfidf:
                        self.precalc_s1_tfidf(s1)
                tf_idf_ls0 = self.fix_s1_tfidf
                tf_idf_ls1 = {ma[7]: ma[10] for ma in self.extract_tf_idf(natural_language_processing.MA.get_mecab_coupled(s2)) if ma[1] in {'動詞', '名詞', '固有名詞', '形容詞', '助詞', '副詞', '助動詞'}}
                vecF = set(_.f7(list(chain.from_iterable([tf_idf_ls0.keys()] + [tf_idf_ls1.keys()]))))
                v1 = np.array([tf_idf_ls0[w] if w in set(tf_idf_ls0) else 0 for w in vecF])
                v2 = np.array([tf_idf_ls1[w] if w in set(tf_idf_ls1) else 0 for w in vecF])
                bunbo = (np.linalg.norm(v1) * np.linalg.norm(v2))
                if bunbo:
                        return np.dot(v1, v2) / bunbo
                else:
                        return 0
class TrigramMarkovChain(MyObject):
        def __init__(self, character = 'sys'):
                self.character = character
                # self.selected_character_database = []
                self.database = TrigramModel.select()
                self.selected_character_database = self.database.where(TrigramModel.character == self.character)
        def get_startwith(self):
                try:
                        Ws = self.selected_character_database.where(    TrigramModel.W1 == '<BOS>', TrigramModel.P2 ==   '名詞').order_by(TrigramModel.cnt.desc())
                        word = self.choose_randomword(Ws, place = 2)
                except Exception as e:
                        word = '...'
                return word
        @_.retry(OperationalError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
        @db.atomic()
        def generate(self, word = '', is_randomize_metasentence = True):
                ans = ''
                # metaframe_str = self.get_metasentence()
                # metaframe = metaframe_str.split(',')
                if not word:
                        word = self.get_startwith()
                try:
                        forward_ans = self.generate_forward(word)
                        if not forward_ans:
                            word = self.get_startwith()
                            forward_ans = ''.join(['......ところで、', self.generate_forward(word)])
                except:
                        _.log_err()
                        forward_ans = ''
                # ans = ''.join([backward_ans, forward_ans])
                ans = forward_ans.replace('<BOS>', '').replace('<EOS>', '')
                return ans
        def choose_randomword(self, Ws, place = 2):
                word_cnt_ls = [w.cnt for w in Ws]
                if not word_cnt_ls:
                        return ''
                cnt_array = np.array([w.cnt for w in Ws])
                if place == 2:
                        words_ls = [w.W2 for w in Ws]
                elif place == 3:
                        words_ls = [w.W3 for w in Ws]
                elif place == 10:
                        words_ls = [w.framework for w in Ws]
                else:
                        words_ls = [w.W1 for w in Ws]
                return np.random.choice(words_ls, p = cnt_array/np.sum(cnt_array))
        def get_metasentence(self, n = 50):
                try:
                        Ms = mSentence.select().where(mSentence.framework.contains('<BOS>,名詞,助詞')).order_by(mSentence.cnt.desc()).limit(n)
                        return self.choose_randomword(Ms, place = 10)
                except DoesNotExist:
                        pass
        def get_same_hinshi(self, hinshi):
                        W = ''
                        n = 10000
                        # print('品詞一致1')
                        if not W:
                                try:
                                        Ws = self.database.where(TrigramModel.P1 == hinshi).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 1)
                                except DoesNotExist:
                                        pass
                        if not W:
                                # print('品詞一致2')
                                try:
                                        Ws = self.database.where(TrigramModel.P2 == hinshi).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 2)
                                except DoesNotExist:
                                        pass
                        # if not W:
                        #         # print('品詞一致3')
                        #         try:
                        #                 Ws = self.selected_character_database.where(TrigramModel.P3 == hinshi).order_by(TrigramModel.cnt.desc()).limit(n)
                        #                 W = self.choose_randomword(Ws, place = 3)
                        #         except Exception as e:
                        #                 pass
                        return W
        def generate_forward(self, startWith = '', Plist = ['<BOS>','名詞','','名詞','助詞','動詞','助詞','助詞','名詞','名詞','名詞','助詞','動詞','助動詞','助動詞','<EOS>'], break_set = {'」', '。', '!', '！', '?', '？'}, is_debug = False, is_correct_with_hinshi = False, n = 100000):
                QuestionPhrase = '<KEY>...？'
                lenP = len(Plist)
                i = 0
                if startWith:
                        ans = ['', startWith]
                else:
                        ans = ['', '<BOS>']
                for i in range(40):
                        W = ''
                        i1 = i+1
                        i2 = i+2
                        pre1 = ans[i]
                        pre2 = ans[i1]
                        if i2 >= lenP:
                                is_correct_with_hinshi = False
                        else:
                            P3 = Plist[i2]
                            P2 = Plist[i1]
                            P1 = Plist[i]
                        if not W and is_correct_with_hinshi:
                                # print('2単語一致前方2品詞一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2, TrigramModel.P3 == P3, TrigramModel.P2 == P2, TrigramModel.P1 == P1).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 3)
                                except DoesNotExist:
                                        pass
                        if not W and is_correct_with_hinshi:
                        # print('2単語一致前方1品詞一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2, TrigramModel.P3 == P3, TrigramModel.P2 == P2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 3)
                                except DoesNotExist:
                                        pass
                        if not W and is_correct_with_hinshi:
                                # print('2単語一致品詞一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2, TrigramModel.P3 == P3).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 3)
                                except DoesNotExist:
                                        pass
                        if not W:
                                # print('2単語一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 3)
                                except DoesNotExist:
                                        pass
                        if not W:
                                # print('1単語一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 3)
                                except DoesNotExist:
                                        pass
                        if not W:
                                if i == 0:
                                        return ''
                                # print('1単語一致2')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W1 == pre1).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 2)
                                except DoesNotExist:
                                        pass
                        if not W and is_correct_with_hinshi:
                                W = self.get_same_hinshi(P2)
                        if ans[-1] != W:
                                ans.append(W)
                        else:
                                break
                        if W in {'<EOS>'}:
                                break
                        # if W in break_set:
                        #         break
                return ''.join(ans)
#
        def generate_backward(self, startWith = '', Plist = ['<EOS>', '名詞', '助詞', '形容詞', '顔文字','顔文字','顔文字','顔文字','顔文字','顔文字','顔文字','顔文字'], break_set = {'「', '」',    '。', '!', '！', '?', '？'}, n = 100):
                QuestionPhrase = '…'
                isAddFACE = False
                if startWith:
                        ans = ['<EOS>', startWith]
                else:
                        ans = ['<EOS>']
                lenP = len(Plist)
                i = 0
                is_correct_with_hinshi = True
                if len(ans) == 1:
                        try:
                                Ws = self.selected_character_database.where(TrigramModel.W3 == ans[0], TrigramModel.P2 == Plist[1]).order_by(TrigramModel.cnt.desc())
                                W = self.choose_randomword(Ws, place = 2)
                        except Exception as e:
                                W = ['...']
                        ans += W
                        i+= 1
                        # p(ans)
                while True:
                        pre1 = ans[i]
                        i1 = i+1
                        pre2 = ans[i1]
                        if i+2 >= lenP:
                                is_correct_with_hinshi = False
                        else:
                                P3 = Plist[i+2]
                                P2 = Plist[i1]
                                P1 = Plist[i]
                        W = ''
                        if not W and is_correct_with_hinshi:
                            # print('2単語一致前方2品詞一致', ans, i)
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2, TrigramModel.P1 == P3, TrigramModel.P2 == P2, TrigramModel.P3 == P1).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 1)
                                except Exception as e:
                                        pass
                        if not W and is_correct_with_hinshi:
                                # print('2単語一致前方1品詞一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2, TrigramModel.P1 == P3, TrigramModel.P2 == P2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 2)
                                except Exception as e:
                                        pass
                        if not W and is_correct_with_hinshi:
                                # print('2単語一致品詞一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2, TrigramModel.P1 == P3).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 1)
                                except Exception as e:
                                        pass
                        if not W and is_correct_with_hinshi:
                                W = self.get_same_hinshi(P1)
                        if not W:
                                # print('2単語一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 1)
                                except Exception as e:
                                        pass
                        if not W:
                                # print('1単語一致')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 1)
                                except Exception as e:
                                        pass
                        if not W:
                                # print('1単語一致2')
                                try:
                                        Ws = self.selected_character_database.where(TrigramModel.W3 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                                        W = self.choose_randomword(Ws, place = 2)
                                except Exception as e:
                                        if i == 0:
                                                return QuestionPhrase
                        if ans[-1] != W:
                            ans.append(W)
                        else:
                            break
                        i = i +1
                        if W == '<BOS>':
                            break
                return ''.join(ans[2::][::-1])
        # print(e)
def updateMC(taskid = 0, character = '', taskdict = {'character':'sys'}):
    try:
        with db.transaction():
            if taskid != 0:
                t = TrigramModel.update(**taskdict).where(TrigramModel.id == taskid)
            else:
                t = TrigramModel.update(**taskdict).where(TrigramModel.character == character)
            t.execute()
    except Exception as e:
        print(e)
        db.rollback()

def saveMetaS(P):
        Pstr = ','.join(P)
        try:
                # db.create_tables([TrigramModel, mSentence], True)
                with db.transaction():
                        try:
                                M, created = mSentence.get_or_create(framework = Pstr)
                                if created == True:
                                        M.framework = Pstr
                                        M.cnt = 1
                                        M.ok = 1
                                        M.ng = 0
                                        M.save()
                                else:
                                        M.cnt = M.cnt + 1
                                        M.save()
                        except Exception as e:
                                d(e)
                        db.commit()
        except Exception as e:
                db.rollback()

def save_modpair(_from, _to, _tag = ''):
    try:
        # db.create_tables([TrigramModel, mSentence, mod_pair], True)
        with db.transaction():
            try:
                M, created = mod_pair.get_or_create(w_from = _from, w_to = _to)
                if created:
                    M.w_from = _from
                    M.w_to = _to
                    M.w_tag = _tag
                    M.cnt = 1
                    M.posi = 1
                    M.nega = 0
                    M.save()
                else:
                    M.cnt = M.cnt + 1
                    M.w_tag = _tag
                    M.save()
            except Exception as e:
                print(e)
            db.commit()
    except Exception as e:
        db.rollback()

def get_modpair(_from = '', _to = '', _tag = '', n = 100):
    ansdic = {"from": '', "to": '', "tag": '', "cnt": ''}
    try:
        # db.create_tables([TrigramModel, mSentence], True)
        with db.transaction():
            try:
                if not _to:
                    Ms = mod_pair.select().where(mod_pair.w_from == _from, mod_pair.w_tag == _tag).order_by(mod_pair.cnt.desc()).limit(n)
                    cntArr = np.array([m.cnt for m in Ms])
                    return np.random.choice([m.w_to for m in Ms], p = cntArr/np.sum(cntArr))
                elif not _from:
                    Ms = mod_pair.select().where(mod_pair.w_to == _to, mod_pair.w_tag == _tag).order_by(mod_pair.cnt.desc()).limit(n)
                    cntArr = np.array([m.cnt for m in Ms])
                    return np.random.choice([m.w_from for m in Ms], p = cntArr/np.sum(cntArr))
                elif not _tag:
                    Ms = mod_pair.select().where(mod_pair.w_to == _to, mod_pair.w_from == _from).order_by(mod_pair.cnt.desc()).limit(n)
                    cntArr = np.array([m.cnt for m in Ms])
                    return np.random.choice([m.w_tag for m in Ms], p = cntArr/np.sum(cntArr))
                else:
                    Ms = mod_pair.select().where(mod_pair.w_to == _to, mod_pair.w_from == _from, mod_pair.w_tag == _tag).order_by(mod_pair.cnt.desc()).limit(n)
                    return Ms[0].w_cnt
            except Exception as e:
                print(e)
            db.commit()
    except Exception as e:
        db.rollback()
        return ansdic

def trigram_main(s, is_debug = False, character = 'sys'):
    try:
        ma = natural_language_processing.MA.get_mecab_coupled(s, couple_target = {'記号', '助動詞', '助詞' ,'名詞'}, cp_kakoi = '{}', cp_splitter = '', masking_format = '{original}',    is_mask_on = 1)
        ma = [[w[0], w[1]] for w in ma]
        ma = [['<BOS>', '<BOS>']] + ma + [['<EOS>', '<EOS>']]
        Plist = [w[1] for w in ma]
        # saveMetaS(Plist)
        wcnt = len(ma)
        triMA = [(ma[i], ma[i+1], ma[i+2]) for i in range(wcnt-2)]
        if is_debug:
            p(triMA)
        return triMA
    except Exception as e:
        d(e, 'trigram_main')
        return None
def learn_trigram(s_ls, character = 'sys', over = 0, save_freqcnt = 5):
    i = 1
    proc = 4
    import queue
    import random
    import time
    import main
    def sender(q, target_ls, process_id):
        time.sleep(process_id)
        try:
            target_length = len(target_ls)
            ini = target_length * process_id // proc
            fin = target_length * (process_id+1) // proc
            split_target_ls = target_ls[ini:fin]
            cnt = 0
            for s in split_target_ls:
                if main.is_kusoripu(s):
                    p('kusoripu', s)
                else:
                    process = multiprocessing.current_process()
                    p('_______', ''.join([process.name, '=>', str(process_id),'] ', str(over + ini + cnt),'/', str(fin)]), '____________________')
                    p(s)
                    try:
                        trigrams = trigram_main(s, is_debug = False, character = 'sys')
                        if not trigrams:
                            raise Exception
                        try:
                            for trigram in trigrams:
                                q.put(trigram, timeout = 5)
                        except queue.Full:
                           d('%s: put() timed out. Queue is Full' % process.name)
                        except Exception as e:
                           d(e, 'q.put()')
                    except Exception as e:
                        d(e, '_learn_trigram1')
                        pass
                    else:
                        cnt += 1
        except Exception as e:
            d(e)
            return None
        else:
            q.close()
            q.join_thread()
    def receiver(q, process_id):
        while True:
            try:
                trigram = q.get(timeout = 5)
                p(trigram)
                if trigram:
                    with db.atomic():
                        save_trigram_in_transaction(trigram, character = character)
                        p('____Receiver-', str(process_id), 'saved!!')
                # time.sleep(random.random())
            except queue.Empty:
                # queue が空だったらループを抜ける.
                d('get() timed out. Queue is Empty')
                break
            except Exception as e:
                d(e)
    ##
    target_ls = s_ls[over:]
    q = multiprocessing.Queue(maxsize=0)
    senders = []
    for i in range(proc):
        process = multiprocessing.Process(target = sender, args=(q, target_ls, i), name='Sender-%02d' % i)
        senders.append(process)
        process.start()
    receivers = []
    i = 1
    process = multiprocessing.Process(target=receiver, args=(q, i), name='Receiver1')
    receivers.append(process)
    process.start()
    for s_r_process in senders + receivers:
        s_r_process.join()

@_.retry(OperationalError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
def save_trigram_in_transaction(tri, character = 'sys'):
    T, is_created = TrigramModel.get_or_create(character = character, W1 = tri[0][0], W2 = tri[1][0], W3 = tri[2][0], P1 = tri[0][1], P2 = tri[1][1], P3 = tri[2][1], defaults={'cnt' : 0, 'posi':1 , 'nega':0})
    T.cnt += 1
    T.save()
# def learn_trigram(s_ls, character = 'sys', over = 0):
#     i = 1;
#     for s in s_ls:
#         if i > over:
#             p('++++++++++++++++++++++++++++++++++++++++++++++++++')
#             p(i, s)
#             try:
#                 trigram_main(s, 1, 1, character = character)
#             except Exception as e:
#                 print(e)
#         i += 1
# def save_SyApairs(s, pair_type = ''):
#     try:
#         cadic = natural_language_processing.SyA.get_CaboCha_dic(s)
#         pairs = natural_language_processing.SyA.get_pairs(cadic, pair_type = pair_type)
#         [save_modpair(_from = pair[0], _to = pair[1][0], _tag = pair[2]) for pair in pairs]
#     except Exception as e:
        # print(e)


# def learnSyA(sList, over = 0):
#     i = 1;
#     for s in sList:
#         if i > over:
#             print('++++++++++++++++++++++++++++++++++++++++++++++++++')
#             print(i, s)
#             try:
#                 save_SyApairs(s, pair_type = '')
#             except Exception as e:
#                 print('')
#         i += 1

def learnLang(sList, character = 'U'):
    i = 1;
    for s in sList:
        p('++++++++++++++++++++++++++++++++++++++++++++++++++')
        p(i, s)
        try:
            # TrigramModel = trigram_main(s, 1, 0, character)
            tfidf = TFIDF()
            tfidf.append_tf_idf_on_ma_result(s, i, True, 0)
        except Exception as e:
            print('')
        i += 1

def extractKeywords(ma, exp = {'助詞', '助動詞', '記号', '接続詞', '数'}):
    def isKeyword(x, exp = {'助詞', '助動詞', '記号', '接続詞', '数'}):
        if x[1] in exp:
            return False
        elif x[2] in exp:
            return False
        else:
            return True
    return [x for x in sorted(ma, key = lambda x: x[10], reverse = True) if isKeyword(x, exp)]

# def addRelateKW(KWdict):
#     KWdict['名詞'] = ['']
#     KWdict['<BOS>'] = [KWdict['名詞'].pop()]
#     KWdict['形容詞'] = ['危ない', '嬉しい', '汚い']
#     KWdict['格助詞'] = ['は']
#     KWdict['記号'] = ['！']
#     return KWdict

# def getSimilarWords(w = '淫夢', cnt = 3, dockerIP = '192.168.59.103'):
#     g = requests.get("http://" + dockerIP + ":22670/distance?a1=" + w).json()
#     return [g['items'][i]['term'] for i in range(cnt)]

# def getAnalogy(w = ['かわいい', '最低'], cnt = 3, dockerIP = '192.168.59.103'):
#     w.append('')
#     w1 = w[0]
#     w2 = w[1]
#     w3 = w[2]
#     if not w[2]:
#         w3 = w2
#     g = requests.get(''.join(["http://",dockerIP,":22670/analogy?a1=", w1, "&a2=", w2, "&a3=", w3])).json()
#     return [g['items'][i]['term'] for i in range(cnt)]

# def associateAns(word):
#     anal = getSimilarWords(w = word, cnt = 3, dockerIP = '192.168.59.103')
#     ans = ''.join([word, 'といえば', anal[0], 'とか', anal[1], 'ですよね。'])
#     return ans
def reform_info(info, username = '@username'):
        try:
                if info['is_collapsed']:
                    raise Exception
                ans = natural_language_processing.anal_info(info)
                if '？' in ans:
                    ans = ''
                else:
                    filler = 'なるほど...'
                    ans = ''.join([filler, ans.format(username = username), ' _φ(•̀ ᴗ    •́ )'])
        except Exception as e:
                p(e)
                ans = '__ERR__'
        if '__ERR__' in ans:
                ans = ''
        return ans

def wordnet_dialog(kw = 'テスト'):
    ans = ''
    s_order = ''
    wn ='wordnet'
    if not kw:
        return ''
    try:
        wn_dic = operate_sql.get_wordnet_result(lemma = kw)
        if not wn_dic:
            raise
        wn_dic_keys = ([key for key in wn_dic.keys()])
        # p(wn_dic.values())
        rand_key = np.random.choice(wn_dic_keys)
        rand_ls = wn_dic[rand_key]
        while rand_ls == [kw]:
            del wn_dic[rand_key]
            rand_key = np.random.choice(wn_dic_keys)
            rand_ls = wn_dic[rand_key]
        if kw in rand_ls:
            rand_ls.remove(kw)
        if rand_key == 'hype':#上位語
            s_order = '{kw}って{wn}の一種ですよね。'
        elif rand_key == 'hypo':#下位語
            s_order = '{kw}といえば、{wn}ってその一種ですよね。'
        elif rand_key == 'mprt': #被構成要素(部分)
            s_order = '{kw}といえば、{wn}ってその一部ですよね。'
        elif rand_key == 'hprt': #構成要素(部分)
            s_order = '{kw}って{wn}の一部ですよね。'
        elif rand_key == 'mmem': #被構成要素(構成員)
            s_order = '{kw}って、{wn}で構成されてますよね。'
        elif rand_key == 'hmem': #構成要素(構成員)
            s_order = '{kw}って、{wn}を構成しますよね。'
        elif rand_key == 'dmnc': #被包含領域(カテゴリ)
            s_order = '{kw}って、{wn}のカテゴリに入りますよね。'
        elif rand_key == 'dmtc': #包含領域(カテゴリ)
            s_order = '{kw}って、{wn}のカテゴリですよね。'
        elif rand_key == 'dmnu': #被包含領域(語法)
            s_order = '{kw}って、{wn}の語法に入りますよね。'
        elif rand_key == 'dmtu': #包含領域(語法)
            s_order = '{kw}って、{wn}の語法ですよね。'
        elif rand_key == 'dmnr': #被包含領域(地域)
            s_order = '{kw}って、{wn}の地域特有のものですよね。'
        elif rand_key == 'dmtr': #包含領域(地域)
            s_order = '{kw}といえば、{wn}とかが地域特有のものですよね。'
        elif rand_key == 'msub':#被構成要素(物質・材料)
            s_order = '{kw}って、{wn}の材料ですよね。'
        elif rand_key == 'hsub':#構成要素(物質・材料)
            s_order = '{kw}って、{wn}を材料にしてつくられてますよね。'
        elif rand_key == 'enta':
            s_order = '{kw}ってことは、当然{wn}してますよね。'
        elif rand_key == 'caus':
            s_order = '{kw}ってことは{wn}するのですね。'
        elif rand_key == 'inst':
            s_order = '{kw}って、{wn}の一例ですよね。'
        elif rand_key == 'hasi':
            s_order = '{kw}って、たとえば{wn}ですよね。'
        elif rand_key == 'attr':
            s_order = '{kw}と{wn}の間にはなにか関係がありますよね。'
        elif rand_key == 'sim':
            s_order = '{kw}と{wn}は似てますよね。'
        elif rand_key == 'coordinate':#同族語
            s_order = '{kw}って、{wn}とかと同じ感じ...ですよね。'
        else:
            s_order = '{kw}って、{wn}とかに関係する？'
        wn = np.random.choice(rand_ls)
        ans = s_order.format(kw = kw, wn = wn)
        return ans
    except Exception as e:
        p(e)
        ans = ''
        return ans
class DialogObject(MyObject):
    def __init__(self, s):
        #TODO]分離
        self.nlp_datas = natural_language_processing.NLPdatas(s)
        ##
        self.s = s
        self.nlp_data = self.nlp_datas.main
        self.cleaned_s = _.clean_text(self.nlp_data.text, isKaigyouOFF = False)
        # self.keygen = self.keywords_gen()
        self.keywords = []
        self.rel_words = []
        self.tfidf = TFIDF()
        self.get_kw_thread = threading.Thread(target = self._get_keywords, args=(s, ), name='get_kw')
        self.get_kw_thread.start()
        # if self.nlp_data.summary.function == '断定':
            # self.save_fact()
    def is_fact(self):
        # db.create_tables([FactModel], True)
        try:
            with db.transaction():
                fact_dict = self.nlp_data.summary
                fact = FactModel.get(entity = fact_dict.entity, value = fact_dict.value, akkusativ = fact_dict.akkusativ, dativ = fact_dict.dativ)
                return fact
        except DoesNotExist as e:
            return None
        except OperationalError as e:
            return None
        except IntegrityError as e:
            d(e)
            db.rollback()
            raise Exception
        except Exception as e:
            d(e)
            return False
    def save_fact(self):
        # db.create_tables([FactModel], True)
        try:
            with db.transaction():
                fact_dict = self.nlp_data.summary
                fact, is_created = FactModel.get_or_create(entity = fact_dict.entity, value = fact_dict.value, akkusativ = fact_dict.akkusativ, dativ = fact_dict.dativ)
                if not is_created:
                    fact.cnt += 1
                else:
                    fact.cnt = 1
                fact.save()
                db.commit()
                return fact, is_created
        except Exception as e:
            p(e)
            db.rollback()
            return False
    def _get_longest_split(self, s = '', split_word = '」'):
        try:
            if not split_word in s:
                return s
            else:
                s_ls = s.split(split_word)
                split_and_len = [(split, len(split)) for split in s_ls if not 'リプライ数' in split]
                s = sorted(split_and_len, key=lambda x:x[1])[-1][0]
                return s
        except:
                return s
    def keywords_gen(self, needs= {'名詞', '固有名詞'}):
        keywords = ''
        if not keywords:
            s = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', self.s)
            tfidf_kws = self.tfidf.extract_keywords_from_text(s, threshold = 50, n = 5, length = 1, is_print = False, needs = needs, random_cnt = 5)
            keywords = [kw for kw in tfidf_kws if not '@' in kw]
        if not keywords:
            keywords = natural_language_processing.MA.get_mecab(s, mode = 7, form = {'名詞'}, exception = {'記号'}, is_debug = False)
        if not keywords:
            keywords = natural_language_processing.MA.get_mecab(s, mode = 7, form = None, exception = {'記号'}, is_debug = False)
        if keywords:
            for keyword in keywords:
                yield keyword
            for keyword in keywords:
                wn_dic = operate_sql.get_wordnet_result(lemma = keyword)
                if wn_dic:
                    wn_keywords = _.flatten(wn_dic.values())
                    for keyword in wn_keywords:
                        yield keyword
    #
    def _get_keywords(self, s, needs= {'名詞', '固有名詞'}):
        s = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', s)
        keywords = self.tfidf.extract_keywords_from_text(s, threshold = 50, n = 5, length = 1, is_print = False, needs = needs, random_cnt = 5)
        keywords = [kw for kw in keywords if not '@' in kw]
        self.keywords.extend(keywords)
        if not self.keywords:
            self.keywords = ['']
        else:
            random.shuffle(self.keywords)

    def _get_rel_words(self):
        if self.keywords:
            for kw in self.keywords:
                wn_dic = operate_sql.get_wordnet_result(lemma = kw)
                if wn_dic:
                    self.rel_words.extend(_.flatten(wn_dic.values()))

    @_.retry(OperationalError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
    @db.atomic()
    def ss_log_sender(self, kw, q, person = '', n = 100):
        dialogs = None
        dialogs = operate_sql.get_ss_dialog_within(kw = kw, person = person, n = n)
        if not dialogs is None:
            for d in dialogs:
                q.append((d[0][1:-1], d[1][1:-1]))
    @_.retry(OperationalError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
    @db.atomic()
    def tweet_log_sender(self, kw, q, UserList = [], BlackList = [], n = 100):
        dialogs = None
        try:
            if not UserList:
                dialogs = TwDialog.select().where(TwDialog.textA.contains(kw), ~TwDialog.nameB << BlackList).order_by(TwDialog.posi.desc()).limit(n)
            else:
                dialogs = TwDialog.select().where(TwDialog.textA.contains(kw), ~TwDialog.nameB << BlackList, TwDialog.nameB << UserList).order_by(TwDialog.posi.desc()).limit(n)
        except DoesNotExist:
            pass
        else:
            if not dialogs is None:
                for d in dialogs:
                    q.append((d.textA, d.textB))
    def adjust_ans(self, ans):
        if ans is None:
            return ''
        ans = self._get_longest_split(ans, split_word = '」')
        ans = self._get_longest_split(ans, split_word = '「')
        ans = self._get_longest_split(ans, split_word = '。')
        ans = self._get_longest_split(ans, split_word = '：')
        ans = self._get_longest_split(ans, split_word = '』')
        ans = self._get_longest_split(ans, split_word = '『')
        now = datetime.now()
        if '<数>秒' in ans:
            sec_str = now.strftime('%S秒')
            ans = ans.replace('<数>秒', sec_str)
        if '<数>分' in ans:
            min_str = now.strftime('%M分')
            ans = ans.replace('<数>分', min_str)
        if '<数>時' in ans:
            hour_str = now.strftime('%H時')
            ans = ans.replace('<数>時', hour_str)
        if '<数>日' in ans:
            ans = ans.replace('<数>日', '一日')
        if '<数>度' in ans:
            ans = ans.replace('<数>度', '二度')
        if '<数>人' in ans:
            ans = ans.replace('<数>人', '2人')
        if '<数>回' in ans:
            ans = ans.replace('<数>回', '数回')
        if '<人名>' in ans:
            if character != 'sys':
                    ans = ans.replace('<人名>', character)
            else:
                    ans = ans.replace('<人名>', 'あるぱか')
        ans = self._get_longest_split(ans, split_word = '<数>')
        ans = self._get_longest_split(ans, split_word = 'さん')
        ans = self._get_longest_split(ans, split_word = '！')
        ans = ans.replace('<接尾>', 'さん').replace('<地域>', 'アキバ')
        ans = ans.replace('Three', '').replace('two', '').replace('one', '').replace('zero', '').replace('RaidOntheCity', '')
        if not ans:
            ans = operate_sql.get_phrase(status = 'あいづち')
        if not ans[-1] in {'。', '!', '?', '！', '？'}:
            ans = ''. join([ans, '。'])
        return ans
    def dialog(self, context = '', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = [], min_similarity = 0.2, character = 'sys', tools = 'SS,WN,LOG,MC', username = '@〜〜'):
        #URL除去
        s = self.nlp_data.text
        ans = ''
        if context:
            try:
                s = ''.join([context.split('</>')[-1], s])
            except:
                pass
        s = _.clean_text(s, isKaigyouOFF = False)
        self.cleaned_s = s
        d_ls = []
        threads = []
        try:
            self.get_kw_thread.join()
            precalc_thread = threading.Thread(target = self.tfidf.precalc_s1_tfidf, args=(self.cleaned_s, ), name='pre_calc')
            precalc_thread.daemon = True
            threads.append(precalc_thread)
            precalc_thread.start()
            q = []
            need_cnt = 3
            #########################
            #I/O operations
            person = ''
            if character != 'sys':
                person = character
            p(self.keywords)
            if 'SS' in tools:
                for kw in self.keywords[:need_cnt]:
                    process = threading.Thread(target = self.ss_log_sender, args=(kw, q, person, 400), name='Sender-SSrel[{}]'.format(kw))
                    threads.append(process)
                    process.start()
            kw_cnt = len(self.keywords)
            short_kw = need_cnt - kw_cnt
            if short_kw > 0:
                self._get_rel_words()
                for kw in self.rel_words[:short_kw]:
                    process = threading.Thread(target = self.ss_log_sender, args=(kw, q, person, 400), name='Sender-SSrel[{}]'.format(kw))
                    threads.append(process)
                    process.start()
            # if 'LOG' in tools:
            #     process = threading.Thread(target = self.tweet_log_sender, args=(q, UserList, BlackList, 20), name='Sender-Twlog')
            #     threads.append(process)
            #     process.start()
            for thread in threads:
                if thread.is_alive():
                    thread.join()
            #Receiver
            ans  = self.receiver(q, min_similarity = min_similarity)
            if not ans:
                if 'MC' in tools:
                    trigram_markov_chain_instance = TrigramMarkovChain(character)
                    ans = trigram_markov_chain_instance.generate(word = self.keywords.pop(), is_randomize_metasentence = is_randomize_metasentence)
                    if not ans:
                        ans = trigram_markov_chain_instance.generate(word = '', is_randomize_metasentence = is_randomize_metasentence)
            if not ans:
                raise
        except StopIteration as e:
            pass
        except Exception as e:
            _.log_err(is_print = True, is_logging = True)
            ans = operate_sql.get_phrase(status = 'あいづち', character = character)
            if '...:[' in ans:
                ans = operate_sql.get_phrase(status = 'あいづち')
            if '...:[' in ans:
                ans = ''
        finally:
            ans = self.adjust_ans(ans)
            return ans

    def receiver(self, q, min_similarity = 0, laplace = 0.02):
        d_ls = []
        if q:
            d_ls = [(self.tfidf.calc_cosine_similarity(s1 = self.cleaned_s, s2 = msg[0]), msg[1]) for msg in q]
        if d_ls:
            sorted_d_ls = sorted(d_ls, key = lambda x: x[0], reverse = True)
            if not sorted_d_ls:
                return ''
            sorted_d_ls = [(sim+laplace, s) for sim, s in sorted_d_ls if sim >= min_similarity]
            if not sorted_d_ls:
                return ''
            sorted_d_ls = _.f7(sorted_d_ls)
            texts = np.array([x[1] for x in sorted_d_ls])
            tf_idf = np.array([float(x[0]) for x in sorted_d_ls])
            per = np.sum(tf_idf)
            rand_p = tf_idf / per
            ans = np.random.choice(texts, 1, replace = False, p = rand_p)[0]
            return ans

class Converter(MyObject):
    def __init__(self):
        self.MA = natural_language_processing.MorphologicalAnalysis()
        self.hira2kata = natural_language_processing.zj
    def large_to_small(self, s):
            if not s:
                end = ''
            else:
                end = s[-1]
            if end in {'あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ', 'が', 'ざ', 'だ', 'ば', 'ぱ', 'ア', 'カ', 'サ', 'タ', 'ナ', 'ハ', 'マ', 'ヤ', 'ラ', 'ワ', 'ガ', 'ザ', 'ダ', 'バ', 'パ'}:
                small = 'ぁ'
            elif end in {'い', 'き', 'し', 'ち', 'に', 'ひ', 'み', 'り', 'ゐ', 'ぎ', 'じ', 'ぢ', 'び', 'ぴ', 'イ', 'キ', 'シ', 'チ', 'ニ', 'ヒ', 'ミ', 'リ', 'ヰ', 'ギ', 'ジ', 'ヂ', 'ビ', 'ピ'}:
                small = 'ぃ'
            elif end in {'う', 'く', 'す', 'つ', 'ぬ', 'ふ', 'む', 'ゆ', 'る', 'を', 'ん', 'ぐ', 'ず', 'づ', 'ぶ', 'ぷ', 'ウ', 'ク', 'ス', 'ツ', 'ヌ', 'フ', 'ム', 'ユ', 'ル', 'ヲ', 'ン', 'グ', 'ズ', 'ヅ', 'ブ', 'プ'}:
                small = 'ぅ'
            elif end in {'え', 'け', 'せ', 'て', 'ね', 'へ', 'め', 'れ', 'ゑ', 'げ', 'ぜ', 'で', 'べ', 'ぺ', 'エ', 'ケ', 'セ', 'テ', 'ネ', 'ヘ', 'メ', 'レ', 'ヱ', 'ゲ', 'ゼ', 'デ', 'ベ', 'ペ'}:
                small = 'ぇ'
            elif end in {'お', 'こ', 'そ', 'と', 'の', 'ほ', 'も', 'よ', 'ろ', 'ご', 'ぞ', 'ど', 'ぼ', 'ぽ', 'オ', 'コ', 'ソ', 'ト', 'ノ', 'ホ', 'モ', 'ヨ', 'ロ', 'ゴ', 'ゾ', 'ド', 'ボ', 'ポ'}:
                small = 'ぉ'
            else:
                small = ''
            return small
    def aegi(self, s):
        self.mas = self.MA.get_mecab_ls(s)
        head = ['ぁあ…っ！', 'んっ..', 'あはっ...//...'] + ['']*5
        ans = np.random.choice(head)
        for ma in self.mas:
            if ma[1] in {'記号'}:
                continue
            # elif ma[1] in {'動詞'}:

            elif ma[1] in {'名詞'} and ma[2] in {'一般','自立', '固有名詞'} and ma[8] != '*':
                if np.random.rand() > 0.5:
                    connect = np.random.choice(['、', '...', 'っ'])
                    ans += ''.join([self.hira2kata(ma[8][0]), connect])
            ans += ma[0]
            if np.random.rand() > 0.5:
                komoji = self.large_to_small(ma[8])
                if not komoji:
                    komoji = 'っ'
            else:
                komoji = ''
            if komoji:
                komoji += np.random.choice(['...', '...', '......' , '', '♡', '♡', '♡', '♡', 'っ'])
            add = ['...んっ...', '......'] + [komoji]*2 + ['…']*4+ ['']*2
            ans += np.random.choice(add)
        last = ['...//', '...♡', '']
        ans += np.random.choice(last)
        ans = ans.replace('っっ', 'っ').replace('ぃっ', '')
        return ans
Conv = Converter()


def constract_nlp(text = '', dialog_obj = None):
    # if dialog_obj is None:
    #     text_without_tag = re.sub(r'(#[^\s　]+)', '', text)
    #     text_without_tag_url = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', text_without_tag)
    #     dialog_obj = DialogObject(text_without_tag_url)
    nlp_summary = dialog_obj.nlp_data.summary
    cmds = dialog_obj.nlp_data.cmds
    action = ''
    target = ''
    is_accepted = False
    if cmds:
        cmd = cmds[0]
        action = cmd['func']
        target = cmd['var']
        mod = cmd['mod']
        if mod == 'all':
            action += '.all'
    if action and target:
        pass
    elif nlp_summary.has_function('疑問(疑問(what))'):
        action = 'search'
    elif nlp_summary.value in {'検索する', '調べる'}:
        action = 'search'
    elif '#とは' in text:
        action = 'search'
    elif nlp_summary.value in {'呼ぶ','よぶ', '呼び出す','よびだす', '呼び出しする', '出す'}:
        action = 'call'
    elif nlp_summary.value in {'作る', 'つくる', '作成する'}:
        if nlp_summary.akkusativ in {'QR'}:
            action = 'make.QR'
    elif nlp_summary.value in {'覚える', '記憶する', '学習する', 'おぼえる'}:
        action = 'learn'
    elif nlp_summary.value in {'勧誘する'}:
        action = 'gacha'
    elif nlp_summary.value in {'やる', 'する'}:
        if nlp_summary.akkusativ == '診断メーカー':
                action = 'shindanmaker'
    elif nlp_summary.value in {'送る','送れる', '送信する'}:
        if nlp_summary.akkusativ in {'kusoripu', 'クソリプ'}:
            action = 'kusoripu'
        else:
            action = 'send?'
    elif nlp_summary.value in {'クソリプ送信する', 'kusoripu送信する','爆撃する'}:
        if nlp_summary.has_function('希望', '要望'):
            action = 'kusoripu'
            target = nlp_summary.dativ.replace('@', '')
    elif nlp_summary.value in {'変更','変更する', '変える', '切り替える', 'チェンジする'}:
        if nlp_summary.akkusativ in {'名前', 'ネーム', 'スクリーンネーム', 'name'}:
                action = 'change.name'
        elif nlp_summary.akkusativ in {'アイコン', 'iKON', '写真', '顔写真', 'icon'}:
                action = 'change.icon'
        elif nlp_summary.akkusativ in {'背景', 'バナー', 'banner'}:
                action = 'change.banner'
    elif nlp_summary.value in {'戻る','もどる', 'なおる', '直る'}:
        if nlp_summary.dativ in {'デフォルト', '元', '元通り'}:
            action = 'default'
    elif nlp_summary.value in {'まねる','真似る', 'まねする', '真似する', 'ものまねする', 'モノマネする', '擬態する', '変身して', 'メタモルフォーゼする'}:
        action = 'imitate'
        target = nlp_summary.akkusativ.replace('@', '')
        if not target:
            target = nlp_summary.dativ.replace('@', '')
    elif nlp_summary.value in {'遊ぶ'}:
        if nlp_summary.has_function('希望', '要望', '勧誘'):
            if np.random.rand() > 0.2:
                action = 'srtr'
            else:
                action = 'battle_game'
    elif nlp_summary.dativ in {'尻取り'}:
        action = 'srtr'
    elif nlp_summary.value in {'尻取りする', '頭取りする', '頭とりする'}:
        action = 'srtr'
    elif nlp_summary.value in {'戦う', '対戦する', '倒す', 'バトルする',  'たたかう', '争う'}:
        if nlp_summary.has_function('希望', '要望', '勧誘'):
            action = 'battle_game'
    elif nlp_summary.value in {'教える', '伝える'}:
        if nlp_summary.akkusativ in {'トレンド', '流行語'}:
            action = 'tell_trendword'
        elif nlp_summary.akkusativ in {'経験値', 'exp', 'EXP', 'Exp'}:
            action = 'tell_exp'
        else:
            action = 'tell?'
    elif nlp_summary.value in {'分析する', '感情分析する'}:
        action = 'sentimental_analysis'
    elif nlp_summary.value in {'御籤する', '占う'}:
        action = 'omikuji'
    elif nlp_summary.value in {'フォロバする'}:
        action = 'followback'
    elif nlp_summary.value in {'起きる', '起こす'}:
        action = 'wake'
    elif nlp_summary.value in {'喘ぐ', 'あえぐ', '逝く', '乱れる', 'みだれる', '悶えて', 'もだえて', 'エッチする', '破廉恥する', 'ハレンチする'}:
        action = 'harenchi'
    elif nlp_summary.value in {'なる'}:
        if nlp_summary.dativ in {'エッチ', '破廉恥', '変態さん', 'はれんち', '変態', '淫乱', '卑猥'}:
            action = 'harenchi'
    if action:
        if nlp_summary.has_function('命令'):
            if np.random.rand() > 0.2:
                action = 'reject'
    return action, target


if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # text = '''@you に‎kusoripu送信して''' 
    text = '''klapto @aa 13分'''   # text = 'したい'
    # trigram_markov_chain_instance = TrigramMarkovChain('海未')
    # ans = trigram_markov_chain_instance.generate(text)
    # p(ans)
    obj = DialogObject(text)
    p(obj.nlp_data)
    # a = constract_nlp(text, obj)
    # p(a)

    # p('オリジナル: ', text)
    # for i in range(10):
    #     p('ちゃんあの喘ぎtake' + str(i), Conv.aegi(text))
    # trigram_markov_chain_instance = TrigramMarkovChain(character)
    # # while True:
    # ans = trigram_markov_chain_instance.generate(word = '日本', is_randomize_metasentence = True)
    # p(ans)
        # time.sleep(0.1)
    # person = '海未'
    # while True:
    #     d_obj = DialogObject(text)
    #     ansu = d_obj.dialog(context = '', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = [], BlackList = [], min_similarity = 0.1, character = person, tools = 'SS', username = '@〜〜')
    #     p(person, ansu)
    #     break

        # d_obj = DialogObject(ansu)
        # ansh = d_obj.dialog(context = '', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = [], BlackList = [], min_similarity = 0.1, character = '穂乃果', tools = 'SSMC', username = '@〜〜')
        # p('穂乃果「', ansh)
        # time.sleep(3)
    # keygen = d_obj.keywords_gen()
    # for key in keygen:
    #     p(key)s

    # db.create_tables([TFIDFModel], True)
    # s_ls = operate_sql.get_twlog_list(n = 100000, UserList = [], contains = '')
    # TFIDF.learn_tf_idf(s_ls)
