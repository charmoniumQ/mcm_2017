#!/usr/bin/env pypy
from __future__ import division, print_function
import json
import random
from matplotlib import pyplot as plt
import numpy as np

class Car(object):
	def __init__(self, x, v):
		'''Start a car off with intial position x and velocity v
		Cars will remember their velocity as you change it'''
		self.xs = [x]
		self.v = v

	def __repr__(self):
		return 'Car({self.x}, {self.v})'.format(**locals())

	__str__ = __repr__

	# function to compute acceleration
	def f(self, car_b, car_f, dt):
		'''Compute desired acceleration given car behind (car_b) and car forward (car_f)
		Both car_b and car_f are guarunteed to be not None
		Concrete subclasses must override.'''
		raise NotImplemented()

	# Use properties to remember the history of assignments to x
	def get_x(self): return self.xs[-1]
	def set_x(self, new_x): self.xs.append(new_x)
	x = property(get_x, set_x)

	def teleport(self, x):
		'''Move and forget previous history of positions'''
		self.xs = [x]

class OptimalCar(Car):
	def f(s, b, f, dt):
		if None in (b, f):
			return 0
		else:
			a = (f.x + b.x - 2*s.x) / pow(dt,2) + (f.v + b.v - 2*s.v) / dt
			a /= 5
			return a 

class RandomCar(Car):
	def __init__(self, bias=0, *args):
		self.bias = bias
		Car.__init__(self, *args)
	def f(self, b, f, dt):
		return random.gauss(self.bias, 200)

class ConstantCar(Car):
	def f(self, b, f, dt):
		return 0

# class CarHuman(Car):
#	 def f(self, b, f, dt):
#		 return 0

class Road(object):
	def __init__(self, cars, (gmin, gmax), (vmin, vmax)):
		'''Place the given cars on the road'''
		cars[0].teleport(0)
		cars[0].v = (vmin + vmax) / 2
		for car_b, car in zip(cars[:-1], cars[1:]):
			car.teleport(car_b.x + random.uniform(gmin, gmax))
			car.v = random.uniform(vmin, vmax)

		cars[0].v = 20
		cars[2].v = 80
		# pad cars with a None place-holder before and after
		self.cars = [None] + cars + [None]

	def simulate(self, T, dt, speedlimit=None):
		'''Simulate the traffic on the road'''
		for _ in range(int(T / dt)):
			self.tick(dt, speedlimit)
		return self.cars[1:-1]

	def tick(self, dt, speedlimit=None):
		'''Advance simulation by one clock-tick of dt'''
		for car_b, car, car_f in zip(self.cars[:], self.cars[1:], self.cars[2:]):
			a = car.f(car_b, car_f, dt)
			if car.v + a * dt > speedlimit:
				# set acceleration to bring velocity up to speedlimit
				a = (speedlimit - car.v) / dt
			car.x += car.v * dt + a * dt**2 / 2
			car.v += a * dt

def transpose(arr):
	return zip(*arr)

def export(cars):
	maxX = max(max(car.xs) for car in cars)
	minX = min(min(car.xs) for car in cars)
	normalized = [[(x - minX) / (maxX - minX) for x in car.xs] for car in cars]
	with open('data.js', 'w') as file:
		file.write('const cars = {};'.format(json.dumps(normalized)))

def spacetime_plot(cars, T):
	maxX = max(max(car.xs) for car in cars)
	minX = min(min(car.xs) for car in cars)
	plt.figure()
	plt.ylim(minX, maxX)
	plt.xlim(0, T)
	ts = np.linspace(0, T, len(cars[0].xs))
	for car in cars:
		plt.plot(ts, car.xs)
	plt.savefig('output.png')

if __name__ == '__main__':
	N = 3
	g_range = (10, 30)
	v_range = (29, 31)
	dt = 0.05
	T = 2.0
	speedlimit = 70

	cars = [RandomCar(70, 0, 0), OptimalCar(0, 0), OptimalCar(0, 0), OptimalCar(0, 0), ConstantCar(0, 0)]
	road = Road(cars, g_range, v_range)
	export(road.simulate(T, dt, speedlimit))
	spacetime_plot(cars, T)
