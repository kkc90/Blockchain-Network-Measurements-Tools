import random
import math
import json
import itertools
import ipaddress
import datetime
import pandas as pd

import numpy as np
import networkx as nx

import plotly as py
import plotly.graph_objs as go

import matplotlib as mpl
import matplotlib.pyplot as plt


# Matplotlib Constant

TICK_FONTSIZE = 15
LABEL_FONTSIZE = 15
LEGEND_FONTSIZE = 13


def generate_random_graph(nb_nodes):
    G = nx.Graph()

    nodes = [i for i in range(0, nb_nodes)]
    G.add_nodes_from(nodes)

    possible_connections = set(itertools.combinations(nodes, 2))

    while not nx.is_connected(G):
        connection = possible_connections.pop()

        G.add_edge(connection[0], connection[1])

    return nx.to_directed(G)


GRAPHS_GENERATORS = {
    "Gaussian Random Partition": nx.gaussian_random_partition_graph,
    "Caveman": nx.connected_caveman_graph,
    "Karate Club": nx.karate_club_graph,
    "Davis Southern Women Club": nx.davis_southern_women_graph,
    "Florentine Families": nx.florentine_families_graph,
    "Random Graph": generate_random_graph,
    "Complete Graph": nx.complete_graph
}

"""
        FUNCTION FOR GENERATING THE P2P NETWORK
"""


def generate_graph(graph_name, **kwargs):
    global GRAPHS_GENERATORS

    if graph_name in GRAPHS_GENERATORS:
        G = GRAPHS_GENERATORS[graph_name](**kwargs)

    else:
        raise Exception("Error : Unknown type of graph - " + graph_name + ".")

    return G.to_directed()

"""
        FUNCTION FOR GETTING SUB-PART OF THE P2P NETWORK
"""


def get_active_graph(G):
    active_nodes_id = get_active_nodes(G)

    active_nodes_graph = nx.subgraph(G, active_nodes_id)

    active_edges_id = get_active_edges(G)

    active_graph = active_nodes_graph.edge_subgraph(active_edges_id)

    return active_graph


def get_active_nodes(G):
    active_nodes_id = list()

    for node_id in G.nodes():
        node = G.nodes[node_id]

        if node["active"] is True:
            active_nodes_id.append(node_id)

    return active_nodes_id


def get_active_edges(G):
    active_edges_id = list()

    for edge_id in G.edges():
        edge = G[edge_id[0]][edge_id[1]]

        if edge["active"] is True:
            active_edges_id.append(edge_id)

    return active_edges_id


def get_inactive_graph(G):
    inactive_nodes_id = get_inactive_nodes(G)

    inactive_nodes_graph = nx.subgraph(G, inactive_nodes_id)

    inactive_edges_id = get_inactive_edges(G)

    inactive_graph = inactive_nodes_graph.edge_subgraph(inactive_edges_id)

    return inactive_graph


def get_inactive_nodes(G):
    inactive_nodes_id = list()

    for node_id in G.nodes():
        node = G.nodes[node_id]

        if node["active"] is False:
            inactive_nodes_id.append(node_id)

    return inactive_nodes_id


def get_inactive_edges(G):
    inactive_edges_id = list()

    for edge_id in G.edges():
        edge = G[edge_id[0]][edge_id[1]]

        if edge["active"] is False:
            inactive_edges_id.append(edge_id)

    return inactive_edges_id


"""
        FUNCTION FOR SIMULATING NETWORK DYNAMIC
"""


def remove_connections(G, n):
    for i in range(0, n):
        active_G = get_active_graph(G)

        active_connections = list(active_G.edges())

        edge_id = random.choice(active_connections)

        remove_connection(G, edge_id)


def remove_connection(G, edge_id):
    if G[edge_id[0]][edge_id[1]]["active"] is False or G[edge_id[1]][edge_id[0]]["active"] is False:
        raise Exception("Error: Trying to remove a non active link (" + str(edge_id[0]) + "," + str(edge_id[1]) + ").")

    G[edge_id[0]][edge_id[1]]["active"] = False
    G[edge_id[1]][edge_id[0]]["active"] = False


