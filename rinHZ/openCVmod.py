#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *

def LUT_G(gamma = 0.75):
	# ガンマ変換ルックアップテーブル
	LUT_G = np.arange(256, dtype = 'uint8' )
	for i in range(256):
		LUT_G[i] = 255 * pow(float(i) / 255, 1.0 / gamma)
	return LUT_G

def LUT_HC(min_table = 50, max_table = 205):
	# ハイコントラストLUT作成
	diff_table = max_table - min_table
	LUT_HC = np.arange(256, dtype = 'uint8' )
	for i in range(0, min_table):
		LUT_HC[i] = 0
	for i in range(min_table, max_table):
		LUT_HC[i] = 255 * (i - min_table) / diff_table
	for i in range(max_table, 255):
		LUT_HC[i] = 255
	return LUT_HC


def LUT_LC(min_table = 50, max_table = 205):
	# ローコントラストLUT作成
	diff_table = max_table - min_table
	LUT_LC = np.arange(256, dtype = 'uint8' )
	for i in range(256):
		LUT_LC[i] = min_table + i * (diff_table) / 255
	return LUT_LC

def decreaseColorKmeans(img_src, K = 4):
	Z = img_src.reshape((-1,3))
	# float32に変換
	Z = np.float32(Z)
# K-Means法
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	ret, label, center=cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
	# UINT8に変換
	center = np.uint8(center)
	res = center[label.flatten()]
	img_dst = res.reshape((img_src.shape))
	return img_dst


def getAltName(filename, workDIR = '', kind1 = 'CV_', kind2 = '', kind3 = ''):
	filefw = filename.split('/')
	imgname = filefw.pop()
	if workDIR == '':
		altfilename = '/'.join(filefw + [''.join([kind1, kind2, kind3,'_',imgname])]).replace('__','_').replace('//','/')
	else:
		DIR2 = filefw.pop()
		DIR = '/'.join(filefw + [workDIR, DIR2])

		altfilename = DIR +'/'+''.join([kind1, kind2, kind3,'_',imgname]).replace('__','_').replace('//','/')
		if os.path.exists(DIR) == False:
			os.mkdir(DIR)
	return altfilename

def IMGprocess(filename, processes = ['HC', 'LC', 'LG', 'HG', 'BL', 'GN','SPN', 'HF', 'VF', 'HR', 'C64'], isSave = True, isShow = False):
	# ルックアップテーブルの生成
	# 変換
	src = cv2.imread(filename)
	imgs = {}
	if 'HC' in processes:
		imgs['HC'] = cv2.LUT(src, LUT_HC())
	if 'LC' in processes:
		imgs['LC'] = cv2.LUT(src, LUT_LC())
	if 'LG' in processes:
		imgs['LG'] = cv2.LUT(src, LUT_G(0.75))
	if 'HG' in processes:
		imgs['HG'] = cv2.LUT(src, LUT_G(1.5))
	if 'BL' in processes:
		average_square = (10,10)
		imgs['BL'] =  cv2.blur(src, average_square)
	if 'GN' in processes:
		row,col,ch= src.shape
		mean = 0
		sigma = 15
		gauss = np.random.normal(mean,sigma,(row,col,ch))
		gauss = gauss.reshape(row,col,ch)
		imgs['GN'] = src + gauss
	if 'SPN' in processes:
		row,col,ch = src.shape
		s_vs_p = 0.5
		amount = 0.004
		sp_img = src.copy()
		# Saltモード
		num_salt = np.ceil(amount * src.size * s_vs_p)
		coords = [np.random.randint(0, i-1 , int(num_salt)) for i in src.shape]
		sp_img[coords[:-1]] = (255,255,255)
		# Pepperモード
		num_pepper = np.ceil(amount* src.size * (1. - s_vs_p))
		coords = [np.random.randint(0, i-1 , int(num_pepper)) for i in src.shape]
		sp_img[coords[:-1]] = (0,0,0)
		imgs['SPN'] = sp_img
	if 'HF' in processes: #Horizontal Flip
		imgs['HF'] = cv2.flip(src, 1)
	if 'VF' in processes: #Vertical Flip
		imgs['VF'] = cv2.flip(src, 1)
	if 'HR' in processes:
		hight = src.shape[0]
		width = src.shape[1]
		imgs['HR'] = cv2.resize(src,(int(hight/2),int(width/2)))
	if 'C4' in processes:
		imgs['C4'] = decreaseColorKmeans(src, K = 4)
	if 'C16' in processes:
		imgs['C16'] = decreaseColorKmeans(src, K = 16)
	if 'C64' in processes:
		imgs['C64'] = decreaseColorKmeans(src, K = 64)
	if isSave and processes!= []:
		[cv2.imwrite(getAltName(filename, kind1 = 'CV_', kind2 = process + '_', kind3 = ''), imgs[process]) for process in processes]
		print('[IMG_Saved]processed...', processes)
	return imgs

