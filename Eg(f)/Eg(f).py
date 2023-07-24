import traceback

from sequence.kernel.process import Process
from sequence.kernel.event import Event
#import logging

# Configure logging
#logging.basicConfig(level=logging.INFO, filename='logs.txt', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')


from sequence.components.memory import Memory, MemoryArray

from sequence.network_management.network_manager import ResourceReservationProtocol



from sequence.network_management.network_manager import NetworkManager
from sequence.network_management.network_manager import StaticRoutingProtocol
from sequence.resource_management.memory_manager import MemoryInfo, MemoryManager

from sequence.topology.node import QuantumRouter
import matplotlib.pyplot as plt
import numpy as np


import os

class myInfo(MemoryInfo):
    def __init__(self, memory: Memory, index: int, state="RAW"):
        super().__init__(memory, index, state)
        self.remote_end_node = None

    def set_remote_end_node(self, remote_end_node):
        self.remote_end_node = remote_end_node.name
        self.remote_end_node_eg_counts = 0
        self.coherence_time = []
        print("remote end node: ", self.remote_end_node)

    def to_entangled(self) -> None:
        """Method to set memory to entangled state."""
        self.state = "ENTANGLED"
        self.remote_node = self.memory.entangled_memory["node_id"]
        self.remote_memo = self.memory.entangled_memory["memo_id"]
        self.fidelity = self.memory.fidelity
        self.entangle_time = self.memory.timeline.now()
        self.entanglement_count +=1
        if self.remote_node == self.remote_end_node:
            print("entangled with end node ", self.remote_end_node)
            eg_coherence_time = self.memory.coherence_time#min(self.memory.coherence_time,self.remote_memo.coherence_time)
            self.coherence_time.append(eg_coherence_time)
            self.memory.expire()
            #self.memory.owner.resource_manager.update(self.memory, 'RAW')
            #self.memory.owner.resource_manager.exp
            '''process = Process(self.memory, "expire", [])
            event = Event(self.memory.timeline.now(), process)
            self.memory.timeline.schedule(event)'''
            self.remote_end_node_eg_counts+=1
        self.eg_history[self.entangle_time] = {}
        self.eg_history[self.entangle_time]["remote_node"]=self.remote_node
        self.eg_history[self.entangle_time]["fidelity"] = self.fidelity


def NewNetworkManager(owner: "QuantumRouter") -> "NetworkManager":
    manager = NetworkManager(owner, [])
    routing = StaticRoutingProtocol(owner, owner.name + ".StaticRoutingProtocol", {})
    rsvp = ResourceReservationProtocol(owner, owner.name + ".RSVP")
    routing.upper_protocols.append(rsvp)
    rsvp.lower_protocols.append(routing)
    manager.load_stack([routing, rsvp])
    return manager

from sequence.topology.router_net_topo import RouterNetTopo

import json
def calculate_distance(total_distance, node1, node2, distance_proportions):
    # Calculate the index positions of the given nodes
    index1 = node1
    index2 = node2

    # Calculate the distances between the nodes based on the distance_proportions
    distance_proportion = 0
    for i in range (index1,index2):
        distance_proportion += distance_proportions[i]
    distance_between_nodes = total_distance * distance_proportion / 100

    return distance_between_nodes

def set_distances(network_config, total_distance, distance_proportions):
    # Load the JSON file
    CC_DISTANCE = total_distance/(len(distance_proportions))
    with open(network_config) as file:
        data = json.load(file)
    
    nodes = data['nodes']
    qconnections = data['qconnections']
    cconnections = data['cconnections']
    
    # Update qconnections distances
    for qconnection in qconnections:
        node1_index = next((i for i, node in enumerate(nodes) if node['name'] == qconnection['node1']), None)
        node2_index = next((i for i, node in enumerate(nodes) if node['name'] == qconnection['node2']), None)
        
        if node1_index is not None and node2_index is not None:
            qconnection['distance'] = calculate_distance(total_distance, node1_index, node2_index, distance_proportions)
    
    # Update cconnections distances
    for cconnection in cconnections:
        cconnection['distance'] = CC_DISTANCE

    # Save the updated JSON file
    with open('networks/2Routers.json', 'w') as file:
        json.dump(data, file, indent=2)




