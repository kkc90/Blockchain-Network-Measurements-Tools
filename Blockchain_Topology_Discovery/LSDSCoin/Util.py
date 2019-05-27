import ipaddress

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import plotly as py
import plotly.graph_objs as go

from LSDSCoin import keychain

GRAPHS_GENERATORS = {
    "Random": nx.random_geometric_graph,
}

network_ip = "127.0.0.0/8"
mining_probability = 0.3
time_before_transaction_distribution = (5, 10)
init_difficulty = 10


def generate_graph(graph_name, nodes_nb, **kwargs):
    global GRAPHS_GENERATORS

    if graph_name in GRAPHS_GENERATORS:
        G = GRAPHS_GENERATORS[graph_name](nodes_nb, **kwargs)
    else:
        raise Exception("Error : Unknown type of graph - " + graph_name + ".")

    return G


def init_network(G, network_ip, mining_probability, time_before_transaction_distribution, init_difficulty,
                   monitor=True):
    ips = iter(ipaddress.IPv4Network(network_ip))

    host_ip = str(next(ips))

    monitor_ip = str(next(ips))
    monitor_node_id = len(G)
    peer_list = list()

    """
        Initialization of the Monitoring Node
    """
    if monitor is True:
        G.add_node(monitor_node_id)
        G.nodes[monitor_node_id]["ip"] = monitor_ip
        G.nodes[monitor_node_id]["pos"] = [0, 0]

    for node_id in G.nodes():
        node = G.nodes[node_id]

        node["ip"] = str(next(ips))

        if monitor is True:
            G.add_edge(monitor_node_id, node_id)

        peer_list.append(node["ip"])

    if monitor is True:
        private_key = keychain.Util.generate_key()

        G.nodes[monitor_node_id]["storage"] = keychain.monitor.Storage(
            src_ip=monitor_ip,
            src_port=8333,
            src_service=keychain.Network.Protocol.Protocol_Constant.NODE_NETWORK,
            network=keychain.Network.Protocol.Protocol_Constant.MAINNET_MAGIC_VALUE,
            bootstrap=peer_list,
            difficulty=init_difficulty,
            private_key=private_key,
            modify_topology=False)

    for node_id in G.nodes():
        if node["ip"] != monitor_node_id:
            node = G.nodes[node_id]
            private_key = keychain.Util.generate_key()

            bootstrap = [G.nodes[adj_id]["ip"] for adj_id in G[node_id]]

            miner = np.random.choice([True, False], p=[mining_probability, (1 - mining_probability)])

            # Use of a log-normal distribution to have only positive values -->
            time_before_transaction = int(np.random.lognormal(time_before_transaction_distribution[0], time_before_transaction_distribution[1]))

            node["storage"] = keychain.store.Storage(
                src_ip=node["ip"],
                src_port=8333,
                src_service=keychain.Network.Protocol.Protocol_Constant.NODE_NETWORK,
                network=keychain.Network.Protocol.Protocol_Constant.MAINNET_MAGIC_VALUE,
                bootstrap=bootstrap,
                miner=miner,
                difficulty=init_difficulty,
                monitor=False,
                time_before_transaction_distribution=time_before_transaction_distribution,
                private_key=private_key,
                modify_topology=False)


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


def plot_graph2(G, graph_name, filename=None):
    fig = plt.figure(graph_name)

    nx.draw(G)

    plt.legend()

    if filename is not None:
        plt.savefig(filename)
