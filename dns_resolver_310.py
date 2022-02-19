import socket
import dns
import dns.message
import dns.query
import dns.rcode
import datetime

output_string = ""
user_input=""
searchingfor_NS=""
requested_domain=""
root_servers = ['192.5.5.241', '192.203.230.10', '192.112.36.4', '198.97.190.53', '192.58.128.30', '199.9.14.201', '199.7.91.13', '192.33.4.12', '192.36.148.17', '193.0.14.129', '202.12.27.33', '199.7.83.42', '198.41.0.4']
root_server=root_servers[0]
# This function sends out a single DNS 'A' request for the given domain to the server specified by destination
def dns_resolver(domain):
    global output_string
    global root_server
    for root_server in root_servers:   # For each of the
        result = dns_query_resolver(domain, root_server,'A')  # This begins the recursive call to query the DNS root server.
        if(result==None):   # If the recursive search returns None, try the next server.
            continue;
        else:
            print(output_string)
            return


def dns_query_resolver(domain, destination, query_type):
    global searchingfor_NS, requested_domain, output_string, root_server

    if(query_type=='A'):
        r_datatype=dns.rdatatype.A
    elif(query_type=='NS'):
        r_datatype=dns.rdatatype.NS
   # if(searchingfor_NS):
      #  domain=requested_domain
    request = dns.message.make_query(domain, r_datatype)
    try:
        response = dns.query.udp(request, destination, timeout=5)
        if (response != None):
            if(response.rcode()==0):  # If the DNS response does not contain an error (ERRCODE=0), continue to analyze it.
                if(len(response.answer) != 0):  # If the DNS response answer parameter is not empty, the query has been successfully resolved
                    if(searchingfor_NS!=""):       # If the resolver has been searching for a name server, check if the server given in the response matches it. If so, the search then continues for the initially requested domain,.
                        if(str(response.answer[0].name)==str(searchingfor_NS)):
                            domain=requested_domain
                            searchingfor_NS=""
                            dns_query_resolver(requested_domain, response.answer[0].items[0].address,"A")
                    else:
                        response_domain=str(response.answer[0].name)
                        response_domain = response_domain[:-1]
                        if(response_domain==requested_domain):   # If the response has an answer, and it is not a name server, it contains the final address of the requested domain located at its Authoritative Name Server.
                            output_string+= requested_domain + "    "+ str(response.answer[0].ttl) + '       IN  A   ' + response.answer[0].items[0].address + "\n"
                        return 1
                    #print(output_string)
                    # print('Successfully resolved domain.')

                elif(len(response.additional)!=0):    # Check the additional field of the response for the TLD server(s) to further the iterative query
                    for TLD_server in response.additional: # Query the authoritative name servers given by the query in order to get closer to the correct address.
                        if(searchingfor_NS!=""):       # If the resolver has been searching for a name server, check if the server given in the response matches it. If so, the search then continues for the initially requested domain,.
                            if(TLD_server==searchingfor_NS):
                                domain=requested_domain
                        if (TLD_server.rdtype==dns.rdatatype.A):    # If the rdtype of the response is A, meaning an IPv4 address, attempt to use it to connect.
                            # domain=str(TLD_server.name)
                            destination=TLD_server.items[0].address
                            output_string += str(TLD_server.name) + "       "+ str(TLD_server.ttl) + "     IN  A   " + destination + "\n"
                           # if(searchingfor_NS):
                               # domain=requested_domain
                        else:
                            continue
                        return dns_query_resolver(domain,destination,'A')
                        # dns_query_resolver(auth_server.name, TLD_server.items)
                        # request=dns.message.make_query(auth_server.name, dns.rdatatype.A)
                        # destination=auth_server.items[0].address
                        # try:
                        #     response = dns.query.udp(request,destination, timeout=5)
                        # except dns.exception.Timeout:
                        #     continue;
                        #
                        # print(auth_server.name)
                        # print(auth_server.items[0])
                elif(len(response.authority)!=0):   # In this case, the response contains name servers but no IP addresses, so the
                    for name_server in response.authority[0].items: # Contact the root server to search for the given name server.
                        searchingfor_NS=name_server
                        return dns_query_resolver(str(name_server),root_server,'A')



            else:
                return None;    # In this case, there was an error with the query. Return none so that the for loop can try the next root server.

    except dns.exception.Timeout:   # If there is an error/timeout when attempting to connect to the given server
        return None
    return response

while(user_input!='Q'):
    requested_domain = input('''Enter the site you'd like to perform a DNS lookup on: ''')
    output_string = "\nQUESTION SECTION:\n" + requested_domain + "     IN  A\n\nANSWER SECTION:\n"
    dns_resolver(requested_domain)
    user_input=input('Enter any key to continue, or Q to quit. ')


#   host = socket.gethostbyname(requested_domain)

#***********************OUTPUT FORMATTING*******************666
# print('\nANSWER SECTION:\n')
# print('A Record : ', requested_domain)
# print('\nQuery time: ')
# print('WHEN: ', date.strftime("%c"))







