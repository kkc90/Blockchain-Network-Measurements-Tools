import geoip2.database
import os
import operator
import csv
import requests
import datetime
import ipaddress

# Service Flags
NODE_NONE = 0  # Nothing
NODE_NETWORK = 1  # Node is capable of serving the complete Block Chain
NODE_GETUTXO = (1 << 1)  # Node is capable of responding to the getutxo protocol request
NODE_BLOOM = (1 << 2)  # Node is capable and willing to handle bloom-filtered connections
NODE_WITNESS = (1 << 3)  # Node can be asked for blocks and transactions including witness data
NODE_XTHIN = (1 << 4)  # Node supports Xtreme Thinblocks
NODE_NETWORK_LIMITED = (1 << 10)  # Node is capable of serving the last 288 blocks (2 days)


def write_list_as_csv(filename, list):
    with open(filename, "w+") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        for i in list:
            writer.writerow([i])


def read_csv_as_list(filename):
    with open(filename, "r") as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)


def write_tuple_as_csv(filename, tuple):
    with open(filename, "w+") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in tuple:
            writer.writerow([key, value])


def write_dict_as_csv(filename, dict):
    with open(filename, "w+") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict.items():
            writer.writerow([key, value])


def read_csv_as_dict(filename):
    with open(filename, "r") as csv_file:
        reader = csv.reader(csv_file)
        return dict(reader)


if not os.path.exists("Measurements/"):
    print("Error: No Measurements to Process.")
    exit(-1)

NB_IP = 0
NB_IPV4 = 0
NB_IPV6 = 0
NB_IPV4_ACTIVE_PEERS = 0
AVERAGE_QUERY_NB = 0

doublon = False

if os.path.exists("Measurements/IP_Table"):
    GEOIP_DATABASE_READER = geoip2.database.Reader('GeoLite2-City/GeoLite2-City.mmdb')
    COUNTRY_STAT = dict()
    IP_Table = list()
    file = open("Measurements/IP_Table", "r")

    for temp in file:
        line = temp.replace("\n", "")
        ipaddress.ip_address(line)

        if line in IP_Table:
            doublon = True

        IP_Table.append(line)
        NB_IP = NB_IP + 1
        try:
            country = GEOIP_DATABASE_READER.city(line).country.name
        except geoip2.errors.AddressNotFoundError:
            country = "Unknown"

        if country in COUNTRY_STAT:
            COUNTRY_STAT[country] = COUNTRY_STAT[country] + 1
        else:
            COUNTRY_STAT[country] = 1
    file.close()

    write_list_as_csv("Measurements/IP_Table.csv", IP_Table)
    write_tuple_as_csv("Measurements/Country_Stat.csv", sorted(COUNTRY_STAT.items(), key=operator.itemgetter(1)))

    if doublon is True:
        print("Error: There are several occurence of ip addresses in IP Table.")
        exit(-1)

else:
    print(
        "Impossible to gather Statistics about the country : The Measurements Folder doesn't contains a Table of Addresses.")

doublon = False

if os.path.exists("Measurements/Active_Peers"):
    GEOIP_DATABASE_READER = geoip2.database.Reader('GeoLite2-City/GeoLite2-City.mmdb')
    ACTIVE_COUNTRY_STAT = dict()
    Active_Peers = dict()
    file = open("Measurements/Active_Peers", "r")

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        ip = line[0]
        ipaddress.ip_address(ip)

        if ip in Active_Peers:
            doublon = True
            print(ip)

        Active_Peers[ip] = line[1]
        NB_IPV4_ACTIVE_PEERS = NB_IPV4_ACTIVE_PEERS + 1
        try:
            country = GEOIP_DATABASE_READER.city(ip).country.name
        except geoip2.errors.AddressNotFoundError:
            country = 'Unknown'

        if country in ACTIVE_COUNTRY_STAT:
            ACTIVE_COUNTRY_STAT[country] = ACTIVE_COUNTRY_STAT[country] + 1
        else:
            ACTIVE_COUNTRY_STAT[country] = 1
    file.close()

    write_dict_as_csv("Measurements/Active_Peers.csv", Active_Peers)
    write_tuple_as_csv("Measurements/Active_Peers_Country_Stat.csv",
                       sorted(ACTIVE_COUNTRY_STAT.items(), key=operator.itemgetter(1)))

    if doublon is True:
        print("Error: There are several occurence of ip addresses in Active Peer Table.")
        exit(-1)
else:
    print(
        "Impossible to gather Statistics about the country of Active Peers : The Measurements Folder doesn't contains a Table of Active Peers.")

doublon = False

if os.path.exists("Measurements/IPV4_Table"):
    IPV4_Table = list()
    file = open("Measurements/IPV4_Table", "r")

    for temp in file:
        line = temp.replace("\n", "")

        if line in IPV4_Table:
            doublon = True

        IPV4_Table.append(line)
        NB_IPV4 = NB_IPV4 + 1

    file.close()

    write_list_as_csv("Measurements/IPV4_Table.csv", IPV4_Table)

    if doublon is True:
        print("Error: There are several occurence of ip addresses in IPv4 Table.")
        exit(-1)
