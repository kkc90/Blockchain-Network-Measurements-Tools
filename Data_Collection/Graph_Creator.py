import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd

# Service Flags
NODE_NONE = 0  # Nothing
NODE_NETWORK = 1  # Node is capable of serving the complete Block Chain
NODE_GETUTXO = (1 << 1)  # Node is capable of responding to the getutxo protocol request
NODE_BLOOM = (1 << 2)  # Node is capable and willing to handle bloom-filtered connections
NODE_WITNESS = (1 << 3)  # Node can be asked for blocks and transactions including witness data
NODE_XTHIN = (1 << 4)  # Node supports Xtreme Thinblocks
NODE_NETWORK_LIMITED = (1 << 10)  # Node is capable of serving the last 288 blocks (2 days)


def read_csv_as_dict(filename):
    return pd.read_csv(filename, index_col=0, squeeze=True).to_dict()


if __name__ == "__main__":
    bitnodes_version_stat = dict()
    bitnodes_country_stat = dict()
    bitnodes_service_stat = dict()
    bitnodes_active_peers = dict()
    bitnodes_ipv4_active_peers = dict()
    bitnodes_ipv6_active_peers = dict()
    bitnodes_other_active_peers = dict()

    directory = "Bitnodes_Measurements/"

    walker = os.walk(directory)
    next(walker)

    for snapshot_name in walker:
        directory = snapshot_name[0]
        _, snapshot_timestamp_date, snapshot_timestamp_time = directory.split("/")[1].split("_")
        snapshot_timestamp = datetime.datetime.strptime((snapshot_timestamp_date + " " + snapshot_timestamp_time),
                                                        "%Y-%m-%d %H:%M:%S")

        active_peers = read_csv_as_dict((directory + "/Bitnodes_Active_Peers.csv"))
        bitnodes_active_peers[snapshot_timestamp] = active_peers

        ipv4_active_peers = read_csv_as_dict((directory + "/Bitnodes_IPV4_Active_Peers.csv"))
        bitnodes_ipv4_active_peers[snapshot_timestamp] = ipv4_active_peers

        ipv6_active_peers = read_csv_as_dict((directory + "/Bitnodes_IPV6_Active_Peers.csv"))
        bitnodes_ipv6_active_peers[snapshot_timestamp] = ipv6_active_peers

        other_active_peers = read_csv_as_dict((directory + "/Bitnodes_Other_Active_Peers.csv"))
        bitnodes_other_active_peers[snapshot_timestamp] = other_active_peers

        country_stat = read_csv_as_dict((directory + "/Bitnodes_Country_Stat.csv"))
        bitnodes_country_stat[snapshot_timestamp] = country_stat

        version_stat = read_csv_as_dict((directory + "/Bitnodes_Version_Stat.csv"))
        bitnodes_version_stat[snapshot_timestamp] = version_stat

        service_stat = read_csv_as_dict((directory + "/Bitnodes_Service_Stat.csv"))
        bitnodes_service_stat[snapshot_timestamp] = service_stat

        print(snapshot_timestamp, len(bitnodes_active_peers[snapshot_timestamp]))

    """
                        Plot of the Distribution of Active Peers with time
    """

    active_peer_distribution = plt.figure("Active Peers Distribution")

    x = list()
    y1 = list()
    y2 = list()
    y3 = list()
    y4 = list()

    tmp = sorted(bitnodes_active_peers)

    for snapshot_timestamp in tmp:
        x.append(snapshot_timestamp)
        y1.append(len(bitnodes_active_peers[snapshot_timestamp]))
        y2.append(len(bitnodes_ipv4_active_peers[snapshot_timestamp]))
        y3.append(len(bitnodes_ipv6_active_peers[snapshot_timestamp]))
        y4.append(len(bitnodes_other_active_peers[snapshot_timestamp]))
        print(snapshot_timestamp, " : ", len(bitnodes_active_peers[snapshot_timestamp]))

    plt.plot(x, y1, x, y2, x, y3, x, y4)
    plt.title("Active Peers Distribution")
    plt.ylabel("Number of active peer")
    plt.legend(["Total", "IPv4", "IPv6", "Other"])
    plt.gcf().autofmt_xdate()

    active_peer_distribution.show()

    input()

    plt.close()
