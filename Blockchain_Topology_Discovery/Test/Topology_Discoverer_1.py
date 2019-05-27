import datetime
import math

from Util import *


def infer_complete_graph(broadcast_information):
    G = nx.DiGraph()

    G.add_nodes_from(list(broadcast_information.keys()), active=True)

    for node_id in G.nodes():

        for adj_node_id in G.nodes():
            if node_id != adj_node_id:
                delay = broadcast_information[adj_node_id] - broadcast_information[node_id]

                if delay >= 0:
                    G.add_edge(node_id, adj_node_id, delay=delay, active=True, delay_var=0.0)

                else:
                    G.add_edge(node_id, adj_node_id, delay=math.inf, active=True, delay_var=0.0)

    return G


def infer_origin(broadcast_information):
    origin = min(broadcast_information, key=lambda k: broadcast_information[k])

    min_sent_time = broadcast_information[origin]

    return origin, min_sent_time


def merge_measurements_graphs(G, prev_G, timestamp, history_to_consider=3):
    if prev_G is None:
        prev_G = nx.DiGraph()

    """
                        ADD THE NODES THAT JUST APPEARED
    """

    new_nodes = set(G.nodes()).difference(set(prev_G.nodes()))

    prev_G.add_nodes_from(new_nodes, active=True)

    """
            LABEL AS UNACTIVE THE NODES AND THE EDGES THAT DON'T APPEAR ANYMORE
    """

    unactive_nodes = set(prev_G.nodes()).difference(set(G.nodes()))

    for node_id in unactive_nodes:
        prev_G.nodes[node_id]["active"] = False

        for adj_node_id in G.nodes():
            if node_id != adj_node_id:
                if (node_id, adj_node_id) in prev_G.edges():
                    prev_G[node_id][adj_node_id]["active"] = False
                    prev_G[adj_node_id][node_id]["active"] = False

                else:
                    prev_G.add_edge(node_id, adj_node_id, active=False, delay=None, delays=list(), delay_var=0.0,
                                    mean_delay=None, timestamp=list())

                    prev_G.add_edge(adj_node_id, node_id, active=False, delay=None, delays=list(), delay_var=0.0,
                                    mean_delay=None, timestamp=list())

    """
            ADD THE NEW MEASUREMENTS TO THE GRAPH
    """

    for node_id in G.nodes():

        if node_id in prev_G.nodes():
            prev_node = prev_G.nodes[node_id]
            prev_node["active"] = True

            for adj_node_id in G.nodes():

                if adj_node_id != node_id:

                    if (node_id, adj_node_id) not in prev_G.edges():
                        prev_G.add_edge(node_id, adj_node_id, active=True, delay=None, delays=list(), delay_var=0.0,
                                        mean_delay=None, timestamp=list())

                    edge = G[node_id][adj_node_id]
                    prev_edge = prev_G[node_id][adj_node_id]

                    prev_edge["active"] = True

                    if edge["delay"] is not None:
                        prev_edge["timestamp"].append(timestamp)

                        prev_edge["delay"] = edge["delay"]
                        prev_edge["delays"].append(edge["delay"])

                        considered_delays = prev_edge["delays"][-history_to_consider::]

                        if len(considered_delays) > 0:
                            prev_edge["delay_var"] = np.var(considered_delays)
                            prev_edge["mean_delay"] = np.mean(considered_delays)

                        else:
                            prev_edge["delay_var"] = 0.0
                            prev_edge["mean_delay"] = None
        else:
            raise Exception("Error: Some new nodes has not been added properly to the graph during the merge")

    return prev_G


class Topology_Discoverer:

    def __init__(self):
        self._graph_measurements = None

        self._broadcast_origins = list()

        self._infered_topology = None

    def infer_topology(self, var_treshold, history_to_consider=None, metric="mean"):
        active_nodes_id = get_active_nodes(self._graph_measurements)

        infered_topology = nx.DiGraph()

        infered_topology.add_nodes_from(active_nodes_id)

        already_considered_edges = list()

        for edge_id in self._graph_measurements.edges():
            if edge_id not in already_considered_edges:
                edge = self._graph_measurements[edge_id[0]][edge_id[1]]
                opposite_edge = self._graph_measurements[edge_id[1]][edge_id[0]]

                if history_to_consider is not None:
                    edge_var = np.var(edge["delays"][-history_to_consider::])

                    opposite_edge_var = np.var(opposite_edge["delays"][-history_to_consider::])

                else:
                    edge_var = np.var(edge["delays"])

                    opposite_edge_var = np.var(opposite_edge["delays"])

                if metric == "mean":
                    edge_value = np.mean([edge_var, opposite_edge_var])

                elif metric == "min":
                    edge_value = np.max([edge_var, opposite_edge_var])

                elif metric == "max":
                    edge_value = np.min([edge_var, opposite_edge_var])

                else:
                    raise Exception("Error: Unknown metric for computing edge value.")

                if edge_value < var_treshold:
                    infered_topology.add_edge(edge_id[0], edge_id[1], delay=edge["delay"])
                    infered_topology.add_edge(edge_id[1], edge_id[0], delay=opposite_edge["delay"])

                already_considered_edges.append((edge_id[0], edge_id[1]))
                already_considered_edges.append((edge_id[1], edge_id[0]))

        self._infered_topology = infered_topology

        return infered_topology

    def update_measurements(self, broadcast_information, display=False):
        infered_origin, curr_min_sent_time = infer_origin(broadcast_information)

        infered_complete_graph = infer_complete_graph(broadcast_information)

        self._graph_measurements = merge_measurements_graphs(infered_complete_graph, self._graph_measurements,
                                                             curr_min_sent_time)

        self._broadcast_origins.append(infered_origin)

        if display is True:
            plot_graph(self._graph_measurements, "P2P Network Measurements", "p2p_network_measurements.html",
                       "delay_var", "Delay Variance", )

    def plot_measurements(self):
        plot_graph(self._graph_measurements, "P2P Network Measurements", "p2p_network_measurements.html",
                   "delay_var", "Delay Variance")

    def plot_infered_topology(self):
        if self._infered_topology is None:
            raise Exception("Error: \'infer_topology\' must be called at least once before being able to plot it.")

        plot_graph(self._infered_topology, "Infered Topology", "infered_topology.html", "delay_var", "Delay Variance", )