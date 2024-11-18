import os
import numpy as np
import mne
import json
import helper
from mne_bids.write import _events_tsv
import shutil
import matplotlib.pyplot as plt
import re

#workaround for -- _tkinter.TclError: invalid command name ".!canvas"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('config.json') as config_json:
    config = helper.convert_parameters_to_None(json.load(config_json))

data_file = config['mne']
raw = mne.io.read_raw_fif(data_file,verbose=False)

events = mne.find_events(raw,stim_channel=config['stim_channel'],
                            output=config['output'],
                            consecutive=config['consecutive'],
                            min_duration=config['min_duration'],
                            shortest_event=config['shortest_event'],
                            mask=config['mask'],
                            uint_cast=config['uint_cast'],
                            mask_type=config['mask_type'],
                            initial_event=config['initial_event'])
report = mne.Report(title='Events')

sfreq = raw.info['sfreq']

events = mne.pick_events(events,include=config['include'],exclude=config['exclude'])

# take all events to combine (syntax = 1,2, 3, 4 -> 100)
if config['event_id_combine']:
    event_id_combine = config['event_id_combine'].split('\n')
    event_id_combine = [re.split(' *, *| *: *',ids) for ids in event_id_combine]
    event_id_combine = [[int(id) for id in event] for event in event_id_combine]
    # take last name as 
    event_to = [id.pop() for id in event_id_combine]

    for ids, to in zip(event_id_combine, event_to):
        events = mne.merge_events(events,ids=ids,new_id=to)

#NEEDS TO HAVE A FORK IN CASE EVENT_ID_CONDITION IS EMPTY
event_id_condition= config['event_id_condition'].replace('\n','')
event_id = eval('{' + event_id_condition + '}')

id_list = list(event_id.values())

# keep only those events named in event_id_condition that are present in raw
id_list = [id for id in id_list if id in events[:,2]]
event_id = {key:val for key, val in event_id.items() if val in id_list}

events = mne.pick_events(events, include=id_list)

_events_tsv(events, np.repeat(0.,events.shape[0]), raw, 'out_dir/events.tsv', trial_type=None, overwrite=True)


report.add_events(events=events, title='Events', sfreq=sfreq, event_id = event_id)

# == SAVE REPORT ==
report.save('out_dir_report/report.html', overwrite=True)