else:
    print(
        "Impossible to gather Statistics about the IPV4_Table : The Measurements Folder doesn't contains a Table of IPV4 Peers.")

doublon = False

if os.path.exists("Measurements/IPV6_Table"):
    IPV6_Table = list()
    file = open("Measurements/IPV6_Table", "r")

    for temp in file:
        line = temp.replace("\n", "")

        if line in IPV6_Table:
            doublon = True

        IPV6_Table.append(line)
        NB_IPV6 = NB_IPV6 + 1

    file.close()

    write_list_as_csv("Measurements/IPV6_Table.csv", IPV6_Table)

    if doublon is True:
        print("Error: There are several occurence of ip addresses in IPv6 Table.")
        exit(-1)
else:
    print(
        "Impossible to gather Statistics about the IPV6_Table : The Measurements Folder doesn't contains a Table of IPV6 Peers.")

doublon = False

if os.path.exists("Measurements/Peers_TCP_Handshake_Duration"):

    file = open("Measurements/Peers_TCP_Handshake_Duration", "r")

    Peers_Handshake_Duration = dict()
    Peers_MAX_RTT = dict()

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        ipaddress.ip_address(line[0])

        if line[0] in Peers_Handshake_Duration:
            doublon = True
            print(line[0])

        Peers_Handshake_Duration[line[0]] = float(line[1])
        Peers_MAX_RTT[line[0]] = (float(line[1]) / 3) * 2

    file.close()

    write_dict_as_csv("Measurements/Peers_TCP_Handshake_Duration.csv", Peers_Handshake_Duration)
    write_dict_as_csv("Measurements/Peers_MAX_RTT.csv", Peers_MAX_RTT)

    if doublon is True:
        print("Error: There are several occurence of ip addresses in TCP Handshake Statistics Table.")
        exit(-1)

else:
    print("Impossible to gather Statistics about the RTT : The Measurements Folder doesn't contains a Table of RTT.")

doublon = False

if os.path.exists("Measurements/Peers_Bitcoin_Handshake_Duration"):

    file = open("Measurements/Peers_Bitcoin_Handshake_Duration", "r")

    Peers_Bitcoin_Handshake_Duration = dict()
    Peers_MAX_RTT = dict()

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        ipaddress.ip_address(line[0])

        if line[0] in Peers_Bitcoin_Handshake_Duration:
            doublon = True

        Peers_Bitcoin_Handshake_Duration[line[0]] = float(line[1])

    file.close()

    write_dict_as_csv("Measurements/Peers_Bitcoin_Handshake_Duration.csv", Peers_Bitcoin_Handshake_Duration)

    if doublon is True:
        print("Error: There are several occurence of ip addresses in Bitcoin Handshake Statistics Table.")
        exit(-1)

else:
    print("Impossible to gather Statistics about the Bitcoin Handshake Duration : The Measurements Folder doesn't contains a Table of Bitcoin Handshake Duration.")

doublon = False

if os.path.exists("Measurements/Connection_failed_stat"):
    file = open("Measurements/Connection_failed_stat", "r")
    Connection_failed_Stat = dict()

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        stat = ""
        for i in line[0:len(line) - 1]:
            stat = stat + i

        Connection_failed_Stat[stat] = int(line[len(line) - 1])

    write_dict_as_csv("Measurements/Connection_Failed_Stat.csv", Connection_failed_Stat)
    file.close()
else:
    print(
        "Impossible to gather Statistics about the Connection_failed_Stat : The Measurements Folder doesn't contains a Table of Connection_failed_Stat.")

doublon = False

if os.path.exists("Measurements/Peers_Query_nb"):
    file = open("Measurements/Peers_Query_nb", "r")
    Peers_Query_nb = dict()
    nb_peers = 0

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        ipaddress.ip_address(line[0])
        nb_query = int(line[1])

        if line[0] in Peers_Query_nb:
            doublon = True

        Peers_Query_nb[line[0]] = nb_query
        AVERAGE_QUERY_NB = AVERAGE_QUERY_NB + nb_query
        nb_peers = nb_peers + 1

    if nb_peers != 0:
        AVERAGE_QUERY_NB = AVERAGE_QUERY_NB / nb_peers

    write_dict_as_csv("Measurements/Peers_Query_nb.csv", Peers_Query_nb)
    file.close()
else:
    print(
        "Impossible to gather Statistics about the Peers_Query_nb : The Measurements Folder doesn't contains a Table of Peers_Query_nb.")

if os.path.exists("Measurements/Service_Stat"):
    file = open("Measurements/Service_Stat", "r")
    Service_Stat = dict()

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        Service_Stat[line[0]] = int(line[1])

    write_dict_as_csv("Measurements/Service_Stat.csv", Service_Stat)
    file.close()
