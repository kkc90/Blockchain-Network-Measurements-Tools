import datetime
import pandas as pd
import math
from scipy import stats
import itertools

from Util import *


def infer_broadcast_graph(broadcast_information):
    inferred_origin, curr_min_sent_time = infer_origin(broadcast_information)

    inferred_shortest_path_tree = nx.DiGraph()

    inferred_shortest_path_tree.add_nodes_from(list(broadcast_information.keys()), active=True)

    for node_id in inferred_shortest_path_tree.nodes():
        if node_id != inferred_origin:
            delay = broadcast_information[node_id] - broadcast_information[inferred_origin]

            inferred_shortest_path_tree.add_edge(inferred_origin, node_id, delay=delay, active=True)

    return inferred_shortest_path_tree


def infer_origin(broadcast_information):
    origin = None
    curr_min_sent_time = datetime.datetime.now()

    for node_id, timestamp in broadcast_information.items():
        sent_time = datetime.datetime.fromtimestamp(timestamp)

        if sent_time < curr_min_sent_time:
            origin = node_id
            curr_min_sent_time = sent_time

    return origin, curr_min_sent_time


def merge_measurements_graphs(G, prev_G, timestamp):
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

    """
            ADD THE NEW MEASUREMENTS TO THE GRAPH
    """

    for node_id in G.nodes():

        if node_id in prev_G.nodes():
            prev_node = prev_G.nodes[node_id]

            # Re-Label as active nodes that were previously supposed as being inactive.
            prev_node["active"] = True

            for adj_node_id in G[node_id]:

                if (node_id, adj_node_id) not in prev_G.edges():
                    prev_G.add_edge(node_id, adj_node_id, active=True, delay=None, delays=list(), delay_var=None,
                                    mean_delay=None, timestamp=list())

                edge = G[node_id][adj_node_id]
                prev_edge = prev_G[node_id][adj_node_id]

                prev_edge["active"] = True
                prev_edge["timestamp"].append(timestamp)

                prev_edge["delay"] = edge["delay"]
                prev_edge["delays"].append(edge["delay"])

                considered_delays = prev_edge["delays"]

                if len(considered_delays) > 0:
                    prev_edge["delay_var"] = np.var(considered_delays)
                    prev_edge["mean_delay"] = np.mean(considered_delays)

                else:
                    prev_edge["delay_var"] = 0.0
                    prev_edge["mean_delay"] = None

        else:
            raise Exception("Error: Some new nodes has not been added properly to the graph during the merge")

    return prev_G


def delays_to_timeseries(timestamps, delays, column_name=None):
    time_serie = pd.DataFrame()

    time_serie['datetime'] = pd.to_datetime(timestamps)

    if column_name is None:
        time_serie["data"] = delays

    else:
        time_serie[column_name] = delays

    time_serie = time_serie.set_index('datetime')

    return time_serie


# Correlation between 0 and 2 with 1 indicating a inverse linear relation and 2 a perfect linear relation
def get_lonely_edges(graph):
    time_series = pd.DataFrame()

    for edge_id in graph.edges:
        delays_edge1 = graph[edge_id[0]][edge_id[1]]["delays"]
        timestamp_delays_edge1 = graph[edge_id[0]][edge_id[1]]["timestamp"]

        time_serie1 = delays_to_timeseries(timestamp_delays_edge1, delays_edge1, column_name=str(edge_id))

        time_series = pd.concat([time_series, time_serie1], axis=1)

    time_series = time_series.interpolate(method='index').dropna()

    corr_matrix = time_series.corr() + 1

    lonely_edges = dict()

    for edge_id in graph.edges:
        all_corr = corr_matrix[str(edge_id)]

        del all_corr[str(edge_id)]

        all_corr = all_corr.dropna()

        if not np.isnan(np.mean(all_corr)):

            lonely_edges[edge_id] = dict()

            lonely_edges[edge_id]["mean"] = np.mean(all_corr)
            lonely_edges[edge_id]["min"] = np.min(all_corr)
            lonely_edges[edge_id]["max"] = np.max(all_corr)

    return lonely_edges


def get_correlation(time_serie1, column_name1, time_serie2, column_name2, method="pearson"):
    tmp = pd.concat([time_serie1, time_serie2], axis=1).interpolate("index").dropna()

    corr = tmp.corr(method)[column_name1][column_name2]

    return corr


