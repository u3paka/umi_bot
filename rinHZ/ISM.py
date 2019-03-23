#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import numpy as np
##______________________
## ISM法 //
## 悩み相談をしながら、構造化モデリングで悪構造問題を良構造に変換し、アドバイスを行う。
def p(text, mode):
	if mode:
		print(text)

def f7(seq): ##高速化ver
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def autoprdBoolenMatrix(matrix):
	products = matrix.dot(matrix)
	# boolean
	products[products > 1] =1
	if products.all() != matrix.all():
		autoproductMatrix(matrix)
	else:
		return products

def npwhere(arr):
	ret = []
	where = np.where(arr)
	whereList = where[0].tolist()
	ret.append(whereList)
	return ret[0]

def calcRcapA(R,A,S):
	RcapA = []
	for Si in range(S):
		Ri = R[Si]
		Ai = A[Si]
		# if Ri != []:
		RiAi = [aRi for aRi in Ri if aRi in Ai]
		RcapA.append(RiAi)
	return RcapA

def listnest2alist(List):
	ans = []
	for factor in List:
		for afact in factor:
			ans.append(afact)
	return ans

# a = listnest2alist([[1]])
# print(a)
def identifyLevelElements(R,A,Structure, pcmd):
	# dirtyCode... リスト内包表記で要修正
	p('~~~~~~~~~~~~~~~~~~~~~~~~~~~', pcmd)
	S = len(R)
	strS = str(S)
	Level = []
	StructureN = []
	RcapA = calcRcapA(R,A,S)
	p('RcapA',pcmd)
	p(RcapA, pcmd)
	for i in range(S):
		Ri = R[i]
		RiAi = RcapA[i]
		if RiAi == Ri:
			Level.append(Ri)
			if Ri != []:
				StructureN.append(i)
		# try:
	altR = []
	p('Level', pcmd)
	Level = [level for level in Level if level != []]
	p(Level, pcmd)
	p('StructureN', pcmd)
	p(StructureN, pcmd)
	avoidLevel = listnest2alist(Level)

	# check discrete or not
	if(len(Level) != 1):
		p('parallel cause-effect... ', pcmd)
		Sconnect = []
		for level in Level:
			if len(level) > 1:
				p(str(level) + ' Not Discrete,  Strongly connected...', pcmd)
				Sconnect.append(level)

		# print(Sconnect)
	for i in range(S):
		Ri = R[i]
		altRi = [r for r in Ri if r not in avoidLevel]
		altR.append(altRi)

	p('altR', pcmd)
	p(altR,pcmd)
	Structure.append(StructureN)
	Structure = [Structure for Structure in Structure if Structure != [] ]
	p('whole_Structure', pcmd)
	p(Structure, pcmd)
	StrProgress = len(listnest2alist(Structure))
	return altR, Structure, StrProgress

def ILEloop(R,A,Structure, pcmd):
	cnt = 1
	altR, Structure, StrProgress = identifyLevelElements(R,A,Structure, pcmd)
	S = len(altR)
	strS = str(S)
	while(StrProgress < S):
		if cnt > 50:
			p('error cnt over', pcmd)
			return Structure.append('ERR')
		else:
			p('continue... progress >> ' + str(StrProgress) + '/' + strS + ' cnt' + str(cnt), pcmd	)
			cnt += 1
			altR, Structure, StrProgress = identifyLevelElements(altR,A,Structure, pcmd)
	# else:
	p('Finished !! ' + str(StrProgress) + '/' + strS, pcmd)
	return Structure

def splitfunc(chunk):
	return chunk.split('\n')

from itertools import chain

def simplifyC(text = 'S1→S5\nS2→S1\nS2→S3\nS2→S4\nS3→S5\nS3→S4\nS4→S3\nS6→S2\nS6→S5', arrow = '→', mode = 'simple'):
	pcmd = False
	if(mode == 'detail'):
		pcmd = True
	chunk = text.split('\n')
	pairs = [arg.split(arrow) for arg in chunk]
	words = list(chain.from_iterable(pairs))
	# print(words)
	factors = f7(words)
	factorscnt = len(factors)
	p('抽出された要素は以下の通りです。', pcmd)
	p(factors, pcmd)
	z = np.zeros((factorscnt,factorscnt))
	I = np.identity(factorscnt)
	
	causels = [pair[0] for pair in pairs]
	effectls = [pair[1] for pair in pairs]
	causeN = [factors.index(cause) for cause in causels]
	effectN = [factors.index(effect) for effect in effectls]
	z[causeN, effectN] = 1
	AdjacencyMatrix = z
	ReachAbilityMatrix = AdjacencyMatrix + I
	# Identifying process of the 1st level lements
	R = []
	A = []
	p('boolean演算を実行します。', pcmd)
	RAM = autoprdBoolenMatrix(ReachAbilityMatrix)
	p('boolにおいて(A+I)^r = (A+I)^(r+1) /= A+I \nとなる可到達行列は以下のとおりです。', pcmd)
	p(RAM, pcmd)
	for Si in range(factorscnt):
		Ai = RAM[:,Si]
		Ri = RAM[Si]
		A.append(npwhere(Ai))
		R.append(npwhere(Ri))

	p('行列から抽出した集合は以下のとおりです。', pcmd)
	p('A', pcmd)
	p(A, pcmd)
	p('R', pcmd)
	p(R, pcmd)
	Structure = []
	Level = []
	Structure = ILEloop(R, A, Structure, pcmd)
	
	p(Structure, pcmd)
	StructureName = []
	p('++++Result Structure each name is mapped like this !!++++', pcmd)
	print('######EFFECT######')
	for level in Structure: 
		levelName = []
		for num in level: 
			levelName.append(factors[num])
		print('↑↑↑↑↑↑↑')
		for name in levelName:
			print(name)
		StructureName.append(levelName)
	print('######CAUSE######')
	return StructureName, Structure

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		text = argvs[1]
		p2 = argvs[2]
		mode = 'simple'
	except:
		text = 'S1→S5\nS2→S1\nS2→S3\nS2→S4\nS3→S5\nS3→S4\nS4→S3\nS6→S2\nS6→S5'
		p2 = 'ISM.detail()'
		mode = 'simple'
	if text == 'demo':
		text = 'S1→S5\nS2→S1\nS2→S3\nS2→S4\nS3→S5\nS3→S4\nS4→S3\nS6→S2\nS6→S5'
	if p2 == 'ISM.detail()':
		mode = 'detail'
	arrow = '→'
	StructureName, Structure = simplifyC(text, arrow, mode)













