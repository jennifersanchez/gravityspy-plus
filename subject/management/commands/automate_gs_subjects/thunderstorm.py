import os
from gwpy.segments import DataQualityFlag
from gwpy.time import tconvert
import pandas as pd

# Define the auxiliary channel names
aux_chnls = [
    "L1:PEM-EX_MIC_VEA_PLUSX_DQ",
    "L1:PEM-CS_MIC_LVEA_INPUTOPTICS_DQ",
    "L1:PEM-EY_MIC_VEA_PLUSY_DQ"
]
start = tconvert('April 1 2019')  # start of O3
end = tconvert('March 27 2020')  # end of O3
flagname = 'L1:DCH-THUNDER_MIC_BP_GT_300'  # from pdf but replace white space for underscores
flag = DataQualityFlag.query_dqsegdb(flagname, start, end)
intervals = [(interval[0], interval[1]) for interval in flag.active]

# Sort the intervals in chronological order
sorted_intervals = sorted(intervals, key=lambda x: x[0])
#print('sorted_intervals:',sorted_intervals)

# Loop through each sorted interval
for interval in sorted_intervals:
    ifo = 'L1'  # Set the IFO value, assuming all intervals are for the same IFO
    start_time, end_time = interval
    event_time = (start_time + end_time) / 2.0
    print("interval",interval)
    print(f"Event Time: {event_time:.3f}")

    for aux_chnl in aux_chnls:
        print("aux_chnl:",aux_chnl)
        os.system(f"../../../.././manage.py make_gspy_subject --event-time {event_time:.3f} --ifo {ifo} --subject_set_id {subject_set_id}  --manual-list-of-auxiliary-channel-names {aux_chnl}")
        
