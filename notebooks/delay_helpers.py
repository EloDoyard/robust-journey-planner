import numpy as np
from time_helpers import get_seconds

'''
    This module contains multiple helpers concerning the delays 
    and the probabilities of a trip succeeding. 
'''

def inverse_cdf_exp(prob, avg):
    '''
        Computes and returns the cumulative distribution function 
        of an exponential law, given the average edge delay and a 
        the probablity constraint
    '''
    return - avg * np.log(1 - prob)

def prob_delay_smaller(dt, avg_delay):
    '''
        Returns the probability that the delay is smaller
        than the average delay, assuming that the average delay
        follows an exponential law
    '''
    # X ~ Exp(avg_delay) return P(X < dt)
    assert(dt >= 0)  
    if avg_delay == 0:
        return 1
    return 1 - np.exp(( - 1 / float(avg_delay)) * dt)

def trip_probability(trip, arrival_time):
    '''
        Given a trip and the desired arrival time, returns the 
        probability of success of that trip
    '''
    # TODO: revoir s'il est valide de commencer par un walking edge
    probability = 1    
    time_sec = get_seconds(arrival_time)
    next_trip_id = "walking"
    
    for edge in list(trip.values())[::-1]:    
        if edge["route_id"] == "walking":
            time_sec -= edge["travel_time"] + 120
        else:
            arrival = get_seconds(edge["dst_arrival"])
            if next_trip_id != edge["route_id"]:
                if next_trip_id == "walking":
                    probability *= prob_delay_smaller(time_sec - arrival , edge["delay"])
                else :
                    probability *= prob_delay_smaller(time_sec - arrival - 120, edge["delay"])
            time_sec = get_seconds(edge["src_departure"])
        next_trip_id = edge["route_id"]
    return probability