from datetime import datetime, timedelta
import pandas as pd

FMT = '%H:%M:%S'

'''
    This module contains methods to handle timestamps and time strings
'''

def get_seconds(str_time):
    '''
        Converts a timestamp to a number of seconds
    '''
    return int(pd.to_datetime(str_time).asm8)/10**9

def compute_delta_time(t1, t2):
    '''
        Computes difference between two string times in seconds
    '''
    return (datetime.strptime(t2, FMT) - datetime.strptime(t1, FMT)).total_seconds()

def time_minus_delta(time, delta):
    '''
        Returns the given string time, minus the given delta
    '''
    new_time = datetime.strptime(time, FMT) - timedelta(seconds=delta)
    return new_time.strftime(FMT)

def time_plus_delta(time, delta):
    '''
        Returns the given string time, plus the given delta
    '''
    new_time = datetime.strptime(time, FMT) + timedelta(seconds=delta)
    return new_time.strftime(FMT)
