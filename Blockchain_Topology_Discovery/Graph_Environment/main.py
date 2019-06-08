import click

import Topology_Discoverer as Topology_Discoverer
from P2P_Network_Simulator import *


def simulate_stable_network(p2p_network, metric="mean"):
    p2p_network.plot()

    topology_handler = Topology_Discoverer.Topology_Discoverer()

    user_left = False

    while user_left is False:

        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        topology_handler.update_measurements(broadcast_information, display=False)

        plot_graph(real_shortest_path_tree, "Broadcast", "broadcast.html")
        p2p_network.plot_discovered_graph()

        if click.confirm('Broadcast Simulation Done. Infer Topology ?', default=True):
            inferred_topology = topology_handler.infer_topology(metric=metric, verbose=True)

            error, mean_delay_error \
                = p2p_network.error_measurements(inferred_topology)

            discovered_error, mean_delay_discovered_error \
                = p2p_network.error_measurements(inferred_topology)

            print("Topology Results : Discovered Graph Error " + str(discovered_error) + " - Total Graph Error "
                  + str(error))

        if not click.confirm('Continue ?', default=True):
            break


def simulate_unstable_network(p2p_network):
    p2p_network.plot()

    topology_handler = Topology_Discoverer.Topology_Discoverer()

    user_left = False

    while user_left is False:

        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        topology_handler.update_measurements(broadcast_information, display=False)

        plot_graph(real_shortest_path_tree, "Broadcast", "broadcast.html")

        if not click.confirm('Broadcast Simulation Done. Continue ?', default=True):
            break

        p2p_network.simulate_jitter()

        nb_peer = p2p_network.get_nb_peer()

        max_nb_possible_connection = nb_peer * (nb_peer - 1)

        curr_nb_connections = p2p_network.get_nb_edges() / 2

        p2p_network.simulate_peer_connecting_and_ending_connections(
            max_nb_connection_added=int((max_nb_possible_connection - curr_nb_connections) / 4),
            max_nb_connection_removed=int(curr_nb_connections / 4)
        )

        nb_active_peers = p2p_network.get_nb_active_peers()

        p2p_network.simulate_peer_leaving_and_entering(1, int(nb_active_peers / 3), 0.5)

        topology_handler.plot_measurements()
        p2p_network.plot()

    p2p_network.plot()

    topology_handler.plot_measurements()


def study_stable_network(p2p_network, max_iteration, step, metric="mean"):
    topology_handler = Topology_Discoverer.Topology_Discoverer()

    errors = dict()
    discovered_errors = dict()

    for i in range(1, max_iteration + 1):
        broadcast_information, real_shortest_path_tree, real_origin = p2p_network.simulate_broadcast()

        topology_handler.update_measurements(broadcast_information)

        if i % step == 0:
            inferred_topology = topology_handler.infer_topology(metric=metric, verbose=True)

            if inferred_topology is not None:

                error, mean_delay_error \
                    = p2p_network.error_measurements(inferred_topology)

                discovered_error, mean_delay_discovered_error \
                    = p2p_network.error_measurements(inferred_topology)

                print(("Iteration " + str(i) + " : Topology Inference Results - Discovered Graph Error "
                       + str(discovered_error) + " - Total Graph Error "
                       + str(error)))

                errors[i] = error
                discovered_errors[i] = discovered_error

            else:
                print(("Iteration " + str(i) + " : "
                       + str((None, None, None, None))))

        if (i + 1) % step == 0:
            print("Iteration " + str(i) + " : Topology Inference ...", end="\r")

        else:
            print("Iteration " + str(i) + " : Broadcast ...", end="\r")

    return errors, discovered_errors


def main():
    network_name = "Random Graph"

    max_iteration = 1000000
    step = 100

    p2p_network = P2P_Network_Simulator(network_name,
                                        min_number_of_connection_per_peer=1,
                                        max_number_of_connection_per_peer=8,
                                        min_delay=20,
                                        max_delay=100,
                                        min_jitter_mean=5,
                                        max_jitter_mean=15,
                                        min_jitter_var=0,
                                        max_jitter_var=2,
                                        min_diffusion_delay_rate=0.2,
                                        max_diffusion_delay_rate=0.9,
                                        nb_nodes=20
                                        )

    # test(p2p_network)

    # simulate_stable_network(p2p_network)

    # simulate_unstable_network(p2p_network)

    errors, discovered_errors = study_stable_network(p2p_network, max_iteration, step)

    # errors = study_unstable_network(p2p_network, max_iteration, step)

    # store_errors("errors.json", errors)

    # plot_error_graphs(errors)


if __name__ == "__main__":
    main()
