import networkx as nx
from networkx.drawing.nx_agraph import read_dot

import pydot

class DotConverter:
    
    def __init__(self):
        self.graph = None

    def create_graph(self, file):
        
        graphs = pydot.graph_from_dot_file(file)

        self.graph = graphs[0]

        # self.graph.get_edges()[1].set_color('blue')
        # self.graph.get_edges()[2].set_color('red')
        # self.graph.get_edges()[3].set_color('green')
        # self.graph.get_edges()[4].set_color('yellow')

    def get_graph(self):
        return self.graph

    def set_edge_colours(self, edges, layer_1_size):
        # RED EDGES: 0-.3
        # YELLOW EDGES: .3 - .6
        # GREEN EDGES 0.6 - 1

        colour_map = []

        # Iterate through edges and get corresponding colours (rank edges)
        
        for edge in self.graph.get_edges():
            str_edge = str(edge)
            print(str_edge)
            for ordered in edges:
                # Get the '->'
                arrow_i = str_edge.index('->')
                first_part = str_edge[0:arrow_i]
                if ordered in first_part:

                    if edges[ordered] < 0.03:
                        colour_map.append('red')
                    elif edges[ordered] > 0.03 and edges[ordered] < 0.06:
                        colour_map.append('yellow')
                    elif edges[ordered] > 0.06:
                        colour_map.append('green')
                    print(colour_map)

        # Now colour the edges
        for e in range(0, layer_1_size):
            print(e)
            print(self.graph.get_edges()[e])
            print(colour_map[e])
            self.graph.get_edges()[e].set_color(colour_map[e])
            
        print(self.graph)
    
    def write_png(self):
        self.graph.write_png("output.png")


''' PLAN

Data set comes in, this module will work with the causality module that will work on data/ ranks causes

Rank the causes that set off the alarm

Red = most problematic, yellow = slight concern, green = not so much

create image and export to GUI

'''