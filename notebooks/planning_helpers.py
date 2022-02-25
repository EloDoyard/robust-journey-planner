import networkx as nx
from time_helpers import time_minus_delta
from delay_helpers import inverse_cdf_exp

'''
    This module offers multiple methods and getters that help 
    the traversal of the graph, and accessing its attributes.
'''

# ======================================================= GRAPH GETTERS =======================================================

def is_transfer_edge(G, edge):
    ''' Checks if edge is a transfer edge'''
    return 'distance' in G.edges[edge]

def get_node_departure_time(G, node):
    ''' Returns departure time of node'''
    return G.nodes[node]['departure_time']

def is_visited(G, node):
    ''' Checks if node was visited previously'''
    return G.nodes[node]['visited']

def get_parent(G, node):
    ''' Returns parent of given node'''
    return G.nodes[node]['parent']

def get_edge_departure(G, edge):
    ''' Returns departure time from edge source'''
    return G.edges[edge]['src_departure']

def get_edge_arrival(G, edge):
    ''' Returns arrival time at edge destination'''
    return G.edges[edge]['dst_arrival']

def get_edge_delay(G, edge):
    ''' Returns mean delay associated to edge'''
    return G.edges[edge]['delay']

def get_route(G, edge):
    ''' Returns trip id associated to edge'''
    return G.edges[edge]['route_id']

def get_travel_time(G, edge):
    ''' Returns travel time associated to edge'''
    return G.edges[edge]['travel_time']

# ======================================================= SEARCH HELPERS =======================================================

def arrives_after(G, edge, lower_bound):
    ''' Checks if the edge arrives after the lower bound'''
    return lower_bound <= get_edge_arrival(G, edge)

def arrives_before(G, edge, upper_bound):
    ''' Checks if the edge arrives before the upper bound'''
    return get_edge_arrival(G, edge) <= upper_bound

def get_edge_departure_time(G, edge):
    '''
        Returns the departure time at the source of the given edge
    '''
    if is_transfer_edge(G, edge):
        # Departure time should account for 2 min change when walking
        return time_minus_delta(get_node_departure_time(G, edge[1]), get_travel_time(G, edge)+120)
    else: 
        return G.edges[edge]['src_departure'] 

def find_candidate_edges(G, dst, time_upper_bound, prob_constraint):
    '''
        Returns a list of edges arriving toward `dst`
        within the given time and confidence constraints
    '''
    candidates = []
    # Candidates are all incoming edges towards the destination 
    incoming_edges = G.in_edges(dst, keys = True)
    for edge in incoming_edges:
        if is_edge_valid(G, edge, time_upper_bound, prob_constraint):
            candidates.append(edge)
    return candidates
    
def is_edge_valid(G, edge, time_upper_bound, prob_constraint):
    '''
        Checks if the given edge satisfies time and probability constraints. 
    '''
    data = G.edges[edge]
    parent = get_parent(G, edge[1])
    if is_transfer_edge(G, edge):
        if parent is None:
            return True
        else :
            return not is_transfer_edge(G, parent) # We accept only one transfer edge in a row
    
    time_lower_bound = time_minus_delta(time_upper_bound, 3600) 
    if not (arrives_after(G, edge, time_lower_bound) and arrives_before(G, edge, time_upper_bound)):
        return False
   
    parent = get_parent(G, edge[1])
    
    delta_constraint = inverse_cdf_exp(prob_constraint, get_edge_delay(G, edge))

    if parent is None: # If root node/edge
        return arrives_before(G, edge,  time_minus_delta(time_upper_bound, delta_constraint))
    
    if get_route(G, parent) == get_route(G, edge):
        return True # If the trip hasn't changed

    if is_transfer_edge(G, parent):
        return arrives_before(G, edge,  time_minus_delta(time_upper_bound, delta_constraint))

    return arrives_before(G, edge,  time_minus_delta(time_upper_bound, delta_constraint + 120))