def set_parameters(topology: RouterNetTopo,distance, Freq):
    # set memory parameters
    
    MEMO_FREQ = Freq
    MEMO_EXPIRE = -1#10e-3
    MEMO_EFFICIENCY =   0.53
    MEMO_FIDELITY =0.99
    WAVE_LENGTH = 500
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        memory_array = node.get_components_by_type("MemoryArray")[0]
        memory_array.update_memory_params("frequency", MEMO_FREQ)
        memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)
        memory_array.update_memory_params("wavelength", WAVE_LENGTH)

    # set detector parameters
    DETECTOR_EFFICIENCY = 1
    
    for node in topology.get_nodes_by_type(RouterNetTopo.BSM_NODE):
        bsm = node.get_components_by_type("SingleAtomBSM")[0]
        bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
    # set entanglement swapping parameters
    SWAP_SUCC_PROB = 0.39
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        
    # set quantum channel parameters
    
    QC_FREQ = 1e11
    for qc in topology.get_qchannels():
        #qc.frequency = QC_FREQ
        qc.distance = qc.distance
    


def simulate(distance, Freq, swapping_order = None):
    distance_proportions = [33,33,33]
    set_distances(network_config, distance, distance_proportions)
    if swapping_order is not None:
        ResourceReservationProtocol.create_rules = swapping_order
    network_topo = RouterNetTopo(network_config)
    tl = network_topo.get_timeline()
    set_parameters(network_topo,distance,Freq)
    # the start and end nodes may be edited as desired 
    
    start_time=1e12
    node1 = network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)[0]
    node2 = network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)[-1]
    node1.resource_manager.memory_manager.memory_map = [myInfo(memory, index) for index, memory in enumerate(node1.resource_manager.memory_manager.memory_array)]
    for my_info in node1.resource_manager.memory_manager.memory_map:
        my_info.set_remote_end_node(node2)
    nm = node1.network_manager
    nm.request(node2.name, start_time, end_time=2e12, memory_size=1,target_fidelity = 0)
    tl.init()
    tl.run()
    """print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in node1.resource_manager.memory_manager:
            print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index),
                                            str(info.remote_node),
                                            str(info.fidelity),
                                            str(info.entangle_time * 1e-12)))
            print("diff time = ", (info.entangle_time-start_time)* 1e-12)"""
    info =  node1.resource_manager.memory_manager[0]
    eg_gen_rate = (info.remote_end_node_eg_counts*1e12)/(tl.now()-start_time)
    

    """for time in info.eg_history:
        if info.eg_history[time]["remote_node"] == node2.name:
            eg_gen_rate = 1e12 / (int(time)-start_time)
            break"""
    #info.entanglement_count = 0
    print("rate: ",eg_gen_rate)
    print("number of success entanglement: ", len(info.coherence_time))
    print("avrage_coherence time: ", sum(info.coherence_time) / len(info.coherence_time))
    return eg_gen_rate


Freqdict = {"1e5":1e5,"1e4":1e4,"1e3":1000,"1e1":10}
Freqdict = {"1e5":-1}


final_distance = 200000
distances = list(range(100, final_distance+1, 10000))
distances = [10000]


from swaping_rules.left2right import create_rulesR2L, create_rulesL2R
swapping_order = {"L2R":create_rulesL2R,"R2L":create_rulesR2L}
network_list = ["networks/0Routers.json","networks/1Routers.json","networks/2Routers.json","networks/3Routers.json"]
network_list = ["networks/2Routers.json"]
for order in swapping_order:
    print("++++Simulation for swaping order :", order)
    for network_config in network_list:
        start_index = network_config.find("/networks/") + len("/networks/")
        end_index = network_config.find(".json")
        network = network_config[start_index:end_index]
        print("++++Simulation for network :", network_config)
        for freq in Freqdict:
            try:
                print("simulation fr freq:", freq)
                rates = []
                for L in distances:
                    rates.append(simulate(L,Freqdict[freq],swapping_order[order]))
                    print("done for ", L)
                directory = "Eg(f)/rates/"+order+"/"+network+"/"
                filename = directory + freq + ".txt"
                # Create the directory if it doesn't exist
                if not os.path.exists(directory):
                    os.makedirs(directory)
                # Save rates to a file
                np.savetxt(filename, rates)
            except Exception as e:
                error_message = traceback.format_exc()

                # Print the complete error
                print("Error occurred:\n", error_message)
                #print("Error occurred:", str(e))
                continue


