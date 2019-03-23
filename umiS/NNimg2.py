#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import openCVmod
NUM_CLASSES = 11
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3

def convData(DIR = "_imgswork"):
	imgdics = utiltools.getDeepPathDic(DIR)
	print(imgdics)
	train_label = [label for address, label in imgdics]
	train_image = [convIMG(address, DIR) for address, label in imgdics]
	train_image = np.asarray(train_image)
	train_label = np.asarray(train_label)
	return train_image, train_label

def convIMG(address, DIR = "_imgswork"):
	imgaddress = DIR+address
	print(imgaddress)
	recogresult = openCVmod.FaceRecognition(imgaddress, isShow = False, saveStyle = '', workDIR = 'work', through = True)
	img = recogresult[0]
	img = openCVmod.adjustIMG(img, K = 0, isHC = True, size = (28, 28))
	return img.flatten().astype(np.float32)/255.0
# convIMG('CV_FACE_icon0_LL1-01_20160212003336.png', '/Users/xxxx')
def convLabel(label):
    tmp = np.zeros(NUM_CLASSES)
    print(tmp)
    tmp[int(label)-1] = 1
    return tmp

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
	print('trainingLABELs... paste it to the predictFunc!!\n', [clsdir for clsdir in os.listdir(DIR) if not clsdir in {'.DS_Store', 'except'}])
	images, labels = convData(DIR)
	data_train, data_test, label_train, label_test = cross_validation.train_test_split(images, labels, test_size=0.2, random_state=38)
	print(label_train)
	classifier = skflow.TensorFlowEstimator(
	    model_fn = CNNmodel, n_classes=NUM_CLASSES, batch_size=10, steps=1000,
	    learning_rate=1e-4, optimizer='Adam', continue_training=True)
	# classifier = skflow.TensorFlowDNNClassifier(hidden_units=[10, 20, 10],
 #                                            n_classes=NUM_CLASSES, steps=1000,
 #                                            early_stopping_rounds=200)
	while True:
		classifier.fit(data_train, label_train, logdir=logdir)
		score = metrics.accuracy_score(label_test, classifier.predict(data_test))
		print('Accuracy: {0:f}'.format(score))
		classifier.save(saveDIR)

 # ['chino', 'eri', 'hanayo', 'honoka', 'kotori', 'maki', 'niko', 'nozomi', 'rin', 'umi']
 # ['others', 'ことり', 'にこ', 'チノ', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽', '雪穂']
def predictAns(filename  = "", isShow = True, model = '', workDIR = '', label =['ことり', 'にこ', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽']):
	classifier = skflow.TensorFlowEstimator.restore(model)
	
	img, altfilename, frame, FACEflag = openCVmod.FaceRecognition(filename, isShow = isShow, saveStyle = 'whole', workDIR = '')
	img = openCVmod.adjustIMG(img, isHC = True, K = 0, size = (28, 28))
	result = classifier.predict(img)
	print(result)
	anslabel = label[result]
	return anslabel, FACEflag, altfilename

