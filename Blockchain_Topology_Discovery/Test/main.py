import click
import math

import Topology_Discoverer_2 as Topology_Discoverer
from P2P_Network_Simulator import *


# Techniques for infering broadcast path.
def infer_broadcast(broadcast_information, real_origin):
    inferred_origin, curr_min_sent_time = Topology_Discoverer.infer_origin(broadcast_information)

    if real_origin != inferred_origin:
        raise Exception(("Error : Inferred Origin " + inferred_origin + " != Real origin " + real_origin))

    inferred_shortest_path_tree = nx.DiGraph()

    inferred_shortest_path_tree.add_nodes_from(list(broadcast_information.keys()), active=True)

    for node_id in inferred_shortest_path_tree.nodes():
        if node_id != inferred_origin:
            delay = broadcast_information[node_id] - broadcast_information[inferred_origin]

            inferred_shortest_path_tree.add_edge(inferred_origin, node_id, delay=delay, active=True)

    inferred_shortest_path_tree.nodes[inferred_origin]["origin"] = True

    return inferred_shortest_path_tree


def test(network_name):
    p2p_network = P2P_Network_Simulator(network_name)

    # p2p_network.plot()

    user_left = False

    while user_left is False:

        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        inferred_shortest_path_tree = infer_broadcast_path(broadcast_information, real_origin)

        plot_broadcast(real_shortest_path_tree, "Broadcast", "broadcast.html")

        plot_broadcast(inferred_shortest_path_tree, "Inferred Broadcast", "inferred_broadcast.html")

        if not click.confirm('Broadcast Simulation Done. Continue ?', default=True):
            break


def simulate_stable_network(network_name):
    p2p_network = P2P_Network_Simulator(network_name)

    p2p_network.plot()

    topology_handler = Topology_Discoverer.Topology_Discoverer()

    user_left = False

    while user_left is False:

        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        topology_handler.update_measurements(broadcast_information, display=False)

        plot_broadcast(real_shortest_path_tree, "Broadcast", "broadcast")

        topology_handler.plot_measurements()

        if not click.confirm('Broadcast Simulation Done. Continue ?', default=True):
            break

    topology_handler.plot_measurements()


def study_stable_network(network_name, max_iteration, step, metric="mean"):
    p2p_network = P2P_Network_Simulator(network_name)

    topology_handler = Topology_Discoverer.Topology_Discoverer()

    thresholds = np.round(np.linspace(0.1, 2, 6), 2)

    errors = dict()

    best_score = -math.inf
    best_treshold = dict()

    for i in range(1, max_iteration + 1):
        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        topology_handler.update_measurements(broadcast_information)

        if i % step == 0:
            error = dict()

            for threshold in thresholds:
                inferred_topology = topology_handler.infer_topology(threshold, metric=metric)

                if inferred_topology is not None:

                    (true_positive, true_negative, false_positive, false_negative), mean_delay_error \
                        = p2p_network.error_measurements(inferred_topology)

                    error[threshold] = (true_positive, true_negative, false_positive, false_negative)

                    score = true_positive/(true_positive + false_negative) \
                            + true_negative/(true_negative + false_positive)

                    if score > best_score:
                        best_score = score
                        best_treshold[i] = threshold

                    print(("Iteration " + str(i) + " - Threshold = " + str(threshold) + " : "
                           + str((true_positive, true_negative, false_positive, false_negative))), end="\r")

            errors[i] = error

    # p2p_network.plot()

    # topology_handler.plot_measurements()

    # topology_handler.plot_inferred_topology()

    return errors


def simulate_unstable_network(network_name):
    p2p_network = P2P_Network_Simulator(network_name)

    p2p_network.plot()

    topology_handler = Topology_Discoverer.Topology_Discoverer()

    user_left = False

    while user_left is False:

        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        topology_handler.update_measurements(broadcast_information, display=False)

        plot_broadcast(real_shortest_path_tree, "Broadcast", "broadcast")

        if not click.confirm('Broadcast Simulation Done. Continue ?', default=True):
            break

        p2p_network.simulate_jitter()
        # p2p_network.simulate_peer_connecting_and_ending_connections()
        # p2p_network.simulate_peer_leaving_and_entering()

        topology_handler.plot_measurements()

    p2p_network.plot()

    topology_handler.plot_measurements()


def study_unstable_network(network_name, max_iteration, step):
    p2p_network = P2P_Network_Simulator(network_name)

    topology_handler = Topology_Discoverer.Topology_Discoverer()

    var_tresholds = [0.0, 1.0, 10.0, 100.0, 500.0]

    errors = dict()

    for i in range(1, max_iteration + 1):
        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        plot_broadcast(real_shortest_path_tree, "Broadcast", "broadcast")

        topology_handler.update_measurements(broadcast_information, display=False)

        if i % step == 0:
            error = dict()

            histories_to_consider = [int(i) for i in np.linspace(1, i, 10)]

            for history_to_consider in histories_to_consider:

                error[history_to_consider] = dict()

                for var_treshold in var_tresholds:
                    inferred_topology = topology_handler.infer_topology(var_treshold, history_to_consider, metric="mean")

                    (true_positive, true_negative, false_positive, false_negative), mean_delay_error \
                        = p2p_network.error_measurements(inferred_topology)

                    error[history_to_consider][var_treshold] \
                        = (true_positive, true_negative, false_positive, false_negative)

                    print(("Iteration " + str(i) + " - " + " Considered Historic = " + str(history_to_consider)
                           + " - Variance Treshold = " + str(var_treshold) + " : "
                           + str((true_positive, true_negative, false_positive, false_negative))), end="\r")

            errors[i] = error

        p2p_network.simulate_jitter()
        # p2p_network.simulate_peer_connecting_and_ending_connections()
        # p2p_network.simulate_peer_leaving_and_entering()

    # p2p_network.plot()

    # topology_handler.plot_measurements()

    # topology_handler.plot_inferred_topology()

    return errors


if __name__ == "__main__":
    network_name = "Florentine Families"
    max_iteration = 1000000
    step = 100

    # test(network_name)

    # simulate_stable_network(network_name)

    # simulate_unstable_network(network_name)

    errors = study_stable_network(network_name, max_iteration, step)

    # errors = study_unstable_network(network_name, max_iteration, step)

    # store_errors("errors.json", errors)

    # plot_error_graphs(errors)
