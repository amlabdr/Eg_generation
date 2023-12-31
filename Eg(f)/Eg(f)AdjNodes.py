from sequence.network_management.network_manager import ResourceReservationProtocol



from sequence.network_management.network_manager import NetworkManager
from sequence.network_management.network_manager import StaticRoutingProtocol

from sequence.topology.node import QuantumRouter
import numpy as np

import os


def NewNetworkManager(owner: "QuantumRouter") -> "NetworkManager":
    manager = NetworkManager(owner, [])
    routing = StaticRoutingProtocol(owner, owner.name + ".StaticRoutingProtocol", {})
    rsvp = ResourceReservationProtocol(owner, owner.name + ".RSVP")
    routing.upper_protocols.append(rsvp)
    rsvp.lower_protocols.append(routing)
    manager.load_stack([routing, rsvp])
    return manager

from sequence.topology.router_net_topo import RouterNetTopo




def set_parameters(topology: RouterNetTopo,distance, Freq):
    # set memory parameters
    nodes_len = len(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER))
    DISTANCE = distance/(1000*(nodes_len-1))
    MEMO_FREQ = Freq
    MEMO_EXPIRE = 10e-3
    MEMO_EFFICIENCY = 0.53
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
        qc.distance=DISTANCE*qc.distance
        qc.frequency = QC_FREQ
    # set classical channel parameters
    for cc in topology.get_cchannels():
         cc.distance = cc.distance*DISTANCE


def simulate(distance, Freq, swapping_order = None):
    if swapping_order is not None:
        ResourceReservationProtocol.create_rules = swapping_order
    network_topo = RouterNetTopo(network_config)
    tl = network_topo.get_timeline()
    set_parameters(network_topo,distance,Freq)
    # the start and end nodes may be edited as desired 
    
    start_time=1e12
    node1 = network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)[0]
    node2 = network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)[-1]
    nm = node1.network_manager
    nm.request(node2.name, start_time, end_time=100e12, memory_size=1,target_fidelity = 0)
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
    eg_gen_rate = 0

    for time in info.eg_history:
        if info.eg_history[time]["remote_node"] == node2.name:
            eg_gen_rate = 1e12 / (int(time)-start_time)
            break
    info.entanglement_count = 0
    print("rate: ",eg_gen_rate)
    return eg_gen_rate


Freqdict = {"1e5":1e5,"1e4":1e4,"1e3":1000,"1e1":10,"2e6":2e6, "inf":-1}

final_distance = 200000
distances = list(range(1, final_distance+1, 10000))

network_list = ["networks/0Routers.json"]
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
                rates.append(simulate(L,Freqdict[freq]))
                print("done for ", L)
            directory = "Eg(f)/rates/"+"/"+network+"/"
            filename = directory + freq + ".txt"
            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
            # Save rates to a file
            np.savetxt(filename, rates)
        except Exception as e:
            print("Error occurred:", str(e))
            continue


