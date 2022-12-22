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
# Generate Dataset from Hveto for classification machine learning
This workflow generate dataset from given period of event time. It uses result of Hveto algorithem to select and rank top N auxiliary channels, by correlation significance to the main channel. In each round, the topN auxiliary channels are the same between different glitch folders with different gravityspy_id as the folder names. The time ranges are [0.5, 1.0, 2.0, 4.0].

```
./manage.py make_gspy_subject --ifo L1 --start-time 1262304018 --end-time 1262390418
```

- It will generate omega scan in folder ./plots/
- The auxiliary channel format is /plots/mm-dd-yyyy/round/gravityspy_id/topN/
- The main channel format is /plots/mm-dd-yyyy/round/gravityspy_id/