def add_connections(G, n, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                    min_diffusion_delay_rate, max_diffusion_delay_rate, node_id=None):

    for i in range(0, n):
        active_G = get_active_graph(G)

        active_peers = set(active_G.nodes())
        active_connections = set(active_G.edges())

        if node_id is None:
            possible_connections = set(itertools.combinations(active_peers, 2)).difference(active_connections)

        else:
            possible_other_peers = active_peers.difference(node_id)
            possible_connections = set([(node_id, i) for i in possible_other_peers]).difference(active_connections)

        edge_id = random.choice(list(possible_connections))

        add_connection(G, edge_id, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var,
                       max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate)


def add_connection(G, edge_id, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                   min_diffusion_delay_rate, max_diffusion_delay_rate):
    if G.nodes[edge_id[0]]["active"] is False or G.nodes[edge_id[1]]["active"] is False:
        raise Exception("Error: Trying to connect non active peer(s) " + edge_id[0] + " and "
                        + edge_id[1] + ".")

    elif G.has_edge(edge_id[0], edge_id[1]) is True and \
            G[edge_id[0]][edge_id[1]]["active"] is True and G[edge_id[1]][edge_id[0]]["active"] is True:
        raise Exception("Error: Trying to create an already active link (" + str(edge_id[0]) + "," + str(edge_id[1])
                        + ").")

    if G.has_edge(edge_id[0], edge_id[1]) is False:
        G.add_edge(edge_id[0], edge_id[1])
        G.add_edge(edge_id[1], edge_id[0])

        G[edge_id[0]][edge_id[1]]["jitter_mean"] = random.uniform(min_jitter_mean, max_jitter_mean)
        G[edge_id[1]][edge_id[0]]["jitter_mean"] = random.uniform(min_jitter_mean, max_jitter_mean)

        G[edge_id[0]][edge_id[1]]["jitter_var"] = random.uniform(min_jitter_var, max_jitter_var)
        G[edge_id[1]][edge_id[0]]["jitter_var"] = random.uniform(min_jitter_var, max_jitter_var)

        # Modelling of the network diffusion delay
        G[edge_id[0]][edge_id[1]]["diffusion_delay_rate"] = random.uniform(min_diffusion_delay_rate,
                                                                           max_diffusion_delay_rate)
        G[edge_id[1]][edge_id[0]]["diffusion_delay_rate"] = random.uniform(min_diffusion_delay_rate,
                                                                           max_diffusion_delay_rate)

        G[edge_id[0]][edge_id[1]]["delay"] = random.uniform(min_delay, max_delay)
        G[edge_id[1]][edge_id[0]]["delay"] = random.uniform(min_delay, max_delay)

        G[edge_id[0]][edge_id[1]]["real_delay"] = G[edge_id[0]][edge_id[1]]["delay"]
        G[edge_id[1]][edge_id[0]]["real_delay"] = G[edge_id[1]][edge_id[0]]["delay"]

        G[edge_id[0]][edge_id[1]]["delays"] = [G[edge_id[0]][edge_id[1]]["delay"]]
        G[edge_id[1]][edge_id[0]]["delays"] = [G[edge_id[1]][edge_id[0]]["delay"]]

    G[edge_id[0]][edge_id[1]]["active"] = True
    G[edge_id[1]][edge_id[0]]["active"] = True


def remove_peers(G, n):
    for i in range(0, n):
        active_G = get_active_graph(G)

        active_peers = list(active_G.nodes())

        peer = random.choice(active_peers)

        remove_peer(G, peer)


def remove_peer(G, node_id):
    if G.nodes[node_id]["active"] is False:
        raise Exception("Error: Trying to a non active peer " + node_id)

    G.nodes[node_id]["active"] = False

    for edge_id, edge_info in G[node_id].items():
        G[edge_id][node_id]["active"] = False
        G[node_id][edge_id]["active"] = False


