from plantuml import PlantUML

def generate_process_diagram(num_resources):
    # Validate input
    if num_resources < 1:
        raise ValueError("Number of resources must be at least 1.")
    
    # Create PlantUML diagram content
    diagram = "@startuml\n"
    diagram += "skinparam direction horizontal\n"
    
    # Create process steps with resources
    for i in range(1, num_resources + 1):
        diagram += f"state Step{i} as \"Step {i}\\nResource {i}\"\n"
    
    # Connect the steps
    for i in range(1, num_resources):
        diagram += f"Step{i} --> Step{i+1}\n"
    
    diagram += "@enduml"
    return diagram

# Example usage
num_resources = 5  # Replace with the desired number of steps/resources
diagram_code = generate_process_diagram(num_resources)

# Print the PlantUML code
print(diagram_code)

simple_diagram_code = """
@startuml
Alice -> Bob: Hello
@enduml
"""

# Optional: To generate and view the diagram, use a PlantUML server or local setup
# Replace 'http://www.plantuml.com/plantuml' with your local PlantUML server if needed
server = PlantUML(url="http://www.plantuml.com/plantuml")
diagram_file = "process_diagram.png"
with open(diagram_file, "wb") as f:
    f.write(server.processes(diagram_code))

diagram_file = "process_diagram_testtest.png"
with open(diagram_file, "wb") as f:
    f.write(server.processes(simple_diagram_code))
#print(f"Diagram saved to {diagram_file}.")



def generate_diagram(user_input):
      # Parse user input to create PlantUML code
  plantuml_code = f"""
  @startuml
  participant User
  participant System

  User -> System: Send request
  System -> User: Process request
  @enduml
  """

  # Generate the diagram
  img = PlantUML.Image(plantuml_code)
  img.make_image(format="png")

  # Display or save the image
  img.show()