"""
Emits a JSON object in which all the stretches on one highway (route)
are stored in a list, against the route's ID.


"""

import csv
import sys
import json

class Stretch:
	"""
	One stretch of the highway between two mileposts
	lst = [route_ID, type, start_milepost, end_milepost, 
		   daily_traffic_count, lanes_dec, lanes_inc]
	"""
	def __init__(self, lst):
		"""Initialize the stretch"""	
		self.route_ID = lst[0]
		self.start_milepost = lst[1]
		self.end_milepost = lst[2]
		self.daily_traffic_count = lst[3]
		self.type = lst[4]
		self.lanes_dec = lst[5]
		self.lanes_inc = lst[6]
		
stretches_by_route_ID = { 5 : [], 90 : [], 405 : [], 520 : [] }

csv_file = open('2017_MCM_Problem_C_Data.csv', 'rb')
data_reader = csv.reader(csv_file, delimiter=' ')
field_titles = next(data_reader)

for data_row in data_reader:
	data_fields = data_row[0].split(',')
	data_lst = []
	for i in range(len(data_fields)):
		data_lst.append(data_fields[i])
	stretches_by_route_ID[int(data_fields[0])].append(Stretch(data_lst))

print json.dumps(stretches_by_route_ID, default=lambda o: o.__dict__, sort_keys=False, indent=4)