import argparse
import cv2
import numpy as np
import os
import textwrap


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
				USAGE: python change_dim.py PATH_TO_FOLDER

				------------------------------------------------------------------------

				This is an algorithm that makes an image training set for Pix2pix
				GAN model. Pass the path to your dataset folder as an argument.
				Make sure this folder contains trainA folder, trainB and trainAB
				folders.

				------------------------------------------------------------------------

				'''), epilog=textwrap.dedent('''\
				The algorithm will be updated with the changes made in the strategy.
				'''))

	# parser.add_argument('model', type=str, help='path to the model file with '
	#                                             '.blend extension, str')
	parser.add_argument('folder', type=str, help='path to the folder with image files',
	                    default=None)

	parser.add_argument('--folder1', type=str, help='path to the second folder',
	                    default=None)
	parser.add_argument('--concat', type=str, help='option to concat two images',
	                    default=None)
	parser.add_argument('--dim', type=int,
	                    help='dimensions of the resulting images', default=512)

	############################################################################

	args = parser.parse_args()

	path = args.folder

	FOLDER1 = args.folder1

	CONCAT = args.concat

	DIM = args.dim

	############################################################################

	for img in os.listdir(path):
		imageA = cv2.imread(path + '/' + img)[237:2357, 117:2237]
		imageA = cv2.resize(imageA, (DIM, DIM), interpolation=cv2.INTER_AREA)
		cv2.imwrite(path + '/' + img, imageA)

		if FOLDER1:
			imageB = cv2.imread(FOLDER1 + '/' + img)[237:2357, 117:2237]
			imageB = cv2.resize(imageB, (DIM, DIM), interpolation=cv2.INTER_AREA)
			cv2.imwrite(FOLDER1 + '/' + img, imageB)

			if CONCAT:
				os.mkdir('trainAB')
				image = np.concatenate([imageA, imageB], axis=1)
				cv2.imwrite('trainAB/' + img, image)