class Topology_Discoverer:

    def __init__(self):
        self._graph_measurements = None

        self._broadcast_origins = list()

        self._infered_topology = None

    # Treshold at which we estimate that two path have no correlation
    def infer_topology(self, treshold, metric="mean", verbose=False):
        if treshold < 0 or treshold > 2:
            raise Exception("Error: Treshold must be a value belonging to the interval [0, 2]")

        active_graph = get_active_graph(self._graph_measurements)

        lonely_edges = get_lonely_edges(active_graph)

        if len(lonely_edges) == 0:
            if verbose is True:
                print("Warning : Not enough data for inferring topology.")
            return None

        sorted_edges = sorted(lonely_edges.items(), key=(lambda x: x[1][metric]), reverse=True)

        print(len(sorted_edges))

        edge = None

        infered_topology = nx.DiGraph()

        infered_topology.add_nodes_from(active_graph.nodes)

        infered_topology.add_edges_from(itertools.permutations(active_graph.nodes, 2))

        # Remove all edges that are considered as not independent from others.
        while nx.is_connected(infered_topology.to_undirected()) and len(sorted_edges) > 0:
            edge, _ = sorted_edges.pop()
            edge_corr = lonely_edges[edge][metric]

            inverse_edge = (edge[1], edge[0])

            if inverse_edge in lonely_edges:
                inverse_edge_corr = lonely_edges[inverse_edge][metric]

                if (inverse_edge, inverse_edge_corr) in sorted_edges:
                    sorted_edges.remove((inverse_edge, inverse_edge_corr))

                    if inverse_edge_corr < treshold and edge_corr < treshold:
                        infered_topology.remove_edge(edge[0], edge[1])
                        infered_topology.remove_edge(edge[1], edge[0])

            elif edge_corr < treshold:
                infered_topology.remove_edge(edge[0], edge[1])
                infered_topology.remove_edge(edge[1], edge[0])

            else:
                break

        if not nx.is_connected(infered_topology.to_undirected()):
            infered_topology.add_edge(edge[0], edge[1])
            infered_topology.add_edge(edge[1], edge[0])

        # Add information about infered edges

        for edge_id in infered_topology.copy().edges:
            infered_topology[edge_id[0]][edge_id[1]]["active"] = True

            if edge_id in lonely_edges:
                infered_topology[edge_id[0]][edge_id[1]]["corr_score"] = lonely_edges[edge_id][metric]

            else:
                infered_topology[edge_id[0]][edge_id[1]]["corr_score"] = math.inf

            if edge_id in self._graph_measurements.edges:
                infered_topology[edge_id[0]][edge_id[1]]["delay"] = self._graph_measurements[edge_id[0]][edge_id[1]]["delay"]
                infered_topology[edge_id[0]][edge_id[1]]["delays"] = self._graph_measurements[edge_id[0]][edge_id[1]]["delays"]
                infered_topology[edge_id[0]][edge_id[1]]["mean_delay"] = np.mean(infered_topology[edge_id[0]][edge_id[1]]["delays"])
                infered_topology[edge_id[0]][edge_id[1]]["delay_var"] = np.var(infered_topology[edge_id[0]][edge_id[1]]["delays"])

            else:
                infered_topology[edge_id[0]][edge_id[1]]["delay"] = None
                infered_topology[edge_id[0]][edge_id[1]]["delays"] = list()
                infered_topology[edge_id[0]][edge_id[1]]["mean_delay"] = None
                infered_topology[edge_id[0]][edge_id[1]]["delay_var"] = None

        self._infered_topology = infered_topology

        return infered_topology

    def update_measurements(self, broadcast_information, display=False):
        infered_origin, curr_min_sent_time = infer_origin(broadcast_information)

        infered_complete_graph = infer_broadcast_graph(broadcast_information)

        self._graph_measurements = merge_measurements_graphs(infered_complete_graph, self._graph_measurements,
                                                             curr_min_sent_time)

        self._broadcast_origins.append(infered_origin)

        if display is True:
            plot_graph(self._graph_measurements, "P2P Network Measurements", "p2p_network_measurements.html",
                       "delay_var", "Delay Variance",)

    def plot_measurements(self):
        plot_graph(self._graph_measurements, "P2P Network Measurements", "p2p_network_measurements.html",
                   "delay_var", "Delay Variance")

    def plot_infered_topology(self):
        if self._infered_topology is None:
            raise Exception("Error: \'infer_topology\' must be called at least once before being able to plot it.")

        plot_graph(self._infered_topology, "Infered Topology", "infered_topology.html", "corr_score", "Correlation",)
