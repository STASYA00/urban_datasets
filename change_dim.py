import cv2
import numpy as np
import os

dim = 256

city = 'bologna'
BASE = "D:/Google Drive/edu/#/thesis/test_scale/"  # gan_maps/bologna/
# BASE = "D:/Google Drive/edu/#/thesis/test_set_3000_tallinn/"

path = BASE + 'trainA'
path1 = BASE + 'trainB'
new_path = BASE + 'trainAB'

for img in os.listdir(path1):
	imageA = cv2.imread(path + '/' + img)[237:2357, 117:2237]
	imageB = cv2.imread(path1 + '/' + img)[237:2357, 117:2237]
	imageA = cv2.resize(imageA, (dim, dim), interpolation=cv2.INTER_AREA)
	imageB = cv2.resize(imageB, (dim, dim), interpolation=cv2.INTER_AREA)
	# imageB = np.ones(imageA.shape) * 255
	image = np.concatenate([imageA, imageB], axis=1)

	cv2.imwrite(new_path + '/' + img, image)
