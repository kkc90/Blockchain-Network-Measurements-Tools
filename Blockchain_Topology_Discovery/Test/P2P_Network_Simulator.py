import datetime
import random
import ipaddress
import math

from Util import *

"""
        FUNCTION FOR ADDING/REMOVING CONNECTION/PEERS OF A P2P NETWORK
"""


def create_p2p_network(graph_name, min_delay, max_delay, network_ip, **kwargs):
    G = generate_graph(graph_name, **kwargs)

    init_p2p_network(G, min_delay, max_delay, network_ip)

    return G


# TO DO --> Put a stochatic distribution on each edge of the network
def init_p2p_network(G, min_delay, max_delay, network_ip):
    ips = iter(ipaddress.IPv4Network(network_ip))

    host_ip = str(next(ips))

    nx.set_node_attributes(G, True, "active")

    nx.set_edge_attributes(G, True, "active")

    nx.set_edge_attributes(G, 0.0, "delay_var")
    nx.set_edge_attributes(G, 0.0, "mean_delay")

    labels = dict()

    for node_id in G.nodes():
        labels[node_id] = str(next(ips))

        for adj_node_id in G[node_id].keys():
            G[node_id][adj_node_id]["delay"] = random.uniform(min_delay, max_delay)
            G[node_id][adj_node_id]["delays"] = [G[node_id][adj_node_id]["delay"]]
            G[node_id][adj_node_id]["mean_delay"] = G[node_id][adj_node_id]["delay"]

    nx.relabel_nodes(G, labels, copy=False)


