###Simpy Simulation app here
# Import Basic packages
import io
import base64
import random
from functools import partial

# Import simulation things
import simpy
import numpy as np
import matplotlib.pyplot as plt
    


###Exports the result as .png plot to be displayed in html


# Approach 2: In-memory with ByteIO-Buffer


#sim.py exposes an API to run simulation based on input and generate results (eg plot)
#Function which app.py calls - sim.py will generate a plot


#####
##### Pasted Previously tryout working sim: Bakery --> Adapt plotcalling logic to trigger this sim. Sim then needs to put out a bytecode image like in the prototype.

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


def patch_resource(resource, post = None):
    original_request = resource.request
    
    def wrapped_request(*args, **kwargs):
        result = original_request(*args, **kwargs)
        if post:
            post(resource)
        return result
        resource.request = wrapped_request



def set_up_simulation_env(param1, param2):
    class Bakery:
        def __init__(self, env):
            self.env = env
            self.oven = simpy.Resource(env, capacity=1)  # Only one oven available

    # Set up and run the simulation
    env = simpy.Environment()
    bakery = Bakery(env)

    # Monitoring setup
    data_monitoring = []
    monitor_func = partial(monitor, data_monitoring)
    patch_resource(bakery.oven, post=monitor_func) # Patch: Add the tracking logic to the oven resource

    # Set up process
    ### TODO -change this to param, eg. param defines the goal of cakes
    n = 50 # Define amount of cakes to be baked
    env.process(bakery_process(env, bakery, n))
    return env

def monitor(data, resource, env, data_monitoring):
    item = (
        env.now, 
        resource.count, 
        len(resource.queue)
        )
    data_monitoring.append(item)
    print("just called the monitor function")

def run_simulation_return_data(param1, param2, env, data_monitoring) :
    env.run(until=50)

def turn_data_into_plot(inputdata):
    
    # Extract timestamps and queue lengths
    if inputdata:
        timestamps = [t[0] for t in inputdata]
        queue_lengths = [t[2] for t in inputdata]
    else:
        timestamps = []
    # Create the plot
    plt.step(timestamps, queue_lengths, where='post')

    # Set plot labels and limits
    plt.xlabel('Time')
    plt.ylabel('Resource Queue Length')
    plt.xlim(0, max(timestamps) + 5)
    plt.ylim(0, max(queue_lengths) + 5)

    # Display the plot
    plt.grid(True)
    plt.show()

def run_simulation_and_generate_plot(param1, param2):
    ### Plot generation (and forwarding to the user dashboard via base64 string) now working in below simple example

    print ("Jetzt kommen params aus Methodendefinition in sim.py")
    print (str(param1))
    print (str(param2))
    print ("Das waren params aus Methodendefinition in sim.py")


    print("starte den geteilten block: Set up, run sim, generate plot")
    env = set_up_simulation_env(param1, param2)
    results_data_for_plot =  run_simulation_return_data(env = env, param1 = param1, param2=param2)
    print(results_data_for_plot)
    output = turn_data_into_plot(inputdata=results_data_for_plot)    # generate matplotliblot out of results_data_for_plot


    ### Possibly move this to the method  turn_data_into_plot       
    output = io.BytesIO()
    plt.savefig(output, format="png")
    output.seek(0) #DJu: Taken from the boilerplate code. Purpose "Rewind the buffer so it can be read from the beginning" - ok fine.
    output_base64 = base64.b64encode(output.getvalue()).decode('utf-8')


    return output_base64
