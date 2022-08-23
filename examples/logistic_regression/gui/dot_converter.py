import pydot

class DotConverter:
    
    def __init__(self):
        self.graph = None

    def create_graph(self, file):
        
        graphs = pydot.graph_from_dot_file(file)

        self.graph = graphs[0]

        self.graph.set_bgcolor("antiquewhite")


    def get_graph(self):
        return self.graph

    def set_edge_colours(self, edges):
        # RED EDGES: 0-.3
        # YELLOW EDGES: .3 - .6
        # GREEN EDGES 0.6 - 1

        colour_map = []

        # Iterate through edges and get corresponding colours (rank edges)

        for ordered in edges:
            print(ordered)
        
        for edge in self.graph.get_edges():
            str_edge = str(edge)
            for ordered in edges:
                # Get the '->'
                arrow_i = str_edge.index('->')
                first_part = str_edge[0:arrow_i]
                if ordered in first_part:
                    if edges[ordered] < 0.04:
                        colour_map.append('red')
                    elif edges[ordered] > 0.04 and edges[ordered] < 0.07:
                        colour_map.append('yellow')
                    elif edges[ordered] > 0.07:
                        colour_map.append('green')

        # Now colour the edges
        for c in range(0, len(self.graph.get_edges())):
            self.graph.get_edges()[c].set_color(colour_map[c])
            
    def write_png(self):

        self.graph.write_png("output.png")
