from LDMX.Framework import ldmxcfg
p = ldmxcfg.Process('test')

p.maxTriesPerEvent = 10000

from LDMX.Biasing import target
from LDMX.SimCore import generators

det = 'ldmx-det-v15-8gev'
mySim = target.dark_brem(
    #A' mass in MeV - set in init.sh to same value in GeV
    1000.0,
    # library path is uniquely determined by arguments given to `dbgen run` in init.sh
    #   easiest way to find this path out is by running `. init.sh` locally to see what
    #   is produced
    'electron_tungsten_MaxE_8.0_MinE_4.0_RelEStep_0.1_UndecayedAP_mA_0.01_run_1',
    det,
    generators.single_8gev_e_upstream_tagger()
)

p.sequence = [ mySim ]

##################################################################
# Below should be the same for all sim scenarios

import os
import sys

p.maxEvents = int(os.environ['LDMX_NUM_EVENTS'])
p.run = int(os.environ['LDMX_RUN_NUMBER'])

p.histogramFile = f'hist.root'
p.outputFiles = [f'events.root']

# Load the full tracking sequance
from LDMX.Tracking import full_tracking_sequence

# Load the ECAL modules
import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions
import LDMX.Ecal.digi as ecal_digi
import LDMX.Ecal.vetos as ecal_vetos

# Load the HCAL modules
import LDMX.Hcal.HcalGeometry
import LDMX.Hcal.hcal_hardcoded_conditions
import LDMX.Hcal.digi as hcal_digi
hcal_digi_reco = hcal_digi.HcalSimpleDigiAndRecProducer()

# Load the TS modules
from LDMX.TrigScint.trigScint import TrigScintDigiProducer
from LDMX.TrigScint.trigScint import TrigScintClusterProducer
from LDMX.TrigScint.trigScint import trigScintTrack
ts_digis = [
        TrigScintDigiProducer.pad1(),
        TrigScintDigiProducer.pad2(),
        TrigScintDigiProducer.pad3(),
        ]

ts_clusters = [
        TrigScintClusterProducer.pad1(),
        TrigScintClusterProducer.pad2(),
        TrigScintClusterProducer.pad3(),
        ]

# Load electron counting and trigger
from LDMX.Recon.electronCounter import ElectronCounter
from LDMX.Recon.simpleTrigger import TriggerProcessor
from LDMX.Recon.fiducialFlag import RecoilFiducialityProcessor

count = ElectronCounter(1,'ElectronCounter')
count.input_pass_name = ''

# Load the DQM modules
from LDMX.DQM import dqm

# Load ecal veto and use tracking in it
ecalVeto = ecal_vetos.EcalVetoProcessor()
ecalMip = ecal_vetos.EcalMipProcessor()
ecal_veto_pnet = ecal_vetos.EcalPnetVetoProcessor()

# Load HCAL veto
import LDMX.Hcal.hcal as hcal
hcal_veto = hcal.HcalVetoProcessor()

# The Tracking modules produce a lot of helpful messages
# but (at the debug level) is too much for commiting the gold log
# into the git working tree on GitHub
p.logger.termLevel = 1 

# Add full tracking for both tagger and recoil trackers: digi, seeds, CFK, ambiguity resolution, GSF, DQM
p.sequence.extend(full_tracking_sequence.sequence)
p.sequence.extend(full_tracking_sequence.dqm_sequence)

p.sequence.extend([
        ecal_digi.EcalDigiProducer(),
        ecal_digi.EcalRecProducer(), 
        ecalVeto,
        ecalMip,
        ecal_veto_pnet,
        hcal_digi_reco,
        hcal_veto,
        *ts_digis,
        *ts_clusters,
        trigScintTrack, 
        RecoilFiducialityProcessor("RecoilFiducialityProcessor"),
        count, TriggerProcessor('trigger', 8000.),
        dqm.DarkBremInteraction(),
        ])

p.sequence.extend(dqm.all_dqm)
