import csv
import ipaddress
import operator
import os

import geoip2.database

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
        "Impossible to gather Statistics about the country : "
        "The Measurements Folder doesn't contains a Table of Addresses.")

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
        "Impossible to gather Statistics about the country of Active Peers : "
        "The Measurements Folder doesn't contains a Table of Active Peers.")

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
        "Impossible to gather Statistics about the IPV4_Table : "
        "The Measurements Folder doesn't contains a Table of IPV4 Peers.")

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
        "Impossible to gather Statistics about the IPV6_Table : "
        "The Measurements Folder doesn't contains a Table of IPV6 Peers.")

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
    print(
        "Impossible to gather Statistics about the Bitcoin Handshake Duration : "
        "The Measurements Folder doesn't contains a Table of Bitcoin Handshake Duration.")

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
        "Impossible to gather Statistics about the Connection_failed_Stat : "
        "The Measurements Folder doesn't contains a Table of Connection_failed_Stat.")

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
        "Impossible to gather Statistics about the Peers_Query_nb : "
        "The Measurements Folder doesn't contains a Table of Peers_Query_nb.")

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
        "Impossible to gather Statistics about the Service : "
        "The Measurements Folder doesn't contains a Table of Service_Stat.")

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
        "Impossible to gather Statistics about the Version : "
        "The Measurements Folder doesn't contains a Table of Version_Stat.")

bitcoin_stat = dict()

bitcoin_stat["NB_IP"] = NB_IP
bitcoin_stat["NB_IPV4"] = NB_IPV4
bitcoin_stat["NB_IPV6"] = NB_IPV6
bitcoin_stat["NB_IPV4_ACTIVE_PEERS"] = NB_IPV4_ACTIVE_PEERS
bitcoin_stat["AVERAGE_QUERY_NB"] = AVERAGE_QUERY_NB

write_dict_as_csv("Measurements/Bitcoin_Stat.csv", bitcoin_stat)