def add_peers(G, n, add_known_peer_proba, min_nb_connection, max_nb_connection, min_delay, max_delay, min_jitter_mean,
              max_jitter_mean, min_jitter_var, max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate,
              network_ip):

    inactive_G = get_inactive_graph(G)

    inactive_peers = list(inactive_G.nodes())

    for i in range(0, n):
        tmp = np.random.random()

        nb_connections = np.random.randint(min_nb_connection, max_nb_connection)

        if len(inactive_peers) > 0 and tmp < add_known_peer_proba:
            peer = random.choice(inactive_peers)
            inactive_peers.remove(peer)

            add_peer(G, peer, nb_connections, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                     min_diffusion_delay_rate, max_diffusion_delay_rate)

        else:
            active_G = get_active_graph(G)

            inactive_G = get_inactive_graph(G)

            known_peers = list(active_G.nodes) + list(inactive_G.nodes)

            peer = None

            for i in ipaddress.IPv4Network(network_ip):
                if i not in known_peers:
                    peer = i
                    break

            if peer is None:
                raise Exception("Error: Not enough IP addresses in network " + str(network_ip))

            add_peer(G, peer, nb_connections, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var,
                     max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate)


def add_peer(G, node_id, nb_connections, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var,
             max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate):
    active_G = get_active_graph(G)

    if node_id in active_G.nodes():
        raise Exception("Error: Trying to add a peer that is already active " + node_id + ".")

    if node_id in G.nodes:
        G.add_node(node_id)

    G.nodes[node_id]["active"] = True

    add_connections(G, nb_connections, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var,
                    max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate, node_id=node_id)


def reconnect_graph(G, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                    min_diffusion_delay_rate, max_diffusion_delay_rate, min_nb_connection_per_peer,
                    max_nb_connection_per_peer):

    active_G = get_active_graph(G)

    for node_id in active_G.nodes():
        if not has_active_connection(G, node_id):
            nb_connection = random.uniform(min_nb_connection_per_peer, max_nb_connection_per_peer)
            add_connections(G, nb_connection, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var,
                            max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate, node_id=node_id)


def has_active_connection(G, node_id):
    if len(G[node_id]) == 0:
        return False

    for adj_node_id in G[node_id]:

        if G[node_id][adj_node_id]["active"] is True:
            return True

    return False


"""
        BROADCAST INFERING
"""


def infer_broadcast_path_from_difference(broadcast_information, real_origin):
    inferred_origin, curr_min_sent_time = Topology_Discoverer_1.infer_origin(broadcast_information)

    if real_origin != inferred_origin:
        raise Exception(("Error : Inferred Origin " + inferred_origin + " != Real origin " + real_origin))

    inferred_shortest_path_tree = nx.DiGraph()

    inferred_complete_graph = Topology_Discoverer_1.infer_complete_graph(broadcast_information)

    for node_id in inferred_complete_graph.nodes:
        if node_id != inferred_origin:

            for adj_node_id in inferred_complete_graph[node_id]:
                if adj_node_id != inferred_origin:

                    value = abs(inferred_complete_graph[inferred_origin][node_id]["delay"] -
                                (inferred_complete_graph[inferred_origin][adj_node_id]["delay"] +
                                 inferred_complete_graph[adj_node_id][node_id]["delay"]))

                    inferred_shortest_path_tree.add_edge(node_id, adj_node_id, delay=value, active=True)

            inferred_shortest_path_tree.add_edge(inferred_origin, node_id, delay=0, active=True)
            inferred_shortest_path_tree.add_edge(node_id, inferred_origin, delay=math.inf, active=True)

    inferred_shortest_path_tree.nodes[inferred_origin]["origin"] = True

    return inferred_shortest_path_tree


