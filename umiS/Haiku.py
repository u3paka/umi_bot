#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import NLP

def Haiku(mas):
    mas = [ma for ma in mas if not ma[0] in set(['、', '。'])]
    origin = [ma[0] for ma in mas]
    metaS = [ma[1] for ma in mas]
    yomi = [ma[8].replace('ャ', '').replace('ュ', '').replace('ョ', '') for ma in mas]
    wlens = [len(w) for w in yomi]
    if not np.sum(wlens) in [17, 18, 19]:
        return ''
    else:
        wlenArr = [np.sum(wlens[0:i+1]) for i in range(len(wlens))]
        if 5 in wlenArr and 12 in wlenArr and 17 in wlenArr:
            index1 = wlenArr.index(5)+1
            index2 = wlenArr.index(12)+1
            comment =  '[5・7・5]'
        # elif 5 in wlenArr and 12 in wlenArr and 18 in wlenArr:
        #     index1 = wlenArr.index(5)+1
        #     index2 = wlenArr.index(12)+1
        #     comment = '[5・7・6]'
        elif 5 in wlenArr and 13 in wlenArr and 18 in wlenArr:
            index1 = wlenArr.index(5)+1
            index2 = wlenArr.index(13)+1
            comment = '[5・8・5]'
        else:
            return ''
        ExSets = set(['助詞', '助動詞', '記号'])
        if mas[index1][1] in ExSets or mas[index2][1] in ExSets:
            return ''
        ExSets2 = set(['非自立', '接尾'])
        if mas[index1][2] in ExSets2 or mas[index2][2] in ExSets2:
            return ''
        return ''.join(['\n',''.join(origin[0:index1]), '\n　', ''.join(origin[index1:index2]), '\n　　', ''.join(origin[index2:]), '...', comment])

if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    s= "私を抜きにしたからといって、彼女としては23日映画館わかってるんやけれど英語をみたいのだよね(๑&gt؂•̀๑)ﾃﾍﾍﾟﾛ"
    s = 'この世をば我が世とぞ思ふ望月のwww'
    # s = 'しかもつだから東京行き...'
    mas = [w for w in NLP.MA.getMeCabList(s) if w[0] != '。']
    ans = Haiku(mas)
    print(ans)