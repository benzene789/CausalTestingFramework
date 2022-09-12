import pydot

class DotConverter:
    
    def __init__(self):
        self.graph = None

    def create_graph(self, file):
        
        graphs = pydot.graph_from_dot_file(file)

        self.graph = graphs[0]

        self.graph.set_bgcolor("grey")


    def get_graph(self):
        return self.graph

    def set_edge_colours(self, nodes):
        # RED EDGES: 0-.035
        # YELLOW EDGES: .035 - .07
        # GREEN EDGES  > 0.07

        colour_map = []

        # Iterate through edges and get corresponding colours (rank edges)

        for node in nodes:
            if nodes[node] < 0.035:
                colour_map.append((node, 'red', nodes[node]))
            elif nodes[node] > 0.035 and nodes[node] < 0.07:
                colour_map.append((node, 'yellow', nodes[node]))
            elif nodes[node] > 0.07:
                colour_map.append((node, 'green', nodes[node]))

        # Now colour in the nodes
        for n in colour_map:
            self.graph.get_node(n[0])[0].set_color(n[1])
            self.graph.get_node(n[0])[0].set_label(n[0] + ': '+ str(round(n[2], 3)))
     
    def write_png(self):
        self.graph.write_png("output.png")
