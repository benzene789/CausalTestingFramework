from tkinter import *

from dot_converter import DotConverter

from dag_test import order_edge_predictions

ordered_edges = order_edge_predictions()

#ordered_edges = {'content': 0.01879569949683063, 'country': 0.05132754239279308, 'plane_transport': 0.08514658977367168, 'weight': 0.09630454351271467, 'S1': 0.267426944694903, 'S2': 0.3230419397194918, 'S3': 0.42156159338025667}

# Get necessary graph data
graph_data = DotConverter()

graph_data.create_graph("./dag.dot")

graph_data.set_edge_colours(ordered_edges)

edges = graph_data.get_graph()

graph_data.write_png()

important_edges = []

# Collect all relevant (coloured) edges
for edge in edges.get_edges():
    # Cast to str from Edge object
    edge_str = str(edge)
    if 'color=red' in edge_str:
        important_edges.append((edge_str, 1))
    elif 'color=yellow' in edge_str:
        important_edges.append((edge_str, 2))
    elif 'color=green' in edge_str:
        important_edges.append((edge_str, 3))
             
# Sort list

important_edges.sort(key=lambda e:e[1])
print(important_edges)

root = Tk()

root.title('CITCOM Nuclear Detector')

canvas = Canvas(root, width = 1000, height = 400)      
canvas.pack()      
img = PhotoImage(file="output.png")      
canvas.create_image(20,20, anchor=NW, image=img)      

heading = Label(text='Edge ranking')
red_key = Label(text='Red = High Contribution')
amber_key = Label(text='Amber = Moderate Contribution')
green_key = Label(text='Green = Minor Contribution')

# Edge text
y_pos = 160
for sorted_edge in important_edges:
    text_label = sorted_edge[0]
    bracket_index = text_label.index('[')-2
    text_label = text_label[0:bracket_index]
    edge_text = Label(text=text_label)
    edge_text.place(x=780,y=y_pos)
    y_pos += 20


heading.place(x=800,y=20)
red_key.place(x=750,y=40)
amber_key.place(x=750,y=60)
green_key.place(x=750,y=80)

root.mainloop()