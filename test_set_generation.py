import json
import numpy as np
import sys
from shapely.geometry import Polygon, Point
from qgis.PyQt.QtCore import QVariant

from time import time

sys.path.append('D:/Google Drive/edu/#/thesis/qgis')
from city_generation import *
from utils import *

BASE_PATH = ''
target_layer = QgsProject.instance().mapLayersByName('urban_blocks_' + city)[0]
building_layer = QgsProject.instance().mapLayersByName('buildings_' + city)
CRS = target_layer.crs()


def add_feature(_v, _pr, f):
	f.setAttributes(['1'])
	_pr.addFeature(f)
	_v.updateExtents()
	_v.commitChanges()
	project.addMapLayer(_v)
	return _v, _pr

def get_feature_color(_layer, _feature):
	for cat in _layer[0].renderer().categories():
		if cat.value() == _feature.attributes()[3]:
			return cat.symbol()

def make_new_layer(name='temp', type='Polygon', attr='id', crs=CRS):
	vl = QgsVectorLayer(type, name, "memory")
	print(name)
	vl.setCrs(crs)
	pr = vl.dataProvider()
	pr.addAttributes([QgsField(attr, QVariant.String)])
	vl.updateFields()
	set_style(vl)
	return vl, pr


class TestDataset(Dataset):
	def __init__(self, path, map, interest_layer:str, trainA: bool=False,
	             extra: bool=False):
		Dataset.__init__(self, 0, path, map, trainA, extra)
		self.interest_layer = QgsProject.instance().mapLayersByName(interest_layer)[0]


	def _make(self):
		n = 0
		try:
			os.mkdir(self.path + 'trainB/')
			if self.trainA:
				os.mkdir(self.path + 'trainA/')
		except Exception as e:
			print(repr(e))
		for feature in self.interest_layer.getFeatures():
			self._pan(feature)
			self._export(self.path + 'trainB/', n)
			if self.trainA == True:
				self._close_block(feature)
				self._export(self.path + 'trainA/', n)
				self._remove_block()
			n += 1
			if self.extra:
				self._calculate(feature, n)


################################################################################

map = OurMap('Layout1')

#######################

# Uncomment if you want to calculate density and green proportion for each block
# and use extra=True
# green_layer = QgsProject.instance().mapLayersByName('YOUR_GREEN_LAYER_NAME')[0]


TRAINA = False  # Change to True if you want a second dataset with a central
				# block feature substituted with an empty block
interest_layer = 'test_layer'

dataset = Dataset(BASE_PATH, map, interest_layer, trainA=TRAINA, extra=False)
dataset.make()

# dataset.save()  # saves generated dictionary of extra values to path/labels.json
