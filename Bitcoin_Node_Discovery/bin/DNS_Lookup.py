import dns.resolver


class DNS_Lookup:
    # List of the DNS Seeds of the bitcoin Network. We'll query those seeds to get back the ip addresses of some full nodes to bootstrap our connection to the P2P Network.
    # /!\ Number of IP Addresses that will be get is not static ! The DNS seeds may provide dynamic DNS seed servers that will automatically scan the network for active nodes IP Addresses.

    dns_seeds = ["seed.bitcoin.sipa.be", "dnsseed.bluematt.me", "dnsseed.bitcoin.dashjr.org", "seed.bitcoinstats.com",
                 "seed.bitcoin.jonasschnelli.ch", "seed.btc.petertodd.org", "seed.bitcoin.sprovoost.nl"]

    def get_DNS_IP(self):
        DNS_Resolver = dns.resolver.Resolver()  # create a new instance named 'myResolver'

        DNS_IP = []
        for i in self.dns_seeds:
            try:
                print("Query to DNS server ", i, "...")

                stop = False
                temp = set()

                while not stop:
                    DNS_Answer = DNS_Resolver.query(i, 'A')
                    tmp_len = len(temp)

                    for j in DNS_Answer:
                        temp.add(j)

                    if len(temp) == tmp_len:
                        stop = True

                stop = False

                while not stop:
                    DNS_Answer = DNS_Resolver.query(i, 'AAAA')

                    tmp_len = len(temp)

                    for j in DNS_Answer:
                        temp.add(j)

                    if len(temp) == tmp_len:
                        stop = True

                DNS_IP = list(set().union(DNS_IP, list(temp)))


            except dns.resolver.Timeout:
                print("Error : Query to DNS server ", i, "Failed : Timeout.")
            except dns.resolver.NXDOMAIN:
                print("Error : Query to DNS server ", i, "Failed : Unkown DNS Server.")
            except dns.resolver.NoNameservers:
                print("Error : Query to DNS server ", i, "Failed : No nameservers are available.")
            except dns.resolver.NoAnswer:
                continue
            except dns.exception.DNSException as exception:
                print("Error : Query to DNS server ", i, "Failed: ", exception)

        print("Number of Seed IP Addresses : ", len(DNS_IP), "\n")
        return DNS_IP
