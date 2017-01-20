#!/usr/bin/env pypy
from __future__ import division
from json import dumps
from random import randrange
from time import time

'''
Remarks.

Everything in meters and seconds
30 m/s ~ 70 mph
1 car is about 4.5 meters long


'''

class Car:
	''' Construct a car at position x with velocity v and acceleration a '''
	def __init__(self, x, v, a=0):
		self.x = x
		self.v = v
		self.a = a
	
	''' Return a car whose position and velocity reflect the passage of s seconds
		for this car, and whose acceleration is given as the parameter a 
	'''
	def tick(self, s, a):
		return Car(self.x + self.v*s + .5*self.a*s*s, self.v + self.a*s, a)
	
	def __repr__(self):
		return '[x = %.3f, v = %.3f, a = %.3f]' % (self.x, self.v, self.a)
	
	__str__ = __repr__

'''
Return an acceleration that keeps you equally between the car in front
and behind.

Arguments:
xb -- the position of the car behind you (None, if no car behind)
vb -- the velocity of the car behind you (None, if no car behind)
xf -- the position of the car ahead of you (None, if no car ahead)
vf -- the velocity of the car ahead of you (None, if no car ahead)
x  -- your own position
v  -- your own velocity
s  -- length of a tick
'''
def f_optimal(xb, vb, xf, vf, x, v, s):
	#~ ret = 0
	#~ if None in (xb, vb, xf, vf, x, v, s):
		#~ ret = 0
	#~ else:
		#~ return (xf+xb-2*x) / pow(s,2) + (vf+vb-2*v)/s
		
		
		#~ xb2 = xb + (v-vb)*s
		#~ xf2 = xf + (vf-v)*s
		#~ xmid = (xb2+xf2) / 2
		#~ D = xmid - x
		#~ ret = 2 * (D - v*s) / (s**2)

	#~ return ret
	
	return 1


'''
Simulate each second of motion for a car
F -- the f function to use for each car
N -- the number of cars
V -- The speed limit of each car
T -- The stopping time for the simulation
S -- the amount of time between each tick
verbose -- whether or not to print to screen
'''
def simulate(F = f_optimal, N=10, V=30, T=120, s=1, verbose=False):
	prev_cars = [Car(0, 30)]# + randrange(6)-3)]
	for x in xrange(1, N):
		prev_cars.append(Car(prev_cars[-1].x + randrange(6, 20), 30))# + randrange(6)-3))

	ret = [[e.x for e in prev_cars]] #All cars before starting

	t = 0
	while t <= T:
		if verbose:
			print 'T =', t, prev_cars, '\n'
		next_cars = [ prev_cars[0].tick(s, F(None, None, prev_cars[1].x, prev_cars[1].v, prev_cars[0].x, prev_cars[0].v, s)) ] #Where cars will be next

		for c in xrange(1, N-1): #All middle cars
			next_cars.append(prev_cars[c].tick(s, F(prev_cars[c-1].x, prev_cars[c-1].v, prev_cars[c+1].x, prev_cars[c+1].v, prev_cars[c].x, prev_cars[c].v, s)))

		#Final car
		next_cars.append(prev_cars[-1].tick(s, F(prev_cars[-2].x, prev_cars[-2].v, None, None, prev_cars[-1].x, prev_cars[-1].v, s)))
		
		#Move on
		ret.append([car.x for car in next_cars])
		prev_cars = next_cars
		t += s
	
	return [list(e) for e in zip(*ret)]
	#~ return ret

arr = simulate(F=lambda *args: 0, N=4, T=20, s=.25, verbose=True)

q = min(min(e) for e in arr) #min
w = max(max(e) for e in arr) #max

print q, w

for row in arr:
	print row

arr = [[ (e-q)/(w-q) for e in row ] for row in arr ]

print 'cow'
for row in arr:
	print row
open('data.js', 'w').write('const cars = %s;\nconst timestamp=%f' % (dumps(arr), time()))
