# gravityspy-plus
# Make Gravity Spy subject and upload to Zooniverse

## Prerequsities
Install Gravityspy-ligo-pipeline dependency package. 

```
git clone https://github.com/Gravity-Spy/gravityspy-ligo-pipeline.git
cd gravityspy-ligo-pipeline
conda create --name gravityspy-plus-py38 -c conda-forge gwpy python-ldas-tools-frameapi python-ldas-tools-framecpp pandas scikit-image python-lal python-ligo-lw python=3.8 --yes
conda activate gravityspy-plus-py38
python -m pip install .
```

See source code in https://github.com/Gravity-Spy/gravityspy-ligo-pipeline

## Manually run make_gspy_subject on a pre-selected set of auxiallary channels
```
./manage.py make_gspy_subject --event-time 1253940741.813 --ifo H1 --manual-list-of-auxiliary-channel-names H1:ASC-AS_A_RF45_Q_YAW_OUT_DQ H1:LSC-REFL_A_LF_OUT_DQ H1:ASC-AS_A_RF45_Q_PIT_OUT_DQ
```

## On LLO using HVeto
```
./manage.py make_gspy_subject --ifo L1 --start-time 1262304018 --end-time 1262390418
```

## On LHO using HVeto
```
./manage.py make_gspy_subject --ifo H1 --start-time 1262790978 --end-time 1262822978
```
