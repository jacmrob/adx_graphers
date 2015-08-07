from __future__ import division
import csv
import sys
import math
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import shutil

'''
	This file parses information from the UCS and Campaign auction results, 
		and the campaign decisions, to analyze how our agent is or is not meeting
		campaign reaches.  Also graphs number of campaigns running per day.

	Outputs:
		Reach_graph : graphs percent of desired impressions received per campaign
		Num_Running : graphs number of campaigns running per day

	author @Jacqueline Roberti
'''


NUM_DAYS = 60

class Campaign:
	# from campaign decisions sheet 
	def __init__(self, row):
		self.cmp_ID = int(row[1])
		self.start = int(row[7])
		self.end = int(row[8])
		self.reach = int(row[9])
		self.bid = 0
		self.id = str(id(self))

''' input: Campaign_Decisions
	output: dictionary of Campaign.id -> Campaign data for all owned campaigns
'''
def unpack_decisions(csv_file1):
	with open(csv_file1, 'rb') as file1:
		reader = csv.reader(file1, delimiter=',')
		cmps = {} # ID -> cmp
		num_running =  {x:0 for x in range(60)} # day -> # cmps running
		next(reader)
		for row in reader:
			e = Campaign(row)

			# record # cmps running per day
			for i in range(e.start-1, e.end):
				num_running[i]+=1

			# if we won the cmp, add its data
			if int(row[1]) in MY_CAMPAIGNS:
				cmps[e.id] = e

	return cmps, num_running

''' input: Campaign_Stat_Reports.csv
	output: dictionary of cmp_id -> impressions reached_per_cmp
''' 
def unpack_campaign(csv_file):
	with open(csv_file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		next(reader)
		reached_per_cmp = defaultdict(float)
		for row in reader:
			reached_per_cmp[int(row[1])] = float(row[2])

			if int(row[1]) not in MY_CAMPAIGNS:
				MY_CAMPAIGNS.append(int(row[1]))

		return reached_per_cmp

def graph_running(num_running, csv_dir):
	plt.plot([x for x in num_running], [num_running[x] for x in num_running], 'co-')

	plt.title("Campaigns running per day")
	plt.xlabel("day")
	plt.ylabel("num campaigns running")
	plt.savefig(fp+"/Num_Running.png", format='png')
	plt.clf()


if __name__ == '__main__':
	csv_dir = sys.argv[1]

	for folder in os.listdir(csv_dir):
		fp = os.path.join(sys.argv[1],folder)
		
		MY_CAMPAIGNS = [] #cIDs

		real_imps = unpack_campaign(fp + "/Campaign_Stat_Reports.csv") 	# cid -> imps reachced
		CMP_DATA, num_running = unpack_decisions(fp + "/Campaign_Decisions.csv")	# cid->cmpdata, day->num cmps running

		with open(fp+'/reaches.csv', 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			x = []
			y=[]
			
			for c in CMP_DATA:
				nc = CMP_DATA[c]
				y.append(int((real_imps[nc.cmp_ID]/nc.reach)*100))
				x.append(nc.start)
				writer.writerow([nc.start, nc.cmp_ID, nc.reach, real_imps[nc.cmp_ID], int((real_imps[nc.cmp_ID]/nc.reach)*100)])

		plt.bar(x, y, width=.8, bottom=None, color='b', label="imps targeted")
		plt.axhline(y=100,xmin=0,xmax=60,c='r', linewidth=0.5)
		plt.xlim(0, 59)
		plt.axis()

		plt.title("Actual reach per campaign, "+ str(len(MY_CAMPAIGNS))+ " campaigns")
		plt.xlabel("cmp start day")
		plt.ylabel("Percent impressions filled")
		plt.savefig(fp+"/Reach_graph.png", format='png')
		plt.clf()

		graph_running(num_running, fp)