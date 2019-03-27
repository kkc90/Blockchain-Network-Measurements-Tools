import csv
import datetime
import ipaddress
import os
import time

import requests

NB_TIME_BETWEEN_SNAPSHOT = 1800  # s

# Service Flags
NODE_NONE = 0  # Nothing
NODE_NETWORK = 1  # Node is capable of serving the complete Block Chain
NODE_GETUTXO = (1 << 1)  # Node is capable of responding to the getutxo protocol request
NODE_BLOOM = (1 << 2)  # Node is capable and willing to handle bloom-filtered connections
NODE_WITNESS = (1 << 3)  # Node can be asked for blocks and transactions including witness data
NODE_XTHIN = (1 << 4)  # Node supports Xtreme Thinblocks
NODE_NETWORK_LIMITED = (1 << 10)  # Node is capable of serving the last 288 blocks (2 days)


def write_dict_as_csv(filename, dict):
    with open(filename, "w+") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict.items():
            writer.writerow([key, value])


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


def add_organisation_stat(orga_stat, orga):
    if orga in orga_stat:
        orga_stat[orga] = orga_stat[orga] + 1
    else:
        orga_stat[orga] = 1


def add_asn_stat(asn_stat, asn):
    if asn in asn_stat:
        asn_stat[asn] = asn_stat[asn] + 1
    else:
        asn_stat[asn] = 1


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


def add_bitnodes_active_peers(bitnodes_active_peers, bitnodes_ipv4_active_peers, bitnodes_ipv6_active_peers, other_active_peer, peer,
                              connection_time):
    if peer.find(".onion") == -1:
        line = peer.replace("[", "").replace("]", "").split(":")
        ip = ""

        if len(line) > 2:
            for i in line[0:len(line) - 1]:
                ip = ip + ":" + i
            ip = ip[1:len(ip)]

            bitnodes_active_peers[ip] = connection_time
            bitnodes_ipv6_active_peers[ip] = connection_time
        else:
            ip = line[0]
            bitnodes_active_peers[ip] = connection_time
            bitnodes_ipv4_active_peers[ip] = connection_time
    else:
        ip = peer.replace("[", "").replace("]", "").split(":")[0]
        bitnodes_active_peers[ip] = connection_time
        other_active_peer[ip] = connection_time


def query_bitnodes_snapshot(directory, url):
    bitnodes_version_stat = dict()
    bitnodes_version_stat["Version"] = "Number of Peer"

    bitnodes_country_stat = dict()
    bitnodes_country_stat["Country"] = "Number of Peer"

    bitnodes_service_stat = dict()
    bitnodes_service_stat["Service"] = "Number of Peer"

    bitnodes_organisation_stat = dict()
    bitnodes_organisation_stat["Organisation Name"] = "Number of Peer"

    bitnodes_asn_stat = dict()
    bitnodes_asn_stat["ASN"] = "Number of Peer"

    bitnodes_active_peers = dict()
    bitnodes_active_peers["IP"] = "Connection Time"

    bitnodes_ipv4_active_peers = dict()
    bitnodes_ipv4_active_peers["IPv4 IP"] = "Connection Time"

    bitnodes_ipv6_active_peers = dict()
    bitnodes_ipv6_active_peers["IPv6 IP"] = "Connection Time"

    other_active_peers = dict()
    other_active_peers["IP"] = "Connection Time"

    req = requests.get(url=url)
    data = req.json()
    nodes = data["nodes"]

    if not os.path.exists(directory):
        os.makedirs(directory)

    for node in nodes:
        add_version_stat(bitnodes_version_stat, nodes[node][0])
        add_country_stat(bitnodes_country_stat, nodes[node][7])
        add_organisation_stat(bitnodes_organisation_stat, nodes[node][12])
        add_asn_stat(bitnodes_asn_stat, nodes[node][11])
        add_service_stat(bitnodes_service_stat, nodes[node][3])
        add_bitnodes_active_peers(bitnodes_active_peers, bitnodes_ipv4_active_peers, bitnodes_ipv6_active_peers,
                                  other_active_peers, node, nodes[node][2])

    write_dict_as_csv((directory + "/Bitnodes_Version_Stat.csv"),
                      bitnodes_version_stat)

    write_dict_as_csv((directory + "/Bitnodes_Country_Stat.csv"),
                      bitnodes_country_stat)

    write_dict_as_csv((directory + "/Bitnodes_Service_Stat.csv"),
                      bitnodes_service_stat)

    write_dict_as_csv((directory + "/Bitnodes_Active_Peers.csv"),
                      bitnodes_active_peers)

    write_dict_as_csv((directory + "/Bitnodes_IPV4_Active_Peers.csv"),
                      bitnodes_ipv4_active_peers)

    write_dict_as_csv((directory + "/Bitnodes_IPV6_Active_Peers.csv"),
                      bitnodes_ipv6_active_peers)

    write_dict_as_csv((directory + "/Bitnodes_Other_Active_Peers.csv"),
                      other_active_peers)

    write_dict_as_csv((directory + "/Bitnodes_Organisation_Stat.csv"),
                      bitnodes_organisation_stat)

    write_dict_as_csv((directory + "/bitnodes_ASN_stat.csv"),
                      bitnodes_asn_stat)


if __name__ == "__main__":

    pages = list()

    page_nb = 170
    while True:
        print("Querying Page ", page_nb, " ...")
        URL = "https://bitnodes.earn.com/api/v1/snapshots/?page=" + str(page_nb) + "&limit=100"

        req = requests.get(url=URL)
        data = req.json()

        if "detail" in data:
            print(data["detail"])
            break

        pages.append(data["results"])

        page_nb = page_nb + 1

    if not os.path.exists("Bitnodes_Measurements/"):
        os.makedirs("Bitnodes_Measurements/")

    prec_snapshot_time = datetime.datetime.fromtimestamp(0)

    page_nb = 0
    for page in pages:
        print("Treating Page ", page_nb, " :")
        i = 0
        for result in page:
            snapshot_time = datetime.datetime.fromtimestamp(result["timestamp"])

            if abs((snapshot_time - prec_snapshot_time).total_seconds()) > NB_TIME_BETWEEN_SNAPSHOT:
                print("Page ", page_nb, " : Treating Snapshot ", i, " : ", snapshot_time)
                directory = "Bitnodes_Measurements/Snapshot_" + str(snapshot_time.strftime("%Y-%m-%d_%H:%M:%S"))
                query_bitnodes_snapshot(directory, result["url"])
                prec_snapshot_time = snapshot_time
                i = i + 1

        page_nb = page_nb + 1