def infer_broadcast_path_with_minimum_spanning_tree(broadcast_information, real_origin):
    inferred_shortest_path_tree = nx.Graph()

    inferred_origin, curr_min_sent_time = Topology_Discoverer_1.infer_origin(broadcast_information)

    if real_origin != inferred_origin:
        raise Exception(("Error : Inferred Origin " + inferred_origin + " != Real origin " + real_origin))

    inferred_complete_graph = Topology_Discoverer_1.infer_complete_graph(broadcast_information)

    for node_id in inferred_complete_graph:
        if node_id != inferred_origin:
            shortest_path = nx.shortest_path(inferred_complete_graph, source=inferred_origin, target=node_id,
                                             weight="delay")

            inferred_shortest_path_tree.add_path(shortest_path)

            last_node_id = inferred_origin

            for adj_node_id in shortest_path:
                if adj_node_id != inferred_origin:

                    inferred_shortest_path_tree[last_node_id][adj_node_id]["delay"] = \
                        inferred_complete_graph[last_node_id][adj_node_id]["delay"]

                    last_node_id = adj_node_id

    inferred_shortest_path_tree.nodes[inferred_origin]["origin"] = True

    return inferred_shortest_path_tree


"""
        FUNCTION FOR PLOTTING GRAPHS
"""


