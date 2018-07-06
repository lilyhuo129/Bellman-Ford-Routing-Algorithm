import sys                      #read arguments from console
import socket                   #socket programing
import json                     #sending and recieving packets
import threading                #multithreading
import time
import os
import copy
#current node info
current_node=sys.argv[1];
current_port=int(sys.argv[2]);
config=sys.argv[3];

#variables used

d={};
dv={}; #distance vector
all_routers=[]   #list of all routers:added as discovered through neighbour's distance vector
nexthop={}     #points out what neighbour will be passed in order to get to route
displayLock=threading.Lock()
routing_table={}
pre_time={}


# Nodes Class
class Nodes:
     def __init__(self, current_node,current_port,config):
        self.current_node=current_node;      #stores the routers name
        self.current_port=current_port;      #stores its own port number
        direct_link={}
        neighbours=[]
        global config_file
        config_file={}
        self.direct_links=direct_link        #costs of get to a router directly
        self.neighbours=neighbours           #stores the list of neighbouring routers
        #reading file
        fo = open(config, "r+");
        data=fo.read();
        nodes=(data.split());
        total_nodes=nodes[0];
        i=1;
        length=len(nodes);
        d[current_node]=[float(0),current_port]
        # d stores the cost, port# against each neighbours name
        while (i!=length):
            d[nodes[i]]=[float(nodes[i+1]), int(nodes[i+2])]
            i+=3;

        #converting dictionary into dict of dict
        #inorder to identify the source of advertised distance vector, form is changed into dict of dict
        #there is only one element in the outer dictionary whose key is the router name whose distance vector it is
        #and value is the config file of the router (which is itself a dictionary)
        value = d.items();
        i=0;
        length=len(d);


        while(i < length ):
            #direct_link stores cost of directly going from router to neighbour against that neighbour
            direct_link[value[i][0]]=value[i][1][0]
            if(value[i][0]!= current_node):
               #stores list of all neighbours of that router
                neighbours.append(value[i][0])
            i+=1;

        dv[current_node]=direct_link
        config_file=dv.copy()      #copy is created so that when distance vector is updated everytime bellman-ford runs, copy does not change
        #print dv

#listening function
def Recv():

    recvIP="localhost"
    recvPort=current_port
    recv=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)    #creating socket/router
    recv.bind((recvIP,recvPort))   #binding router to its designated port
    dist_vctr={}         #Converted distance vector sent by neighbour
    dist_vector={}       #intermediate dictionary:only used for conversion
    print ("SERVER HERE!\nThe server is ready to receive")
    #loop ensure that runs infinitely
    while 1:
        current_time=time.time();
        message, clientAddress = recv.recvfrom(2048)
        dst_vector= json.loads(message)
        #jason returns sent message in unicode
        #converting unicode into ascii
        for key in dst_vector.keys():
            neighbor=key.encode('ascii','ignore')
        for key,val in dst_vector[neighbor].items():
            key=key.encode('ascii','ignore')
            dist_vector[key]=val
        dist_vctr[neighbor]=dist_vector.copy()
        #setting recieved info to null so that new message does not get mixed with it
        dist_vector={}

        #updates are made here in routing_table
        #initially routing_table is empty so we add config file of router and distance vector sent by neighbour to it
        #after first iteration, it simply updates the stored data (counter for any change as distance vectors sent my neighbours may change)
        routing_table[current_node]=config_file[current_node].copy()
        routing_table.update(dist_vctr)
        #routing table is basically a dictionary of dictionay which stores
        #distance vectors of neighbours against their names along with config file
        #of current router against its name
        


        #time is noted on arrival of each packet, if a packet from a neighbour is not recieved in 40 seconds, it is considered dead and its cost is set to infinity
        for node in node1.neighbours:
        # first packet from neighbour arrived
            if neighbor not in pre_time.keys():
                pre_time[neighbor]=current_time;
        # packet from this neig has received
            else:
            # packet was received in time
                if node==neighbor and pre_time[neighbor] != float('INF'):
                    pre_time[neighbor]=current_time
                #router went offline and has not come online
                elif (node == neighbor and pre_time[neighbor] == float('INF')):
                    pre_time[neighbor]=current_time
                #for all other neighbouring routers
                elif (node != neighbor and node in pre_time.keys()):
                # time out for that node, dead node
                #time remains same for 3 iterartions
                    if current_time - pre_time[node] > 10:
                         #node time set to infinity, node deleted fom config file info, and last hop towards that node
                        pre_time[node] = float('INF')
                        del routing_table[current_node][node]
                        del routing_table[node]
                        del nexthop[node]


        #for the iterations after time is set infinity
        for node in pre_time.keys():
             if (pre_time[node] == float('inf') and node in routing_table.keys() ):
                  del routing_table[current_node][node]
                  del routing_table[node]
                  


        #triggering thread that runs bellman-ford algorithm and passing routing table as argument
        threading.Thread(target=bellman_ford, args=(routing_table,)).start()
    #closing socket
    recv.close()


