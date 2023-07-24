import json
def calculate_distance(total_distance, node1, node2, percentages):
    # Calculate the index positions of the given nodes
    index1 = node1
    index2 = node2

    # Calculate the distances between the nodes based on the percentages
    distance_percentage = 0
    for i in range (index1,index2):
        distance_percentage += percentages[i]
    distance_between_nodes = total_distance * distance_percentage / 100

    return distance_between_nodes

def set_distances(network_config, total_distance, percentages):
    # Load the JSON file
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
            qconnection['distance'] = calculate_distance(total_distance, node1_index, node2_index, percentages)
    
    # Update cconnections distances
    for cconnection in cconnections:
        node1_index = next((i for i, node in enumerate(nodes) if node['name'] == cconnection['node1']), None)
        node2_index = next((i for i, node in enumerate(nodes) if node['name'] == cconnection['node2']), None)
        
        if node1_index is not None and node2_index is not None:
            cconnection['distance'] = calculate_distance(total_distance, node1_index, node2_index, percentages)
    
    # Save the updated JSON file
    with open('networks/2Routers.json', 'w') as file:
        json.dump(data, file, indent=2)


network_config = "networks/2Routers.json"
total_distance = 1000
distance_percentages = [25, 25, 50]


set_distances(network_config, total_distance, distance_percentages)


"""
from sequence.topology.node import QuantumRouter
from sequence.topology.router_net_topo import RouterNetTopo
network_config = "networks/2Routers.json"
topology = RouterNetTopo(network_config)
tl = topology.get_timeline()
routers_list = topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)
distance_percentages = [40, 10, 50]
node1 = 0
node2 = 2
total_distance = 100

for qc in topology.get_qchannels():
    print(qc.sender.name)
for cc in topology.get_cchannels():
    print(cc.sender.name)


# Calculate the distance between the nodes
distance = calculate_distance(total_distance, node1, node2, distance_percentages)

# Print the result
print(f"The distance between node {node1} and node {node2} is {distance}")
"""

