import datetime
import random
import ipaddress
import numpy as np

from Util import *

"""
        FUNCTION FOR ADDING/REMOVING CONNECTION/PEERS OF A P2P NETWORK
"""


def create_p2p_network(graph_name, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var,
                       max_jitter_var,min_diffusion_delay_rate, max_diffusion_delay_rate, network_ip, **kwargs):
    G = generate_graph(graph_name, **kwargs)

    init_p2p_network(G, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                     min_diffusion_delay_rate, max_diffusion_delay_rate, network_ip)

    return G


def init_p2p_network(G, min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                     min_diffusion_delay_rate, max_diffusion_delay_rate, network_ip):
    ips = iter(ipaddress.IPv4Network(network_ip))

    host_ip = str(next(ips))

    nx.set_node_attributes(G, True, "active")

    nx.set_edge_attributes(G, True, "active")

    labels = dict()

    for node_id in G.nodes():
        labels[node_id] = str(next(ips))

        for adj_node_id in G[node_id].keys():
            # Modelling of the network delay
            G[node_id][adj_node_id]["jitter_mean"] = random.uniform(min_jitter_mean, max_jitter_mean)
            G[node_id][adj_node_id]["jitter_var"] = random.uniform(min_jitter_var, max_jitter_var)

            # Modelling of the network diffusion delay
            G[node_id][adj_node_id]["diffusion_delay_rate"] = random.uniform(min_diffusion_delay_rate,
                                                                             max_diffusion_delay_rate)

            G[node_id][adj_node_id]["delay"] = random.uniform(min_delay, max_delay)

            G[node_id][adj_node_id]["real_delay"] = G[node_id][adj_node_id]["delay"]

            G[node_id][adj_node_id]["delays"] = [G[node_id][adj_node_id]["delay"]]

    nx.relabel_nodes(G, labels, copy=False)


