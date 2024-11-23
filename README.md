CS50 Final Project: Simulation Web App

- Requirement: 
Input - User can control simulation from a web app
Output - User sees simulation result as matplotlib plot. Also, user sees real-time simulation events happening (=console output)

- Approach: 

Project

app.py: Flask script, that administrates everything
sim.py: Simulation extracted out into separate file. Runs simulation based on user inputs and creates output (result plot .jpg-images and realtime console simulation run)
Folder: static/images: Holds the images --> HTML page loads them



Folder structure
/app.py <-- Flask app
/sim.py <-- Simulation
/static/images/plot.jpg <-- Gets updated with each simulation run
/templates/ <--> Folder that holds the webpage templates
