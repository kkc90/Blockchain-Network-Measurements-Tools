import os
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
    return pd.read_csv(filename, header=None, index_col=0, squeeze=True).to_dict()


def add_dict(dict1, dict2):
    for key, value in dict1.items():
        if key in dict2:
            dict2[key] = dict2[key] + value
        else:
            dict2[key] = value

    return dict2


def add_version_stat(version_stat, version):
    if version in version_stat:
        version_stat[version] = version_stat[version] + 1
    else:
        version_stat[version] = 1


def add_country_stat(country_stat, country):
    if country in country_stat:
        country_stat[country] = country_stat[country] + 1
    else:
        country_stat[country] = 1


def add_service_stat(service_stat, service):
    stat = get_service(service)

    if str(stat) in service_stat:
        service_stat[str(stat)] = service_stat[str(stat)] + 1
    else:
        service_stat[str(stat)] = 1


def get_service(service):
    result = []
    tmp = service

    if tmp == NODE_NONE:
        result.append("NODE_NODE")

    if tmp >= NODE_NETWORK_LIMITED:
        result.append("NODE_NETWORK_LIMITED")
        tmp = tmp - NODE_NETWORK_LIMITED

    if tmp >= NODE_XTHIN:
        result.append("NODE_XTHIN")
        tmp = tmp - NODE_XTHIN

    if tmp >= NODE_WITNESS:
        result.append("NODE_WITNESS")
        tmp = tmp - NODE_WITNESS

    if tmp >= NODE_BLOOM:
        result.append("NODE_BLOOM")
        tmp = tmp - NODE_BLOOM

    if tmp >= NODE_GETUTXO:
        result.append("NODE_GETUTXO")
        tmp = tmp - NODE_GETUTXO

    if tmp >= NODE_NETWORK:
        result.append("NODE_NETWORK")
        tmp = tmp - NODE_NETWORK

    if len(result) == 0 or tmp != 0:
        result.append("OTHER")

    return result


def add_bitnodes_active_peers(bitnodes_active_peers, bitnodes_ipv4_active_peers, bitnodes_ipv6_active_peers, peer, connection_time):
    if peer.find(".onion") == -1:
        line = peer.replace("[", "").replace("]", "").split(":")
        ip = ""

        if len(line) > 2:
            for i in line[0:len(line) - 1]:
                ip = ip + ":" + i
            ip = ip[1:len(ip)]
        else:
            ip = line[0]

        bitnodes_active_peers[ip] = connection_time
        type = ipaddress.ip_address(ip).version

        if type == 4:
            bitnodes_ipv4_active_peers[ip] = connection_time
        elif type == 6:
            bitnodes_ipv6_active_peers[ip] = connection_time


if __name__ == "__main__":
    BITNODES_VERSION_STAT = dict()
    BITNODES_COUNTRY_STAT = dict()
    BITNODES_SERVICE_STAT = dict()
    BITNODES_ACTIVE_PEERS = dict()
    BITNODES_IPV4_ACTIVE_PEERS = dict()
    BITNODES_IPV6_ACTIVE_PEERS = dict()

    directory = "Bitnodes_Measurements/"

    walker = os.walk(directory)
    next(walker)

    for snapshot_name in walker:
        snapshot_timestamp = walker[0]

        active_peers = read_csv_as_dict((snapshot_timestamp + "/Bitnodes_Active_Peers.csv"))
        BITNODES_ACTIVE_PEERS.update(active_peers)

        ipv4_active_peers = read_csv_as_dict((snapshot_timestamp + "/Bitnodes_IPV4_Active_Peers.csv"))
        BITNODES_IPV4_ACTIVE_PEERS.update(ipv4_active_peers)

        ipv6_active_peers = read_csv_as_dict((snapshot_timestamp + "/Bitnodes_IPV6_Active_Peers.csv"))
        BITNODES_IPV6_ACTIVE_PEERS.update(ipv6_active_peers)

        version_stat = read_csv_as_dict((snapshot_timestamp + "/Bitnodes_Version_Stat.csv"))
        add_dict(BITNODES_VERSION_STAT, version_stat)

        service_stat = read_csv_as_dict((snapshot_timestamp + "/Bitnodes_Service_Stat.csv"))
        add_dict(BITNODES_SERVICE_STAT, service_stat)

