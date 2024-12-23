#* app.py: Flask script which administrates the following: Display of web app, management of input data, triggering simulation data, output generation based on simulation data
#    * This is the central file and to be started from consule using "flask run"
#    * Simulation logic is abstracted away into sim.py as much as possible. The exception being the "SimulationConfiguration" objects which package the parameter input coming from the user through the webapp and being passed to the simulation manager object.
#    * app.py interacts with sim.py through the API which sim.py exposes ("Pass configuration and receive results")


import os
from flask import Flask, render_template, Response, request, redirect, url_for, session
from flask_session import Session
from sim import ( 
    SimulationConfiguration, 
    ConfigProcessRessource,
    SimulationManager)


num_resources_default = 3

emptyconfig = SimulationConfiguration( 
    productionunits = 1, 
    simulationtime=480,
    ressourceconfigs = []
    )
for i in range(num_resources_default):
    emptyprocessresource = ConfigProcessRessource(
        ressourcename=(str(i)),
        ressourcecapacity=1,
        time_produnit = 15
        )
    emptyconfig.ressourceconfigs.append(emptyprocessresource)

samplesimconfig2res = SimulationConfiguration( 
    productionunits = 50000, 
    simulationtime=480,
    ressourceconfigs = [
        ConfigProcessRessource(
            ressourcename="res1", 
            ressourcecapacity=2,
            time_produnit = 15
            ),        
        ConfigProcessRessource(
            ressourcename="res2", 
            ressourcecapacity=1,
            time_produnit = 15
            )
        ]
    )


app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["Testing"] = True
app.config["DEBUG"] = True
Session(app)



simmanager = SimulationManager()

@app.route("/")
def index():
    ###Show the dashboard. Check if the user has in the session previously ran the simulation and you find the picture in the session var, then display it 
    #Simply see if someone has already stored the picture in the session variable and it can be forwarded to show it  (by the user triggering the simulation and storing the image in the session variable). If not (because its the first time) forward nothing.
    #Note: It is not this route's job to trigger the creation of the picture. This will be instead done by "/submit_form".
    
    plotimages = session.get("plotimages", None) 

    return render_template("page.html", 
                           plotimages = plotimages, 
                           num_ressourcebased_processsteps = num_resources_default
                           )


@app.route("/cleargraph", methods=["POST"])
def cleargraph():
    print("Clearingattempt")
    simmanager.clearplots()
    if "plotimages" in session:
        session["plotimages"] = []
    
    sim_results = simmanager.run_sim_from_config_get_results(runconfig=emptyconfig)
    session["plotimages"] = sim_results["plots"]

    return redirect("/")

@app.route("/submit_form", methods=["GET", "POST"])
def submit_form():
    #With this method listen constantly if someone gives the order to run the sim. 
    #If yes forward the parameters to the sim logic, take what it returns (the image) and put it in the sessionvar.
    #Then your job is done, you dont need to display it. Redirect to the main dashboard display. It will pick up the image out of the session var on its own.
    print("Form submission received")
    print("Request method:", request.method)
    print("Form data:", request.form)
     
    
    button = request.form.get("clear")
    print(button)


    formdata = request.form.to_dict()
    print(formdata)

    num_resources = int(formdata["num_resources"]) #Save the number of ressources / ressource parameters and use this info to read out all the resourceparameters
    productionunits = formdata["productionunits"]
    simulationtime = formdata["simulationtime"]
    

    simconfig = SimulationConfiguration(
            productionunits = productionunits,
            simulationtime=simulationtime,
            ressourceconfigs=[]
            )
    
    for i in range (num_resources):
        resourceconfig = ConfigProcessRessource(
            ressourcename="res_"+str(i),
            ressourcecapacity=int(formdata["capacity_ressource_"+str(i)],),
            time_produnit = int(formdata["time_produnit_"+str(i)],)
            )
        simconfig.ressourceconfigs.append(resourceconfig)
    
    ###The below is the key expression that links everything together: 
    # The web app has packaged the user input of simulation parameters into the expected datastructure of type SimulationConfiguration. 
    # Via the API which sim.py exposes as part of its SimulationManager object, it feeds it into sim.py, which calculates it and returns the results in the following way.
    # The simulationManager sets up a simulation core
    sim_results = simmanager.run_sim_from_config_get_results(runconfig=simconfig)
    session["plotimages"] = sim_results["plots"]
    
    

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

