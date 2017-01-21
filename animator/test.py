#!/usr/bin/env pypy
from engine import *

class OptimalCar(Car):
	def f(s, b, f, dt, bl, fl, br, fr):
		if None in (b, f):
			return 0
		else:
			a = (f.x + b.x - 2*s.x) / pow(dt,2) + (f.v + b.v - 2*s.v) / dt
			a /= 10
			return a

class RandomCar(Car):
	def __init__(self, bias=0):
		self.bias = bias
		Car.__init__(self)
	def f(self, b, f, dt):
		return random.gauss(self.bias, 200)

class ConstantCar(Car):
	def f(self, b, f, dt):
		return 0

if __name__ == '__main__':
	N = 3
	g_range = (10, 30)
	v_range = (29, 31)
	dt = 0.05
	T = 2.0
	speedlimit = 70

	lanes = []
	for lane in range(4):
		cars = [RandomCar(20)] +  [OptimalCar() for _ in range(10)] + [RandomCar(-1)]
		lanes.append(Lane(randomly_place(cars)))
	road = Road(lanes)
	road.simulate(T, dt, speedlimit)
	export(road)
	spacetime_plot([cars for cars in lane.cars for lane in road.lanes], T)