class P2P_Network_Simulator:

    def __init__(self, network_name, min_delay=1, max_delay=100, min_jitter=1, max_jitter=10, network_ip="123.0.0.0/8",
                 **kwargs):
        self._G = create_p2p_network(network_name, min_delay, max_delay, network_ip, **kwargs)

        self._min_delay = min_delay
        self._max_delay = max_delay

        self._network_ip = network_ip

        self._min_jitter = min_jitter
        self._max_jitter = max_jitter

    def plot(self):
        plot_graph(self._G, "P2P Network", "p2p_network.html", "delay._var", "Delay Variance", )

    """
            FUNCTION FOR SIMULATING THE BROADCAST OF A BLOCK/TRANSACTION
    """

    def simulate_broadcast(self, jitter=False):
        shortest_path_tree = nx.DiGraph()

        active_G = get_active_graph(self._G)

        active_nodes = list(active_G.nodes)

        if len(active_nodes) == 0:
            raise Exception("Error: Broadcast can't be done in a network with no active nodes.")

        origin = np.random.choice(active_nodes)

        origin_sent_time = datetime.datetime.now()

        broadcast_information = dict()
        broadcast_information[origin] = origin_sent_time.timestamp()

        for node_id in active_nodes:
            if node_id != origin:
                shortest_path = nx.shortest_path(active_G, source=origin, target=node_id, weight="delay")
                shortest_path_tree.add_path(shortest_path)

                last_node_id = shortest_path[0]
                sent_time = origin_sent_time

                for adj_node_id in shortest_path[1::]:
                    sent_time += datetime.timedelta(0, active_G[last_node_id][adj_node_id]["delay"])
                    shortest_path_tree[last_node_id][adj_node_id]["delay"] = \
                        active_G[last_node_id][adj_node_id]["delay"]

                    last_node_id = adj_node_id

                broadcast_information[node_id] = sent_time.timestamp()

        shortest_path_tree.nodes[origin]["origin"] = True

        return broadcast_information, shortest_path_tree, origin

    """
            FUNCTION FOR SIMULATING THE DYNAMIC OF THE NETWORK
    """

    def simulate_jitter(self):
        for node_id in self._G.nodes():

            for adj_node_id in self._G[node_id].keys():
                self._G[node_id][adj_node_id]["delay"] += random.uniform(self._min_jitter, self._max_jitter)
                self._G[node_id][adj_node_id]["delays"] += [self._G[node_id][adj_node_id]["delay"]]

                self._G[node_id][adj_node_id]["delay_var"] = np.var(self._G[node_id][adj_node_id]["delays"])
                self._G[node_id][adj_node_id]["mean_delay"] = np.mean(self._G[node_id][adj_node_id]["delays"])

    def simulate_peer_connecting_and_ending_connections(self, max_nb_connection_added, max_nb_connection_removed,
                                                        min_connection_delay, max_connection_delay):
        nb_connection_added = np.random.randint(-max_nb_connection_removed, max_nb_connection_added)

        if nb_connection_added < 0:
            remove_connections(self._G, -nb_connection_added)
        else:
            add_connections(self._G, nb_connection_added, min_connection_delay, max_connection_delay)

        re_connect_graph(self._G, self._min_delay, self._max_delay)

    def simulate_peer_leaving_and_entering(self, max_nb_peer_added, max_nb_peer_removed, add_known_peer_proba,
                                           min_nb_connection, max_nb_connection, min_connection_delay,
                                           max_connection_delay):
        """
        :param max_nb_peer_added: the maximum number of peer that can be added.
        :param max_nb_peer_removed: the maximum number of peer that can be removed.
        :param add_known_peer_proba: the proportion of added peer that were previously part
                of the network and then left.
        :param min_nb_connection: the minimum number of connection that the peer will have.
        :param max_nb_connection: the maximum number of connection that the peer will have.
        :param min_connection_delay: the minimum connection delays of the connection.
        :param max_connection_delay: the maximum connection delays of the connection.

        :return:
        """

        nb_peer_added = np.random.randint(-max_nb_peer_removed, max_nb_peer_added)

        if nb_peer_added < 0:
            remove_peers(self._G, -nb_peer_added)
        else:
            add_peers(self._G, nb_peer_added, add_known_peer_proba, min_nb_connection, max_nb_connection,
                      min_connection_delay,
                      max_connection_delay)

        re_connect_graph(self._G, self._min_delay, self._max_delay)

    def remove_peer(self, peer_id):
        remove_peer(self._G, peer_id)

    def remove_random_active_peer(self):
        tmp = list(get_active_graph(self._G).nodes())

        peer_id = np.random.choice(tmp)

        remove_peer(self._G, peer_id)

        re_connect_graph(self._G, self._min_delay, self._max_delay)

        return peer_id

    def get_nb_peer(self):
        return len(self._G.nodes())

    def get_nb_edges(self):
        return len(self._G.edges())

    def error_measurements(self, infered_topology):
        nb_infered_edges = len(infered_topology.edges()) / 2  # Because directed Graph

        nb_real_edges = len(self._G.edges()) / 2  # Because directed graph

        nb_infered_nodes = len(infered_topology.nodes())

        nb_real_nodes = len(self._G.nodes())

        total_possible_edges = (nb_real_nodes * (nb_real_nodes - 1)) / 2

        true_positive = 0

        false_positive = 0

        true_negative = 0

        false_negative = 0

        delay_error = list()

        already_considered_edges = list()

        for edge in self._G.edges():
            if edge not in already_considered_edges:

                if infered_topology.has_edge(edge[0], edge[1]):
                    true_positive = true_positive + 1

                    infered_edge_delay = infered_topology[edge[0]][edge[1]]["delay"]

                    real_edge_delay = self._G[edge[0]][edge[1]]["delay"]

                    if infered_topology[edge[0]][edge[1]]["delay"] is not None:
                        delay_error.append(np.abs(infered_edge_delay - real_edge_delay))

                    infered_edge_delay = infered_topology[edge[1]][edge[0]]["delay"]

                    real_edge_delay = self._G[edge[1]][edge[0]]["delay"]

                    if infered_topology[edge[1]][edge[0]]["delay"] is not None:
                        delay_error.append(np.abs(infered_edge_delay - real_edge_delay))

                else:
                    false_negative = false_negative + 1

                already_considered_edges.append((edge[0], edge[1]))
                already_considered_edges.append((edge[1], edge[0]))

        mean_delay_error = np.mean(delay_error)

        nb_infer_negative = (total_possible_edges - nb_infered_edges)

        true_negative = nb_infer_negative - false_negative

        false_positive = nb_infered_edges - true_positive

        if (true_positive + false_negative) != nb_real_edges:
            raise Exception("Error: The number of True positive added to the number of False negative must be equal to "
                            "the number of positive.")

        elif (true_negative + false_positive) != (total_possible_edges - nb_real_edges):
            raise Exception("Error: The number of True negative added to the number of False positive must be equal to "
                            "the number of negative.")

        return (true_positive, true_negative, false_positive, false_negative), mean_delay_error
