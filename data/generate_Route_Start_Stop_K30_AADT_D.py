file = open('K_Factors_By_Site.txt', 'rb')
K_factors_by_site = file.readlines()
titles_2 = K_factors_by_site[0]
K_factors_by_site = K_factors_by_site[1:]

clean_data = open('Route_Start_Stop_K30_AADT_D.csv', 'w')
clean_data.write('Route_ID,Start,Stop,K30,AADT,D\n')

ROUTE_ID = 0
START = 1
STOP = 2
ACTUAL_POST = 3
K30 = 4
AADT = 5
D = 6

by_route_ID = { 5 : [], 90 : [], 405 : [], 520 : [] }

for line in K_factors_by_site:
	field_list = line.split(' ')
	if not field_list[1].isdigit():
		continue
	if int(field_list[1]) in (5, 90, 405, 520):
		lst = []
		lst.append(int(field_list[1]))   # ROUTE_ID
		lst.append(0)            		 # START
		lst.append(0)			 		 # STOP
		lst.append(float(field_list[2])) # ACTUAL_POST
		lst.append(float(field_list[4])) # K30
		field_list[3] = field_list[3].replace(',', '')
		lst.append(float(field_list[3])) # AADT
		lst.append(float(field_list[7])) # D
		by_route_ID[int(field_list[1])].append(lst)
	
for route_ID in (5, 90, 405, 520):
	lists = by_route_ID[route_ID]
	lists.sort(lambda a, b: -1 if float(a[3]) < float(b[3]) else 1)
	for i in range(0, len(lists)):
		lst = lists[i]
		if i == 0:
			lst[STOP] = lst[ACTUAL_POST] + (lists[1][ACTUAL_POST] - lst[ACTUAL_POST]) / 2
			lst[START] = lst[ACTUAL_POST] - (lists[1][ACTUAL_POST] - lst[ACTUAL_POST]) / 2
			if lst[START] < 0:
				lst[START] = 0
		elif i == len(lists) - 1:
			lst[START] = lst[ACTUAL_POST] - (lst[ACTUAL_POST] - lists[i-1][ACTUAL_POST]) / 2
			lst[STOP] = lst[ACTUAL_POST] + (lst[ACTUAL_POST] - lists[i-1][ACTUAL_POST]) / 2
		else: 
			lst[STOP] = lst[ACTUAL_POST] + (lists[i+1][ACTUAL_POST] - lst[ACTUAL_POST]) / 2
			lst[START] = lst[ACTUAL_POST] - (lst[ACTUAL_POST] - lists[i-1][ACTUAL_POST]) / 2
		
	for lst in lists:
		i = 0
		for data in lst:
			if i != 3:
				if isinstance(data, str):
					data = data.replace(',', '')
				clean_data.write(str(data))
				clean_data.write(',')
			i += 1
		clean_data.write('\n')
	
clean_data.close()