else:
    print(
        "Impossible to gather Statistics about the Service : The Measurements Folder doesn't contains a Table of Service_Stat.")

if os.path.exists("Measurements/Version_Stat"):
    file = open("Measurements/Version_Stat", "r")
    Version_Stat = dict()

    for temp in file:
        line = temp.replace("\n", "").split(" : ")
        Version_Stat[line[0]] = int(line[1])

    write_dict_as_csv("Measurements/Version_Stat.csv", Version_Stat)
    file.close()
else:
    print(
        "Impossible to gather Statistics about the Version : The Measurements Folder doesn't contains a Table of Version_Stat.")

bitcoin_stat = dict()

bitcoin_stat["NB_IP"] = NB_IP
bitcoin_stat["NB_IPV4"] = NB_IPV4
bitcoin_stat["NB_IPV6"] = NB_IPV6
bitcoin_stat["NB_IPV4_ACTIVE_PEERS"] = NB_IPV4_ACTIVE_PEERS
bitcoin_stat["AVERAGE_QUERY_NB"] = AVERAGE_QUERY_NB

write_dict_as_csv("Measurements/Bitcoin_Stat.csv", bitcoin_stat)


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


def add_service_stat(service_stat, service):
    stat = get_service(service)

    if str(stat) in service_stat:
        service_stat[str(stat)] = service_stat[str(stat)] + 1
    else:
        service_stat[str(stat)] = 1


def add_bitnodes_active_peers(bitnodes_active_peers, bitnodes_ipv4_active_peers, bitnodes_ipv6_active_peers, peer):
    if peer.find(".onion") == -1:
        line = peer.replace("[", "").replace("]", "").split(":")
        ip = ""

        if len(line) > 2:
            for i in line[0:len(line) - 1]:
                ip = ip + ":" + i
            ip = ip[1:len(ip)]
        else:
            ip = line[0]

        bitnodes_active_peers.append(ip)
        type = ipaddress.ip_address(ip).version
        if type == 4:
            bitnodes_ipv4_active_peers.append(ip)
        elif type == 6:
            bitnodes_ipv6_active_peers.append(ip)


BITNODES_VERSION_STAT = dict()
BITNODES_COUNTRY_STAT = dict()
BITNODES_SERVICE_STAT = dict()
BITNODES_ACTIVE_PEERS = list()
BITNODES_IPV4_ACTIVE_PEERS = list()
BITNODES_IPV6_ACTIVE_PEERS = list()

if not os.path.exists("Measurements/Bitnodes/"):
    os.makedirs("Measurements/Bitnodes/")

URL = "https://bitnodes.earn.com/api/v1/snapshots/latest/"

req = requests.get(url=URL)
data = req.json()
nodes = data["nodes"]

snapshot_time = datetime.datetime.fromtimestamp(data["timestamp"])

if not os.path.exists("Measurements/Bitnodes/Snapshot_" + str(snapshot_time)):
    os.makedirs("Measurements/Bitnodes/Snapshot_" + str(snapshot_time))

for node in nodes:
    add_version_stat(BITNODES_VERSION_STAT, nodes[node][0])
    add_country_stat(BITNODES_COUNTRY_STAT, nodes[node][7])
    add_service_stat(BITNODES_SERVICE_STAT, nodes[node][3])
    add_bitnodes_active_peers(BITNODES_ACTIVE_PEERS, BITNODES_IPV4_ACTIVE_PEERS, BITNODES_IPV6_ACTIVE_PEERS, node)

write_dict_as_csv(("Measurements/Bitnodes/Snapshot_" + str(snapshot_time) + "/Bitnodes_Version_Stat.csv"),
                  BITNODES_VERSION_STAT)
write_dict_as_csv(("Measurements/Bitnodes/Snapshot_" + str(snapshot_time) + "/Bitnodes_Country_Stat.csv"),
                  BITNODES_COUNTRY_STAT)
write_dict_as_csv(("Measurements/Bitnodes/Snapshot_" + str(snapshot_time) + "/Bitnodes_Service_Stat.csv"),
                  BITNODES_SERVICE_STAT)
write_list_as_csv(("Measurements/Bitnodes/Snapshot_" + str(snapshot_time) + "/Bitnodes_Active_Peers.csv"),
                  BITNODES_ACTIVE_PEERS)
write_list_as_csv(("Measurements/Bitnodes/Snapshot_" + str(snapshot_time) + "/Bitnodes_IPV4_Active_Peers.csv"),
                  BITNODES_IPV4_ACTIVE_PEERS)
write_list_as_csv(("Measurements/Bitnodes/Snapshot_" + str(snapshot_time) + "/Bitnodes_IPV6_Active_Peers.csv"),
                  BITNODES_IPV6_ACTIVE_PEERS)
