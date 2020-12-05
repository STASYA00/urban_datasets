import json
import numpy as np
import sys
from shapely.geometry import Polygon, Point
from qgis.PyQt.QtCore import QVariant

from time import time

sys.path.append('D:/Google Drive/edu/#/thesis/qgis')
from utils import *

city = 'milan'
BASE_PATH = 'D:/Google Drive/edu/#/thesis/gan_maps/{}_green/'.format(city)
PART = 'A'

samples = 1500
#FIELD = 'CODE2012'
#categories = ['11100', '11210']  # '12100'
interest_layer = QgsProject.instance().mapLayersByName('zone_of_interest_' + city)[0]
for i in interest_layer.getFeatures():
	main_feature = i
	print(main_feature.geometry().area())

target_layer = QgsProject.instance().mapLayersByName('urban_blocks_' + city)[0]
building_layer = QgsProject.instance().mapLayersByName(
	'buildings_' + city)
green_layer = QgsProject.instance().mapLayersByName('green_milan')[0]
green_layer1 = QgsProject.instance().mapLayersByName('green_milan1')[0]
CRS = target_layer.crs()

threshold = 0.2
threshold_q = 8

def find_feature(feature, _layer=building_layer[0]):
	area = 0
	total_features = 0
	for f in _layer.getFeatures():
		# takes 0.09 sec, 0.22 worst case
		if feature.geometry().contains(f.geometry()):
			area += f.geometry().area()
			total_features += 1
	return round(area / feature.geometry().area(), 2), total_features


def make_new_layer(name='temp', type='Polygon', attr=['id'], crs=None):
	_v = QgsVectorLayer(type, name, "memory")
	_v.setCrs(crs)
	pr = _v.dataProvider()
	for _a in attr:
		pr.addAttributes([QgsField(_a, QVariant.String)])
	_v.updateFields()
	set_style(_v)
	return _v, pr

def set_style(_layer, _color=None):
	"""
	Function that sets a style to the given layer
	:param _layer: layer, QgsLayer
	:param _color: color the layer will be rendered with, QColor
	:return:
	"""
	if _color is None:
		_color = QColor("white")
	_layer.renderer().symbol().setColor(_color)

names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]

name = 'buildings_' + city
layer = QgsProject.instance().mapLayersByName(name)
project = QgsProject.instance()
manager = project.layoutManager()
layoutName = 'Layout1'
layouts_list = manager.printLayouts()
# remove any duplicate layouts
for layout in layouts_list:
	if layout.name() == layoutName:
		manager.removeLayout(layout)
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName(layoutName)
manager.addLayout(layout)

# create map item in the layout
map = QgsLayoutItemMap(layout)
map.setRect(20, 20, 20, 20)

# set the map extent
ms = QgsMapSettings()
# for l in layer:
# print(l[0].name())
ms.setLayers(layer)  # set layers to be mapped
rect = QgsRectangle(ms.fullExtent())
rect.scale(0.01)
ms.setExtent(rect)
map.setExtent(rect)
map.setBackgroundColor(QColor(255, 255, 255, 0))
layout.addLayoutItem(map)

map.setExtent(QgsRectangle(0, 0, 0 + rect.width(),
						   0 + rect.height()))
d = {}
n = 0
v, pr = make_new_layer(crs=CRS)

# for category in categories:
# 	print(category)
features = target_layer.getFeatures()  # QgsFeatureRequest(
	# QgsExpression("\"{0}\" = '{1}'".format(FIELD, category)))
for i, feature in enumerate(features):
	if main_feature.geometry().contains(feature.geometry()):
		# if i >= samples:
		# 	break
		density, _quantity = find_feature(feature)
		if density > threshold:
			if _quantity > threshold_q:
				center = [feature.geometry().centroid().asPoint().x(),
						  feature.geometry().centroid().asPoint().y()]
				map.setExtent(QgsRectangle(center[0] - (rect.width() / 2),
										   center[1] - (rect.height() / 2),
										   center[0] + (rect.width() / 2),
										   center[1] + (rect.height() / 2)))
				map.attemptMove(QgsLayoutPoint(10, 20, QgsUnitTypes.LayoutMillimeters))
				map.attemptResize(
					QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))
				map.setScale(3000.0)

				layout = manager.layoutByName(layoutName)
				exporter = QgsLayoutExporter(layout)

				fn = BASE_PATH + 'train{0}/map{1}.png'.format('B', n)
				exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())

				# if PART == 'A':
				v, pr = add_feature(v, pr, feature)
				set_style(v, _color=QColor("white"))
				built_proportion = round(density, 2)
				green_proportion = round(find_feature(feature,_layer=green_layer)[0], 2) + round(find_feature(feature, _layer=green_layer1)[0], 2)

				d['map' + str(n)] = [map.extent().xMinimum(),
									 map.extent().yMinimum(),
									 map.extent().xMaximum(),
									 map.extent().yMaximum(), 0,
									 built_proportion]

				# coords = square_to_coord(d['map' + str(n)])
				# add_polygon_to_layer(['map' + str(n)], coords, vl, pr)

				layout = manager.layoutByName(layoutName)
				exporter = QgsLayoutExporter(layout)

				fn = BASE_PATH + 'train{0}/map{1}.png'.format(PART, n)
				exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())

				n += 1
				try:
					with edit(v):
						listOfIds = [feat.id() for feat in v.getFeatures()]
						v.deleteFeatures(listOfIds)
				# project.removeMapLayer(v.id())
				except AttributeError:
					pass

				if n >= samples:
					break
# QgsProject.instance().removeMapLayer(v.id())

# vl.commitChanges()
# QgsProject.instance().addMapLayer(vl)
# vl.commitChanges()
# set_style(vl)
# if PART == 'A':
with open(BASE_PATH + 'labels_density.json', 'w') as k:
	json.dump(d, k)
