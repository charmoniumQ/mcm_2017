import collections
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import json
from util import *

cmap = cm.magma

def normalize_a(frame, car, a, dt, speedlimit):
    '''Prevent cars from accelerating past speedlimit or decelerating past zero'''
    if speedlimit is not None and car[frame].v + a * dt > speedlimit:
        # accelerate exactly to speedlimit instead
        return (speedlimit - car[frame].v) / dt
    elif car[frame].v + a * dt < 0:
        # decelerate exactly to zero instead
        return car[frame].v / dt
    else:
        return a

class CarInstant(DotDict):
    car_i = 0
    def __init__(self, state, lane, x, v, a, i=None, **kwargs):
        DotDict.__init__(self, **kwargs)
        self.state, self.lane, self.x, self.v, self.a = state, lane, x, v, a
        if i is None:
            self.i = CarInstant.car_i
            CarInstant.car_i += 1
        else:
            self.i = i

    def copy(self):
        return CarInstant(**self.as_dict())

    def kinematics(self):
        '''Packs kinematic variables into tuple (state, x, v, a)'''
        return (self.state, self.lane, self.x, self.v, self.a)

def check_mirror(frame, car, lane_offset, lanes):
    lane = car[frame].lane + lane_offset
    if lane in lanes:
        if lane == car[frame].lane:
            # if searching your lane
            for before_car, center_car, after_car in zip_adj(lanes[lane], 3, 1):
                if after_car is None or after_car[frame].x > car[frame].x:
                    return  before_car, after_car
        else:
            # if searching other lane
            for before_car, after_car in zip_adj(lanes[lane], 2, 1):
                if after_car is None or after_car[frame].x > car[frame].x:
                    return before_car, after_car
    else:
         return None, None

def delane(frame, road):
    lanes = collections.defaultdict(list)
    for car in road:
        lanes[car[frame].lane].append(car)
    return lanes

def simulate(road, max_lane, dt, speedlimit, strategies):
    '''
    road: array as follows road[which car][which frame] -> CarInstant
    dt: size of one frame
    frames: number of frames to simulate
    speedlimit: speed cap on cars
    strategies: dict as follows strategies[string] -> (function(frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after) -> new_state, lane_change, new_a)'''
    for frame in range(0, len(road[0]) - 1):
        lanes = delane(frame - 1, road)
        for car in road:
            car_before, car_after = check_mirror(frame, car, 0, lanes)
            car_left_before, car_left_after = check_mirror(frame, car, -1, lanes)
            car_right_before, car_right_after = check_mirror(frame, car, 1, lanes)
            state_, lane, x, v, a_ = car[frame].kinematics()
            state, lane_change, a = strategies[state_](frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after)
            normalize_a(frame, car, a, dt, speedlimit)
            car[frame + 1].state = state
            car[frame + 1].lane = clamp(lane + lane_change, 0, max_lane)
            car[frame + 1].x = a * dt**2 / 2 + v * dt + x
            car[frame + 1].v = a * dt + v
            car[frame + 1].a = a
        road = sorted(road, key=lambda car: car[frame].x)

linestyles = {
    'strat_optimal': '--',
    'strat_random': '-',
}

def export(road, dt):
    '''export data and graph for HTML viewer
    road: array as follows road[which car][which frame] -> CarInstant'''

    max_x = max(car_instant.x for car in road for car_instant in car)
    max_lane = max(car_instant.lane for car in road for car_instant in car)
    road_dict = [[car_instant.as_dict() for car_instant in car] for car in road]

    with open('data.js', 'w') as f:
        f.write('const road = {};\n'.format(json.dumps(road_dict)))
        f.write('const max_x = {};\n'.format(max_x))
        f.write('const max_lane = {};\n'.format(max_lane))
        f.write('const dt = {};\n'.format(dt))

        ts = np.arange(0, len(road[0])) * dt
        max_lane = max(cari.lane for car in road for cari in car)
        for lane in range(max_lane):
            pass

    for lane in range(max_lane + 1):
        print('exporting graph for lane {lane}'.format(**locals()))
        plt.figure(figsize=(4, 5))
        plt.ylim(0, max_x)
        plt.xlim(0, len(road[0]) * dt)
        plt.xlabel('time')
        plt.ylabel('dist')
        for car in road:
            xs = []
            ts = []
            for frame, c in enumerate(car):
                if c.lane == lane:
                    xs.append(c.x)
                    ts.append(frame * dt)
                else:
                    plt.plot(ts, xs, color=cmap(c.i / len(road)), linestyle=linestyles[car[0].state])
                    xs = []
                    ts = []
            else:
                plt.plot(ts, xs, color=cmap(c.i / len(road)), linestyle=linestyles[car[0].state])
        plt.savefig('lane_{lane}.png'.format(**locals()))
