import os
from gwpy.segments import DataQualityFlag
from gwpy.time import tconvert
import pandas as pd

# Define the auxiliary channel names
aux_chnls = [
    "H1:ASC-X_TR_A_NSUM_OUT_DQ",
    "H1:ASC-X_TR_A_PIT_OUT_DQ",
    "H1:ASC-Y_TR_A_NSUM_OUT_DQ"
]

start = tconvert('April 1 2019')  # start of O3
end = tconvert('March 27 2020')  # end of O3
flagname = 'L1:DCH-THUNDER_MIC_BP_GT_300'  # from pdf but replace white space for underscores
flag = DataQualityFlag.query_dqsegdb(flagname, start, end)
intervals = [(interval[0], interval[1]) for interval in flag.active]

# Sort the intervals in chronological order
sorted_intervals = sorted(intervals, key=lambda x: x[0])

# Convert the intervals to a DataFrame for easier grouping by IFO
df = pd.DataFrame(sorted_intervals, columns=['start', 'end'])
df['ifo'] = 'H1'  # Set the IFO value, assuming all intervals are for the same IFO

# Group the DataFrame by IFO
grouped = df.groupby('ifo')

# Loop through each IFO and its corresponding group of intervals
for ifo, group in grouped:
    event_times = (group["start"].values + group["end"].values) / 2.0
    
    for event_time in event_times:
        for aux_chnl in aux_chnls:
            command = f"../../../.././manage.py make_gspy_subject --event-time {event_time:.3f} --ifo {ifo} --manual-list-of-auxiliary-channel-names {aux_chnl}"
            os.system(command)
