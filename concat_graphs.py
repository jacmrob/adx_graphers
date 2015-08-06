'''
	This file concatonates 4 graphs into a single pdf displaying them side by side
	Inputs can be changed in runAllGraphers.sh

	author @Jacqueline Roberti  
'''

import sys
import os
from PIL import Image 


if __name__ == '__main__':
	csv_dir = sys.argv[1]

	for folder in os.listdir(csv_dir):
		fp = os.path.join(sys.argv[1],folder)

		height, width = int(8.27 * 300), int(11.7 * 300) # A4 at 300dpi
		
		page = Image.new("RGB", (width, height), 'white')
	
		page.paste(Image.open(fp+str(sys.argv[2])).resize((width/2, height/2), Image.ANTIALIAS), box=(0,0))
		page.paste(Image.open(fp+ str(sys.argv[3])).resize((width/2, height/2), Image.ANTIALIAS), box=(int(width/2.+.5),0))
		page.paste(Image.open(fp+str(sys.argv[4])).resize((width/2, height/2), Image.ANTIALIAS), box=(0, int(height/2. +.5)))
		page.paste(Image.open(fp+str(sys.argv[5])).resize((width/2, height/2), Image.ANTIALIAS), box=(int(width/2.+.5), int(height/2.+.5)))
		page.save(fp+'/Graph_Viewer', "PDF")