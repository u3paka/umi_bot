#!/usr/bin/env python
# -*- coding: utf-8 -*-
##______________________
## MeCabによる形態素解析 //
# import MeCab
import subprocess
import re
from itertools import chain

def Kaomoji(s):
    text = '[0-9A-Za-zぁ-ヶ一-龠]';
    non_text = '[^0-9A-Za-zぁ-ヶ一-龠]';
    allow_text = '[ovっつ゜ニノ三二]';
    hw_kana = '[ｦ-ﾟ]';
    open_branket = '[\(∩꒰（]';
    close_branket = '[\)∩꒱）]';
    arround_face = '(?:' + non_text + '|' + allow_text + ')*';
    face = '(?!(?:' + text + '|' + hw_kana + '){3,}).{3,}';
    face_char = re.compile(arround_face + open_branket + face + close_branket + arround_face);
    facelist = face_char.findall(s)
    cleaned = re.sub(face_char, '(^ ^)' , s)
    return cleaned, facelist

def specialWord(s):
    spe_char = re.compile('\[{.+?}\]');
    spelist = spe_char.findall(s)
    cleaned = re.sub(spe_char, '<SPE>' , s)
    return cleaned, [s.replace('[{', '').replace('}]', '') for s in spelist]
# print(specialWord('あいうえお[{あ}]'))
class MorphologicalAnalysis:#MeCab
    #OLD
    def get_morpho(self,sentence):
        text = MeCab.Tagger("-Owakati")
        node = text.parse(sentence)
        result = node.rstrip("\n").split(" ")
        return result
    def get_genkei2(self, sentence,Debug=False):
        print("Please up to date get_katakana() to getMeCab()")
        return self.getMeCab(sentence=sentence,mode="-g",form="動詞,名詞,副詞,形容詞",exception="",returnstyle="tuple",Debug=Debug)
    def get_katakana(self, sentence,Debug=False):
        print("Please up to date get_katakana() to getMeCab()")
        return self.getMeCab(sentence=sentence,mode="-k",form="",exception="",returnstyle="tuple",Debug=Debug)
    def get_noun(self, sentence):
        print("Please up to date get_noun() to getMeCab()")
        return self.getMeCab(sentence=sentence,mode="",form="",exception="",returnstyle="tuple",Debug=Debug)

    def cmdMeCab(self, s):
        try:
            MECAB = '/usr/local/bin/mecab'
            DIC = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
            s = s.replace('\n','').replace('(','').replace(')','')
            cmd= 'echo %s | %s -d %s'%(s, MECAB, DIC)
            p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_data, stderr_data = p.communicate()
            ret = stdout_data
            ret = ret.decode('utf-8')
            ret = ret.replace('\t',',')
            ret = ret.split('\n')
            return ret
        except:
            return ''
    def splitMeCab(self, info):
        ma = info.split(',')
        length = len(ma)
        if length != 10:
            for x in range(10 - length):
                ma.append('*')
        if ma[7] == '*':
            ma[7] = ma[0]
        return ma

    def getMeCabList(self, s):
        sentence = s.replace('&amp', '&').replace('&gt', '>').replace('&lt', '<')
        spe = []
        if '[{' in sentence:
            sentence, spe = specialWord(sentence)
        cleanedS, Face = Kaomoji(sentence)
        if spe != []:
            clList = cleanedS.split('<SPE>')
            info_of_words = [self.cmdMeCab(s) for s in clList if not s in ['EOS', '']]
            maList = [[self.splitMeCab(info) for info in infox if not info in ['EOS', '']] for infox in info_of_words]
            if clList[0] != '':
                specnt = len(spe)
                maList = [maList[i] + [[spe[i], '名詞', '特別', '*', '*', '*', '*', spe[i], '*', '*']] for i in range(specnt)] + [maList[specnt]]
            else:
                maList = [[[spe[i], '名詞', '特別', '*', '*', '*', '*', spe[i], '*', '*']] + maList[i] for i in range(len(spe))]
            maList = list(chain.from_iterable(maList))
        else:
            infos = self.cmdMeCab(cleanedS)
            maList = [self.splitMeCab(info) for info in infos if not info in ['EOS', '']]
        if Face != []:
            Face0 =  Face[0]
            Kao =  [Face0, '顔文字', '顔文字', '*', '*', '*', '*', Face0, 'カオ', 'カオ']
            maList = [ma if not ma[0] == '^ ^' else Kao for ma in maList]
        return maList

    def couple(self, i, ma, cpTG = ['助詞', '記号', '助動詞'], ismaskON = 1):
        try:
            ma1 = ma[i]
            ma0 = ma[i-1]
            ma2 = ma[i+1]
            ma11 = ma1[1]
            ma12 = ma1[2]
            ma13 = ma1[3]
            ma01 = ma0[1]
            ma02 = ma0[2]
            ma22 = ma2[2]
            macnt = len(ma)
            if i != 0 and ma01 == ma11 in cpTG or ma22 == '接尾' or ma13 == ma2[3] in ['人名']:
                return
            elif 'CP' in ma02:
                ## 再考の余地あり...
                return
            elif ma11 == ma2[1] in cpTG:
                n = 0
                cp = []
                while(True):
                    cp.append(ma[i+n][0])
                    n += 1
                    if ma[i][1] != ma[i+n][1]:
                        break
                ma[i][0] = ''.join(cp)
                if ma11 in ['助動詞', '記号']:
                    info = ma11
                else:
                    info = ma[i+n-1][2]
                ma[i][1] = info
                ma[i][2] = 'CP' + info
                return ma[i]
            elif ma11 == '助詞':
                if ma11 in ma12:
                    ma[i][1] = ma[i][2]
                return ma[i]
            elif ma12 == '接尾':
                if ismaskON:
                    if ma0[3] == '人名':
                        ma00 = '<人名>'
                    elif ma0[2] == '数':
                        ma00 = '<数>'
                    else:
                        ma00 = ma0[0]
                else:
                    ma00 = ma[0]
                w = ma00 + ma[i][0]
                ma[i][0] = w
                ma[i][7] = w
                return ma[i]
            elif ismaskON:
                word = ma1[0]
                if ma12 == '固有名詞':
                    if ma13 == '人名':
                        ma[i][0] = '<' + ma13 + '>'
                        ma[i][1] = ma12
                        return ma[i]
                    return ma[i]
                elif ma12 == '数':
                    ma[i][0] = '<数>'
                    return ma[i]
                else:
                    return ma[i]
            else:
                return ma[i]
        except Exception as e:
            return ma[i]

    def getMeCabCP(self, s):
        if s == '':
            return []
        if not s[-1] in ['。.！! ？?']:
            s+='。'
        ma = self.getMeCabList(s)
        cntMA = len(ma)
        mas = [ma for ma in [self.couple(i, ma) for i in range(cntMA)] if ma != None]
        return mas

    #Main
    def getMeCab(self, sentence, mode = 7, form = ['名詞'], exception = ["記号"], isDebug = False):
        def isExcepted(w, form, exception):
            if True in [w[i] in exception for i in range(8)] or w[0] == '*':
                return False
            elif w[1] in form:
                return True
            else:
                return False
        try:
            #原文のscreening
            sentence = sentence.replace("\u3000","").replace("\t",",")
            #MeCabモジュールなしで。
            # info_of_words = self.cmdMeCab(sentence)
            ma = self.getMeCabList(sentence)
            if isDebug:
                print("[Debug] mode:")
                print(words)
            return [w[mode] for w in ma if isExcepted(w, form = form, exception = exception)]
        except:
            return ''

    def split2List(self, s, parser = ','):
        if parser in s:
            sList = s.split(parser)
        else:
            sList = [s]
        return sList

    def changeStyle(self, words, style = 'tuple'):
        if style=="tuple":
            return tuple(words)
        elif style=="list":
            return words
        else: return("Error:return style")

    def removeEmpty(self, list):
        while (True):
            try:
                list.remove("")
            except:
                break
        return list

