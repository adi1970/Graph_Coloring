from flask import Flask, render_template, request
import networkx as nx
import random
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

def visualize_graph(G, node_colors, algorithm_name):
    pos = nx.spring_layout(G)
    labels = {node: node for node in G.nodes()}

    nx.draw(G, pos, with_labels=True, labels=labels, node_color=node_colors, cmap=plt.cm.rainbow)
    plt.title(f'{algorithm_name} Coloring')

    # Save the plot to a BytesIO object
    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)

    # Encode the image to base64 for embedding in HTML
    img_encoded = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    plt.close()

    return img_encoded

def greedy_coloring(graph):
    node_colors = {}

    for node in graph.nodes():
        used_colors = set(node_colors[neighbor] for neighbor in graph.neighbors(node) if neighbor in node_colors)
        available_colors = set(range(len(graph))) - used_colors
        node_colors[node] = min(available_colors)

    return node_colors

def backtracking_coloring(graph):
    def is_safe(node, color):
        for neighbor in graph.neighbors(node):
            if node_colors[neighbor] == color:
                return False
        return True

    def backtrack(node):
        if node == len(graph):
            return True

        for color in range(len(graph)):
            if is_safe(node, color):
                node_colors[node] = color

                if backtrack(node + 1):
                    return True

                node_colors[node] = -1

        return False

    node_colors = {node: -1 for node in graph.nodes()}
    backtrack(0)
    return node_colors

def generate_random_graph(num_nodes, probability):
    G = nx.erdos_renyi_graph(num_nodes, probability)
    return G

def generate_complete_graph(num_nodes):
    G = nx.complete_graph(num_nodes)
    return G

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_nodes = int(request.form['num_nodes'])
        probability = float(request.form['probability'])
        graph_type = request.form['graph_type']
        coloring_algorithm = request.form['coloring_algorithm']

        if graph_type == 'random':
            graph = generate_random_graph(num_nodes, probability)
        elif graph_type == 'complete':
            graph = generate_complete_graph(num_nodes)
        else:
            return render_template('index.html', error='Invalid graph type')

        plots = {}

        # Greedy Coloring
        if coloring_algorithm == 'greedy':
            greedy_colors = greedy_coloring(graph)
            plots['greedy'] = visualize_graph(graph, list(greedy_colors.values()), 'Greedy')
        elif coloring_algorithm == 'backtracking':
            backtracking_colors = backtracking_coloring(graph)
            plots['backtracking'] = visualize_graph(graph, list(backtracking_colors.values()), 'Backtracking')
            
        # Inside the index function

        if 'probability' in request.form and request.form['probability']:
            probability = float(request.form['probability'])
        else:
          probability = 1  # Set a default value if probability is not provided

        return render_template('index.html', plots=plots)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
