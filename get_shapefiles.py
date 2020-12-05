import argparse
import numpy as np
import osmnx as ox
import textwrap


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
		USAGE: python get_shapefiles.py "Torino, Italia"

		------------------------------------------------------------------------

		This is an algorithm that extracts shapefiles of buildings and roads
		from the area of interest from OpenStreetMap.org. The area of interest is
		defined as a query that osm receives.

		------------------------------------------------------------------------

		'''), epilog=textwrap.dedent('''\
		Note: data from OSM is available under the Open Database License.
		'''))

	# parser.add_argument('model', type=str, help='path to the model file with '
	#                                             '.blend extension, str')
	parser.add_argument('place', type=str, help='place to get the maps of')

	############################################################################

	args = parser.parse_args()

	PLACE = args.place

	print(PLACE)

	############################################################################

	def geom_check(df, dtype):
		_geom_check = [1 if x.geom_type != dtype else 0 for x in df['geometry']]
		if len(np.unique(_geom_check)) > 1:
			df = df.loc[df['geometry'].geom_type == dtype]
		return df

	city = PLACE.split(' ')[0]

	print('Working on the road grid...')
	graph = ox.graph_from_place(PLACE)
	# Get roads
	edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
	print(edges.columns)
	try:
		edges = edges[['osmid', 'name', 'geometry', 'width', 'length']]
	except Exception:
		edges = edges[['osmid', 'geometry']]
	for col in edges.columns:
		edges[col] = [x if not isinstance(x, list) else x[0] for x in edges[col]]

	edges = geom_check(edges, 'LineString')

	edges = edges.to_crs('EPSG:32632')
	edges.to_file(city + '_roads.shp')
	print('Roads successfully written as shapefile.')

	# get building footprints
	print('Working on building footprints...')
	buildings = ox.footprints_from_place(PLACE)
	buildings = buildings[['osmid', 'building:levels', 'geometry', 'height']]
	buildings = geom_check(buildings, 'Polygon')
	for col in buildings.columns:
		buildings[col] = [x if not isinstance(x, list) else x[0] for x in buildings[col]]

	print(buildings.columns)

	buildings = buildings.to_crs('EPSG:32632')
	buildings.to_file(city + '_buildings.shp')
	print('Buildings successfully written as shapefile.')