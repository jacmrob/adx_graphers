'''
	This file parses information from the tautonnement process, graphing supply, demand
		and price variation, as well as the number of iterations before convergance on 
		each day of the game

	Output:
		Tautonnement directory : contains graphs of price variation per market per day for a 
			sampling of days, and demand - supply variation per market for a sampling of days 
		Tautonnement_Variation : graphs # iterations in tautonnement per day over the course
			of a game

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
SAMPLE_DAYS = [10,20,30,40,50]
SUPPLY = {}
COLORS = {}

''' data structure to store return of tautonnement process''' 
class Entry:
	def __init__(self, row):
		self.day = int(row[0])
		self.iter = int(row[1])
		self.demand = float(row[2])
		self.price = float(row[3])
		#sex, age, inc
		self.mkt = row[6] + row[5] + row[4]

		self.id = str(id(self))


def unpack_taut(csv_file):
	days = defaultdict(list)
	entries = {}
	for row in csv.reader(open(csv_file)):
		e = Entry(row)
		entries[e.id] = e
		days[e.day].append(e.id)

	return entries, days

def unpack_supply(csv_file):
	with open(csv_file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		next(reader)
		supply = {}
		for row in reader:
			mkt = row[0] + row[1] + row[2]
			supply[mkt] = float(row[3])

	return supply

''' maps market segment to a color for graphing'''
def make_color_array():
	color_dict = {}
	w = '#ff6600'
	colors = ['bo-', 'go-','ro-','co-','mo-','yo-','ko-', w]
	i = 0
	for mkt in SUPPLY:
		color_dict[mkt] = colors[i]
		i+=1 

	return color_dict

################################################################################

''' Graphs price per iteration for a given day ''' 
def daily_price(entry_dict, day_dict, day, fp):
	my_entries = day_dict[day]
	my_markets = defaultdict(list)

	for e in my_entries:
		my_markets[entries[e].mkt].append(e)


	for mkt in my_markets:
		plt.plot([entries[e].iter for e in my_markets[mkt]], [entries[e].price for e in my_markets[mkt]], COLORS[mkt], label=str(mkt))
		plt.legend(loc=1, prop={'size':6})

	plt.title("Tautonnement Price Variation on day " + str(day))
	plt.xlabel("iteration")
	plt.ylabel("price after iteration")
	plt.savefig(fp+ "/" +str(day)+"_price.png", format='png')
	#plt.legend(loc=1, prop={'size':6})
	plt.clf()

''' Graphs demand per iteration for a given day ''' 
def daily_demand(entry_dict, day_dict, day, fp):
	my_entries = day_dict[day]
	my_markets = defaultdict(list)

	for e in my_entries:
		my_markets[entries[e].mkt].append(e)


	for mkt in my_markets:
		plt.plot([entries[e].iter for e in my_markets[mkt]], [entries[e].demand for e in my_markets[mkt]], COLORS[mkt], label=str(mkt))
		plt.legend(loc=1, prop={'size':6})

	plt.title("Tautonnement Demand Variation on day " + str(day))
	plt.xlabel("iteration")
	plt.ylabel("demand")
	plt.savefig(fp+ "/" +str(day)+"_demand.png", format='png')
	#plt.legend(loc=1, prop={'size':6})
	plt.clf()

''' Graphs (demand-supply) per iteration for a given day''' 
def daily_supply_demand(entry_dict, day_dict, day, fp):
	
	my_entries = day_dict[day]
	my_markets = defaultdict(list)

	for e in my_entries:
		my_markets[entries[e].mkt].append(e)

	for mkt in my_markets:
		plt.plot([entries[e].iter for e in my_markets[mkt]], [entries[e].demand-SUPPLY[mkt] for e in my_markets[mkt]], COLORS[mkt], label=str(mkt))
		plt.legend(loc=1, prop={'size':6})

	plt.title("Tautonnement Demand Variation on day " + str(day))
	plt.xlabel("iteration")
	plt.ylabel("demand - supply")
	plt.savefig(fp+ "/" +str(day)+"_supply_demand.png", format='png')
	plt.clf()	

''' Graphs # iterations/day for an entire game''' 
def iter_grapher(entry_dict, day_dict, fp):
	grapher = {}
	for d in day_dict:
		grapher[d] = entry_dict[day_dict[d][-1]].iter 

	plt.plot([k for k in grapher], [grapher[k] for k in grapher], 'mo-')

	plt.title("Tautonnement Variation")
	plt.xlabel("day")
	plt.ylabel("# iterations")
	plt.savefig(fp+"/Tautonnement Variation.png", format='png')
	plt.clf()



if __name__ == '__main__':
	csv_dir = sys.argv[1]

	# per folder in results directory, parse data and run graphing algorithms 
	for folder in os.listdir(csv_dir):
		fp = os.path.join(sys.argv[1],folder)
		
		entries, days = unpack_taut(fp + "/Taut_Returns.csv")
		SUPPLY = unpack_supply(fp+"/Supply.csv")
		COLORS = make_color_array()
		
		iter_grapher(entries, days, fp)

		taut_dir = fp+"/Tautonnement"
		if not os.path.exists(taut_dir):
			os.makedirs(taut_dir)
		else:
			shutil.rmtree(taut_dir)
			os.makedirs(taut_dir)

		# pick sample days to test
		for d in SAMPLE_DAYS:
			daily_price(entries, days, d, taut_dir)
			daily_supply_demand(entries, days, d, taut_dir)

