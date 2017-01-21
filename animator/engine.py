from __future__ import division, print_function
import json
import random
from matplotlib import pyplot as plt
import numpy as np

# (setq indent-tabs-mode t)
# (setq python-indent 4)
# (setq tab-width 4)

def zip_adj(lst, adj, nones):
	'''Iterates over lst in tuples where each tuple has `adj` consecutive elements of lst
	`nones` will pad the list on both sides with that many nones

		>>> lst = list(range(6))
		>>> list(zip_adj(lst, adj=3, nones=0))
		[(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
		>>> list(zip_adj(lst, adj=3, nones=1))
		[(None, 0, 1), (0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, None)]
'''
	lst = [None] * nones + lst + [None] * nones
	lists = [lst[i:] for i in range(adj)]
	return zip(*lists)

class Car(object):
	def __init__(self):
		'''Start a car off with intial position x and velocity v
		Cars will remember their position as you change it'''
		self.xs = []
		self.vs = []

	def __repr__(self):
		return 'Car({self.x}, {self.v})'.format(**locals())
		__str__ = __repr__

	def f(self, car_backwards, car_forwards, dt, leftlane_car_backwards, leftlane_car_forwards, rightlane_car_backwards, rightline_car_forwards):
		'''Compute desired acceleration given car behind cars
		Concrete subclasses must override.'''
		raise NotImplemented()

	def get_x(self):
		if len(self.xs) == 0:
			raise RuntimeError('No position has been set')
		return self.xs[-1]
	def set_x(self, new_x):
		self.xs.append(new_x)
	def del_x(self):
		self.xs = []
	x = property(get_x, set_x, del_x, 'Change and log new position')

	def get_v(self):
		if len(self.vs) == 0:
			raise RuntimeError('No velocity has been set')
		return self.vs[-1]
	def set_v(self, new_v):
		self.vs.append(new_v)
	def del_v(self):
		self.vs = []
	v = property(get_v, set_v, del_v, 'Change and log new velocity')

	def lasttick(self):
		'''Return a copy of self in the position from the last tick'''
		copy = Car()
		copy.xs = self.xs[:-1]
		copy.vs = self.vs[:-1]

def check_mirror(car, otherlane):
	'''looks over your shoulder to see who is there
	Returns (otherlane_car_backwards, otherlane_car_forwards)
	each of which could be None if no car is present'''

	if otherlane is None:
		return (None, None)

	for otherlane_car, next_otherlane_car in zip_adj(otherlane.cars, 2, 1):
		if next_otherlane_car is None or next_otherlane_car.x > car.x:
			break
		return (otherlane_car, next_otherlane_car)

def normalize_a(car, a, dt, speedlimit):
	'''Prevent cars from accelerating past speedlimit or decelerating past zero'''
	if car.v + a * dt > speedlimit:
		# accelerate exactly to speedlimit instead
		return (speedlimit - car.v) / dt
	elif car.v + a * dt < 0:
		# decelerate exactly to zero instead
		return car.v / dt
	else:
		return a

class Lane(object):
	def __init__(self, cars):
		self.cars = cars

	def tick(self, dt, leftlane, rightline, speedlimit=None):
		for car_b, car, car_f in zip_adj(self.cars, 3, 1):
			car_b_l, car_f_l = check_mirror(car, leftlane)
			car_b_r, car_f_r = check_mirror(car, rightlane)
			a = car.f(car_b, car_f, car_b_l, car_f_l, car_b_r, car_f_r, dt)
			a = normalize_a(car, a, dt, speedlimit)
			car.x += car.v * dt + a * dt**2 / 2
			car.v += a * dt
		self.cars = sorted(self.cars, key=lambda car: car.x)

	def lasttick(self):
		'''Returns a copy of a lane witha copy of cars as they were in the last tick'''
		return Lane([car.lasttick() for car in self.cars])

class Road(object):
		def __init__(self, lanes):
			self.lanes = lanes

		def simulate(self, T, dt, speedlimit=None):
			for _ in range(int(T / dt)):
				self.tick(dt, speedlimit)

		def tick(self, dt, speedlimit=None):
			'''Advance simulation by one clock-tick of dt'''
			for leftlane, lane, rightlane in zip_adj(self.lanes, 3, 1):
				leftlane = leftlane.lasttick()
				lane.tick(dt, leftlane, rightlane, speedlimit)

def randomly_place(cars, (gmin, gmax), (vmin, vmax)):
	'''Randomly place cars with a random gap (between gmin and gmax) with a
	random initial velocity (between vmin and vmax) both with uniform distribution'''
	cars[0].x = 0
	cars[0].v = (vmin + vmax) / 2
	for car_b, car in zip(cars[:-1], cars[1:]):
		car.x = car_b.x + random.uniform(gmin, gmax)
		car.v = random.uniform(vmin, vmax)

def export(cars):
	maxX = max(max(car.xs) for car in cars)
	normalized = [[x / maxX for x in car.xs] for car in cars]
	with open('data.js', 'w') as file:
		file.write('const cars = {};'.format(json.dumps(normalized)))
		file.write('const scale = {:.10f}'.format(1/x))

def spacetime_plot(cars, T):
	maxX = max(max(car.xs) for car in cars)
	minX = min(min(car.xs) for car in cars)
	plt.figure(figsize=(5,5))
	plt.ylim(minX, maxX)
	plt.xlim(0, T)
	ts = np.linspace(0, T, len(cars[0].xs))
	for car in cars:
		plt.plot(ts, car.xs)
		plt.savefig('output.png')

__all__ = ['Car', ]
