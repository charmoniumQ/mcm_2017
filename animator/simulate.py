import collections
from strategies import strategies
from util import *

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
        self.laps = 0
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
        if car[frame].visible:
            lanes[car[frame].lane].append(car)
    return lanes

def simulate(road, max_lane, max_dist, dt, speedlimit):
    '''
    road: array as follows road[which car][which frame] -> CarInstant
    dt: size of one frame
    frames: number of frames to simulate
    speedlimit: speed cap on cars
    strategies: dict as follows strategies[string] -> (function(frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after) -> new_state, lane_change, new_a)'''
    for frame in range(0, len(road[0]) - 1):
       print(frame)
        road.sort(key=lambda car: car[frame].x)
        lanes = delane(frame, road)
        # for car in road:
        for i, lane in lanes.items():
            for car_before, car, car_after in zip_adj(lane, 3, 1):
                if car[frame].visible:
                    # car_before, car_after = check_mirror(frame, car, 0, lanes)
                    # car_left_before, car_left_after = check_mirror(frame, car, -1, lanes)
                    car_left_before, car_left_after = None, None
                    # car_right_before, car_right_after = check_mirror(frame, car, 1, lanes)
                    car_right_before, car_right_after = None, None
                    state_, lane, x, v, a_ = car[frame].kinematics()
                    state, lane_change, a = strategies[state_](frame, dt, car, car_before, car_after, car_left_before, car_left_after, car_right_before, car_right_after)
                    normalize_a(frame, car, a, dt, speedlimit)
                    car[frame + 1].state = state
                    car[frame + 1].lane = clamp(lane + lane_change, 0, max_lane)
                    car[frame + 1].x = a * dt**2 / 2 + v * dt + x 
                    car[frame + 1].v = a * dt + v
                    car[frame + 1].a = a
                    if max_dist is not None and car[frame + 1].x > max_dist:
                        car[frame + 1].visible = False
                else:
                    car[frame + 1].visible = False
        for i, lane in lanes.items():
            first_car = lane[0]
            if hasattr(first_car[frame], 'birth'):
                new_first_c = first_car[frame].birth(frame + 1, first_car)
                if new_first_c is not None:
                    new_first_car = [new_first_c.copy() for _ in range(len(road[0]))]

                    for new_first_c in new_first_car[:frame+1]:
                        new_first_c.visible = False
                    for new_first_c in new_first_car[frame+1:]:
                        new_first_c.visible = True
                    road.insert(0, new_first_car)
    print(len(road))
