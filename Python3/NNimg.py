#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import cv2
from itertools import chain

import numpy as np
import tensorflow as tf
import tensorflow.python.platform
from sklearn import cross_validation, metrics, preprocessing
import skflow
from sklearn.externals import joblib
import openCVmod
NUM_CLASSES = 12
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3

def convData(DIR = "_imgswork"):
	imgdics = getDeepPathDic(DIR)
	print(imgdics)
	le = preprocessing.LabelEncoder()
	train_label = [label for address, label in imgdics]
	train_image = [convIMG(address, DIR) for address, label in imgdics]
	train_image = np.asarray(train_image)
	train_label = np.asarray(train_label)
	return train_image, train_label
def convIMG(address, DIR = "_imgswork"):
	imgaddress = DIR+address
	print(imgaddress)
	img, altfilename, frame, flag = openCVmod.FaceRecognition(imgaddress, isShow = False, saveStyle = '', workDIR = '')
	img = openCVmod.adjustIMG(img, K = 64, size = (28, 28))
	return img.flatten().astype(np.float32)/255.0
def convLabel(label):
    tmp = np.zeros(NUM_CLASSES)
    print(tmp)
    tmp[int(label)] = 1
    return tmp

def getDeepPathDic(DIR):
	def filebool(jpg):
		if jpg in set(['.DS_Store']):
			return False
		elif '.' in jpg:
			return True
		else:
			return False
	clsdirs = os.listdir(DIR)
	clsdirs = [clsdir for clsdir in clsdirs if not clsdir in set(['.DS_Store'])]
	imgdics = list(chain.from_iterable([[(''.join([clsdirs[i],'/', jpg]), i)  for jpg in os.listdir(DIR + clsdirs[i]) if filebool(jpg)] for i in range(len(clsdirs))]))
	return imgdics

def preIMGprocess(DIR = "", workDIR = '_imgswork', processes = []):
	imgdics = getDeepPathDic(DIR)
	[openCVmod.FaceRecognition(filename = DIR+address, isShow = False, saveStyle = 'icon', workDIR = workDIR) for address, label in imgdics]
	workPATH = DIR + workDIR + '/'
	facedics = getDeepPathDic(workPATH)
	[openCVmod.IMGprocess(filename = workPATH+address, isSave = True, processes = processes) for address, label in facedics]

### Convolutional network
def max_pool_2x2(tensor_in):
    return tf.nn.max_pool(tensor_in, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
        padding='SAME')

def conv_model(X, y, keep_prob = 0.5):
	keep_prob = 0.5
	X = tf.reshape(X, [-1, 28, 28, 3])
	with tf.variable_scope('conv_layer1'):
		h_conv1 = skflow.ops.conv2d(X, n_filters=32, filter_shape=[5, 5], bias=True, activation=tf.nn.relu)
		h_pool1 = max_pool_2x2(h_conv1)
	with tf.variable_scope('conv_layer2'):
	    h_conv2 = skflow.ops.conv2d(h_pool1, n_filters=64, filter_shape=[5, 5],
	                                bias=True, activation=tf.nn.relu)
	    h_pool2 = max_pool_2x2(h_conv2)
	    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
	h_fc1 = skflow.ops.dnn(h_pool2_flat, hidden_units = [1024], activation=tf.nn.relu, keep_prob=keep_prob)
	h_fc1 = tf.nn.dropout(h_fc1, keep_prob)
	return skflow.models.logistic_regression(h_fc1, y, class_weight=None)
def CNNmodel(X, y):
	keep_prob = tf.placeholder(tf.float32)
	return conv_model(X, y, keep_prob = keep_prob)
### Linear classifier.
# classifier = skflow.TensorFlowLinearClassifier(
#     n_classes=NUM_CLASSES, batch_size=100, steps=1000, learning_rate=0.01)
# classifier.fit(data_train, label_train)
# score = metrics.accuracy_score(label_test, classifier.predict(data_test))
# print('Accuracy: {0:f}'.format(score))
def train(DIR = "", saveDIR = "/Users/xxxx'):
	print('trainingLABELs... paste it to predictFunc!!\n', [clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])])
	images, labels = convData(DIR)
	data_train, data_test, label_train, label_test = cross_validation.train_test_split(images, labels)
	classifier = skflow.TensorFlowEstimator(
	    model_fn = CNNmodel, n_classes=NUM_CLASSES, batch_size=10, steps=200,
	    learning_rate=1e-4, optimizer='Adam', continue_training=True)
	while True:
		classifier.fit(data_train, label_train, logdir=logdir)
		score = metrics.accuracy_score(label_test, classifier.predict(data_test))
		print('Accuracy: {0:f}'.format(score))
		classifier.save(saveDIR)
 # ['chino', 'eri', 'hanayo', 'honoka', 'kotori', 'maki', 'niko', 'nozomi', 'rin', 'umi']
def predictAns(filename  = "rin/show.png", isShow = True, model = '/Users/xxxx']):
	classifier = skflow.TensorFlowEstimator.restore(model)
	# imgaddress = "rin/images-10.jpeg"
	# imgaddress = '/Users/xxxx'
	img, altfilename, frame, FACEflag = openCVmod.FaceRecognition(filename, isShow = isShow, saveStyle = 'whole', workDIR = '')
	img = openCVmod.adjustIMG(img, isHC = True, K = 0, size = (28, 28))
	result = classifier.predict(img)
	anslabel = label[result]
	return anslabel, FACEflag, altfilename

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	from itertools import chain
	model = "/Users/xxxx/Dropbox/Project/umiA/Data/ML_Brain/DNN_skf/"
	filename = 'maki/sr-maki-cool-shoki-go.jpg'
	# DIR = 'umi/'

	# preIMGprocess(DIR = "", workDIR ='_imgswork')

	# train(DIR = "_imgswork/", saveDIR = "/Users/xxxx/OneDrive/imgs/DNN_skf")

	# adrs = [DIR+clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])]
	anslabel, FACEflag, altfilename = predictAns(filename  = filename, isShow = 0, model = model)
	print(anslabel, FACEflag, altfilename)







