### 17.11 - Refactored to Object Oriented


# Import Basic packages
import io
import base64
import random
from functools import partial
from typing import List

# Import simulation things
import simpy
import numpy as np
import matplotlib.pyplot as plt

class SimulationCore:
    def __init__(self, simconfig):
        self.config = simconfig
        self.env = simpy.Environment()
        self.simclass = Bakery(
            input_env=self.env, 
            parameterlist_ressourcebased_processsteps=simconfig.ressourceconfigs)
        
        list_of_resources_to_be_monitored = []
        for processstep in self.simclass.ressourcebased_processsteps:
            list_of_resources_to_be_monitored.append(processstep.stepresource)

        self.monitor = Monitor(
            env = self.env, 
            list_of_resources_to_be_monitored = list_of_resources_to_be_monitored)
        
    def run_sim(self):
        num_cakes = self.config.params_sim["productionunits"]
        untiltime = self.config.params_sim["untiltime"]

        self.env.process(self.simclass.bakery_cakebatch_random_starting_time(num_cakes=num_cakes)) #30 is number of cakes
        self.env.run(until=untiltime)

    # def run_sim_based_on_configuration(self):
    #     self.env.process(self.simclass.bakery_cakebatch_random_starting_time(num_cakes=runconfig.params["productionunits"])) #30 is number of cakes
    #     untiltime = self.config.params["untiltime"]
    #     self.env.run(until=untiltime)

    def run_visualization(self):
        self.visualizer = Visualizer(where_to_find_data=self.monitor.data_monitoring)
        #self.plot = self.visualizer.return_plot()
        self.plots = self.visualizer.return_list_of_plots_for_ressources()

    # def clear_monitoring_data(self):
    #     self.monitor.data_monitoring = {}
    #     self.run_visualization()
    def clear_monitoring_data(self):
        if hasattr(self, 'monitor'):
            for resource, data_list in self.monitor.data_monitoring.items():
                data_list.clear()     
        plt.close('all')       

class Monitor:
    def __init__(self, env, list_of_resources_to_be_monitored):
        self.env = env
        self.data_monitoring = {}
        
        ###OLD MONITOR - replaced by the multi-resource approach below
        #self.monitor_partial_func = partial(self.monitor_func, env, resource_to_be_monitored, self.data_monitoring)
        #self.patch_resource(resource = resource_to_be_monitored, post=self.monitor_partial_func)
        #self.patch_resource(resource=resource_to_be_monitored, targetdatalist=self.data_monitoring, post=self.monitor_partial_func)
        ###

        for resource_to_be_monitored in list_of_resources_to_be_monitored:
            #Create  sub-datalist for this resource to be monitored
            self.data_monitoring[resource_to_be_monitored] = [] # resource_to_be_monitored is a class object - can this work?
            
            #Create  the partial function specific for this resource to be monitored
            self.monitor_partial_func = partial(
                self.monitor_func, 
                input_env=self.env, 
                input_resource=resource_to_be_monitored, 
                target_datalist=self.data_monitoring[resource_to_be_monitored]
                )

            self.patch_resource(
                resource_to_be_monitored, 
                self.data_monitoring[resource_to_be_monitored], 
                post=self.monitor_partial_func
                )
        
    
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
        
        #Additional logic for cumulative/separated plots
        self.figures = {} 
        self.graphcolors = ["blue", "yellow", "purple", "green","red", "black","orange"]
        self.index_currentcolor = 0

    
    def return_list_of_plots_for_ressources (self):
        ressources_to_be_plotted = self.data.keys()
        list_of_plots_for_ressources = []

        #for data_for_one_ressource in self.data: #TODO: Self.data ist falsch - rausholen auf Basis der datenstruktur der monitordaten (dictionary mit listen)
        for ressource in ressources_to_be_plotted:
            ressource_data_to_be_plotted = self.data[ressource]
            plot = self.generate_plot(
                inputdata = ressource_data_to_be_plotted,
                ressourcename=ressource)
            list_of_plots_for_ressources.append(plot)

        #Increment the color
        self.index_currentcolor +=1
        
        return list_of_plots_for_ressources
        

        


    def generate_plot(self, inputdata, ressourcename):        
        # First step: Check if ressource has already a plot, if not create one
        if ressourcename not in self.figures:
            self.figures[ressourcename] = plt.figure()
        
        #Activating the figure
        plt.figure()
        
        # Extract timestamps and queue lengths
        if inputdata:
            self.timestamps = [t[0] for t in inputdata]
            self.queue_lengths = [t[2] for t in inputdata]
        else:
            self.timestamps = []
            self.queue_lengths = []
        
        # Choose current color
        currentcolor = self.graphcolors[self.index_currentcolor % len(self.graphcolors)] #Take the index of the color (and make sure it doesnt go out of bounds)

        # Create the plot
        plt.step(self.timestamps, self.queue_lengths, where='post',
                 color = currentcolor,
                 label = f'Run {self.index_currentcolor +1}')
        plt.legend()

        # Set plot labels and limits
        plt.title(ressourcename)
        plt.xlabel('Time')
        plt.ylabel('Resource Queue Length')
        
        if self.timestamps and self.queue_lengths:
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
        #plt.close("all")
        return output_base64


