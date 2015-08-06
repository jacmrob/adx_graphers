'''
	This file parses data from the waterfall algorithm, ucs and campaign auction
		results, and campaign decisions. Uses the csv files written by BrownAgent.

	Outputs: 
		P_Per_Campaign directory : contains graphs of target budget and actual
			money spent per day per campaign for all owned campaigns
		Q_Per_Campaign directory : contains graphs of target impressions and actual 
			impressions met per day per campaign for all owned campaigns 

		Budget_spent : graph of percent budget spent per campaign 
		Percent_received : graph of percent desired impressions received per day
			per campaign
		Quality : graph of quality score per day
		UCS : graph of ucs cost and score per day 

	It also has the ability to analyze the bid bundle with the unpack_bidbundle
		method, which is written but not used here. 

	author @Jacqueline Roberti  

'''

import csv
import sys
import math
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import shutil
from sets import Set


NUM_DAYS = 60
COLORS = ['bo-', 'go-','ro-','co-','mo-','yo-','ko-']

''' Data class from Waterfall Alg. return'''
class Entry:
	def __init__(self, row):
		self.day = int(row[0])

		sex = (0 if row[1]=='LOW_INCOME' else 1)
		age = (0 if row[2]=='YOUNG' else 1)
		income = (0 if row[3]=='MALE' else 1)

		self.mkt = (sex, age, income)

		self.cmp_ID = int(row[4])
		self.p = float(row[5])
		self.b = float(row[6])
		self.q = int(row[7])

		self.id = str(id(self))

''' Data class from Campaign Decisions report '''
class Campaign: 
	def __init__(self, row):
		self.cmp_ID = int(row[1])
		self.start = int(row[7])
		self.end = int(row[8])
		self.reach = int(row[9])
		self.bid = 0
		self.id = str(id(self))
		self.budget = 0

''' Data class from bid bundle report'''
class Bid_Bundle:
	def __init__(self, row):
		self.day = int(row[0])
		self.cmp_ID = int(row[7])
		self.mkt = (row[1], row[2], row[3])
		self.bid = int(row[8])


#############################
''' UNPACK CSV FILES '''
#############################