MA = MorphologicalAnalysis()

## ______________________
## CaboChaによる構文解析 //
# import CaboCha
# class SyntacticAnalysis:#CaboCha
#     def getWords(self,tree, chunk):
#         surface=""
#         for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size):
#             token = tree.token(i)
#             features = token.feature.split(',')
#             if features[0] == '名詞':
#                 surface += token.surface
#             elif features[0] == '形容詞':
#                 surface += features[6]
#                 break
#             elif features[0] == '動詞':
#                 surface += features[6]
#                 break
#         return surface

#     def getTree(self,sentence):
#         c=CaboCha.Parser()
#         tree=c.parse(sentence)
#         print(tree.toString(CaboCha.FORMAT_TREE))

#     def cmdCaboCha(self, s):
#         command= 'echo %s | cabocha'%(s)
#         ret = subprocess.check_output(command, shell=True)
#         ret = ret.decode('utf-8')
#         ret = ret.replace('\t',',')
#         ret = ret.split('\n')
#         return ret

#     def getRelation(self,line):
#         cp = CaboCha.Parser('-form')
#         tree = cp.parse(line)
#         chunk_dic = {}
#         chunk_id = 0
#         for i in range(0, tree.size()):
#             token = tree.token(i)
#             if token.chunk:
#                 chunk_dic[chunk_id] = token.chunk
#                 chunk_id += 1
#         tuples = []
#         for chunk_id, chunk in chunk_dic.items():
#             if chunk.link > 0:
#                 from_surface =  self.getWords(tree, chunk)
#                 to_chunk = chunk_dic[chunk.link]
#                 to_surface = self.getWords(tree, to_chunk)
#                 tuples.append((from_surface, to_surface))
#         return tuples

