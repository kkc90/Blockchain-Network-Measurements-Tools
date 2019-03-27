import plotly.graph_objs as go
import plotly as py

import matplotlib.pyplot as plt

import networkx as nx

from LSDSCoin import keychain
G = nx.random_geometric_graph(200, 0.125) # Example of Graph generation


def create_network(G):
    private_key = generate_key()

    storage_list = dict()
    for node in G.nodes():
        ip = node["ip"]
        pass
        storage = keychain.store.Storage(ip, bootstrap, miner, difficulty, private_key=private_key, modify_topology=True)


def plot_graph2(G, graph_name, filename=None):
    fig = plt.figure(graph_name)

    nx.draw(G)

    plt.legend()

    if filename is not None:
        plt.savefig(filename)


def plot_graph1(G, graph_name, filename=None):
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
        node_info = '# of connections: ' + str(len(adjacencies[1]))
        node_trace['text'] += tuple([node_info])

    fig = go.FigureWidget(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=graph_name,
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    if filename is not None:
        py.offline.plot(fig, filename=filename)
    else:
        py.offline.plot(fig)