def plot_graph(G, graph_name, filename, edge_value=None, edge_name=None):
    pos = nx.spring_layout(G, dim=3)

    """
            COLORBAR AND COLORSCALE DEFINITION
    """

    if edge_value is not None and edge_name is not None:
        value = list()

        for edge in list(G.edges.values()):
            if not math.isinf(edge[edge_value]):
                value += [edge[edge_value]]

        min_value = np.min(value)
        max_value = np.max(value) + 1

        cmap_colorscale = "YlGnBu"
        cmap = mpl.cm.get_cmap("YlGnBu_r")
        delay_norm = mpl.colors.Normalize(vmin=min_value, vmax=max_value)

        custom_colorbar = dict(title=edge_name,
                               xanchor='left',
                               yanchor='top',
                               titleside='right',
                               tickangle=20,
                               thickness=50,
                               len=1,
                               outlinewidth=2.2,
                               )

        """
                MIDDLE EDGE TRACES (for text display when hover)
        """

        middle_edge_node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color=[],
                cmax=max_value,
                cmin=min_value,
                size=2,
                colorscale=cmap_colorscale,
                colorbar=custom_colorbar,
                showscale=True,

            ),
            opacity=0.3,
            showlegend=False,
            hoverlabel=dict(
                bgcolor=[]
            )
        )

        active_middle_edge_node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color=[],
                cmax=max_value,
                cmin=min_value,
                size=2,
                colorscale=cmap_colorscale,
                colorbar=custom_colorbar,
                showscale=True,

            ),
            opacity=0.3,
            showlegend=False,
            hoverlabel=dict(
                bgcolor=[]
            )
        )

        inactive_middle_edge_node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color="red",
                cmax=max_value,
                cmin=min_value,
                size=2,
            ),
            opacity=0.3,
            showlegend=False,
        )

    else:

        """
                MIDDLE EDGE TRACES (for text display when hover)
        """

        middle_edge_node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                size=2,
                color=[],

            ),
            opacity=0.3,
            hoverlabel=dict(
                bgcolor=[]
            ),
            showlegend=False,
        )

        active_middle_edge_node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                size=2,
                color=[],

            ),
            opacity=0.3,
            hoverlabel=dict(
                bgcolor=[]
            ),
            showlegend=False,
        )

        inactive_middle_edge_node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                size=2,
                color=[],

            ),
            opacity=0.3,
            hoverlabel=dict(
                bgcolor=[]
            ),
            showlegend=False,
        )

    """
                    EDGE TRACES DEFINITION
    """

    edge_traces = list()
    active_edge_traces = list()
    inactive_edge_traces = list()

    considered_edges = list()

    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]

        if [(x0, x1), (y0, y1), (z0, z1)] not in considered_edges:

            """
                    GET EDGES INFORMATIONS
            """

            tmp = G[edge[0]][edge[1]].copy()

            if "delays" in tmp:
                del tmp["delays"]

            if "timestamp" in tmp:
                del tmp["timestamp"]

            edge_info = edge[0] + " -> " + edge[1] + " : " + str(tmp)

            directed_edge = False

            if (edge[1], edge[0]) in G.edges():

                tmp = G[edge[1]][edge[0]].copy()

                if "delays" in tmp:
                    del tmp["delays"]

                if "timestamp" in tmp:
                    del tmp["timestamp"]

                edge_info += "<br>" + edge[1] + " -> " + edge[0] + " : " + str(tmp)

                directed_edge = True

            if edge_name is None and edge_value is None:
                color = "black"
                
                if "active" in G[edge[0]][edge[1]] and G[edge[0]][edge[1]]["active"] is True:
                    legend_group = "Active Links"

                    showlegend = False

                    active_middle_edge_node_trace['x'] += tuple([(x0 + x1) / 2])
                    active_middle_edge_node_trace['y'] += tuple([(y0 + y1) / 2])
                    active_middle_edge_node_trace['z'] += tuple([(z0 + z1) / 2])
                    active_middle_edge_node_trace["marker"]["color"] += tuple([color])
                    active_middle_edge_node_trace["hoverlabel"]["bgcolor"] += tuple([color])

                    active_middle_edge_node_trace["text"] += tuple([edge_info])

                    edge_trace = go.Scatter3d(
                        x=tuple([x0, x1, None]),
                        y=tuple([y0, y1, None]),
                        z=tuple([z0, z1, None]),
                        mode='lines',
                        hoverinfo='none',
                        line=dict(
                            width=1.5,
                            color=color
                        ),
                        opacity=1.0,
                        showlegend=showlegend,
                        name=legend_group,
                        legendgroup=legend_group,
                    )

                    active_edge_traces.append(edge_trace)

                elif "active" in G[edge[0]][edge[1]] and G[edge[0]][edge[1]]["active"] is False:
                    legend_group = "Inactive Links"

                    if len(inactive_edge_traces) == 0:
                        showlegend = True

                    else:
                        showlegend = False

                    inactive_middle_edge_node_trace['x'] += tuple([(x0 + x1) / 2])
                    inactive_middle_edge_node_trace['y'] += tuple([(y0 + y1) / 2])
                    inactive_middle_edge_node_trace['z'] += tuple([(z0 + z1) / 2])

                    inactive_middle_edge_node_trace["text"] += tuple([edge_info])

                    edge_trace = go.Scatter3d(
                        x=tuple([x0, x1, None]),
                        y=tuple([y0, y1, None]),
                        z=tuple([z0, z1, None]),
                        mode='lines',
                        hoverinfo='none',
                        line=dict(
                            width=1.5,
                            color="red"
                        ),
                        opacity=1.0,
                        showlegend=showlegend,
                        name=legend_group,
                        legendgroup=legend_group,
                    )

                    inactive_edge_traces.append(edge_trace)

                else:
                    legend_group = "Classic Links"

                    showlegend = False

                    middle_edge_node_trace['x'] += tuple([(x0 + x1) / 2])
                    middle_edge_node_trace['y'] += tuple([(y0 + y1) / 2])
                    middle_edge_node_trace['z'] += tuple([(z0 + z1) / 2])
                    middle_edge_node_trace["marker"]["color"] += tuple([color])
                    middle_edge_node_trace["hoverlabel"]["bgcolor"] += tuple([color])

                    middle_edge_node_trace["text"] += tuple([edge_info])

                    edge_trace = go.Scatter3d(
                        x=tuple([x0, x1, None]),
                        y=tuple([y0, y1, None]),
                        z=tuple([z0, z1, None]),
                        mode='lines',
                        hoverinfo='none',
                        line=dict(
                            width=1.5,
                            color=color
                        ),
                        opacity=1.0,
                        showlegend=showlegend,
                        name=legend_group,
                        legendgroup=legend_group,
                    )

                    edge_traces.append(edge_trace)

            else:
                if not math.isinf(G[edge[0]][edge[1]][edge_value]) and \
                        directed_edge is True and not math.isinf(G[edge[1]][edge[0]][edge_value]):

                    mean_value = np.mean([G[edge[0]][edge[1]][edge_value], G[edge[1]][edge[0]][edge_value]])
                    rgba_color = cmap(delay_norm(mean_value))

                    color = mpl.colors.to_hex(rgba_color)

                    opacity = 1.0

                elif math.isinf(G[edge[0]][edge[1]][edge_value]) and \
                        (directed_edge is True and not math.isinf(G[edge[1]][edge[0]][edge_value])):

                    rgba_color = cmap(delay_norm(G[edge[1]][edge[0]][edge_value]))

                    color = mpl.colors.to_hex(rgba_color)

                    opacity = 1.0

                elif not math.isinf(G[edge[0]][edge[1]][edge_value]) and \
                        (directed_edge is False or math.isinf(G[edge[1]][edge[0]][edge_value])):
                    rgba_color = cmap(delay_norm(G[edge[0]][edge[1]][edge_value]))

                    color = mpl.colors.to_hex(rgba_color)

                    opacity = 1.0

                else:
                    rgba_color = cmap(max_value)

                    color = mpl.colors.to_hex(rgba_color)

                    opacity = 0.2

                if "active" in G[edge[0]][edge[1]] and G[edge[0]][edge[1]]["active"] is True:
                    legend_group = "Active Links"

                    showlegend = False

                    active_middle_edge_node_trace['x'] += tuple([(x0 + x1) / 2])
                    active_middle_edge_node_trace['y'] += tuple([(y0 + y1) / 2])
                    active_middle_edge_node_trace['z'] += tuple([(z0 + z1) / 2])
                    active_middle_edge_node_trace["marker"]["color"] += tuple([color])
                    active_middle_edge_node_trace["hoverlabel"]["bgcolor"] += tuple([color])

                    active_middle_edge_node_trace["text"] += tuple([edge_info])

                    edge_trace = go.Scatter3d(
                        x=tuple([x0, x1, None]),
                        y=tuple([y0, y1, None]),
                        z=tuple([z0, z1, None]),
                        mode='lines',
                        hoverinfo='none',
                        line=dict(
                            width=1.5,
                            color=color
                        ),
                        opacity=opacity,
                        showlegend=showlegend,
                        name=legend_group,
                        legendgroup=legend_group,
                    )

                    active_edge_traces.append(edge_trace)

                elif "active" in G[edge[0]][edge[1]] and G[edge[0]][edge[1]]["active"] is False:
                    legend_group = "Inactive Links"

                    if len(inactive_edge_traces) == 0:
                        showlegend = True

                    else:
                        showlegend = False

                    inactive_middle_edge_node_trace['x'] += tuple([(x0 + x1) / 2])
                    inactive_middle_edge_node_trace['y'] += tuple([(y0 + y1) / 2])
                    inactive_middle_edge_node_trace['z'] += tuple([(z0 + z1) / 2])

                    inactive_middle_edge_node_trace["text"] += tuple([edge_info])

                    edge_trace = go.Scatter3d(
                        x=tuple([x0, x1, None]),
                        y=tuple([y0, y1, None]),
                        z=tuple([z0, z1, None]),
                        mode='lines',
                        hoverinfo='none',
                        line=dict(
                            width=1.5,
                            color="red"
                        ),
                        opacity=1.0,
                        showlegend=showlegend,
                        name=legend_group,
                        legendgroup=legend_group,
                    )

                    inactive_edge_traces.append(edge_trace)

                else:
                    legend_group = "Classic Links"

                    showlegend = False

                    middle_edge_node_trace['x'] += tuple([(x0 + x1) / 2])
                    middle_edge_node_trace['y'] += tuple([(y0 + y1) / 2])
                    middle_edge_node_trace['z'] += tuple([(z0 + z1) / 2])
                    middle_edge_node_trace["marker"]["color"] += tuple([color])
                    middle_edge_node_trace["hoverlabel"]["bgcolor"] += tuple([color])

                    middle_edge_node_trace["text"] += tuple([edge_info])

                    edge_trace = go.Scatter3d(
                        x=tuple([x0, x1, None]),
                        y=tuple([y0, y1, None]),
                        z=tuple([z0, z1, None]),
                        mode='lines',
                        hoverinfo='none',
                        line=dict(
                            width=1.5,
                            color=color
                        ),
                        opacity=1.0,
                        showlegend=showlegend,
                        name=legend_group,
                        legendgroup=legend_group,
                    )

                    edge_traces.append(edge_trace)

            considered_edges.append([(x0, x1), (y0, y1), (z0, z1)])
            considered_edges.append([(x1, x0), (y1, y0), (z1, z0)])

    """
                    NODE TRACES DEFINITION
    """

    node_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color="blue",
            size=6,
            line=dict(
                width=2
            )
        ),
        showlegend=False,
    )

    origin_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color="yellow",
            size=6,
            line=dict(
                width=2
            )
        ),
        showlegend=True,
        name="Broadcast origin"
    )

    active_node_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color=[],
            size=6,
            line=dict(
                width=2
            )
        ),
        showlegend=True,
        name="Active Nodes"
    )

    inactive_node_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color=[],
            size=6,
            line=dict(
                width=2
            )
        ),
        showlegend=True,
        name="Inactive Nodes"
    )

    for node in G.nodes():
        x, y, z = pos[node]

        if "origin" in G.nodes[node]:

            origin_trace['x'] += tuple([x])
            origin_trace['y'] += tuple([y])
            origin_trace['z'] += tuple([z])

            node_info = 'IP: ' + node

            origin_trace['text'] += tuple([node_info])

        elif "active" in G.nodes[node] and  G.nodes[node]["active"] is True:
            active_node_trace['x'] += tuple([x])
            active_node_trace['y'] += tuple([y])
            active_node_trace['z'] += tuple([z])

            nb_connection = len(G[node])

            active_node_trace['marker']['color'] += tuple(["green"])

            node_info = 'IP: ' + node + "<br>" + '# of connections: ' + str(nb_connection)

            active_node_trace['text'] += tuple([node_info])

        elif "active" in G.nodes[node] and G.nodes[node]["active"] is False:
            inactive_node_trace['x'] += tuple([x])
            inactive_node_trace['y'] += tuple([y])
            inactive_node_trace['z'] += tuple([z])

            nb_connection = 0

            inactive_node_trace['marker']['color'] += tuple(["red"])

            node_info = 'IP: ' + node + "<br>" + '# of connections: ' + str(nb_connection)

            inactive_node_trace['text'] += tuple([node_info])

        else:
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['z'] += tuple([z])

            node_info = 'IP: ' + node

            node_trace['text'] += tuple([node_info])

    axis = dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

    fig = go.FigureWidget(data=[node_trace, origin_trace, active_node_trace, inactive_node_trace,
                                middle_edge_node_trace, active_middle_edge_node_trace, inactive_middle_edge_node_trace]
                               + edge_traces + active_edge_traces + inactive_edge_traces,
                          layout=go.Layout(
                              title=graph_name,
                              titlefont=dict(
                                  size=16
                              ),
                              showlegend=True,
                              scene=dict(
                                  xaxis=dict(axis),
                                  yaxis=dict(axis),
                                  zaxis=dict(axis),
                              ),
                              hovermode='closest',
                              margin=dict(b=20, l=5, r=5, t=40),
                          )
                          )

    if filename is not None:
        py.offline.plot(fig, filename=filename)
    else:
        py.offline.plot(fig)

