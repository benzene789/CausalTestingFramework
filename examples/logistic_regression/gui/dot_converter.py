import pydot

class DotConverter:
    
    def __init__(self):
        self.graph = None

    def create_graph(self, file):
        graphs = pydot.graph_from_dot_file(file)
        self.graph = graphs[0]

        self.graph.set_bgcolor("white")

        # self.graph.get_edges()[1].set_color('blue')
        # self.graph.get_edges()[2].set_color('red')
        # self.graph.get_edges()[3].set_color('green')
        # self.graph.get_edges()[4].set_color('yellow')

    def get_dot_file(self):
        return self.graph
    
    def write_png(self):
        self.graph.write_png("output.png")


''' PLAN

Data set comes in, this module will work with the causality module that will work on data/ ranks causes

Rank the causes that set off the alarm

Red = most problematic, yellow = slight concern, green = not so much

create image and export to GUI

'''