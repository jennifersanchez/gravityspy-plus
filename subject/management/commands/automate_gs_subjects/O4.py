#!/usr/bin/env python
# coding: utf-8

from gwpy.table import EventTable
from gwpy.time import tconvert
import pandas as pd
import os 

start = tconvert('June 1 2023')
end = tconvert('June 2 2023')
detector = 'L1'
subject_set_id = 118217 

#-- Fetch data from Gravity Spy database
event_table = EventTable.fetch('gravityspy','glitches_v2d0',
                               selection=[f'ml_label=Scattered_Light','ml_confidence>.9',
                                          f'{start}<event_time<{end}', f'ifo={detector}','model_name=O4_v1'],
                               user='mla', passwd='gl1tch35Rb4d!')

#-- Select relavent columns
selected_columns = ['event_time', 'start_time', 'duration', 'Scattered_Light', 'model_name', 'ifo', 'ml_confidence']
events_df = event_table.to_pandas()
events_df = events_df[selected_columns]
events_df['end_time'] = events_df['start_time'] + events_df['duration'] #create our own end_time column
events_df.sort_values(by='event_time', inplace=True) #sort in chronological order

def format_float(value):
    return f'{value:.5f}'
pd.options.display.float_format = format_float

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(events_df)

#-- Loop through all start_times
for index, row in events_df.iterrows():
    start_time = row['start_time']
    end_time = row['end_time']
    ifo = row['ifo'] 
    print(f"(start, end) = ({start_time}, {end_time})")
    os.system(f"../../../.././manage.py make_gspy_subject --ifo {ifo} --subject_set_id {subject_set_id} --start-time {start_time} --end-time {end_time}")




