import argparse
import cv2
import functools
import json
from math import log10
import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import Polygon, Point, MultiPolygon
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
import textwrap

import warnings
warnings.filterwarnings("ignore")


def get_buildings(image, threshold=6):
	image = cv2.erode(image, np.ones((3, 3)), 1)
	c, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	c = [x for x in c if len(x) >= threshold]
	c = [[tuple(x[0]) for x in cont] for cont in c]
	polygons = []
	for cont in c:
		coords = Polygon(cont).centroid.coords[0]
		if image[int(coords[0])][int(coords[1])] > 0:
			polygons.append(Polygon(cont))
	polygons = [p for p in polygons if p.area > 1]
	return polygons


def get_block(result, name):
	threshold = 6
	if name.startswith('tallinn'):
		threshold = 4
	polygons = get_new_buildings(result)

	if name.startswith('bengaluru'):
		block = MultiPolygon(polygons).minimum_rotated_rectangle
	else:
		block = MultiPolygon(polygons).convex_hull
	return polygons, block


def get_mask(result, name):
	polygons, block = get_block(result, name)
	#     if block.geom_type == 'Polygon':
	border = [[[int(x), int(y)]] for x, y in block.exterior.coords]

	dist = [MultiPolygon(polygons).centroid.distance(p.centroid) for p in
			polygons]
	if len(dist) > 1:
		if np.max(dist) > 100:
			polygons.pop(dist.index(np.max(dist)))

	black = np.zeros(result.shape)
	return cv2.drawContours(black, [np.array(border)], -1, 255, -1)

def between_buildings_distance(polygons):
	dist = [MultiPolygon(polygons).centroid.distance(p.centroid) for p in polygons]
	if len(dist) > 1:
		if np.max(dist) > 100:
			polygons.pop(dist.index(np.max(dist)))
	between_dist = []
	for i, p in enumerate(polygons):
		try:
			between_dist.append(np.min([p.exterior.distance(x.exterior) for x in polygons[:i] + polygons[i+1:]]))
		except ValueError:
			pass
	if len(between_dist) > 0:
		return np.mean(between_dist)
	else:
		return 0

def street_distance(result, name):
	polygons, block = get_block(result, name)
	dist = [MultiPolygon(polygons).centroid.distance(p.centroid) for p in polygons]
	if len(dist) > 1:
		if np.max(dist) > 100:
			polygons.pop(dist.index(np.max(dist)))
	return np.min([x.distance(block.exterior) for x in polygons])


def count_density(name, path):
	threshold = 4
	image = cv2.imread("{}/{}".format(path, name), 0)
	imageA = image[:, :int(image.shape[1] / 2)]
	imageB = image[:, int(image.shape[1] / 2):]
	result = imageB - imageA
	kernel = np.ones((3, 3))
	result = cv2.erode(result, kernel, iterations=1)
	mask = get_mask(result, name)
	mask = mask > 0
	out = mask * (imageA - result)
	out = out < 120
	out = mask * out
	out = out > 0
	out = out.astype(np.uint8)
	polygons = get_new_buildings(out)

	area = MultiPolygon(polygons).convex_hull
	return round(np.unique(out, return_counts=True)[1][1] / area.area,
				 3), area, out


def get_new_buildings(image):
#     image = cv2.erode(image, np.ones((3,3)), 1)
	points = np.concatenate([np.where(image > 0)[0].reshape(-1,1), np.where(image > 0)[1].reshape(-1,1)], axis=1)
	clusters = dbscan.fit_predict(points)
	buildings = []
	for c in np.unique(clusters):
		if c > -1:
			black = np.zeros((image.shape[0], image.shape[1], 1))
			for point in points[clusters==c]:
				black[point[0]][point[1]] = 1
			black = black.astype(np.uint8)
			c, _ = cv2.findContours(black, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			if len(c) > 0:
				c = sorted(c, key=cv2.contourArea, reverse=True)
			c = c[0]
			c = [tuple(x[0]) for x in c]
			if len(c) >= 3:
				buildings.append(Polygon(c))
	return buildings


class Metric:
	def __init__(self):
		self.name = 'generic'
		self.scores = []

	def calculate(self, path: str):
		return self._calculate(path)

	def _calculate(self, path: str):
		for name in os.listdir(path):
			try:
				_value = self._get(path, name)
				if _value:
					self.scores.append(_value)
			except Exception:
				pass
		return self.result()

	def _get(self, path: str, name: str):
		return 0

	def result(self):
		print("{}\t{}".format('Mean ' + self.name, round(np.mean(self.scores), 2)))
		print("{}\t{}".format('Median ' + self.name, round(np.median(self.scores), 2)))


class FootprintAreaMetric(Metric):
	def __init__(self):
		Metric.__init__(self)
		self.name = 'footprint_area'

	def _get(self, path: str, name:str):
		if COURTS == 0:
			result = np.mean([x.area for x in get_buildings(
				count_density(name, FOLDER)[2], 4)])
			if result < 1000:
				return result
		else:
			result = np.mean([x.area for x in get_buildings(
				count_density(name, FOLDER)[2], 6)])
			if result < 1000:
				return result


class BuildingDensityMetric(Metric):
	def __init__(self):
		Metric.__init__(self)
		self.name = 'building_density'

	def _get(self, path: str, name: str):
		return count_density(name, path)[0]


class BetweenBuildingDistanceMetric(Metric):
	def __init__(self):
		Metric.__init__(self)
		self.name = 'between_building_distance'

	def _get(self, path: str, name: str):
		image = cv2.imread("{}/{}".format(path, name), 0)
		result = image[:, int(image.shape[1] / 2):] - image[:, :int(image.shape[1] / 2)]
		mask = get_mask(result, name) > 0
		out = mask * result
		out = out > 40
		out = mask * out
		out = out > 0
		out = out.astype(np.uint8)
		n = get_new_buildings(out)[1:]
		return between_buildings_distance(n)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
		USAGE: python metrics.py image_folder

		------------------------------------------------------------------------

		This is an algorithm that calculates the metrics for the images from the
		urban dataset.

		------------------------------------------------------------------------

		'''), epilog=textwrap.dedent('''\
		The algorithm will be updated with the changes made in the strategy.
		'''))

	# parser.add_argument('model', type=str, help='path to the model file with '
	#                                             '.blend extension, str')
	parser.add_argument('folder', type=str, help='path to the image dir',
						default=None)

	############################################################################

	args = parser.parse_args()

	FOLDER = args.folder

	COURTS = 1

	THRESHOLD = 0.5

	############################################################################

	dbscan = DBSCAN(eps=1, min_samples=2)

	for metric in [FootprintAreaMetric, BuildingDensityMetric,
	               BetweenBuildingDistanceMetric]:
		metric().calculate(FOLDER)








