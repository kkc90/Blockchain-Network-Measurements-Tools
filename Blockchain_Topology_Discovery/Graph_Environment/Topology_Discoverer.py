import datetime
import pandas as pd
import math
import itertools

from Util import *


def infer_edge_measures(broadcast_information):
    inferred_origin, curr_min_sent_time = infer_origin(broadcast_information)

    inferred_edge_measures = nx.DiGraph()

    inferred_edge_measures.add_nodes_from(list(broadcast_information.keys()), active=True)

    for node_id in inferred_edge_measures.nodes():
        if node_id != inferred_origin:
            delay = broadcast_information[node_id] - broadcast_information[inferred_origin]

            inferred_edge_measures.add_edge(inferred_origin, node_id, delay=delay, active=True)

    return inferred_edge_measures


def infer_broadcast_graph(correlation_graph, broadcast_informations):
    broadcast_path = dict()

    for (origin, _), broadcast_information in broadcast_informations.items():
        if origin not in broadcast_path.keys():
            broadcast_path[origin] = dict()

            for target, timestamp in broadcast_information.items():
                best_score = -math.inf
                max_corr_score_path = None

                for path in nx.all_simple_paths(correlation_graph, source=origin, target=target):
                    nb_node_in_path = len(path)

                    curr_score = 0
                    for i in range(1, nb_node_in_path):
                        curr_node_id = path[i - 1]
                        adj_node_id = path[i]

                        if curr_node_id in broadcast_path and target in broadcast_path[curr_node_id]:
                            curr_score += broadcast_path[curr_node_id][target][0]

                        else:
                            curr_score += correlation_graph[curr_node_id][adj_node_id]["corr_score"]

                    mean_score = curr_score / nb_node_in_path

                    if mean_score > best_score:
                        best_score = mean_score
                        max_corr_score_path = path

                broadcast_path[origin][target] = (best_score, max_corr_score_path)


def infer_broadcast_paths(correlation_graph, origin, broadcast_information):
    broadcast_paths = list()

    for node_id, timestamp in broadcast_information.items():
        if node_id != origin:
            max_corr_score_path, best_score = get_weighted_shortest_path(correlation_graph, origin, node_id)

            broadcast_paths.append(max_corr_score_path)

    return broadcast_paths


def get_path_correlation(correlation_graph, path):
    nb_node_in_path = len(path)

    curr_score = 0
    for i in range(1, nb_node_in_path):
        curr_node_id = path[i - 1]
        adj_node_id = path[i]

        curr_score += correlation_graph[curr_node_id][adj_node_id]["corr_score"]

    mean_score = curr_score / nb_node_in_path

    return mean_score