#     def showPairs(self,sentence):
#         SyA_tuples=self.getTuples(sentence)
#         for t in  SyA_tuples:
#             print(t[0] + ' => ' + t[1])

#     def getTuples(self,sentence):
#         tuples=self.getRelation(sentence)
#         return tuples
# SyA=SyntacticAnalysis()

# ##______________________
# ## npjadicによる感情分析 //
# import npjadic
# class SentimentAnalysis:
#     def makeDic(self):
#         dic=npjadic.dic
#         dic=dic.replace("\n",":")
#         nplist=dic.split(':')
#         i=0
#         wordslist=[]
#         valuelist=[]
#         for i in range(len(nplist)):
#             if i%4==1:
#                 wordslist.append(nplist[i])
#             if i%4==2:
#                 wordslist.append(nplist[i])
#             if i%4==0:
#                 valuelist.append(nplist[i])
#                 valuelist.append(nplist[i])
#         NPdic=dict(zip(wordslist,valuelist))
#         return NPdic

#     def getNPscore(self,text,Debug=False):
#         # print(NPdic[0])
#         NPdic=self.makeDic()
#         word=MA.getMeCab(sentence=text,mode="-g",form="動詞,名詞,形容詞,副詞"  ,exception="",returnstyle="tuple",Debug=True)
#         #exception="非自立,助詞類接続,サ変・スル"
#         if Debug==True:
#             print(word)
#         i=0
#         sumscore=0
#         for i in range(len(word)):
#             if word[i] in NPdic:
#                 score=NPdic[word[i]]
#                 if Debug==True:
#                     print(word[i]+":"+score)
#                 sumscore+=round(float(score),8)
#                 sumscore=round(sumscore,8)
#             i+=1
#         ansscore=round(sumscore,8)
#         if Debug==True:
#             print("NPScore:"+str(ansscore))
#         return(ansscore)
# SeA=SentimentAnalysis()
def nvChain(mas, i):
    if ma11 == ma2[1] in cpTG:
        n = 0
        cp = []
        while(True):
            cp.append(ma[i+n][0])
            n += 1
            if ma[i][1] != ma[i+n][1]:
                break
        ma[i][0] = ''.join(cp)
        if ma11 in ['助動詞', '記号']:
            info = ma11
        else:
            info = ma[i+n-1][2]
        ma[i][1] = info
        ma[i][2] = 'CP' + info
        return ma[i]
if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    s= "私を抜きにしたからといって、彼女としては23日映画館わかってるんやけれど英語をみたいのだよね(๑&gt؂•̀๑)ﾃﾍﾍﾟﾛ"
    # s = ''
    nouns = MA.getMeCabList(s)
    # s = ('できたにゃ！味付け海苔だにゃ！ご飯のお供には最高だけど絵里ちゃんは海苔が嫌いらしいからあの味を楽しめないのは残念にゃ…', 2)
    # nouns = MA.getMeCab(s, mode = 7, form = ["名詞"])
    print(nouns)


