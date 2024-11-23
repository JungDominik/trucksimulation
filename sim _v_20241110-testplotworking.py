###Simpy Simulation app here
import simpy
import matplotlib.pyplot as plt
import numpy as np



###Exports the result as .png plot to be displayed in html


# Approach 2: In-memory with ByteIO-Buffer


#sim.py exposes an API to run simulation based on input and generate results (eg plot)
#Function which app.py calls - sim.py will generate a plot
def run_simulation_and_generate_plot(param1, param2):
    ### Plot generation (and forwarding to the user dashboard via base64 string) now working in below simple example

    print ("Jetzt kommen params aus Methodendefinition in sim.py")
    print (str(param1))
    print (str(param2))
    print ("Das waren params aus Methodendefinition in sim.py")

    ###Start of testing plot -can be replaced if real sim plot works
    fig, ax = plt.subplots()
    ax.set_ylim([0, 100])
    ax.plot([1, 2, 3], [int(param1), int(param2), int(param1) + int(param2)])
    ### End of testingplot

    # set_up_simulation_env(param1, param2)
    # results_data_for_plot =  run_sim()
    # generate matplotliblot out of results_data_for_plot




    
    import io
    output = io.BytesIO()
    plt.savefig(output, format="png")
    output.seek(0) #DJu: Taken from the boilerplate code. Purpose "Rewind the buffer so it can be read from the beginning" - ok fine.

    import base64
    output_base64 = base64.b64encode(output.getvalue()).decode('utf-8')


    return output_base64


#####
##### Pasted Previously tryout working sim: Bakery --> Adapt plotcalling logic to trigger this sim. Sim then needs to put out a bytecode image like in the prototype.

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


import matplotlib.pyplot as plt

# Extract timestamps and queue lengths
timestamps = [t[0] for t in data_monitoring]
queue_lengths = [t[2] for t in data_monitoring]

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