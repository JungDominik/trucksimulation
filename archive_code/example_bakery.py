# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 17:38:56 2024

@author: d.jung
"""

import simpy
import random
from functools import partial

class Bakery:
    def __init__(self, env):
        self.env = env
        self.oven = simpy.Resource(env, capacity=1)  # Only one oven available

def make_cake(env, name, bakery):
    print(f"{name} starts preparing at {env.now}")
    prep_time = random.randint(2, 5)
    yield env.timeout(prep_time)
    print(f"{name} finished preparation at {env.now}")

    print(f"{name} waiting for the oven at {env.now}")
    with bakery.oven.request() as req:
        yield req  # Wait until the oven is available
        print(f"{name} starts baking at {env.now}")
        bake_time = random.randint(8, 12)
        yield env.timeout(bake_time)
        print(f"{name} finished baking at {env.now}")

    cool_time = random.randint(3, 6)
    yield env.timeout(cool_time)
    print(f"{name} is ready at {env.now}")

def bakery_process(env, bakery, n):
    for i in range(n):  # Make n cakes
        env.process(make_cake(env, f'Cake {i+1}', bakery))
        yield env.timeout(random.randint(1, 3))  # Time between starting each cake



def monitor(data, resource):
    item = (
        env.now, 
        resource.count, 
        len(resource.queue)
        )
    data_monitoring.append(item)
    print("just called the monitor function")


def patch_resource(resource, post = None):
    original_request = resource.request
    
    def wrapped_request(*args, **kwargs):
        result = original_request(*args, **kwargs)
        if post:
            post(resource)
        return result
    
    resource.request = wrapped_request






# Set up and run the simulation
env = simpy.Environment()
bakery = Bakery(env)

# Monitoring setup
data_monitoring = []
monitor_func = partial(monitor, data_monitoring)
patch_resource(bakery.oven, post=monitor_func) # Patch: Add the tracking logic to the oven resource

# Set up process
n = 50 # Define amount of cakes to be baked
env.process(bakery_process(env, bakery, n))



env.run(until=50)