from tkinter import *
import tkinter

from dot_converter import DotConverter

from dag_test import DAG_FILE, order_edge_predictions

import pandas as pd

import sys

import time as tm

# Get necessary graph data

start = tm.time()

class GUI():
    
    def __init__(self, dag_file, csv) -> None:
        self.root = Tk()
        self.graph = DotConverter()
        self.DAG_FILE = dag_file
        self.possible_col_values = {}
        self.data = pd.read_csv(csv)
        # Remove 'unamed' column
        self.data = self.data.loc[:, ~self.data.columns.str.contains('^Unnamed')]
        self.shipment = []
        self.canvas = Canvas(self.root, width = 1300, height = 500)
        self.img = None
        self.buttons = []
        self.button_vals = []
        self.ordered_edges = {}
        self.important_edges = []
        self.edges = None
        self.shipment_df = pd.DataFrame()
        
    def create_graph(self):
        self.graph.create_graph(self.DAG_FILE)
        self.graph.write_png()
        
    def get_possible_col_values(self):
        for col in self.data.columns:
            if self.data[col].dtype != 'float':
                self.possible_col_values[col] = list(self.data[col].unique())
            # For floating values
            else:
                self.possible_col_values[col] = []
                
    def display_gui(self):
        self.create_graph()
        self.get_possible_col_values()

        self.root.title('CITCOM Nuclear Detector')
        button_labels = []
        self.canvas.pack()      
        self.img = PhotoImage(file="output.png")      
        self.canvas.create_image(20,20, anchor=NW, image=self.img)
        
        for col_vals in self.possible_col_values:
            
            if self.data[col_vals].dtype == 'float':
                # TextBox Creation
                inputtxt = Text(self.root,
                                height = 1,
                                width = 5)
                self.buttons.append(inputtxt)
                self.button_vals.append(inputtxt)
            else:
                clicked = StringVar()

                clicked.set(self.possible_col_values[col_vals][0])

                option_menu = OptionMenu(self.root, clicked, *self.possible_col_values[col_vals])

                self.buttons.append(option_menu)
                self.button_vals.append(clicked)

            button_labels.append(Label(self.root, text=col_vals))

        print(self.button_vals)

        for button in range(0, len(self.buttons)):
            button_labels[button].pack(side=LEFT)
            self.buttons[button].pack(side=LEFT)
            
        MyButton1 = Button(self.root, text="Submit", width=10, command=self.run_shipment)
        MyButton1.pack()
        
        heading = Label(text='Edge ranking')
        red_key = Label(text='Red = High Contribution')
        amber_key = Label(text='Amber = Moderate Contribution')
        green_key = Label(text='Green = Minor Contribution')

        heading.place(x=1000,y=20)
        red_key.place(x=950,y=40)
        amber_key.place(x=950,y=60)
        green_key.place(x=950,y=80)

        self.root.mainloop()
        
    def run_shipment(self):
            
        for val in self.button_vals:
            if isinstance(val, tkinter.Text):
                self.shipment.append(float(val.get(1.0, "end-1c")))
            else:
                other = val.get()
                if(other == '1' or other == '0'):
                    self.shipment.append(int(other))
                else:
                    self.shipment.append(other)
        
        df_columns = self.possible_col_values.keys()
        self.shipment_df = pd.DataFrame([self.shipment], columns=df_columns)
                
        self.shipment = []
        self.get_ordered_edges()
        self.colour_edges()
        
    def get_ordered_edges(self):
        self.ordered_edges = {'weight': 0.01216715599137369, 'country': 0.05132754239279308, 'content': 0.0568774476997031, 'plane_transport': 0.08514658977367168, 'S1': 0.24569181638837456, 'S2': 0.3230419397194918, 'S3': 0.42156159338025667}

        #self.ordered_edges = order_edge_predictions(self.shipment_df)

    def colour_edges(self):
        self.graph.set_edge_colours(self.ordered_edges)
        
        self.edges = self.graph.get_graph()
        
        # Collect all relevant (coloured) edges
        for edge in self.edges.get_nodes():
            # Cast to str from Edge object
            edge_str = str(edge)
            if 'color=red' in edge_str:
                self.important_edges.append((edge_str, 1))
            elif 'color=yellow' in edge_str:
                self.important_edges.append((edge_str, 2))
            elif 'color=green' in edge_str:
                self.important_edges.append((edge_str, 3))
                
        # Sort list
        self.important_edges.sort(key=lambda e:e[1])
        print(self.important_edges)
        
        # Edge text
        y_pos = 120
        for sorted_edge in self.important_edges:
            text_label = sorted_edge[0]
            bracket_index = text_label.index('[')-1
            text_label = text_label[0:bracket_index]
            edge_text = Label(text=text_label)
            edge_text.place(x=1000,y=y_pos)
            y_pos += 20

        # Delete the canvas image
        self.canvas.delete('all')
 
        self.graph.write_png()   
        self.img = PhotoImage(file="output.png")      
        self.canvas.create_image(20,20, anchor=NW, image=self.img)

        print('RESET')
        self.ordered_edges = {}
        self.important_edges = []

        end = tm.time()

        print('TAKEN ', end-start, ' SECONDS')

        self.root.mainloop()

if __name__ == "__main__":
    DAG_FILE = sys.argv[1]
    csv = sys.argv[2]
    gui = GUI(DAG_FILE, csv)
    
    
    gui.display_gui()
    