import networkx as nx
from random import choice
from planning_helpers import *
from delay_helpers import trip_probability

'''
    This module contains the methods used by our planning algorithm. 
'''

def find_path(G_, src, dst, arrival_time, prob_constraint, banned_edges = []) :
    """ 
        Given a graph, finds a path from the source that arrives 
        at the destination before the provided arrival time. 
        The banned edges are removed from the graph and are not considered when searching. 
    """
    
    G = G_.copy()
    G.remove_edges_from(banned_edges)
    
    # Initially, no node is visited
    nx.set_node_attributes(G, False, 'visited')

    current_node = dst
    
    # Departure time: time before which one should leave to make the connection in time. 
    nx.set_node_attributes(G, {current_node: arrival_time}, 'departure_time')

    # Parent: attribute to help reconstruct the chosen path (points to the next node)
    nx.set_node_attributes(G, {current_node: None}, 'parent')
    queue = []

    while current_node != src:
        # Mark node as visited
        nx.set_node_attributes(G, {current_node: True}, 'visited')

        # Determine candidate edges and add to queue
        queue += find_candidate_edges(G, current_node, get_node_departure_time(G, current_node), prob_constraint)
        # Filter out already visisted nodes
        queue = [edge for edge in queue if not is_visited(G, edge[0])]
        
        # Reverse sort queue according to latest departure times
        queue.sort(key = lambda edge: get_edge_departure_time(G, edge), reverse=True)    
        
        if len(queue) == 0 :
            return '406'
        
        # Take the best edge to explore
        current_edge = queue.pop(0)

        while current_edge in queue:
            queue.remove(current_edge)

        # Update current node and set its departure time
        current_node = current_edge[0]
        nx.set_node_attributes(G, {current_node: get_edge_departure_time(G, current_edge)}, 'departure_time')

        # Set parent 
        nx.set_node_attributes(G, {current_node: current_edge}, 'parent')
        
    return G

def compute_n_trips(top_n, G, src, dst, arrival_time, prob_constraint) :
    """
        Given a graph, finds `top_n` paths from the source that arrives 
        at the destination before the provided arrival time 
        and according the desired probability of success of such paths. 
    """
    found_trips = []
    banned_edges = []

    # Estimated number of transfers during the trip
    n_transfers = 3

    print(f"\rLooking for trips... ({len(found_trips)}/{top_n})", end="")
    while len(found_trips) < top_n :
        path = find_path(G, src, dst, arrival_time, prob_constraint**(1/n_transfers), banned_edges)

        if path != '406' :
            trip = retrieve_trip(path, src, dst)
            proba_path = trip_probability(trip, arrival_time)
            if proba_path < prob_constraint :
                n_transfers += 1
            else :
                found_trips.append((trip, proba_path))
                # Choose a transport edge to remove from the graph at random 
                banned_edges.append(choice([edge for edge in trip.keys() if not is_transfer_edge(G,edge)]))
                
            print(f"\rLooking for trips... ({len(found_trips)}/{top_n})", end="")
        else :
            print(f"\rOnly ({len(found_trips)}/{top_n}) found.", end="")
            break

    return found_trips

def retrieve_trip(G, src, dst):
    '''
        Given the graph result of a trip search, returns
        the found path by traversing it from src to dst
    '''
    node = src
    trip = {}
    while node != dst :
        edge = G.nodes[node]['parent']
        trip[edge] = G.edges[edge]
        node = edge[1]
    return trip