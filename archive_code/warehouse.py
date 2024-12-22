# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 22:41:22 2024

@author: d.jung
"""

import simpy

#Setup parameters
DURATION_PARKING = 5
DURATION_TRIP = 2

#Setup everything
def car(env):
    while(True):
        print (f"start driving at  {env.now}")
        yield env.timeout(DURATION_TRIP)
    
        
        print (f"start parking at  {env.now}")
        yield env.timeout(DURATION_PARKING)

def car2(env):
    while(True):
        print (f"car2 start driving at  {env.now}")
        yield env.timeout(DURATION_TRIP)
    
        
        print (f"car2 start parking at  {env.now}")
        yield env.timeout(DURATION_PARKING)
    
    

# def example(env):

#     value = yield env.timeout(1, value=42)

#     print('now=%d, value=%d' % (env.now, value))


#Start the simulation
env = simpy.Environment()
#env.process()






env = simpy.Environment()

p = env.process(car(env))
q = env.process(car2(env))



env.run(until=100)

# run_warehouse(TODO: env etc)