'''Input: Waterfall_Alg_Data
	Returns:  dictionary of day -> Entry
			  dictionary of mkt -> Entry
			  dictionary of e.id -> Entry 
'''
def unpack_waterfall(csv_file):
	with open(csv_file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		days = defaultdict(set)
		mkts = defaultdict(set)
		entries = {}
		next(reader) 

		for row in reader:
			e = Entry(row)
			entries[e.id] = e

			days[e.day].add(e.id)
			mkts[e.mkt].add(e.id)
		return days, mkts, entries

'''input: 	Daily_Bid_Bundles.csv
	returns : 	dictionary of Entries (entry.id-> entry)
				dictionary of day-> entry.id
'''
def unpack_bidbundle(csv_file):
	with open(csv_file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		next(reader)
		entries = {}
		days = defaultdict(set)

		for row in reader:
			e = Bid_Bundle(row)
			entries[e.id] = e
			days[e.day].add(e.id)

		return entries, days


''' input : AdNetwork_Reports.csv
	returns: list of dictionaries of market segments, day-> mkt seg -> (# won, avg price)
'''
def unpack_report(csv_file):
	with open(csv_file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		next(reader)

		mkts_won = [{}for x in range(NUM_DAYS)]
		for row in reader:
			day = int(row[0])
			if int(row[4]) != 0:
				mkts_won[day][(row[1], row[2], row[3])] = int(row[4]), float(row[5])

		return mkts_won


''' Input: Campaign_Stat_Reports.csv
	returns: dictionary of impressions reached (day, cmp id) -> # imps
			 dictionary of costs day -> cid -> cost
'''
def unpack_campaign(csv_file):
	with open(csv_file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		reached_imps = {x:defaultdict(int) for x in range(NUM_DAYS)} # day, id -> imps
		reached_cost = {x:defaultdict(int) for x in range(NUM_DAYS)} # day, id -> cost
		next(reader)
		for row in reader:
			
			reached_imps[int(row[0])][int(row[1])] = float(row[2])
			reached_cost[int(row[0])][int(row[1])] = float(row[4])

			# keep track of cIDs of all owned campaigns 
			if int(row[1]) not in MY_CAMPAIGNS:
				MY_CAMPAIGNS.append(int(row[1]))

		return reached_imps, reached_cost


'''Input: Campaign_Decisions.csv, UCS_and_Campaign_Auctions.csv
   returns: dictoinary of Campaign data structures (cmp.ID -> cmp data) only for agent's owned campaigns
'''
def unpack_camp_decisions(csv_file1, csv_file2):
	with open(csv_file1, 'rb') as file1:
		reader = csv.reader(file1, delimiter=',')
		cmps = {}
		next(reader)
		for row in reader:
			e = Campaign(row)
			cmps[e.cmp_ID] = e

	with open(csv_file2, 'rb') as file2:
		reader = csv.reader(file2, delimiter=',')
		next(reader)
		ucs= {} # day -> (ucs level, ucs cost)
		quality = {} #day -> quality 
		for row in reader:
			ucs[int(row[0])] = [float(row[1]), float(row[2])]
			quality[int(row[0])] = float(row[8])

			# if campaign is owned, set budget and bid
			if int(row[4]) in MY_CAMPAIGNS:
				cmps[int(row[4])].bid = int(row[5])
				cmps[int(row[4])].budget = float(row[7])

	return cmps, ucs, quality


##########################
''' MAKE OUR GRAPHS '''
##########################

''' Per campaign, graphs targetted Q values (from waterfall) 
	and actual Q values (from campaign reports)
	Outputs to Q_Per_Campaign directory '''
def q_per_campaign(days, entries, impressions, csv_dir):
	mydir = csv_dir + "/Q_Per_Campaign"
	if not os.path.exists(mydir):
		os.makedirs(mydir)
	else:
		shutil.rmtree(mydir)
		os.makedirs(mydir)

	# campaign -> day -> q, stored for totals graph
	totals_targeted, totals_recieved = {}, {}

	for campaign in MY_CAMPAIGNS:
		red, blue = [], []
		totals_recieved[campaign]={}
		totals_targeted[campaign]={}

		# for each day, sum over qs per campaign in all mkt segs
		for d in range(NUM_DAYS):
			waterfall_q = sum([entries[e].q for e in days[d] if entries[e].cmp_ID == campaign])

			if (waterfall_q !=0):
				blue.append((d+1,waterfall_q))
				totals_targeted[campaign][d+1] = waterfall_q

			# actual impressions received on day d for campaign dic
			for dic in impressions[d]:
				if dic == campaign:
					red.append((d-1,  impressions[d][dic]))
					totals_recieved[campaign][d-1] = impressions[d][dic]

		b2 = [red[j-1][1] + blue[i][1] for i in range(len(blue)) for j in range(len(red)) if red[j][0] ==blue[i][0]]

		plt.step([x[0] for x in red], [y[1] for y in red], 'r--')
		plt.plot([x[0] for x in red], [y[1] for y in red], 'ro')
		if len(blue)==len(b2) :
			plt.step([x[0] for x in blue], b2, 'b--')
			plt.plot([x[0] for x in blue], b2, 'bs')

		cmp_id=str(campaign)
		title = cmp_id + ", days " +str(CMP_DATA[campaign].start) + "-"+str(CMP_DATA[campaign].end)+", reach: " +str(CMP_DATA[campaign].reach)
		plt.title(title)
		plt.xlabel("days")
		plt.ylabel("# impressions")
		plt.savefig(csv_dir+ "/Q_Per_Campaign/"+cmp_id+".png", format='png')
		plt.clf()

	return totals_targeted, totals_recieved 

''' Per campaign, graphs targetted P values (from waterfall) 
	and actual amount spent 
	Outputs to P_Per_Campaign directory '''
def p_per_campaign(days, entries, costs, impressions, csv_dir):
	mydir = csv_dir + "/P_Per_Campaign"
	if not os.path.exists(mydir):
		os.makedirs(mydir)
	else:
		shutil.rmtree(mydir)
		os.makedirs(mydir)

	totals_spent = {} # cmp->money spent
	for campaign in MY_CAMPAIGNS:
		totals_spent[campaign] = {} #cmp->day->amt spent
		red, blue = [],[]
		for d in range(NUM_DAYS):

			waterfall_p = sum([entries[e].p*entries[e].q for e in days[d] if entries[e].cmp_ID == campaign])
			if (waterfall_p !=0):
				blue.append((d+1,waterfall_p))

			# actual costs for campaign dic on day d
			for dic in costs[d]:
				if dic == campaign:
					red.append((d-1,  costs[d][dic]*impressions[d][dic]))
					totals_spent[campaign][d-1] = costs[d][dic]

		b2 = [red[j-1][1] + blue[i][1] for i in range(len(blue)) for j in range(len(red)) if red[j][0] ==blue[i][0]]

		plt.step([x[0] for x in red], [y[1] for y in red], 'r--')
		plt.plot([x[0] for x in red], [y[1] for y in red],'ro')
		if len(b2) == len(blue):
			plt.step([x[0] for x in blue], b2, 'b--')
			plt.plot([x[0] for x in blue], b2, 'bs')
		cmp_id=str(campaign)

		plt.title(cmp_id)
		plt.xlabel("days")
		plt.ylabel("cost")
		plt.savefig(csv_dir+ "/P_Per_Campaign/"+cmp_id+".png", format='png')
		plt.clf()

	return totals_spent

'''plots percent impressions received per campaign over the course of a game'''
def q_totals_plot(q_tar, q_rec, csv_dir):
	# takes in maps of cmp id -> {day : imps targeted} and cmp id->{day: imps received}

	n=0
	for c in q_tar:
		tar_sorted_keys = sorted(q_tar[c].keys())
		rec_sorted_keys = sorted(q_rec[c].keys())

		# put in catch for if target == received 

		# take the difference of imps recieved yesterday and today if not first day of campaign 
		new_rec = {x:(q_rec[c][x]-q_rec[c][x-1] if x-1>=q_rec[c].iterkeys().next() else q_rec[c][x]) for x in rec_sorted_keys}

		plt.plot([x for x in tar_sorted_keys if x in rec_sorted_keys], [(q_tar[c][x]-new_rec[x])/q_tar[c][x] for x in rec_sorted_keys if x in tar_sorted_keys], COLORS[n])
		n=(n+1)%len(COLORS) # iterate through colors 

	plt.xlabel("days")
	plt.ylabel("%" " away from target per cmp")
	plt.title("%" + " received")
	plt.xlim(0, 59)
	plt.axis()
	plt.savefig(csv_dir+"/Percent_received.png", format='png')
	plt.clf()


''' plots percent of budget spent per campaign over the course of a game'''
def p_totals_plot(spent, csv_dir):
	x, y= [], [] # (x,y) for campaigns with money spent
	x2, y2 =[],[]	# (x,y) for marking campaigns with no money spent 
	for c in spent:
		nc = CMP_DATA[c]
		last_day = max(k for k,v in spent[c].items())
		# per campaign, x = start day, y = (amt. spent on last day / budget) * 100

		if spent[c][last_day] == 0:
			# if we spent no money on campaign, mark with an x 
			x2.append(nc.start)
			y2.append(10)
		else:
			x.append(nc.start)
			y.append((spent[c][last_day] / nc.budget)*100)

	# currently graphed on a logarithmic scale because of the range of values.
	# when we go over, we go wayyyyyyy over 
	plt.bar(x, y, width=.8, bottom=None, color='m', label="cost", log=True) 
	plt.plot(x2, y2, 'rx')
	plt.xlabel("cmp start day")
	plt.ylabel("%" " buget spent")
	plt.title("Budget Spent, campaigns: "+str(len(spent)))
	plt.axhline(y=100,xmin=0,xmax=60,c='r', linewidth=0.5)
	plt.xlim(0, 59)
	plt.yscale('log')
	plt.axis()
	plt.savefig(csv_dir+"/Budget_spent.png", format='png')
	plt.clf()


''' plots ucs level and ucs cost against day''' 
def plot_ucs(ucs, csv_dir):
	# ucs maps day -> ucs level, ucs cost 
	fig = plt.figure()
	y1 = fig.add_subplot(111)
	y2 = y1.twinx()

	y1.plot([x for x in ucs], [ucs[x][0] for x in ucs], color='b', label="ucs level")
	y2.plot([x for x in ucs], [ucs[x][1] for x in ucs], color='m', label="ucs cost")

	y1.legend(loc=2, prop={'size':6})
	y2.legend(loc=1, prop={'size':6})

	plt.xlabel("days")
	y1.set_ylabel("ucs level")
	y2.set_ylabel("ucs cost")
	plt.xlim(1, 58)
	y1.set_ylim(-0.01,1)
	y2.set_ylim(-0.01,1)
	plt.title("UCS level and cost per day")
	plt.savefig(csv_dir+"/UCS.png", format='png')
	plt.clf()

''' plots quality score against day''' 
def plot_quality(quality, csv_dir):
	plt.plot([x for x in quality], [quality[x] for x in quality])
	plt.title("Quality Scores")
	plt.xlabel("days")
	plt.ylabel("quality score")
	plt.ylim(0, 1)
	plt.xlim(1, 58)
	plt.savefig(csv_dir+"/Quality.png", format='png')
	plt.clf()


if __name__ == '__main__':
	csv_dir = sys.argv[1]

	# per folder in results directory, run graphing algorithms 
	for folder in os.listdir(csv_dir):
		fp = os.path.join(sys.argv[1],folder)
		
		# these are global variables for a game: list of owned campaigns and map from cid to their data
		MY_CAMPAIGNS = []
		CMP_DATA = {}

		wtr_days, wtr_mkts, wtr_entries = unpack_waterfall(fp +"/Waterfall_Alg_Data.csv")
			#wtr_days = day-> cmp data
			#wtr_mkts = mkt-> cmp data
			#wtr_entries = e.id -> cmp data
		real_imps, real_cost = unpack_campaign(fp + "/Campaign_Stat_Reports.csv")
			#real_imps = (day, cid) -> # imps
			#real_cost = (day, cid) -> cost

		CMP_DATA, ucs, quality= unpack_camp_decisions(fp + "/Campaign_Decisions.csv", fp+"/UCS_and_Campaign_Auctions.csv")
			#CMP_DATA = cid -> Campaign
			#ucs = day-> (ucs leve, ucs cost)
			#quality= day-> quality score

		q_tar, q_rec = q_per_campaign(wtr_days, wtr_entries, real_imps, fp)
		spent = p_per_campaign(wtr_days, wtr_entries, real_cost, real_imps, fp)

		q_totals_plot(q_tar, q_rec, fp)
		p_totals_plot(spent, fp)

		plot_ucs(ucs, fp)
		plot_quality(quality, fp)