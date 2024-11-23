import os
from flask import Flask, render_template, Response, request, redirect, url_for, session
from flask_session import Session
from sim import run_sim_from_config_get_results, SimulationConfiguration



app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["Testing"] = True
app.config["DEBUG"] = True
Session(app)

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
    plotimage = session.get("plotimage", None) 

    
    return render_template("page.html", plotimage = plotimage)

@app.route("/submit_form", methods=["GET","POST"])
def submit_form():
    #With this method listen constantly if someone gives the order to run the sim. 
    #If yes forward the parameters to the sim logic, take what it returns (the image) and put it in the sessionvar.
    #Then your job is done, you dont need to display it. Redirect to the main dashboard display. It will pick up the image out of the session var on its own.
    
    print ("jetzt in submit  form")
    productionunits = request.form.get("productionunits")
    num_resources = request.form.get("num_resources")
    
    #print(formdata_1)
    #return render_template("page.html") #Muss was anderes, nämlich dass das Bild angezeigt wird
    #return redirect("/") # Redirect scheint zu gehen --> Evtl als nächstes redirect verarbeitung der Inputs durch sim. 
    #return redirect(url_for("plot_png", param1=param1, param2=param2)) ## Geht aber returnt nur das Plotbild, nicht Dashboard
    
    runconfig = SimulationConfiguration(productionunits=productionunits, num_resources=num_resources)

    # Possibly unneccessarily complex
    sim_results = run_sim_from_config_get_results(runconfig=runconfig)
    session["plotimage"] = sim_results["plot"]

    return redirect("/")


### Possibly not needed
# @app.route("/plot.png")
# def plot_png():
#     print ("starting plot_png")
#     #TODO: Get from user the params
#     #possibly like this
#     param1 = request.args.get("param1", type = str)
#     param2 = request.args.get("param2", type = str)

#     print ("Jetzt params")
#     print (str(param1))
#     print (str(param2))
#     print ("Das waren die params")

#     output_plot = ulation_and_generate_plot(param1, param2)

#     session["image"] = output_plot

#     # return Response(output_plot.getvalue(), mimetype="image/png") #Verarbeitet schonmal input korrekt und gibt den input-basierten Plot zurück. TODO: Plot als Element in einer Seite
#     redirect("/")

if __name__ == "__main__":
    app.run(debug=True)



##### Todo 27. Oct:
# Restructure app
# In HTML: Start sim from runbutton, generates all outputs & stores in the session var
# Then the HTML img's pull the output from the session filesystem storage / session variable