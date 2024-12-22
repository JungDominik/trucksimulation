import os
from flask import Flask, render_template, Response, request, redirect, url_for, session
from flask_session import Session
from sim import (
    run_sim_from_config_get_results, 
    SimulationConfiguration, 
    ConfigProcessRessource,
    SimulationManager)


num_ressourcebased_processsteps = 3

emptyconfig = SimulationConfiguration( 
    productionunits = 1, 
    ressourceconfigs = []
    )
for i in range(num_ressourcebased_processsteps):
    emptyprocessresource = ConfigProcessRessource(
        ressourcename=(str(i)),
        ressourcecapacity=1,
        time_produnit = 15
        )
    emptyconfig.ressourceconfigs.append(emptyprocessresource)

samplesimconfig2res = SimulationConfiguration( 
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
    
    print ("started in Index")
    #print(f"Current working directory: {os.getcwd()}")
    #print(f"Template folder: {os.path.join(os.getcwd(), 'templates')}")

    # ##### Start of testing: Creates a test base64 image --> Works
    # import io
    # import base64
    # from PIL import Image, ImageDraw
    # # Create a simple 100x100 red image
    # image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # RGB red
    # draw = ImageDraw.Draw(image)
    # draw.text((10, 40), "Test", fill=(255, 255, 255))  # Add some text for distinction

    # # Save the image to a BytesIO object
    # image_io = io.BytesIO()
    # image.save(image_io, format="PNG")
    # image_io.seek(0)  # Move to the beginning of the BytesIO buffer

    # # Encode the image as a base64 string and store it in the session
    # session["image"] = base64.b64encode(image_io.getvalue()).decode("utf-8")
    # ##### End of testing

    #Simply see if someone has already stored the picture in the session variable and it can be forwarded to show it  (by the user triggering the simulation and storing the image in the session variable). If not (because its the first time) forward nothing.
    #Note: It is not this methods job to trigger the creation of the picture.
    #plotimage = session.get("plotimage", None) 
    
    

    plotimages = session.get("plotimages", None) 

    
    return render_template("page.html", 
                           plotimages = plotimages, 
                           num_ressourcebased_processsteps = num_ressourcebased_processsteps
                           )


@app.route("/cleargraph", methods=["POST"])
def cleargraph():
    print("Clearingattempt")
    simmanager.clearplots()
    if "plotimages" in session:
        session["plotimages"] = []
    #print(session["simcore"])

    sim_results = simmanager.run_sim_from_config_get_results(runconfig=emptyconfig)
    session["plotimages"] = sim_results["plots"]

    return redirect("/")

@app.route("/submit_form", methods=["GET", "POST"])
def submit_form():
    print("Form submission received")
    print("Request method:", request.method)
    print("Form data:", request.form)
    #With this method listen constantly if someone gives the order to run the sim. 
    #If yes forward the parameters to the sim logic, take what it returns (the image) and put it in the sessionvar.
    #Then your job is done, you dont need to display it. Redirect to the main dashboard display. It will pick up the image out of the session var on its own.
    
    
    button = request.form.get("clear")
    print(button)


    formdata = request.form.to_dict()

    num_resources = int(formdata["num_resources"]) #Save the number of ressources / ressource parameters and use this info to read out all the resourceparameters
    productionunits = formdata["productionunits"]
    

    simconfig = SimulationConfiguration(
            productionunits = productionunits,
            ressourceconfigs=[]
            )
    
    for i in range (num_resources):
        resourceconfig = ConfigProcessRessource(
            ressourcename="res_"+str(i),
            ressourcecapacity=int(formdata["capacity_ressource_"+str(i)],),
            time_produnit = int(formdata["time_produnit_"+str(i)],)
            )
        simconfig.ressourceconfigs.append(resourceconfig)
    
    
    sim_results = simmanager.run_sim_from_config_get_results(runconfig=simconfig)
    session["plotimages"] = sim_results["plots"]
    
    

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

