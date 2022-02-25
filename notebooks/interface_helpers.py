import pandas as pd
from math import ceil
import ipywidgets as widgets
import plotly.graph_objects as go
from IPython.display import display, clear_output, HTML

from planning import compute_n_trips 
from planning_helpers import is_transfer_edge
from time_helpers import time_plus_delta, time_minus_delta

'''
    This module contains functions that aid the drawing and layout 
    of the Voila interface.
'''

# We do not own this icons. They can be accessed on www.thenounproject.com
icon_start = 'https://static.thenounproject.com/png/59715-200.png'
icon_walk = 'https://static.thenounproject.com/png/3516-200.png'
icon_train = 'https://static.thenounproject.com/png/143378-200.png'
icon_tram = 'https://static.thenounproject.com/png/79183-200.png'
icon_bus = 'https://static.thenounproject.com/png/7190-200.png'
icon_funi = 'https://static.thenounproject.com/png/386490-200.png'
icon_boat = 'https://static.thenounproject.com/png/243-200.png'
icon_car = 'https://static.thenounproject.com/png/7189-200.png'

# Map transport types to icons
icons = {
    'InterRegio': icon_train, 
    'Intercity': icon_train, 
    'S-Bahn': icon_train, 
    'Bus': icon_bus, 
    'Tram': icon_tram, 
    'Standseilbahn': icon_funi,
    'RegioExpress': icon_train, 
    'Schiff': icon_boat, 
    'Eurocity': icon_train, 
    'Taxi': icon_car, 
    'Luftseilbahn': icon_funi, 
    'ICE': icon_train, 
    'TGV': icon_train, 
    'none': 'https://upload.wikimedia.org/wikipedia/commons/8/89/HD_transparent_picture.png'
}

def path_to_image_html(path):
    '''
        Embeds the image path in an html image tag
    '''
    return '<img src="'+ path + '" width="20" >'

def parse_stop(stop, stops_by_id, with_platform = True):
    '''
        Given a stop, returns its name, and the platform 
        associated if possible and if requested
    '''
    name = stops_by_id[stop]['name']
    if with_platform and ':' in stop:
        name+= ', Platform {}'.format(stop.split(':')[-1])
    return name


def trip_summary(G, trip, probability, stops_by_id):
    '''
        Given a generated trip (sequence of edges with their data), produces:
        - A nice long summary containing each step of the trip (with information)
        - A short 'title' summary for the trip
        - The number of changes and total walking distance for sorting
    '''
    n_transfers = 0
    walked_distance = 0
    summary = []
    previous_route = '' 
    
    for i, (edge, data) in enumerate(trip):
        # First line corresponds to the departure point
        if i == 0:
            if is_transfer_edge(G, edge):
                next_start = trip[i + 1][1]['src_departure']
                time = time_minus_delta(next_start, data['travel_time'])
            else:
                time = data['src_departure']
            summary.append([icon_start, '', time, parse_stop(edge[0], stops_by_id)])

        # If the edge is a transfer edge
        if is_transfer_edge(G, edge):
            n_transfers += 1
            walked_distance += data['distance']*1e3
            action = 'Walk ({:.0f} meters)'.format(data['distance']*1e3)
            time = "{}'".format(to_minutes(data['travel_time']))
            summary.append([icon_walk, '', time, action])
        
        else:
            # If there has been a change of trip (i.e. from train to bus)
            if previous_route != data['route_id']:
                icon = icons[data['route_desc']]
                time = data['src_departure']
                info = '{} {}'.format(data['route_desc'], data['route_short_name'])
                summary.append([icon, info, time, parse_stop(edge[0], stops_by_id)])
                previous_route = data['route_id']
            
            # If the trip is still the same
            else:
                summary.append([icons['none'], '', data['src_departure'], parse_stop(edge[0], stops_by_id, with_platform = False)])

            # If it is the last edge of this part of the trip
            if i < len(trip) - 1 and data['route_id'] != trip[i + 1][1]['route_id']:
                summary.append([icons['none'], '', data['dst_arrival'], parse_stop(edge[1], stops_by_id)])

    # Consider the last leg of the trip
    last_edge, last_data = trip[-1]
    if is_transfer_edge(G, last_edge):
        previous_end = trip[-2][1]['dst_arrival']
        final_time = time_plus_delta(previous_end, data['travel_time'])
    else:
        final_time = last_data['dst_arrival']
    summary.append([icon_start, '', final_time, parse_stop(last_edge[1], stops_by_id)])     
    
    # Generate short summary
    short_summary = '{}, {} - {}, {}. Probability {:.2}. '.format(summary[0][3], summary[0][2] , summary[-1][3], summary[-1][2], probability)
    short_summary += 'Change {} times. Walk {:.0f} meters in total.'.format(n_transfers, walked_distance)
    
    # Generate visited nodes list
    nodes = [edge[0][0] for edge in trip]
    nodes.append(trip[-1][0][1]) 
    
    return short_summary, summary, nodes, n_transfers, walked_distance

def to_minutes(seconds):
    '''
        Parses the number of seconds to minutes (rounded up)
    '''
    return ceil(seconds/60)

def create_trip_view(G, long_summary, nodes):
    '''
        Creates a horizontal view to display a trip summary and its map 
    '''
    trip_info = display_trip(long_summary)
    trip_map = display_map(G, nodes)
    return widgets.HBox([trip_info, trip_map])

def display_trip(long_summary):
    '''
        Given the long summary generated for the trip, 
        display it in an output widget
    '''
    op = widgets.Output()
    with op:
        display(HTML(pd.DataFrame(long_summary, columns=[' ', '', '', '']).to_html(index = False, 
                                                                                   escape=False,
                                                                                   formatters={' ': path_to_image_html})))
    return op

def display_map(G, nodes):
    '''
        Given the nodes of a trip, display them on a map
        in an output widget
    '''
    op = widgets.Output()
    with op:        
        names = [G.nodes[node]['name'] for node in nodes]
        fig = go.Figure(go.Scattermapbox(
            mode = "markers+lines",
            lon = [G.nodes[node]['lon'] for node in nodes],
            lat = [G.nodes[node]['lat'] for node in nodes],
            name = "",
            hovertemplate = names,
            hovertext = names,
            marker = {'size': 10, "color" : "red"}))
        
        fig.update_layout(
            margin ={'l':0,'t':0,'b':0,'r':0},
            width = 800, 
            height = 450,
            mapbox = {
                'style': "carto-positron",
                'center': {'lon': 8.540192, 'lat': 47.378177},
                'zoom': 11})
        fig.show()
    return op