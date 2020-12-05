import qgis
from qgis.core import *
# from PyQt4.QtGui import *
# from PyQt4.QtCore import *

def add_feature(_v, _pr, feature):
	convexhull = feature.geometry().convexHull()
	f = QgsFeature()
	f.setGeometry(convexhull)
	f.setAttributes(['1'])
	_pr.addFeature(f)
	_v.updateExtents()
	_v.commitChanges()
	QgsProject.instance().addMapLayer(_v)
	return _v, _pr


def add_polygon_to_layer(_attr, _coords, _layer, _pr):
	f = QgsFeature()
	_coords = [QgsPointXY(x[0], x[1]) for x in _coords]
	polygon = QgsGeometry.fromPolygonXY([_coords])
	f.setGeometry(polygon)
	f.setAttributes(_attr)
	_pr.addFeature(f)
	_layer.updateExtents()

def find_feature(center_point, _layer, categories=[]):
	for feature in _layer.getFeatures():
		# takes 0.09 sec, 0.22 worst case
		if feature.geometry().contains(
				QgsPointXY(center_point[0], center_point[1])):
			if feature.attributes()[3] in categories:
				return feature

def find_features_poly(feat, _layer):
	_total = 0
	for _feature in _layer.getFeatures():
		if feat.geometry().contains(_feature.geometry()):
			_total += _feature.geometry().area()
	return _total

def get_feature_color(_layer, _feature):
	for cat in _layer[0].renderer().categories():
		if cat.value() == _feature.attributes()[3]:
			print(cat.symbol().color())
			return cat.symbol()

def one_feature_layer(feature):
	_v, _pr = make_new_layer()
	_f = feature
	# f.setGeometry(feature.geometry())
	_v, _pr = add_feature(_v, _pr, _f)
	return _v

def pan(canvas, x, y):
	currExt = canvas.extent()
	canvasCenter = currExt.center()
	dx = x
	dy = y

	xMin = currExt.xMinimum() + dx
	xMax = currExt.xMaximum() + dx

	yMin = currExt.yMinimum() + dy
	yMax = currExt.yMaximum() + dy

	newRect = QgsRectangle(xMin, yMin, xMax, yMax)
	canvas.setExtent(newRect)
	canvas.refresh()



def square_to_coord(square):
	"""
	Function that transforms a bounding box in a list of coordinates.
	:param square: bounding box as consequent points, list
	:return: list of coordinates, list
	"""
	_coords = [(square[0], square[1]),
	           (square[0], square[3]),
	           (square[2], square[3]),
	           (square[2], square[1]),
	           (square[0], square[1])]
	return _coords

