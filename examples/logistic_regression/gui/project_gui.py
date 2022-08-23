from tkinter import *

from dot_converter import DotConverter

from dag_test import DAG_FILE, order_edge_predictions, data

#ordered_edges = order_edge_predictions()

#ordered_edges = {'delivery_type': 0.03575459348292154, 'length': 0.06103142107123971, 'S1': 0.14477390855858718, 'S2': 0.2209859128621069, 'delivery_location': 0.3259888140591345, 'S3': 0.4918543484480269}

# Get necessary graph data

# class GUI():
    
#     def __init__(self) -> None:
#         self.root = Tk()
#         self.canvas = Canvas(root, width = 1000, height = 400)      
#         self.canvas.pack()      
#         img = PhotoImage(file="output.png")      
#         self.canvas.create_image(20,20, anchor=NW, image=img)




graph_data = DotConverter()

graph_data.create_graph(DAG_FILE)

# graph_data.set_edge_colours(ordered_edges)

# edges = graph_data.get_graph()

graph_data.write_png()

# important_edges = []

# # Collect all relevant (coloured) edges
# for edge in edges.get_edges():
#     # Cast to str from Edge object
#     edge_str = str(edge)
#     if 'color=red' in edge_str:
#         important_edges.append((edge_str, 1))
#     elif 'color=yellow' in edge_str:
#         important_edges.append((edge_str, 2))
#     elif 'color=green' in edge_str:
#         important_edges.append((edge_str, 3))
             
# Sort list

# important_edges.sort(key=lambda e:e[1])
# print(important_edges)

def get_possible_col_values(data):
    possible_col_vals = {}
    for col in data.columns:
        if data[col].dtype != 'float':
            possible_col_vals[col] = list(data[col].unique())

    return possible_col_vals

def display_shipment():
    shipment = []
    print(clicked.get())
    # for button in buttons:
    #     shipment.append(button)
    #     print(clicked.get())
    # print(shipment)
    # print('ass')

possible_vals = get_possible_col_values(data)

print(possible_vals)

root = Tk()

root.title('CITCOM Nuclear Detector')

canvas = Canvas(root, width = 1000, height = 400)      
canvas.pack()      
img = PhotoImage(file="output.png")      
canvas.create_image(20,20, anchor=NW, image=img)


buttons = []

for k in possible_vals:
    clicked = StringVar()
    print(possible_vals[k][0])

    clicked.set(possible_vals[k][0])

    option_menu = OptionMenu(root, clicked, *possible_vals[k], command=display_shipment)

    print(option_menu)

    buttons.append(option_menu)

for b in buttons:
    b.pack()

MyButton1 = Button(root, text="Submit", width=10, command=display_shipment)
MyButton1.pack()

root.mainloop()

# heading = Label(text='Edge ranking')
# red_key = Label(text='Red = High Contribution')
# amber_key = Label(text='Amber = Moderate Contribution')
# green_key = Label(text='Green = Minor Contribution')

# # Edge text
# # y_pos = 160
# # for sorted_edge in important_edges:
# #     text_label = sorted_edge[0]
# #     bracket_index = text_label.index('[')-2
# #     text_label = text_label[0:bracket_index]
# #     edge_text = Label(text=text_label)
# #     edge_text.place(x=780,y=y_pos)
# #     y_pos += 20


# # heading.place(x=800,y=20)
# # red_key.place(x=750,y=40)
# # amber_key.place(x=750,y=60)
# # green_key.place(x=750,y=80)

# root.mainloop()