class Bakery:
    # def __init__(self, input_env, resourcecapacity):
    #     self.env = input_env
    #     self.team = simpy.Resource(self.env, capacity = resourcecapacity)
    #     self.oven = simpy.Resource(self.env, capacity = resourcecapacity)
    
    def bakery_cakebatch_random_starting_time(self, num_cakes):
        for i in range(num_cakes):  # Make n cakes
            self.env.process(self.process_definition_produce_one_cake(f'Cake {i+1}'))
            yield self.env.timeout(random.randint(1, 3))  # Time between starting each cake

    ### 30. Nov - Switched off because hopefully replaced by below
    # def process_definition_produce_one_cake(self, name):
    #     print(f"{name} starts preparing at {self.env.now}")
    #     prep_time = random.randint(2, 5)
    #     yield self.env.timeout(prep_time)
    #     print(f"{name} finished preparation at {self.env.now}")

    #     print(f"{name} waiting for the teammember at {self.env.now}")
    #     with self.team.request() as req_team:
    #         yield req_team  # Wait until the oven is available
    #         print(f"{name} starts teaming at {self.env.now}")
    #         team_time = random.randint(8, 12)
    #         yield self.env.timeout(team_time)
    #         print(f"{name} finished teaming at {self.env.now}")
        
    #     with self.oven.request() as req_oven:
    #         yield req_oven  # Wait until the oven is available
    #         print(f"{name} starts baking at {self.env.now}")
    #         oven_time = random.randint(8, 12)
    #         yield self.env.timeout(oven_time)
    #         print(f"{name} finished baking at {self.env.now}")
        
        
    #     cool_time = random.randint(3, 6)
    #     yield self.env.timeout(cool_time)
    #     print(f"{name} is ready at {self.env.now}")


    ###### Concept for stepbased rewrite
    ### new INITROUTINE OF THE BAKERY (?) ###
    def __init__(self, input_env, parameterlist_ressourcebased_processsteps):
        self.env = input_env
        self.ressourcebased_processsteps = []
        ### Looks like broken, rewrite below
        # for i in range(len(parameterlist_ressourcebased_processsteps)):
        #     self.ressourcebased_processsteps.append(RessourcebasedProcessstep)

        for config in parameterlist_ressourcebased_processsteps:
            stepresource = simpy.Resource(
                self.env,
                capacity=config.params_ressource["ressourcecapacity"]
            )

            processstep_params = {
                "stepnumber": len(self.ressourcebased_processsteps),
                "stepname": config.params_ressource["ressourcename"],
                "stepresource": stepresource,
                #"timeneeded_step": random.randint(5, 10) # Replaced below with the input from the user
                "timeneeded_step": config.params_ressource["time_produnit"]
            }

            self.ressourcebased_processsteps.append(RessourcebasedProcessstep(processstep_params))



    ### Ende INITROUTINE ###
        
    ### REWRITTEN Process "one cake"
        
    # def process_definition_produce_one_cake(self, name):
    #     for ressourcebased_processstep in self.ressourcebased_processsteps:
    #         print(f"{name} entering Step XXX at {self.env.now}")
    #         #with self.ressources[i].stepresource.request as ressourcerequest_processstep: ###Geht evtl einfacher (alles verpackt in ressourcebased processstep), siehe drunter
    #         with ressourcebased_processstep.stepresource.request as ressourcerequest:
    #             yield ressourcerequest  # Wait until the step-ressource is available
    #             print(f"{name} starts using the ressource for this step at {self.env.now}")
    #             timeneeded_step = ressourcebased_processstep.timeneeded_step

    #             yield self.env.timeout(timeneeded_step)
    #             print(f"{name} finished baking at {self.env.now}")
                
    #seems to work
    def process_definition_produce_one_cake(self, name):
        for ressourcebased_processstep in self.ressourcebased_processsteps:
            #print(f"{name} entering Step {ressourcebased_processstep.stepname} at {self.env.now}")
            
            # Use yield with the request method
            req = ressourcebased_processstep.stepresource.request()
            yield req  # Wait until the step-resource is available
            
            try:
                #print(f"{name} starts using the resource for this step at {self.env.now}")
                timeneeded_step = ressourcebased_processstep.timeneeded_step

                yield self.env.timeout(timeneeded_step)
                #print(f"{name} finished step {ressourcebased_processstep.stepname} at {self.env.now}")
            finally:
                # Always release the resource
                ressourcebased_processstep.stepresource.release(req)


    # def process_definition_2_bake_one_cake(self, name):
    #     print(f"{name} starts preparing at {self.env.now}")
    #     prep_time = random.randint(2, 5)
    #     yield self.env.timeout(prep_time)
    #     print(f"{name} finished preparation at {self.env.now}")

    #     print(f"{name} waiting for the oven at {self.env.now}")
    #     with self.oven.request() as req:
    #         yield req  # Wait until the oven is available
    #         print(f"{name} starts baking at {self.env.now}")
    #         bake_time = random.randint(8, 12)
    #         yield self.env.timeout(bake_time)
    #         print(f"{name} finished baking at {self.env.now}")

    #     cool_time = random.randint(3, 6)
    #     yield self.env.timeout(cool_time)
    #     print(f"{name} is ready at {self.env.now}")

    
