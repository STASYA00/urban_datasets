import json
import numpy as np
import sys
from shapely.geometry import Polygon, Point
from qgis.PyQt.QtCore import QVariant

from time import time

sys.path.append('D:/Google Drive/edu/#/thesis/qgis')
from utils import *

city = 'milan'
BASE_PATH = ''

SAMPLES = 5

target_layer = QgsProject.instance().mapLayersByName('urban_blocks_' + city)[0]
building_layer = QgsProject.instance().mapLayersByName('buildings_' + city)
CRS = target_layer.crs()


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


class OurMap:
	"""
	Class that sets up the layout and the canvas.
	"""
	def __init__(self, layout_name):
		self.project = QgsProject.instance()
		self.manager = self.project.layoutManager()
		self.layout_name = layout_name
		self._clean_layouts()

		self.layout = QgsPrintLayout(self.project)
		self.layout.initializeDefaults()
		self.layout.setName(self.layout_name)
		self.manager.addLayout(self.layout)
		self.map = QgsLayoutItemMap(self.layout)
		self.layer = QgsProject.instance().mapLayersByName('buildings_milan')



		self.background_color = (255, 255, 255, 0)

		self._set_map()

	def _clean_layouts(self):
		layouts_list = self.manager.printLayouts()
		# remove any duplicate layouts
		for _layout in layouts_list:
			if _layout.name() == self.layout_name:
				self.manager.removeLayout(_layout)

	def _set_map(self):
		self.map.setRect(20, 20, 20, 20)
		ms = QgsMapSettings()
		ms.setLayers(self.layer)  # set layers to be mapped
		self.rect = QgsRectangle(ms.fullExtent())
		self.rect.scale(0.01)

		ms.setExtent(self.rect)
		self.map.setExtent(self.rect)
		self.map.setBackgroundColor(QColor(*self.background_color))
		self.layout.addLayoutItem(self.map)
		self.map.setExtent(QgsRectangle(0, 0, 0 + self.rect.width(),
		                                0 + self.rect.height()))


class Dataset:
	"""
	Class that generates a normal dataset from a map
	"""
	def __init__(self, samples, path, map, trainA: bool=False, extra: bool=False):
		"""
		Class initialization.
		:param samples: number of samples to generate, int
		:param path: path to save the images to, str
		:param map: map, OurMap class
		:param extra: parameter allowing to generate additional parameters such as
		building density and the proportion of green in a block, bool, default False
		"""
		self.crs = CRS
		self.samples = samples
		self.path = path
		if not self.path.endswith('/'):
			self.path += '/'
		self.threshold = 0.2
		self.threshold_q = 4
		self.scale = 3000
		self.layout_name = 'Layout1'
		self.map = map
		self.v, self.pr = make_new_layer(crs=self.crs)

		self.trainA = trainA
		self.extra = extra
		self.dict = {}

	def make(self):
		return self._make()

	def save(self):
		with open(self.path + 'labels.json', 'w') as k:
			json.dump(self.dict, k)

	def _calculate(self, feature, n):
		built_proportion = round(find_feature(feature)[0], 2)
		green_proportion = round(find_feature(feature,
		                                      _layer=green_layer)[0], 2)
		self.dict[n] = [self.map.map.extent().xMinimum(),
		                self.map.map.extent().yMinimum(),
		                self.map.map.extent().xMaximum(),
		                self.map.map.extent().yMaximum(), green_proportion,
		                built_proportion]

	def _check(self, feature):
		_density, _quantity = find_feature(feature)
		if _density > self.threshold:
			if _quantity > self.threshold_q:
				return True

	def _close_block(self, feature):
		self.v, self.pr = add_feature(self.v, self.pr, feature)
		set_style(self.v, _color=QColor("white"))

	def _export(self, path, n):
		layout = self.map.manager.layoutByName(self.layout_name)
		exporter = QgsLayoutExporter(layout)

		fn = path + 'map{0}.png'.format(n)
		exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())

	def _make(self):
		n = 0
		features = target_layer.getFeatures()
		try:
			os.mkdir(self.path + 'trainB/')
			if self.trainA:
				os.mkdir(self.path + 'trainA/')
		except Exception as e:
			print(repr(e))
		for i, feature in enumerate(features):
			if self._check(feature):
				self._pan(feature)
				self._export(self.path + 'trainB/', n)
				if self.trainA == True:
					self._close_block(feature)
					self._export(self.path + 'trainA/', n)
					self._remove_block()
				n += 1
				if self.extra:
					self._calculate(feature, n)
			if n > self.samples:
				break

	def _pan(self, feature):
		center = [feature.geometry().centroid().asPoint().x(),
		          feature.geometry().centroid().asPoint().y()]
		self.map.map.setExtent(QgsRectangle(center[0] - (self.map.rect.width() / 2),
		                           center[1] - (self.map.rect.height() / 2),
		                           center[0] + (self.map.rect.width() / 2),
		                           center[1] + (self.map.rect.height() / 2)))
		self.map.map.attemptMove(QgsLayoutPoint(10, 20, QgsUnitTypes.LayoutMillimeters))
		self.map.map.attemptResize(
			QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))
		self.map.map.setScale(self.scale)

	def _remove_block(self):
		try:
			with edit(self.v):
				listOfIds = [feat.id() for feat in self.v.getFeatures()]
				self.v.deleteFeatures(listOfIds)
		# project.removeMapLayer(v.id())
		except AttributeError:
			pass


map = OurMap('Layout1')

#######################

# Uncomment if you want to calculate density and green proportion for each block
# and use extra=True
# green_layer = QgsProject.instance().mapLayersByName('YOUR_GREEN_LAYER_NAME')[0]


TRAINA = False  # Change to True if you want a second dataset with a central
				# block feature substituted with an empty block

dataset = Dataset(SAMPLES, BASE_PATH, map, trainA=TRAINA, extra=False)
dataset.make()

# dataset.save()  # saves generated dictionary of extra values to path/labels.json

