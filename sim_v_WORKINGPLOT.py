###Simpy Simulation app here
import simpy
import matplotlib.pyplot as plt
import numpy as np



###Exports the result as .png plot to be displayed in html


# Approach 2: In-memory with ByteIO-Buffer


#sim.py exposes an API to run simulation based on input and generate results (eg plot)
#Function which app.py calls - sim.py will generate a plot
def run_simulation_and_generate_plot(param1, param2):
    #pass 'TODO'

    print ("Jetzt kommen params aus Methodendefinition in sim.py")
    print (str(param1))
    print (str(param2))
    print ("Das waren params aus Methodendefinition in sim.py")

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [int(param1), int(param2), int(param1) + int(param2)])

    import io
    output = io.BytesIO()
    plt.savefig(output, format="png")
    output.seek(0) #DJu: Taken from the boilerplate code. Purpose "Rewind the buffer so it can be read from the beginning" - ok fine.

    return output