class P2P_Network_Simulator:

    def __init__(self, network_name, min_number_of_connection_per_peer, max_number_of_connection_per_peer,
                 min_delay, max_delay, min_jitter_mean, max_jitter_mean, min_jitter_var, max_jitter_var,
                 min_diffusion_delay_rate, max_diffusion_delay_rate, network_ip="123.0.0.0/8", **kwargs):

        self._G = create_p2p_network(network_name, min_delay, max_delay, min_jitter_mean, max_jitter_mean,
                                     min_jitter_var, max_jitter_var, min_diffusion_delay_rate, max_diffusion_delay_rate,
                                     network_ip, **kwargs)

        nx.freeze(self._G)

        self._min_delay = min_delay
        self._max_delay = max_delay

        self._min_jitter_mean = min_jitter_mean
        self._max_jitter_mean = max_jitter_mean

        self._min_jitter_var = min_jitter_var
        self._max_jitter_var = max_jitter_var

        self._min_diffusion_delay_rate = min_diffusion_delay_rate
        self._max_diffusion_delay_rate = max_diffusion_delay_rate

        self._min_number_of_connection_per_peer = min_number_of_connection_per_peer
        self._max_number_of_connection_per_peer = max_number_of_connection_per_peer

        self._network_ip = network_ip

        self._discovered_G = nx.DiGraph()

    """
            FUNCTION FOR SIMULATING THE BROADCAST OF A BLOCK/TRANSACTION
    """

    def simulate_broadcast(self, origin_set=None, jitter=False, diffusion_spreading=False):
        shortest_path_tree = nx.DiGraph()

        active_G = get_active_graph(self._G)

        active_nodes = list(active_G.nodes)

        if len(active_nodes) == 0:
            raise Exception("Error: Broadcast can't be done in a network with no active nodes.")

        if origin_set is None:
            origin = np.random.choice(active_nodes)

        elif not isinstance(origin_set, str):
            origin = np.random.choice(origin_set)

        else:
            origin = origin_set

        origin_sent_time = datetime.datetime.now()

        broadcast_information = dict()

        broadcast_information[origin] = origin_sent_time.timestamp()

        if jitter is True or diffusion_spreading is True:
            for edge_id in self._G.edges:
                if jitter is True:

                    self._G[edge_id[0]][edge_id[1]]["real_delay"] = self._G[edge_id[0]][edge_id[1]]["delay"] \
                                                                    + random.normalvariate(
                        self._G[edge_id[0]][edge_id[1]]["jitter_mean"],
                        np.sqrt(self._G[edge_id[0]][edge_id[1]]["jitter_var"]))

                if diffusion_spreading is True:
                    self._G[edge_id[0]][edge_id[1]]["real_delay"] = self._G[edge_id[0]][edge_id[1]]["delay"] \
                                                                    + random.expovariate(
                        self._G[edge_id[0]][edge_id[1]]["diffusion_delay_rate"])

                if self._G[edge_id[0]][edge_id[1]]["real_delay"] > 0:
                    self._G[edge_id[0]][edge_id[1]]["delays"] += [self._G[edge_id[0]][edge_id[1]]["real_delay"]]

                else:
                    remove_connection(self._G, edge_id)

        paths_length, shortest_paths = nx.single_source_dijkstra(active_G, source=origin, weight="real_delay")

        for node_id, shortest_path in shortest_paths.items():
            if node_id != origin:
                shortest_path_tree.add_path(shortest_path)

                reception_time = origin_sent_time + datetime.timedelta(0, seconds=paths_length[node_id])

                broadcast_information[node_id] = reception_time.timestamp()

        edge_attributes = {(u, v): ddict for u, v, ddict in self._G.edges(data=True)}

        nx.set_edge_attributes(shortest_path_tree, edge_attributes)

        shortest_path_tree.nodes[origin]["origin"] = True

        if not nx.is_connected(nx.to_undirected(shortest_path_tree)):
            raise Exception("Error: Broadcast is not returning a connected graph.")

        nx.set_node_attributes(self._discovered_G, "active", False)

        self._discovered_G.add_nodes_from(shortest_path_tree.nodes, active=True)

        self._discovered_G.add_edges_from(shortest_path_tree.edges(data=True))

        return broadcast_information, shortest_path_tree, origin

    """
            FUNCTION FOR SIMULATING THE DYNAMIC OF THE NETWORK
    """

    def simulate_jitter(self):
        for node_id in self._G.nodes():

            for adj_node_id in self._G[node_id].keys():
                self._G[node_id][adj_node_id]["delay"] = random.normalvariate(
                    self._G[node_id][adj_node_id]["jitter_mean"],
                    np.sqrt(self._G[node_id][adj_node_id]["jitter_var"])
                )

                self._G[node_id][adj_node_id]["delays"] += [self._G[node_id][adj_node_id]["delay"]]

    def simulate_peer_connecting_and_ending_connections(self, max_nb_connection_added, max_nb_connection_removed):
        """
        :param max_nb_connection_added:
        :param max_nb_connection_removed:

        :return:
        """

        nb_connection_added = np.random.randint(0, max_nb_connection_added)

        add_connections(self._G, nb_connection_added, self._min_delay, self._max_delay, self._min_jitter_mean,
                        self._max_jitter_mean, self._min_jitter_var, self._max_jitter_var,
                        self._min_diffusion_delay_rate, self._max_diffusion_delay_rate)

        nb_connection_removed = np.random.randint(0, max_nb_connection_removed)

        remove_connections(self._G, nb_connection_removed)

        reconnect_graph(self._G, self._min_delay, self._max_delay,
                        self._min_jitter_mean, self._max_jitter_mean, self._min_jitter_var, self._max_jitter_var,
                        self._min_diffusion_delay_rate, self._max_diffusion_delay_rate,
                        self._min_number_of_connection_per_peer, self._max_number_of_connection_per_peer)

    def simulate_peer_leaving_and_entering(self, max_nb_peer_added, max_nb_peer_removed, add_known_peer_proba):
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

        nb_peer_added = np.random.randint(0, max_nb_peer_added)

        add_peers(self._G, nb_peer_added, add_known_peer_proba, self._min_number_of_connection_per_peer,
                  self._max_number_of_connection_per_peer, self._min_delay, self._max_delay, self._min_jitter_mean,
                  self._max_jitter_mean, self._min_jitter_var, self._max_jitter_var, self._min_diffusion_delay_rate,
                  self._max_diffusion_delay_rate, self._network_ip)

        nb_peer_remove = np.random.randint(0, max_nb_peer_removed)

        remove_peers(self._G, nb_peer_remove)

        reconnect_graph(self._G, self._min_delay, self._max_delay, self._min_jitter_mean, self._max_jitter_mean,
                        self._min_jitter_var, self._max_jitter_var,
                        self._min_diffusion_delay_rate, self._max_diffusion_delay_rate,
                        self._min_number_of_connection_per_peer, self._max_number_of_connection_per_peer)

    def get_nb_active_peers(self):
        return len(get_active_graph(self._G).nodes)

    def get_nb_peer(self):
        return len(self._G.nodes())

    def get_nb_edges(self):
        return len(self._G.edges())

    def discovered_graph_error(self, inferred_topology):
        return inferred_graph_error_measurements(self._discovered_G, inferred_topology)

    def error_measurements(self, inferred_topology):
        return inferred_graph_error_measurements(self._G, inferred_topology)

    def plot(self):
        plot_graph(self._G, "P2P Network", "p2p_network.html")

    def plot_discovered_graph(self):
        plot_graph(self._discovered_G, "Discovered P2P Network", "discovered_p2p_network.html")
