import json
import numpy as np
import sys
from shapely.geometry import Polygon, Point
from qgis.PyQt.QtCore import QVariant

from time import time

# sys.path.append('D:/Google Drive/edu/#/thesis/qgis')
# from utils import *

buildings = ['11100', '11210', '11220', '11230', '12100', '11300', '14200']

test_layer = QgsProject.instance().mapLayersByName('test')[0]
heat_layer = QgsProject.instance().mapLayersByName('urban_heat_milano copy')
landuse_layer = QgsProject.instance().mapLayersByName('landuse')
CRS = heat_layer[0].crs()

n = 0
start = [510626, 5031266]

def add_feature(_v, _pr, f):
    f.setAttributes(['1'])
    _pr.addFeature(f)
    _v.updateExtents()
    _v.commitChanges()
    project.addMapLayer(_v)
    return _v, _pr

def find_feature(center_point, _layer = landuse_layer[0]):
    for feature in _layer.getFeatures():
        # takes 0.09 sec, 0.22 worst case
        if feature.geometry().contains(QgsPointXY(center_point[0],
                                                  center_point[1])):
            # if feature.attributes()[3] in buildings:
            return feature
    
def get_feature_color(_layer, _feature):
    for cat in _layer[0].renderer().categories():
        if cat.value() == _feature.attributes()[3]:
            return cat.symbol()

def set_style(_layer, _color=QColor("white")):
    _layer.renderer().symbol().setColor(_color)

def make_new_layer(name='temp', type='Polygon', attr='id', crs=CRS):
    vl = QgsVectorLayer(type, name, "memory")
    print(name)
    vl.setCrs(crs)
    pr = vl.dataProvider()
    pr.addAttributes([QgsField(attr, QVariant.String)])
    vl.updateFields()
    set_style(vl)
    return vl, pr

# vl, pr = make_new_layer(name='temp')

name = 'A020101_Building_Volumes'
layer = QgsProject.instance().mapLayersByName(name)

project = QgsProject.instance()
manager = project.layoutManager()
layoutName = 'Layout_test'
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
ms = QgsMapSettings()
ms.setLayers(layer)
rect = QgsRectangle(ms.fullExtent())
rect.scale(0.04)
ms.setExtent(rect)
map.setExtent(rect)
map.setBackgroundColor(QColor(255, 255, 255, 0))
layout.addLayoutItem(map)
map.setExtent(QgsRectangle(start[0], start[1],
                           start[0] + rect.width(),
                           start[1] + rect.height()))

v, pr = make_new_layer()

for feature in test_layer.getFeatures():
	n = feature.attributes()[1]
	center = feature.geometry().centroid().asPoint()
	map.setExtent(QgsRectangle(center.x() - int(0.5 * rect.width()),
	                           center.y() - int(0.5 * rect.height()),
	                           center.x() + int(0.5 * rect.width()),
	                           center.y() + int(0.5 * rect.height())))

	map.refresh()
	map.attemptMove(QgsLayoutPoint(10, 20, QgsUnitTypes.LayoutMillimeters))
	map.attemptResize(QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))
	layout = manager.layoutByName(layoutName)
	# exporter = QgsLayoutExporter(layout)

	# fn = 'D:/Google Drive/edu/#/thesis/gan_maps/test/B/{}.png'.format(n)
	# exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())

	######################
	# For landuse polygons
	f = find_feature([map.extent().center()[0],
	                  map.extent().center()[1]])
	# value = f.attributes()[3]
	s = get_feature_color(landuse_layer, f)
	color = s.color().name()

	########################
	v, pr = add_feature(v, pr, feature)
	set_style(v, _color=QColor('black'))

	map.refresh()
	map.attemptMove(QgsLayoutPoint(10, 20, QgsUnitTypes.LayoutMillimeters))
	map.attemptResize(QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))
	layout = manager.layoutByName(layoutName)
	exporter = QgsLayoutExporter(layout)

	fn = 'D:/Google Drive/edu/#/thesis/gan_maps/test/D/{}.png'.format(n)
	exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())

	try:
		with edit(v):
			listOfIds = [feat.id() for feat in v.getFeatures()]
			v.deleteFeatures(listOfIds)
	# project.removeMapLayer(v.id())
	except AttributeError:
		pass


