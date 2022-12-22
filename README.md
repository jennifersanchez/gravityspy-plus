# Gravity Spy Plus 2.0
# Prerequsities

## Login to LIGO Server with SSH
- Register for a LIGO account
- Follow the instruction in LIGO account settings to set up SSH key
```
ssh your_user_name@ssh.ligo.org        
```
- Enter the password and login
- Choose the No.3 LHO server normally
- Choose any machine

## Install Gravityspy-ligo-pipeline dependency package. 

```
git clone https://github.com/Gravity-Spy/gravityspy-ligo-pipeline.git
cd gravityspy-ligo-pipeline
conda create --name gravityspy-plus-py38 -c conda-forge gwpy python-ldas-tools-frameapi python-ldas-tools-framecpp pandas scikit-image python-lal python-ligo-lw python=3.8 --yes
conda activate gravityspy-plus-py38
python -m pip install .
```

See source code in https://github.com/Gravity-Spy/gravityspy-ligo-pipeline.

## Install Gravity Spy Plus
```
cd ..
git clone https://github.com/haorenzhi/gravityspy-plus.git
```

## Login to Zooniverse 

- Register for a Zooniverse account
- Add login credentials below into shell run control file (normally ~/.bashrc or ~/.zshrc)
```
#Panoptes Login
export PANOPTES_USERNAME=(your zooniverse username)
export PANOPTES_PASSWORD=(your zooniverse password)
```

# Make Gravity Spy subject and upload to Zooniverse
This pipeline generate omega scans from given event time on both main channel and auxiliary channels. Then it concatenate main channels and auxiliary channels PNGs vertically into a subject. Finally it upload all subjects to Zooniverse subject sets.

Under the hood, given an event time of Gravity Spy event at which an excess noise event occurred, the interferometer id, the round number of Hveto rounds and number of auxiliary channels, it returns a set of combination images for main channel and auxiliary channels with highest correlation in multiple durations and upload it to the zooniverse project set.

- ifo (str): What interferometer had this an excess noise event.
- manual_list_of_auxiliary_channel_names (list)[optional, None]: This will override any auxiliary channel list that might have been supplied by the auxiliary_channel_correlation_algorithm and force this to be the auxiliary channels that are associated with this Subject.
## Manually run make_gspy_subject on a pre-selected set of auxiliary channels
```
cd gravityspy-plus
./manage.py make_gspy_subject --event-time 1253940741.813 --ifo H1 --manual-list-of-auxiliary-channel-names H1:ASC-AS_A_RF45_Q_YAW_OUT_DQ H1:LSC-REFL_A_LF_OUT_DQ H1:ASC-AS_A_RF45_Q_PIT_OUT_DQ
```

## Use Hveto to select top N auxiliary channels within a period of event time with LLO
```
./manage.py make_gspy_subject --ifo L1 --start-time 1262304018 --end-time 1262390418
```

## Or with LHO
```
./manage.py make_gspy_subject --ifo H1 --start-time 1262790978 --end-time 1262822978
```
# Parse Classifications from Zooniverse
This pipeline parse classifications from Zooniverse that are annotated by volunteers. The classification is whether the glitch in auxiliary channel is related to glitch in main/h(t) channel. Then it will save each classification as an item in psql database table, which records the annotation and subject information, such as channel names and event time.

## Install Homebrew 
See instruction on https://docs.brew.sh/Installation

## Install Postgresql
```
​​brew install postgresql
```

## Add login credentials below into ~/.bashrc 
```
#Django Login
export GRAVITYSPYPLUS_DATABASE_NAME="gravityspyplus"
export GRAVITYSPYPLUS_DATABASE_USER="django_gravityspyplus_user"
export GRAVITYSPYPLUS_DATABASE_PASSWORD="(contact lab for password)"
export GRAVITYSPYPLUS_DATABASE_HOST="gravityspyplus.ciera.northwestern.edu"
export GRAVITYSPYPLUS_DATABASE_PORT="5432"
```

## Parse classifications from Zooniverse and save into Psql database
```
./manage.py parse_gspy_classifications --workflow-id=23089
```

## Login to psql database
```
psql -U django_gravityspyplus_user -d gravityspyplus -h gravityspyplus.ciera.northwestern.edu
```

## View parsed classifications table in psql database
```
\d
select * from classification_classfication;
```