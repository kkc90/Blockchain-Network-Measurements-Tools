import random
import math
import json

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

GRAPHS_GENERATORS = {
    "Gaussian Random Partition": nx.gaussian_random_partition_graph,
    "Caveman": nx.connected_caveman_graph,
    "Karate Club": nx.karate_club_graph,
    "Davis Southern Women Club": nx.davis_southern_women_graph,
    "Florentine Families": nx.florentine_families_graph,
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

        edge_id = active_connections[np.random.randint(0, len(active_connections))]

        remove_connection(G, edge_id)


def remove_connection(G, edge_id):
    if G[edge_id[0]][edge_id[1]]["active"] is False or G[edge_id[1]][edge_id[0]]["active"] is False:
        raise Exception("Error: Trying to remove a non active link (" + str(edge_id[0]) + "," + str(edge_id[1]) + ").")

    G[edge_id[0]][edge_id[1]]["active"] = False
    G[edge_id[1]][edge_id[0]]["active"] = False


def add_connections(G, n, min_delay, max_delay, node_id=None):
    for i in range(0, n):
        active_G = get_active_graph(G)

        active_peers = list(active_G.nodes())
        active_connections = list(active_G.edges())

        possible_connections = list()

        if node_id is None:
            for peer1 in active_peers:
                for peer2 in active_peers:
                    if (peer1, peer2) not in active_connections and peer1 != peer2:
                        possible_connections.append((peer1, peer2))

        else:
            for peer2 in active_peers:
                if (node_id, peer2) not in active_connections and node_id != peer2:
                    possible_connections.append((node_id, peer2))

        edge_id = possible_connections[np.random.randint(0, len(possible_connections))]

        add_connection(G, edge_id, min_delay, max_delay)


def add_connection(G, edge_id, min_delay, max_delay):
    if G.nodes[edge_id[0]]["active"] is False or G.nodes[edge_id[1]]["active"] is False:
        raise Exception("Error: Trying to connect non active peer(s) " + edge_id[0] + " and "
                        + edge_id[1] + ".")

    elif G.has_edge(edge_id[0], edge_id[1]) and G[edge_id[0]][edge_id[1]]["active"] is True or \
            G[edge_id[1]][edge_id[0]]["active"] is True:
        raise Exception("Error: Trying to create an already active link (" + str(edge_id[0]) + "," + str(edge_id[1])
                        + ").")

    if not G.has_edge(edge_id[0], edge_id[1]):
        G.add_edge(edge_id[0], edge_id[1])
        G[edge_id[0]][edge_id[1]]["delay"] = random.uniform(min_delay, max_delay)
        G[edge_id[0]][edge_id[1]]["delay_var"] = 0.0
        G[edge_id[0]][edge_id[1]]["mean_delay"] = G[edge_id[0]][edge_id[1]]["delay"]

    G[edge_id[0]][edge_id[1]]["active"] = True
    G[edge_id[1]][edge_id[0]]["active"] = True


def remove_peers(G, n):
    for i in range(0, n):
        active_G = get_active_graph(G)

        active_peers = list(active_G.nodes())

        remove_peer(G, active_peers[np.random.randint(0, len(active_peers))])


def remove_peer(G, node_id):
    if G.nodes[node_id]["active"] is False:
        raise Exception("Error: Trying to a non active peer " + node_id)

    G.nodes[node_id]["active"] = False

    for edge_id, edge_info in G[node_id].items():
        G[edge_id][node_id]["active"] = False
        G[node_id][edge_id]["active"] = False


def add_peers(G, n, add_known_peer_proba, min_nb_connection, max_nb_connection, min_connection_delay,
              max_connection_delay):
    for i in range(0, n):
        tmp = np.random.random()

        nb_connections = np.random.randint(min_nb_connection, max_nb_connection)

        if tmp < add_known_peer_proba:
            inactive_G = get_inactive_graph(G)

            inactive_peers = list(inactive_G.nodes())

            add_peer(G, inactive_peers[np.random.randint(0, len(inactive_peers))], nb_connections=nb_connections,
                     min_connection_delay=min_connection_delay, max_connection_delay=max_connection_delay)

        else:
            active_G = get_active_graph(G)

            inactive_G = get_inactive_graph(G)

            known_peers = list(active_G.nodes) + list(inactive_G.nodes)

            add_peer(G, len(known_peers), nb_connections=nb_connections,
                     min_connection_delay=min_connection_delay, max_connection_delay=max_connection_delay)


def add_peer(G, node_id, nb_connections, min_connection_delay, max_connection_delay):
    active_G = get_active_graph(G)

    if node_id in active_G.nodes():
        raise Exception("Error: Trying to add a peer that is already active " + node_id + ".")

    G.add_node(node_id)

    add_connections(G, nb_connections, min_connection_delay, max_connection_delay, node_id=None)


def re_connect_graph(G, min_delay, max_delay):
    active_G = get_active_graph(G)

    for node_id in active_G.nodes():
        if not has_active_connection(G, node_id):
            other_nodes_id = list(active_G.nodes())
            other_nodes_id.remove(node_id)
            min_nb_connection = np.random.randint(0, len(other_nodes_id) - 1)
            max_nb_connection = np.random.randint(min_nb_connection, len(other_nodes_id))

            nb_connection = np.random.randint(min_nb_connection, max_nb_connection)

            for i in range(0, nb_connection):
                adj_node_id = np.random.choice(other_nodes_id)
                add_connection(G, (node_id, adj_node_id), min_delay, max_delay)

            print("Reconnection of", node_id, "with", str(nb_connection))


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


def plot_graph(G, graph_name, filename, edge_value, edge_name):
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

    elif edge_value is None and edge_name is None:

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

    else:
        raise Exception("Error: Either both edge value id and edge name must be specified or none.")

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
                    inactive_middle_edge_node_trace["marker"]["color"] += tuple([color])
                    inactive_middle_edge_node_trace["hoverlabel"]["bgcolor"] += tuple([color])

                    inactive_middle_edge_node_trace["text"] += tuple([edge_info])

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
                    inactive_middle_edge_node_trace["marker"]["color"] += tuple([color])
                    inactive_middle_edge_node_trace["hoverlabel"]["bgcolor"] += tuple([color])

                    inactive_middle_edge_node_trace["text"] += tuple([edge_info])

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