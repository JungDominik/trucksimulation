### 17.11 - Refactored to Object Oriented


# Import Basic packages
import io
import base64
import random
from functools import partial

# Import simulation things
import simpy
import numpy as np
import matplotlib.pyplot as plt

class SimulationCore:
    def __init__(self, configobject):
        self.config = configobject
        
        self.env = simpy.Environment()
        self.simclass = Bakery(self.env, resourcecapacity=self.config.params["num_resources"])
        self.monitor = Monitor(env = self.env, resource_to_be_monitored = self.simclass.oven)
        
    def run_sim(self):
        num_cakes = self.config.params["productionunits"]
        untiltime = self.config.params["untiltime"]

        self.env.process(self.simclass.bakery_cakebatch_random_starting_time(num_cakes=num_cakes)) #30 is number of cakes
        self.env.run(until=untiltime)

    # def run_sim_based_on_configuration(self):
    #     self.env.process(self.simclass.bakery_cakebatch_random_starting_time(num_cakes=runconfig.params["productionunits"])) #30 is number of cakes
    #     untiltime = self.config.params["untiltime"]
    #     self.env.run(until=untiltime)

    def run_visualization(self):
        self.visualizer = Visualizer(where_to_find_data=self.monitor.data_monitoring)
        self.plot = self.visualizer.return_plot()
        

class Monitor:
    def __init__(self, env, resource_to_be_monitored):
        self.data_monitoring = []
        self.monitor_partial_func = partial(self.monitor_func, env, resource_to_be_monitored, self.data_monitoring)
        #self.patch_resource(resource = resource_to_be_monitored, post=self.monitor_partial_func)
        self.patch_resource(resource=resource_to_be_monitored, targetdatalist=self.data_monitoring, post=self.monitor_partial_func)
        
    
    def patch_resource(self, resource, targetdatalist, post = None):
        original_request = resource.request
    
        def wrapped_request(*args, **kwargs):
            result = original_request(*args, **kwargs)
            if post:
                post() #DJu: This used to be "post(resource)" according to the Simpy Documentation. Said it has to many arguments, I removed it, now works. No idea why...
            return result
        resource.request = wrapped_request

    def monitor_func(self, input_env, input_resource, target_datalist):
        item = (
            input_env.now,
            input_resource.count,
            len(input_resource.queue)
            )
        target_datalist.append(item)

class Visualizer:
    def __init__(self, where_to_find_data):
        self.data = where_to_find_data
    
    def return_plot(self):
        plot = self.generate_plot(self.data)
        return plot
        

    def generate_plot(self, inputdata):
        # Extract timestamps and queue lengths
        if inputdata:
            self.timestamps = [t[0] for t in inputdata]
            self.queue_lengths = [t[2] for t in inputdata]
        else:
            self.timestamps = []
        # Create the plot
        plt.step(self.timestamps, self.queue_lengths, where='post')

        # Set plot labels and limits
        plt.xlabel('Time')
        plt.ylabel('Resource Queue Length')
        plt.xlim(0, max(self.timestamps) + 5)
        plt.ylim(0, max(self.queue_lengths) + 5)

        # Display the plot
        #plt.grid(True)
        #plt.show()

        ### Possibly move this to the method  turn_data_into_plot       
        output = io.BytesIO()
        plt.savefig(output, format="png")
        output.seek(0) #DJu: Taken from the boilerplate code. Purpose "Rewind the buffer so it can be read from the beginning" - ok fine.
        output_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
        
        return output_base64


class Bakery:
    def __init__(self, input_env, resourcecapacity):
        self.env = input_env
        self.oven = simpy.Resource(self.env, capacity = resourcecapacity)
    
    def process_definition_make_one_cake(self, name):
        print(f"{name} starts preparing at {self.env.now}")
        prep_time = random.randint(2, 5)
        yield self.env.timeout(prep_time)
        print(f"{name} finished preparation at {self.env.now}")

        print(f"{name} waiting for the oven at {self.env.now}")
        with self.oven.request() as req:
            yield req  # Wait until the oven is available
            print(f"{name} starts baking at {self.env.now}")
            bake_time = random.randint(8, 12)
            yield self.env.timeout(bake_time)
            print(f"{name} finished baking at {self.env.now}")

        cool_time = random.randint(3, 6)
        yield self.env.timeout(cool_time)
        print(f"{name} is ready at {self.env.now}")

    def bakery_cakebatch_random_starting_time(self, num_cakes):
        for i in range(num_cakes):  # Make n cakes
            self.env.process(self.process_definition_make_one_cake(f'Cake {i+1}'))
            yield self.env.timeout(random.randint(1, 3))  # Time between starting each cake


class SimulationConfiguration:
    def __init__(self,  productionunits, num_resources):
        self.params = {
            "untiltime": 480,
            "productionunits": int(productionunits),
            "num_resources": int(num_resources)
        }


def run_sim_from_config_get_results(runconfig):
        sim_results = {}

        mysim = SimulationCore(configobject=runconfig)
        
        #mysim.run_sim_based_on_configuration()
        mysim.run_sim()
        mysim.run_visualization()
        
        # Possibly unneccessarily complex / memory intensive --> Review
        sim_results["plot"] = mysim.plot
        
        return sim_results