"""
                ERROR MANAGEMENT  
"""


def inferred_graph_error_measurements(real_graph, esti_graph):
    nb_inferred_edges = len(esti_graph.edges()) / 2  # Because directed Graph

    nb_real_edges = len(real_graph.edges()) / 2  # Because directed graph

    nb_infered_nodes = len(esti_graph.nodes())

    nb_real_nodes = len(real_graph.nodes())

    total_possible_edges = (nb_real_nodes * (nb_real_nodes - 1)) / 2

    true_positive = 0

    false_positive = 0

    true_negative = 0

    false_negative = 0

    delay_error = list()

    already_considered_edges = list()

    for edge in real_graph.edges():
        if edge not in already_considered_edges:

            if esti_graph.has_edge(edge[0], edge[1]):
                true_positive = true_positive + 1

                if esti_graph[edge[0]][edge[1]]["delay"] is not None:
                    infered_edge_delay = esti_graph[edge[0]][edge[1]]["delay"]

                    real_edge_delay = real_graph[edge[0]][edge[1]]["delay"]

                    delay_error.append(np.abs(infered_edge_delay - real_edge_delay))

                if esti_graph[edge[1]][edge[0]]["delay"] is not None:
                    infered_edge_delay = esti_graph[edge[1]][edge[0]]["delay"]

                    real_edge_delay = real_graph[edge[1]][edge[0]]["delay"]

                    delay_error.append(np.abs(infered_edge_delay - real_edge_delay))

            else:
                false_negative = false_negative + 1

            already_considered_edges.append((edge[0], edge[1]))
            already_considered_edges.append((edge[1], edge[0]))

    mean_delay_error = np.mean(delay_error)

    nb_infer_negative = (total_possible_edges - nb_inferred_edges)

    true_negative = nb_infer_negative - false_negative

    false_positive = nb_inferred_edges - true_positive

    if (true_positive + false_negative) != nb_real_edges:
        raise Exception("Error: The number of True positive added to the number of False negative must be equal to "
                        "the number of positive.")

    elif (true_negative + false_positive) != (total_possible_edges - nb_real_edges):
        raise Exception("Error: The number of True negative added to the number of False positive must be equal to "
                        "the number of negative.")

    return (true_positive, true_negative, false_positive, false_negative), mean_delay_error


