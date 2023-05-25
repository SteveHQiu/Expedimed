#%%
import sys, argparse
from dataclasses import dataclass
from random import shuffle
from statistics import mean, stdev

from pandas import DataFrame

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--arg1", required=False)
parser.add_argument("-b", "--arg2", required=False)

args = parser.parse_args()
if len(sys.argv) > 1:
    print(args.arg1, args.arg2)
    
else:
    pass


#%%
TOT_PT = 200

@dataclass
class Patient:
    """
    Generic patient class
    
    ctas_lvl: CTAS level of patient
    ruoc: required units of care needed (i.e., number of hours standardized to generic ED provider)
    wait_time: wait time experienced in hours 
    """
    
    ctas_lvl: int
    ruoc: float # Required units of care, Also serves as progress counter
    wait_time: float = 0
    
@dataclass
class HCProvider:
    """
    Generic Health care provider 
    
    
    work_per_hr: speed of work (not implemented yet)
    min_ctas: most acute CTAS level that they can see
    num_pt: number of patients assigned to provider
    assigned_pt: reference to instance of assigned patient 
    """
    
    
    work_per_hr: float = 1
    min_ctas: int = 1
    num_pt: int = 0
    assigned_pt: Patient = None



class Hospital:
    def __init__(self,
                 pt_list: list[Patient],
                 hcp_list: list[HCProvider],
                 interval = 0.25) -> None:
        self.patients = pt_list
        self.providers = hcp_list
        self.interval: float = interval # Interval between patient arrival In hours, also serves as the clock speed of simulation
        self.waitingroom: list[Patient] = []
        self.disch_pt: list[Patient] = []
        
    def runSim(self):
        while len(self.disch_pt) < TOT_PT: # When both are non-empty
            if self.patients: # Only pop if patients are still in queue
                pt = self.patients.pop(0)
                self.waitingroom.append(pt)
            
            self.waitingroom.sort(key=lambda item: item.ctas_lvl) # Sort by CTAS
            
            # print(F"Beginning of interval. Pt left: {len(self.patients) - len(self.disch_pt)}")
            # print(self.waitingroom)
            
            hcps_avail = [hcp for hcp in self.providers if hcp.num_pt == 0] # Find all available HCPs
            for hcp in hcps_avail:
                potential_pt = [pt for pt in self.waitingroom if pt.ctas_lvl >= hcp.min_ctas]
                if potential_pt: # If list not empty
                    pt_ind = self.waitingroom.index(potential_pt[0]) # Get WR pt that is the most suitable
                    curr_pt = self.waitingroom.pop(pt_ind) # Take patient from waiting room
                    hcp.num_pt = 1 # Occupy HCP 
                    hcp.assigned_pt = curr_pt # Assign pt 
            
            # Work cycle begins 
            for wr_pt in self.waitingroom:
                wr_pt.wait_time += self.interval # Add interval time to pt
            
            hcps_occ = [hcp for hcp in self.providers if hcp.num_pt == 1] # Find occupied HCPs
            for hcp in hcps_occ: # Complete cycle with each HCP
                hcp.assigned_pt.ruoc -= self.interval # Subtract interval from required units of care
                if hcp.assigned_pt.ruoc <= 0:
                    self.disch_pt.append(hcp.assigned_pt) # Discharge pt
                    hcp.assigned_pt = None # Unassign pt
                    hcp.num_pt = 0 # Free up HCP
            # print(F"End of interval")
            # print(self.waitingroom)
        assert not self.patients and not self.waitingroom # Assume both are empty 
        print(F"Discharged patients: {len(self.disch_pt)}")
        return self.disch_pt
            
if 0:            
    pt_groups = [
                [Patient(ctas_lvl=1, ruoc=5) for i in range(int(TOT_PT*0.02))],
                [Patient(ctas_lvl=2, ruoc=3) for i in range(int(TOT_PT*0.08))],
                [Patient(ctas_lvl=3, ruoc=3) for i in range(int(TOT_PT*0.50))],
                [Patient(ctas_lvl=4, ruoc=1) for i in range(int(TOT_PT*0.30))],
                [Patient(ctas_lvl=5, ruoc=1) for i in range(int(TOT_PT*0.10))],
                ]

    pt_groups = [
                [Patient(ctas_lvl=1, ruoc=4) for i in range(int(TOT_PT*0.02))],
                [Patient(ctas_lvl=2, ruoc=1.5) for i in range(int(TOT_PT*0.08))],
                [Patient(ctas_lvl=3, ruoc=1.5) for i in range(int(TOT_PT*0.50))],
                [Patient(ctas_lvl=4, ruoc=0.75) for i in range(int(TOT_PT*0.30))],
                [Patient(ctas_lvl=5, ruoc=0.75) for i in range(int(TOT_PT*0.10))],
                ]

waittimes = []
for i in range(50):
    pt_groups = [
                [Patient(ctas_lvl=1, ruoc=1.5) for i in range(int(TOT_PT*0.02))],
                [Patient(ctas_lvl=2, ruoc=1) for i in range(int(TOT_PT*0.08))],
                [Patient(ctas_lvl=3, ruoc=1) for i in range(int(TOT_PT*0.50))],
                [Patient(ctas_lvl=4, ruoc=0.5) for i in range(int(TOT_PT*0.30))],
                [Patient(ctas_lvl=5, ruoc=0.5) for i in range(int(TOT_PT*0.10))],
                ]

    pt_list = [pt for sublist in pt_groups for pt in sublist]
    shuffle(pt_list) # Shuffle patients

    hcp_list = [HCProvider() for i in range(2)] + [HCProvider(min_ctas=3) for i in range(3)]

    hospital1 = Hospital(pt_list=pt_list, hcp_list=hcp_list)
    hospital1.runSim()
    mean_waittime = mean([pt.wait_time for pt in hospital1.disch_pt])
    waittimes.append(mean_waittime)
    print(F"Mean wait time in hours: {mean_waittime}")
    
print(F"Overall Monte Carlo wait time: {mean(waittimes)} +/- {stdev(waittimes)}")


#%%


#%%
### Debug watch list
# [hcp.assigned_pt for hcp in self.providers]
# self.providers[0].assigned_pt.ruoc
# self.providers[1].assigned_pt.ruoc
# self.providers[2].assigned_pt.ruoc
# self.providers[3].assigned_pt.ruoc
# len(self.disch_pt)
# %%
