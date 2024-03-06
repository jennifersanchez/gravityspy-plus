import pandas as pd
import datetime as dt
import os

#-- Set the path to the directory where the csv files are stored
path = "./detector_data"

#-- Create a list of the csv files in the directory
csv_files = ["L1_O3a.csv"]

#-- Auxiliary channel names
aux_chnls = [
    "L1:LSC-REFL_A_LF_OUT_DQ",
    "L1:ASC-REFL_B_RF9_Q_YAW_OUT_DQ",
    "L1:LSC-POP_A_LF_OUT_DQ"
]

#-- Zooniverse subject ID
subject_set_id = 118217

#-- Iterate over each csv file and extract the relevant data
data = []
for file in csv_files:
    df = pd.read_csv(os.path.join(path, file))
    df = df[df["ml_confidence"] >= 0.99] # filter for ml_confidence of 0.99 or greater
    df = df[df["ml_label"] == "Whistle"] # filter for ml_label "Whistle"
    df = df[df["event_time"] > 1238166018] # GPS time
    df = df[["ifo", "ml_label", "ml_confidence", "event_time"]] #extract relevant columns
    data.append(df)

#-- Concatenate the dataframes into a single dataframe
df = pd.concat(data)
df = df.sort_values(by="event_time") # sort the DataFrame by event_time in chronological order
df = df.drop_duplicates(subset=["event_time"]) # remove repeating event_time values
print(df)

#-- Length of event time colomn
event_time_length = len(df[["event_time"]])
print("event_time_length:",event_time_length) # allows to see how many subjects to expect

#-- Group the data by ifo and create subject sets for each ifo
for ifo, group in df.groupby("ifo"):
    event_times = group["event_time"].values
    for i in range(event_time_length):
        event_time = event_times[i]
        for aux_chnl in aux_chnls: # loops over each channel in aux_chnls
            os.system(f"../../../.././manage.py make_gspy_subject --event-time {event_time} --ifo {ifo} --subject_set_id {subject_set_id} --manual-list-of-auxiliary-channel-names {aux_chnl}")
            
