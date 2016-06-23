__description__ = \
"""
models.py

Models subclassed from ITCModel used to model (and fit) ITC data.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import numpy as np

class ITCModel:
    """
    Base class from which all ITC models should be sub-classed.  Each model
    should have an __init__ method that populates the model and a dQ method
    that returns dQ as a function of a set of keyword parameters.
    """
    
    def __init__(self):
        pass
    
    def dQ(self):
        pass
    
    @property
    def mole_ratio(self):
        
        return self._T_conc[1:]/self._S_conc[1:]

class SingleSite(ITCModel):
    """
    Binding at a single site. 
    """
    
    def __init__(self,
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):
                 
        """
        S_cell: stationary concentration in cell in M
        S_syringe: stationary concentration in syringe in M
        T_cell: titrant concentration cell in M
        T_syringe: titrant concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL. 
        shot_start: first shot to use in fit
        """
        
        self._S_cell = S_cell
        self._S_syringe = S_syringe
        
        self._T_cell = T_cell
        self._T_syringe = T_syringe
            
        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)
        
        self._determine_titration_conc()

    
    def _determine_titration_conc(self):
        """
        Determine the concentrations of stationary and titrant species in the
        cell given a set of titration shots and initial concentrations of both 
        the stationary and titrant species. 
        """
        
        self._volume = np.zeros(len(self._shot_volumes)+1)
        self._S_conc = np.zeros(len(self._shot_volumes)+1)
        self._T_conc = np.zeros(len(self._shot_volumes)+1)
        
        self._volume[0] = self._cell_volume
        self._S_conc[0] = self._S_cell
        self._T_conc[0] = self._T_cell
        
        for i in range(len(self._shot_volumes)):
            
            self._volume[i+1] = self._volume[i] + self._shot_volumes[i]
            
            dilution = self._volume[i]/self._volume[i+1]
            added = self._shot_volumes[i]/self._volume[i+1]
            
            self._S_conc[i+1] = self._S_conc[i]*dilution + self._S_syringe*added
            self._T_conc[i+1] = self._T_conc[i]*dilution + self._T_syringe*added
            
    def dQ(self,K,dH,fx_competent=1.0,dilution_heat=0.0):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.
        """
        
        # ----- Determine mole fractions -----
        S_conc_corr = self._S_conc*fx_competent
        b = S_conc_corr + self._T_conc + 1/K
        ST = (b - np.sqrt((b)**2 - 4*S_conc_corr*self._T_conc))/2
    
        self._mol_fx_st = ST/S_conc_corr
        self._mol_fx_s = 1 - self._mol_fx_st
        
        # ---- Relate mole fractions to heat -----
        X = dH*(self._mol_fx_st[1:] - self._mol_fx_st[:-1])
    
        to_return = self._cell_volume*S_conc_corr[1:]*X + self._T_conc[1:]*dilution_heat
        
        return to_return

class SingleSiteCompetitor(ITCModel):
    """
    Competition between two ligands for the same site.  Model taken from:

    Sigurskjold BW (2000) Analytical Biochemistry 277(2):260-266
    doi:10.1006/abio.1999.4402
    http://www.sciencedirect.com/science/article/pii/S0003269799944020
    """
 
    def __init__(self,            
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 C_cell=200e-6,C_syringe=0.0,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):
                 
        """
        S_cell: stationary concentration in cell in M
        S_syringe: stationary concentration in syringe in M
        T_cell: titrant concentration cell in M
        T_syringe: titrant concentration syringe in M
        C_cell: competitor concentration cell in M
        C_syringe: competitor concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL. 
        shot_start: first shot to use in fit
        """
        
        self._S_cell = S_cell
        self._S_syringe = S_syringe
         
        self._T_cell = T_cell
        self._T_syringe = T_syringe
        
        self._C_cell = C_cell
        self._C_syringe = C_syringe
        
        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)
        
        self._determine_titration_conc()
                 
    def _determine_titration_conc(self):
        """
        Determine the concentrations of stationary, titrant and competitor 
        species in the cell given a set of titration shots and initial
        concentrations of species in the cell and syringe.
        """
        
        self._volume = np.zeros(len(self._shot_volumes)+1)
        self._S_conc = np.zeros(len(self._shot_volumes)+1)
        self._T_conc = np.zeros(len(self._shot_volumes)+1)
        self._C_conc = np.zeros(len(self._shot_volumes)+1)
        
        self._volume[0] = self._cell_volume
        self._S_conc[0] = self._S_cell
        self._T_conc[0] = self._T_cell
        self._C_conc[0] = self._C_cell
        
        for i in range(len(self._shot_volumes)):
            
            self._volume[i+1] = self._volume[i] + self._shot_volumes[i]
            
            dilution = self._volume[i]/self._volume[i+1]
            added = self._shot_volumes[i]/self._volume[i+1]
            
            self._S_conc[i+1] = self._S_conc[i]*dilution + self._S_syringe*added
            self._T_conc[i+1] = self._T_conc[i]*dilution + self._T_syringe*added
            self._C_conc[i+1] = self._C_conc[i]*dilution + self._C_syringe*added


    def dQ(self,K,Kcompetitor,dH,dHcompetitor,fx_competent=1.0,dilution_heat=0.0):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.
        """
    
        # ----- Determine mole fractions -----
        S_conc_corr = self._S_conc*fx_competent
    
        c_a = K*S_conc_corr
        c_b = Kcompetitor*S_conc_corr
        r_a = self._T_conc/S_conc_corr
        r_b = self._C_conc/S_conc_corr
        
        alpha = 1/c_a + 1/c_b + r_a + r_b - 1
        beta = (r_a - 1)/c_b + (r_b - 1)/c_a + 1/(c_a*c_b)
        gamma = -1/(c_a*c_b)
        theta = np.arccos((-2*alpha**3 + 9*alpha*beta - 27*gamma)/(2*np.sqrt((alpha**2 - 3*beta)**3)))
    
        self._mol_fx_s = (2*np.sqrt(alpha**2 - 3*beta) * np.cos(theta/3) - alpha)/3
        self._mol_fx_st = r_a*self._mol_fx_s/(1/c_a + self._mol_fx_s)
        self._mol_fx_sc = r_b*self._mol_fx_s/(1/c_b + self._mol_fx_s)
    
        # ---- Relate mole fractions to heat -----
        X = dH*(self._mol_fx_st[1:] - self._mol_fx_st[:-1])
        Y = dHcompetitor*(self._mol_fx_sc[1:] - self._mol_fx_sc[:-1])
        
        to_return = self._cell_volume*S_conc_corr[1:]*(X + Y) + self.S_conc[1:]*dilution_heat
        
        return to_return
        