def adjustIMG(img, isHC = True, K = 0, size = (28, 28)):
	if isHC:
		img = cv2.LUT(img, LUT_HC(min_table = 50, max_table = 205))
	if K > 0:
		img = decreaseColorKmeans(img, K = K)
	img = cv2.resize(img, size)
	return img

def FaceRecognition(filename = testpic, isShow = True, saveStyle = 'icon', workDIR = '_imgswork', frameSetting = {'thickness': 2, 'color':(0, 0, 255)}, through = False):
	def faceProcess(faces, i, frameSetting = frameSetting):
		# flag = True
		flag = False
		F = faces[i]
		#(四角の左上のx座標, 四角の左上のy座標, 四角の横の長さ, 四角の縦の長さ)
		Ftop = F[1]
		Fbottom = Ftop + F[3]
		Fleft = F[0]
		Fright = Fleft + F[2]
		if not (Ftop<0 or Fbottom>height or  Fleft<0 or Fright>width):
			thickness = frameSetting['thickness']
			image = frame[Ftop+thickness: Fbottom-thickness, Fleft+thickness:Fright-thickness]
			margin = min((Fbottom-Ftop)/4, Ftop, height-Fbottom, Fleft, width-Fright)
			icon = frame[Ftop-margin:Fbottom+margin, Fleft-margin:Fright+margin]
			# cv2.rectangle(frame, (Fleft, Ftop), (Fright, Fbottom), frameSetting['color'], thickness = thickness)
			if saveStyle != '':
				altfilename = getAltName(filename, workDIR = workDIR, kind1 = 'CV_', kind2 = 'FACE_', kind3 = saveStyle + str(i))
				if saveStyle == 'icon':
					cv2.imwrite(altfilename, image)
				else:
					cv2.rectangle(frame, (Fleft, Ftop), (Fright, Fbottom), frameSetting['color'], thickness = thickness)
					cv2.imwrite(altfilename, frame)
			else:
				altfilename = filename
		else:
			image = frame 
			altfilename = filename
		if isShow:
			cv2.imshow('img',frame)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
		return image, altfilename, frame
	frame = cv2.imread(filename)
	if through:
		return frame, filename, frame, True
	else:
		faceDetectorAnime = cv2.CascadeClassifier(cv2CascadeClassifier)
	grayimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = faceDetectorAnime.detectMultiScale(grayimg, scaleFactor = 1.1, minNeighbors = 5, minSize = (24, 24))
	height, width = grayimg.shape[:2]
	facecnt = len(faces)
	print(filename, str(facecnt))
	if facecnt == 0:
		return frame, filename, frame, False
	else:
		try:
			results = [faceProcess(faces, i) for i in range(facecnt)]
			# maxSIZE
			maxicon = results[0]
			return maxicon[0], maxicon[1], maxicon[2], True
		except Exception as e:
			print(e)
			return frame, filename, frame, False

def preIMGprocess(DIR = "", workDIR = 'face', processes = [], isFaced = True):
	imgdics = utiltools.getDeepPathDic(DIR)
	print(imgdics)
	if isFaced == False:
		[FaceRecognition(filename = DIR+address, isShow = False, saveStyle = 'icon', workDIR = workDIR) for address, label in imgdics]
	workPATH = DIR + workDIR + '/'
	print(workPATH)
	facedics = utiltools.getDeepPathDic(workPATH)
	print(facedics)
	[IMGprocess(filename = workPATH+address, isSave = True, processes = processes) for address, label in facedics]

if __name__ == '__main__':
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	filename = "/Users/xxxx/OneDrive/imgs/learn/others/CV_FACE_icon0_LL1-01_20160212002218.png"
	filename = '/Users/xxxx'
	# img, altfilename, frame, flag = FaceRecognition(filename, isShow = 0, saveStyle = '', workDIR = '')
	# print(img)
	preIMGprocess(DIR = "/Users/xxxx'])
	# IMGprocess(filename, isSave = True)






