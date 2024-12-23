#* sim.py: Simulation extracted out into separate file. Runs simulation based on user inputs and creates output (result plot .jpg-images and realtime console simulation run)
#    * Main access point is the API ("Pass configuration and receive results")
#    * Structured into simulation manager which administrates simulation core, a data monitor which stores timestamp data during the process of the simulation and the visualization which turns the data into plots.
#    * Simulation logic is based on the Discrete Event Simulation paradigm which is a standard paradigm for industrial processes. It utilizes the SimPy package.
#    * Plot generation utilizes matplotlib library
#    * Extraction of plot images to the webapp works by converting them to base64 encoded strings


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
        self.simclass = Factory(
            input_env=self.env, 
            parameterlist_ressourcebased_processsteps=simconfig.ressourceconfigs)
        
        list_of_resources_to_be_monitored = []
        for processstep in self.simclass.ressourcebased_processsteps:
            list_of_resources_to_be_monitored.append(processstep.stepresource)

        self.monitor = Monitor(
            env = self.env, 
            list_of_resources_to_be_monitored = list_of_resources_to_be_monitored)
        
    def run_sim(self):
        num_widgets = self.config.params_sim["productionunits"]
        untiltime = self.config.params_sim["untiltime"]

        self.env.process(self.simclass.factory_widgetbatch_random_starting_time(num_widgets=num_widgets)) #30 is number of widgets
        self.env.run(until=untiltime)

    def run_visualization(self):
        self.visualizer = Visualizer(
            where_to_find_data=self.monitor.data_monitoring, 
            simuntil = self.config.params_sim["untiltime"])
        #self.plot = self.visualizer.return_plot()
        self.plots = self.visualizer.return_list_of_plots_for_ressources()


    def clear_monitoring_data(self):
        if hasattr(self, 'monitor'):
            for resource, data_list in self.monitor.data_monitoring.items():
                data_list.clear()     
        plt.close('all')       

class Monitor:
    def __init__(self, env, list_of_resources_to_be_monitored):
        self.env = env
        self.data_monitoring = {}
        
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
            
            ### added in - to be confirmed
            self.env.process(self.continuous_monitor(
                resource = resource_to_be_monitored, 
                target_datalist=self.data_monitoring[resource_to_be_monitored]
            ))
        
    
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
    
    # Attempt to replace monitor_func() / add into the Monitor loop
    def continuous_monitor(self, resource, target_datalist):
        while True:
            # Capture current state
            item = (
                self.env.now,  # Current time
                resource.count,  # Number of resources in use
                len(resource.queue)  # Current queue length
            )
            self.data_monitoring[resource].append(item)
            target_datalist.append(item)
            
            # Wait for a short time before next monitoring
            yield self.env.timeout(1)

class Visualizer:
    def __init__(self, where_to_find_data, simuntil):
        self.data = where_to_find_data
        self.simuntil = simuntil
        
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
        
        # print (inputdata)

        # Choose current color
        currentcolor = self.graphcolors[self.index_currentcolor % len(self.graphcolors)] #Take the index of the color (and make sure it doesnt go out of bounds)

        # Create the plot
        plt.step(self.timestamps, self.queue_lengths, where='post',
                 color = currentcolor,
                 label = f'Run {self.index_currentcolor +1}')
        plt.legend()

        # Set plot labels and limits
        #plt.title(ressourcename)
        plt.xlabel('Time')
        plt.ylabel('Resource Queue Length')
        
        if self.timestamps and self.queue_lengths:
            plt.xlim(0, self.simuntil + 5)
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


class Factory:  
    def factory_widgetbatch_random_starting_time(self, num_widgets):
        for i in range(num_widgets):  # Make n widgets
            self.env.process(self.process_definition_produce_one_widget(f'widget {i+1}'))
            yield self.env.timeout(random.randint(1, 3))  # Time between starting each widget


    ###### Concept for stepbased rewrite
    ### new INITROUTINE OF THE Factory (?) ###
    def __init__(self, input_env, parameterlist_ressourcebased_processsteps):
        self.env = input_env
        self.ressourcebased_processsteps = []

        for config in parameterlist_ressourcebased_processsteps:
            stepresource = simpy.Resource(
                self.env,
                capacity=config.params_ressource["ressourcecapacity"]
            )

            processstep_params = {
                "stepnumber": len(self.ressourcebased_processsteps),
                "stepname": config.params_ressource["ressourcename"],
                "stepresource": stepresource,                
                "timeneeded_step": config.params_ressource["time_produnit"]
            }

            self.ressourcebased_processsteps.append(RessourcebasedProcessstep(processstep_params))
    ### Ende INITROUTINE ###
        
    ### REWRITTEN Process "one widget"
    def process_definition_produce_one_widget(self, name):
        for ressourcebased_processstep in self.ressourcebased_processsteps:
            print(f"Minute {self.env.now}: {name} just entered step {ressourcebased_processstep.stepname}. Ressource queue is {len(ressourcebased_processstep.stepresource.queue)}")
            
            # Use yield with the request method
            req = ressourcebased_processstep.stepresource.request()
            yield req  # Wait until the step-resource is available
            
            try:
                print(f"Minute {self.env.now}: {name} starts using the resource for this step. Ressource queue is {len(ressourcebased_processstep.stepresource.queue)}")
                timeneeded_step = ressourcebased_processstep.timeneeded_step

                yield self.env.timeout(timeneeded_step)
                print(f"Minute {self.env.now}: {name} finished step {ressourcebased_processstep.stepname}. Ressource queue is {len(ressourcebased_processstep.stepresource.queue)}")
            finally:
                # Always release the resource
                ressourcebased_processstep.stepresource.release(req)


    

class ConfigProcessRessource:
    def __init__(self,  ressourcename, ressourcecapacity, time_produnit):
        self.params_ressource = {
            "ressourcename" : ressourcename,
            "ressourcecapacity" : ressourcecapacity,
            "time_produnit" : time_produnit
            }

class SimulationConfiguration:
    def __init__(self,  productionunits, simulationtime, ressourceconfigs:List[ConfigProcessRessource]):
        self.params_sim = {
            "untiltime": int(simulationtime),
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
    #The top level object that manages the handling and Input/Output logic with the webapp. Returning results and clearing the results.
    #Starts the actual simulation and data logic (Simulation Core, Monitor object and Visualizer)
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


#Sampleconfig for running a manual simulation. Currently only process with one resource
#samplesimconfig = SimulationConfiguration( 
#    productionunits = 50000,
#    simulationtime=480, 
#    ressourceconfigs = [
#        ConfigProcessRessource(
#            ressourcename="res1", 
#            ressourcecapacity=2,
#            time_produnit = 15
#            ),        
#        ConfigProcessRessource(
#            ressourcename="res2", 
#            ressourcecapacity=1,
#            time_produnit = 10
#            )
#        ]
#    )


#def testsim():
#    mysim = SimulationCore(samplesimconfig)
#    mysim.run_sim()
#    mysim.run_visualization()