#broadcast function
def Sender():
    #loop ensures that runs infinitely
    while 1:

        #getting port numbers where to send data i.e. port numbers of neighbours
        port_list=[]
        for value in d.items():
            port_list.append(value[1][1]);
        serverIP="localhost"
        #creating socket for sending, there is no need to bind it as sending port is irrelevant
        #therefore it is dynamically assigned
        sender=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #using json to convert distance vector into a sendable for
        strings = json.dumps(dv)

        # sending data i.e distance vector to each neighbour
        for items in port_list:
            if int(items)!=current_port:
                sender.sendto(strings.encode(),(serverIP, int(items)))
        #gives gap of 5secs before resending distance vector
        time.sleep(5)
        #closing socket
        sender.close()




def bellman_ford(routing_table):


    #adding those neighbours in my_neighbours whose distance vector has been recieved / that has become online
    my_neighbour=[]
    for node in routing_table:
        for neighbour in node1.neighbours:
            if(node == neighbour):
                my_neighbour.append(node)


    #finding out all routers
    abc=[]          #list used for conversion

    #creating list of all routers known
    #those which are neighbours to current router plus those present in distance vector advertised by neighbour
    for node in routing_table:
        for neighbour in routing_table[node]:
             #dead links excluded
             if (neighbour in pre_time.keys()  and pre_time[neighbour]== float('inf')):
                pass
             else:
                abc.append(neighbour)


    #to remove repetition
    my_set= set(abc)
    all_routers= list(my_set)

    #algorithm starts
    #setting all non neighbour nodes to infinity
    for node in routing_table:
        for router in all_routers:
            if(router not in routing_table[node].keys()):
                     routing_table[node][router]=float('inf')

    #this contains two loop:
    #outer loop runs of all known routers and inner loop runs for all neighbours whose distance vector has been recieved
    for router in all_routers:
        for neighbour in my_neighbour:
                #checks if ditance of current node-router is greater (distance of neighbour-router + distance of current node-neighbour)
                #basically looks for alternate routes through neighbours i.e. (distance of neighbour-router + distance of current node-neighbour)
                #measures it again direct distance to that router i.e. ditance of current node-router
            if (routing_table[current_node][router] > routing_table[neighbour][router] + routing_table[current_node][neighbour]):
                #updates value to shorter distance and puts neighbour through which it goes into nexthop dictionary against that router
                min_distance = routing_table[neighbour][router] + routing_table[current_node][neighbour]
                routing_table[current_node][router]=min_distance
                #if router is a neighbour and min_cost calculated is less than or equal to direct link cost 
                if(router in my_neighbour and config_file[current_node][router]<=min_distance):
                     routing_table[current_node][router]=config_file[current_node][router]
                     nexthop[router]= 'direct'
                else:
                     nexthop[router] = neighbour
                #for the first time algo runs, dict nexthop will be empty hence to define direct link, we add this condition
                #after that, next time dict nexthop already has values in it so there will be no need to change nexthop unless shorter distance is detected
                #which is already catered to in the if statement
            elif (len(nexthop.keys()) != len(all_routers)):
                nexthop[router] = 'direct'
                #incase same distance has been calculated through other distance vectors
            elif(router in my_neighbour and config_file[current_node][router] <= routing_table[current_node][router]):
                     routing_table[current_node][router]=config_file[current_node][router]
                     nexthop[router]= 'direct'


    #updating distance vector
    dv[current_node] = routing_table[current_node]
    #display function is called
    display()

def display():
        #this lock prevents other routers from using this function which it is already being used
        #to make sure right data is displayed in right window
        with displayLock:
            #clears screen everytime before display
            os.system("cls")
            print("\n I am Router " + current_node + '\n')
            for node in dv[current_node].keys():
                  print(" Least cost path to router " + node + " : through " + nexthop[node] + " with  cost " +  str("{0:.1f}".format(dv[current_node][node]) + "\n"))




#instance of node class created
node1=Nodes(current_node,current_port,config)
#threads for sending and recieving are triggered
threading.Thread(target=Sender).start()
threading.Thread(target=Recv).start()
