'''
Created on Aug 14, 2024

@author: kjsmi
'''
import datetime, numpy

def datetime_time_remaining(pr_timedelta_list, pr_count, pr_total, timedelta_span=0, method="SIMPLE"):
    
    # If timedelta window is zero, set it to the length of the list.
    if timedelta_span == 0:
        
        timedelta_span = len(pr_timedelta_list)
        
    # Clip timedelta list to length of window, and convert to seconds.
    clip_pr_timedelta_list = [float(i.total_seconds()) for i in pr_timedelta_list[0:timedelta_span]]
    
    # Get the number of iterations remaining.
    pr_remaining = pr_total - pr_count
    
    if method == "SIMPLE":
        
        # Get the average amount of time elapsed per iteration within the timedelta window.
        pr_avg_time = numpy.average(clip_pr_timedelta_list)
        
    elif method == "WEIGHTED":
        
        # Weight more recent iterations higher.
        pr_avg_time = numpy.average(clip_pr_timedelta_list, weights=range(0,len(clip_pr_timedelta_list)))
    
    else:
        
        raise Exception('Method must be "SIMPLE" or "WEIGHTED"')
    
    # Multiply average time by remaining runs to estimate the amount of time remaining.
    est_runtime_delta = datetime.timedelta(seconds=(pr_remaining * pr_avg_time))
    
    # 
    return est_runtime_delta

# Prints 'percent complete' messages to console at specified intervals.
# Intervals are in percentage points: '5' will produce messages at each 5% interval.
def prcnt_complete(pr_timedelta_list, pr_total, pr_time, prcnt_inc=5, leading_spaces=0, leading_text="", timedelta_span=0, method="SIMPLE"):
    
    pr_count = len(pr_timedelta_list)
    
    leading_spaces_str = "".join([" " for i in range(0, leading_spaces)]) #@UnusedVariable
    
    # Create list of breakpoints.
    breakpoints = [(pr_total / (100/prcnt_inc)) * i  for i in range(1, int((100/prcnt_inc))+1)]
    
    # Create dictionary to hold breakpoints.
    breakpoint_dict = {}
    
    # Round values in breakpoint list to integers, so that they correspond to pr_count values.
    for i, j in enumerate(breakpoints):
    
        breakpoint_dict[int(j) + bool(j%1)] = ((i+1)*prcnt_inc)
    
    # Estimate time remaining.
    est_string = str(datetime_time_remaining(pr_timedelta_list, pr_count, pr_total, timedelta_span, method)).split(".")[0]
    
    # If pr_count is in the breakpoint dict, print message to console.
    if pr_count in breakpoint_dict.keys():
        
        print("{}{} {}% complete, approx. {} left...".format(leading_spaces_str, leading_text, breakpoint_dict[pr_count], est_string))

