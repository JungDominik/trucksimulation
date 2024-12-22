# CS50 Final Project: Process Simulation Web App
#### Video Demo:  https://youtu.be/vNqZQv4Y_jY
#### Description below

**High level description**
* The following project is a webapp which allows the user to simulate production processes over time. 
* The process to be simulated consists of ressources such as machines, staff team, computers etc. which process the production units (eg. "widgets") moving through them.  Each ressource can be configured with its processing time and its capacity (eg. unit capacity of a machine, staff in a team, slots in an oven).
    * Key logic is the resourcebased process step: A process that requires production units to pass through a step with a lead time, provided that it has free capacity. 
    * If no capacity is available, a queue forms until the resource capacity frees up.
* The simulation is aimed at process managers who are responsible for planning the process details such that the capacity is optimally utilized.
* Specifically of interest is the development of the queue length in a process step over time. Based on the development of this KPI, the process manager can decide whether a change needs to be made to the capacity of this process step.

**Requirements**
* Flexibility to adapt to any linear production process based on capacity-restricted steps. Number of steps to be chosen by user.
* User input - User can control simulation from a web app. This means entering the parameterization of the simulation in two steps.
    * Input of parameters on level of simulation (timespan to be simulated, units to be produced)
    * Input of parameters on level of process step / resource: Lead time in step and capacity of step
* Output - User sees simulation result (=queue length) plot over simulation time. 


**Usage**
* Through the UI the users enter the parameters. All parameters need to be entered. The HTML UI will ensure that all parameter fields are filled with positive integers.
* The first type of parameters is on level of general simulation configuration: (timespan to be simulated, units to be produced)
* The second type of parameters concerns configuration of each individual resource/process step: Lead time in step and capacity of step
* The user can then start and simulate, which will fill the queue graphs for earch resource/process step.
* The user can reset the simulation with the button "Clear graph".

** How to download and install **
TODO
- Copy the repository code to a directory on your machine
- Start the web app from the terminal using 
```
flask run
```

**Approach/Structuring**
* app.py: Flask script which administrates the following: Display of web app, management of input data, triggering simulation data, output generation based on simulation data
    * This is the central file and to be started from consule using "flask run"
    * Simulation logic is abstracted away into sim.py as much as possible. The exception being the "SimulationConfiguration" objects which package the parameter input coming from the user through the webapp and being passed to the simulation manager object.
    * app.py interacts with sim.py through the API which sim.py exposes ("Pass configuration and receive results")
* sim.py: Simulation extracted out into separate file. Runs simulation based on user inputs and creates output (result plot .jpg-images and realtime console simulation run)
    * Main access point is the API ("Pass configuration and receive results")
    * Structured into simulation manager which administrates simulation core, a data monitor which stores timestamp data during the process of the simulation and the visualization which turns the data into plots.
    * Simulation logic is based on the Discrete Event Simulation paradigm which is a standard paradigm for industrial processes. It utilizes the SimPy package.
    * Plot generation utilizes matplotlib library
    * Extraction of plot images to the webapp works by converting them to base64 encoded strings
* Folder: static/images: Holds the images --> HTML page loads them


**Folder structure**
* /app.py <-- Flask app
* /sim.py <-- Simulation
* /static/images/plot.jpg <-- Gets updated with each simulation run
* /templates/ <--> Folder that holds the webpage templates

**Roadmap**

The following future extensions are in consideration

* Simulation log: Provide simulation log to the user on level of event (eg. "Minute x: Widget y is entering production step z")
* Process diagram: Dynamically generate the process diagram based on user configuration of the process (using PlantUML diagram)
* Additional options to generate the generation of widgets, eg. based on a probability distribution over the length of the simulation time.

**Authors and acknowledgment**
Author is Dominik Jung, as part/final project of the Harvard/EdX online MOOC CS50x: Introduction to Computer Science. Author can be reached at dominikjung[at]gmx.de and or[ linkedin.com/JungDominik](https://www.linkedin.com/in/jungdominik/)

The project drew on the usage of LLMs such as OpenAI ChatGPT and Anthropic Claude for the following usecases: Debating architecture decisions, debugging.