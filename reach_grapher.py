from __future__ import division
import csv
import sys
import math
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import shutil

if __name__ == '__main__':
	csv_dir = sys.argv[1]

	for folder in os.listdir(csv_dir):
		fp = os.path.join(sys.argv[1],folder)


		with open(fp+"/reaches.csv", 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			x =[]
			y=[]
			for row in reader:
				y.append(int(row[4]))
				x.append(int(row[0]))

			print x
			print y

		plt.bar(x, y, width=.3, bottom=None, color='b', label="imps targeted")
		plt.bar(x,y, width =.3, bottom=None, color ='c', label= "imps received")

		plt.title("Actual reach per campaign")
		plt.xlabel("cmp start day")
		plt.ylabel("Percent impressions filled")
		plt.savefig(fp+"/Reach_graph.png", format='png')
		plt.clf()
