from strategies import strategies
from util import project_dict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import json

cmap = cm.magma

linestyles = {
    'strat_optimal': '--',
    'strat_random': '-',
    'strat_gipps': '--',
    'strat_leader': '-',
    'strat_idm': '-',
}

def export_json(road, max_dist, dt):
    max_lane = max(car_instant.lane for car in road for car_instant in car)
    keys = {'x', 'i', 'state', 'visible', 'lane'}
    road_dict = [[project_dict(car_instant.as_dict(), keys) for car_instant in car] for car in road]

    with open('data.js', 'w') as f:
        f.write('const road = {};\n'.format(json.dumps(road_dict)))
        f.write('const max_x = {};\n'.format(max_dist))
        f.write('const max_lane = {};\n'.format(max_lane))
        f.write('const dt = {};\n'.format(dt))

def export_graph(road, max_dist, dt):
    ts = np.arange(0, len(road[0])) * dt
    max_lane = max(car_instant.lane for car in road for car_instant in car)
    for lane in range(max_lane + 1):
        print('exporting graph for lane {lane}'.format(**locals()))
        plt.figure(figsize=(4, 5))
        plt.ylim(0, max_dist)
        plt.xlim(0, len(road[0]) * dt)
        plt.xlabel('time')
        plt.ylabel('dist')
        for car in road:
            xs = []
            ts = []
            for frame, c in enumerate(car):
                if c.lane == lane and c.visible:
                    xs.append(c.x)
                    ts.append(frame * dt)
                else:
                    plt.plot(ts, xs, color=cmap(c.i / len(road)), linestyle=linestyles[car[0].state])
                    xs = []
                    ts = []
            else:
                plt.plot(ts, xs, color=cmap(c.i / len(road)), linestyle=linestyles[car[0].state])
        plt.savefig('lane_{lane}.png'.format(**locals()))