def store_errors(filename, errors):
    with open(filename, 'w') as outfile:
        json.dump(errors, outfile)


def plot_error_graphs(errors):
    pass


"""
        CORRELATION TESTING FUNCTIONS
"""


def create_random_time_series(start_date, end_date, column_name=None):
    a = dict()

    curr_date = start_date

    while curr_date < end_date:
        nb_seconds_elapsed = random.uniform(12, 137)

        curr_date = curr_date + datetime.timedelta(seconds=nb_seconds_elapsed)

        a[curr_date] = random.uniform(0, 100)

    dates = pd.DataFrame(a.keys(), columns=["date"])

    time_serie = pd.DataFrame()

    time_serie['datetime'] = pd.to_datetime(dates["date"])

    if column_name is None:
        time_serie["data"] = a.values()

    else:
        time_serie[column_name] = a.values()

    time_serie = time_serie.set_index('datetime')

    return time_serie


def get_correlation(time_serie1, time_serie2, method):
    tmp = pd.concat([time_serie1, time_serie2], axis=1).interpolate()

    return tmp.corr(method)


def get_sum_time_serie(time_serie1, column_name1, time_serie2, column_name2):
    if column_name1 == column_name2:
        raise Exception("Error : Columns must have different names.")

    tmp = pd.concat([time_serie1, time_serie2], axis=1).interpolate()

    time_serie3 = tmp[column_name1] + tmp[column_name2]


def test_correlation(start_date, end_date):

    time_serie1 = create_random_time_series(start_date, end_date, column_name="edge1")

    time_serie2 = create_random_time_series(start_date, end_date, column_name="edge2")

    tmp = pd.concat([time_serie1, time_serie2], axis=1).interpolate()