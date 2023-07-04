from sequence.network_management.network_manager import NetworkManager
from sequence.network_management.network_manager import StaticRoutingProtocol
from sequence.network_management.network_manager import ResourceReservationProtocol
from sequence.topology.node import QuantumRouter
import matplotlib.pyplot as plt
import numpy as np
def NewNetworkManager(owner: "QuantumRouter") -> "NetworkManager":
    manager = NetworkManager(owner, [])
    routing = StaticRoutingProtocol(owner, owner.name + ".StaticRoutingProtocol", {})
    rsvp = ResourceReservationProtocol(owner, owner.name + ".RSVP")
    routing.upper_protocols.append(rsvp)
    rsvp.lower_protocols.append(routing)
    manager.load_stack([routing, rsvp])
    return manager

from sequence.topology.router_net_topo import RouterNetTopo




def set_parameters(topology: RouterNetTopo,distance):
    # set memory parameters
    nodes_len = len(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER))
    DISTANCE = distance/nodes_len
    MEMO_FREQ = -1
    MEMO_EXPIRE = 0.6e-3
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY =0.8
    WAVE_LENGTH = 1550
    ATTENUATION = 0.0002
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
    SWAP_SUCC_PROB = 1
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        
    # set quantum channel parameters
    
    QC_FREQ = 1e11
    for qc in topology.get_qchannels():
        qc.distance=DISTANCE
        qc.frequency = QC_FREQ
        qc.attenuation = ATTENUATION
    # set classical channel parameters
    for cc in topology.get_cchannels():
         cc.distance = DISTANCE


def simulate(distance, TARGET_F):
    
    network_topo = RouterNetTopo(network_config)
    tl = network_topo.get_timeline()
    set_parameters(network_topo,distance)
    # the start and end nodes may be edited as desired 
    
    start_time=1e12
    node1 = network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)[0]
    node2 = network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)[-1]
    nm = node1.network_manager
    nm.request(node2.name, start_time, end_time=1.5e12, memory_size=1,target_fidelity = TARGET_F)
    
    tl.init()
    
    tl.run()
    info =  node1.resource_manager.memory_manager[0]
    eg_gen_rate = 0
    """for info in node1.resource_manager.memory_manager:
            print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index),
                                            str(info.remote_node),
                                            str(info.fidelity),
                                            str(info.entangle_time * 1e-12)))
            print("diff time = ", (info.entangle_time-start_time)* 1e-12)"""
    for time in info.eg_history:
        if info.eg_history[time]["remote_node"] == node2.name:
            eg_gen_rate = 1e12 / (int(time)-start_time)
            break
    
    info.entanglement_count = 0
    print("rate: ",eg_gen_rate)
    print("fidelity: ",info.eg_history[time]["fidelity"])
    return eg_gen_rate



TARGET_F = {"0.5":0.5,"0.6":0.6,"0.9":0.9}



network_config = "networks/3nodes.json"
start_index = network_config.find("/networks/") + len("/networks/")
end_index = network_config.find(".json")
network = network_config[start_index:end_index]
final_distance = 300000
distances = list(range(1, final_distance+1, 10000))
distances = [100000]
for F in TARGET_F:
    print("simulation fr F:", F)
    rates = []
    for L in distances:
        rates.append(simulate(L, TARGET_F[F]))
        print("done for ", L)
    """# Save rates to a file
    filename = "adjacentEg_(TCH)/rates/2memo"+tch+".txt"
    # Save rates to a file
    np.savetxt(filename, rates)


"""