### Needs to be adapted to config of multiple ressources
# class SimulationConfiguration:
#     def __init__(self,  productionunits, num_resources):
#         self.params = {
#             "untiltime": 480,
#             "productionunits": int(productionunits),
#             "num_resources": int(num_resources)
#         }

class ConfigProcessRessource:
    def __init__(self,  ressourcename, ressourcecapacity, time_produnit):
        self.params_ressource = {
            "ressourcename" : ressourcename,
            "ressourcecapacity" : ressourcecapacity,
            "time_produnit" : time_produnit
            }

class SimulationConfiguration:
    def __init__(self,  productionunits, ressourceconfigs:List[ConfigProcessRessource]):
        self.params_sim = {
            "untiltime": 480,
            "productionunits": int(productionunits)
            }
        self.ressourceconfigs = ressourceconfigs


class RessourcebasedProcessstep:
    def __init__(self, parameters_processstep:list):
        self.stepnumber = parameters_processstep["stepnumber"]
        self.stepname = parameters_processstep["stepname"]
        self.stepresource = parameters_processstep["stepresource"]
        self.timeneeded_step = parameters_processstep["timeneeded_step"]

class SimulationManager:
    def __init__(self):
        self.mysim = None
        self.sim_results = {}        

    def run_sim_from_config_get_results(self, runconfig:SimulationConfiguration):
        self.mysim = SimulationCore(simconfig=runconfig)
        
        #mysim.run_sim_based_on_configuration()
        self.mysim.run_sim()
        self.mysim.run_visualization()
        
        # Possibly unneccessarily complex / memory intensive --> Review
        #sim_results["plot"] = mysim.plot
        self.sim_results["plots"] = self.mysim.plots
        self.sim_results["simcore"] = self.mysim
        
        return self.sim_results

    def clearplots (self):
        #print("startingclearing")
        self.mysim.clear_monitoring_data()
        #self.mysim.visualizer
        #print("clearing done")

        # Explicitly clear monitoring data
        if self.mysim and hasattr(self.mysim, 'monitor'):
            for resource, data_list in self.mysim.monitor.data_monitoring.items():
                data_list.clear()
        
        # Clear matplotlib figures
        plt.close('all')
        
        # Clear the plots in sim_results
        if "plots" in self.sim_results:
            self.sim_results["plots"] = []
        
        print("Clearing done")

### Methods to be exposed
def run_sim_from_config_get_results(runconfig:SimulationConfiguration):
        sim_results = {}

        mysim = SimulationCore(simconfig=runconfig)
        
        #mysim.run_sim_based_on_configuration()
        mysim.run_sim()
        mysim.run_visualization()
        
        # Possibly unneccessarily complex / memory intensive --> Review
        #sim_results["plot"] = mysim.plot
        sim_results["plots"] = mysim.plots
        sim_results["simcore"] = mysim
        
        return sim_results





#Sampleconfig for running a manual simulation. Currently only process with one resource
samplesimconfig = SimulationConfiguration( 
    productionunits = 50000, 
    ressourceconfigs = [
        ConfigProcessRessource(
            ressourcename="res1", 
            ressourcecapacity=2,
            time_produnit = 15
            ),        
        ConfigProcessRessource(
            ressourcename="res2", 
            ressourcecapacity=1,
            time_produnit = 10
            )
        ]
    )


def testsim():
    mysim = SimulationCore(samplesimconfig)
    mysim.run_sim()
    mysim.run_visualization()