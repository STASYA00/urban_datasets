## Urban Datasets Generator

This script is intended to be used inside QGIS Software to create an image urban datasets. The contents of the images can vary based on the shapefiles available to you:)

### How To Use

1. Open QGIS
2. Upload your shapefiles and style them according to your needs
3. Go to ```Plugins -> Python Console```
4. NAvigate to ```city_generator.py``` and choose it
5. Set the variables:
* SAMPLES - number of images to generate
* BASE_PATH - path to save the images to
6. If you need to generate the images with an empty block in the center change Dataset in the code executive part to ADataset
7. Enjoy!

### What if I don't have any shapefiles?

Don't worry! There is a script that gets the shapefiles from the region you need directly from <a href="https://www.openstreetmap.org/">OpenStreetMap</a> data <a href="https://opendatacommons.org/licenses/odbl/">(OdBL license)</a>. The script will make one shapefile with the roads and one with the buildings. Find a good location for your dataset and follow the steps:

1. Install <a href="https://www.anaconda.com/products/individual">Conda</a>
2. Install <a href="https://osmnx.readthedocs.io/en/stable/">osmnx</a> package in a new environment named osm

```
$conda config --prepend channels conda-forge
$conda create -n osm --strict-channel-priority osmnx
```
  
3. Activate the environment:
```
$conda activate osm
```
  
4. Run the script, placing the name of your geographical location inside (make sure it corresponds to osm naming and query):
```
$python get_shapefiles.py "City, Country"
```
If you do not need the whole city shapefile to be downloaded you can specify just one zone:
```
$python get_shapefiles.py "Zone, City, Country"
```
Example:
```
$python get_shapefiles.py "Bovisa, Milan, Italy"
```