def get_weighted_shortest_path(correlation_graph, origin, target):
    best_score = -math.inf
    max_corr_score_path = None

    for path in nx.all_simple_paths(correlation_graph, source=origin, target=target):
        mean_score = get_path_correlation(correlation_graph, path)

        if mean_score > best_score:
            best_score = mean_score
            max_corr_score_path = path

    return max_corr_score_path, best_score


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
            LABEL AS INACTIVE THE NODES AND THE EDGES THAT DON'T APPEAR ANYMORE
    """

    unactive_nodes = set(prev_G.nodes()).difference(set(G.nodes()))

    for node_id in unactive_nodes:
        prev_G.nodes[node_id]["active"] = False

        # Connection to all active nodes must be considered as inactive
        for adj_node_id in prev_G[node_id]:
            prev_G[node_id][adj_node_id]["active"] = False

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
                    prev_G.add_edge(node_id, adj_node_id, active=True, delay=None, delays=list(), timestamp=list())

                edge = G[node_id][adj_node_id]
                prev_edge = prev_G[node_id][adj_node_id]

                prev_edge["active"] = True
                prev_edge["timestamp"].append(timestamp)

                prev_edge["delay"] = edge["delay"]
                prev_edge["delays"].append(edge["delay"])

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


def get_correlation_graph(graph, lonely_edges, metric):
    nodes = list(graph.nodes)

    correlation_graph = nx.DiGraph()

    correlation_graph.add_nodes_from(nodes)

    correlation_graph.add_edges_from(lonely_edges)

    for edge_id, corr_info in lonely_edges.items():

        # We will use the "correlation measure" as a metric to be able to calculate the minimum shortest path
        #           which corresponds to the path having a minimum correlation score (taking only lonely edges)
        correlation_graph[edge_id[0]][edge_id[1]]["corr_score"] = corr_info[metric]

        if (edge_id[1], edge_id[0]) not in lonely_edges:
            correlation_graph.add_edge(edge_id[1], edge_id[0], corr_score=corr_info[metric])

    return correlation_graph


def compute_edges_correlation(graph):
    """

    :param graph:
    :return: Correlation Matrix with score between 0 and 2 with
                        0 = inverse linear relation,
                        1 = no correlation,
                        2 = perfect linear relation
    """

    time_series = pd.DataFrame()

    for edge_id in graph.edges:
        delays_edge1 = graph[edge_id[0]][edge_id[1]]["delays"]
        timestamp_delays_edge1 = graph[edge_id[0]][edge_id[1]]["timestamp"]

        time_serie1 = delays_to_timeseries(timestamp_delays_edge1, delays_edge1, column_name=str(edge_id))

        time_series = pd.concat([time_series, time_serie1], axis=1)

    edges_correlation_matrix = time_series.interpolate(method='index').dropna()

    edges_correlation_matrix = np.abs(edges_correlation_matrix.corr(method="pearson"))

    edges_correlation = dict()

    for edge_id in graph.edges:
        all_corr = edges_correlation_matrix[str(edge_id)].copy()

        del all_corr[str(edge_id)]

        all_corr = all_corr.dropna()

        if not np.isnan(np.mean(all_corr)):

            edges_correlation[edge_id] = dict()

            edges_correlation[edge_id]["mean"] = np.mean(all_corr)
            edges_correlation[edge_id]["min"] = np.min(all_corr)
            edges_correlation[edge_id]["max"] = np.max(all_corr)

    return edges_correlation


def get_correlation(time_serie1, column_name1, time_serie2, column_name2, method="pearson"):
    tmp = pd.concat([time_serie1, time_serie2], axis=1).interpolate("index").dropna()

    corr = tmp.corr(method)[column_name1][column_name2]

    return corr


class Topology_Discoverer:

    def __init__(self):
        self._graph_measurements = None

        self._broadcast_informations = dict()

        self._inferred_topology = None

    # Threshold at which we estimate that two path have no correlation
    def infer_topology(self, metric="mean", verbose=False):
        edges_correlation = compute_edges_correlation(self._graph_measurements)

        if len(edges_correlation) == 0:
            if verbose is True:
                print("Warning : Not enough data for inferring topology - Correlations cannot be computed.")

            return None

        correlation_graph = get_correlation_graph(self._graph_measurements, edges_correlation, metric)

        if not nx.is_connected(nx.to_undirected(correlation_graph)):
            if verbose is True:
                print("Warning : Not enough data for inferring topology "
                      "- Correlations does not lead to a connected graph.")

            return None

        self._inferred_topology = nx.DiGraph()
        already_processed_origin = set()

        for (origin, _), broadcast_information in self._broadcast_informations.items():
            if origin not in already_processed_origin:
                broadcast_paths = infer_broadcast_paths(correlation_graph, origin, broadcast_information)

                for path in broadcast_paths:
                    self._inferred_topology.add_path(path)

                already_processed_origin.add(origin)

        # Add information about inferred edges
        for edge_id in self._inferred_topology.edges:

            if edge_id in edges_correlation:
                self._inferred_topology[edge_id[0]][edge_id[1]]["corr_score"] = edges_correlation[edge_id][metric]

            else:
                self._inferred_topology[edge_id[0]][edge_id[1]]["corr_score"] = math.inf

            if edge_id in self._graph_measurements.edges:
                self._inferred_topology[edge_id[0]][edge_id[1]]["delay"] = \
                    self._graph_measurements[edge_id[0]][edge_id[1]]["delay"]

                self._inferred_topology[edge_id[0]][edge_id[1]]["delays"] = \
                    self._graph_measurements[edge_id[0]][edge_id[1]]["delays"]

            else:
                self._inferred_topology[edge_id[0]][edge_id[1]]["active"] = True
                self._inferred_topology[edge_id[0]][edge_id[1]]["delay"] = None
                self._inferred_topology[edge_id[0]][edge_id[1]]["delays"] = list()

            if (edge_id[1], edge_id[0]) not in self._inferred_topology.edges:
                self._inferred_topology.add_edge(edge_id[1], edge_id[0], delay=None, delays=list())

        return self._inferred_topology

    def update_measurements(self, broadcast_information, display=False):
        infered_origin, curr_min_sent_time = infer_origin(broadcast_information)

        inferred_edge_measures = infer_edge_measures(broadcast_information)

        self._graph_measurements = merge_measurements_graphs(inferred_edge_measures, self._graph_measurements,
                                                             curr_min_sent_time)

        self._broadcast_informations[(infered_origin, curr_min_sent_time)] = broadcast_information

        if display is True:
            plot_graph(self._graph_measurements, "P2P Network Measurements", "p2p_network_measurements.html",
                       "delay_var", "Delay Variance",)

    def plot_measurements(self):
        plot_graph(self._graph_measurements, "P2P Network Measurements", "p2p_network_measurements.html",
                   "delay_var", "Delay Variance")

    def plot_inferred_topology(self):
        if self._inferred_topology is None:
            raise Exception("Error: \'infer_topology\' must be called at least once before being able to plot it.")

        plot_graph(self._inferred_topology, "Infered Topology", "infered_topology.html", "corr_score", "Correlation", )
