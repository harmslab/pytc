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
        
        return self._A_total[1:]/self._P_total[1:]

class SingleSite(ITCModel):
    """
    Binding at a single site. 
    """
    
    def __init__(self,
                 P_cell=100e-6,P_syringe=0.0,
                 A_cell=0.0,   A_syringe=1000e-6,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):
                 
        """
        P_cell: protein concentration in cell in M
        P_syringe: protein concentration in syringe in M
        A_cell: ligand A concentration cell in M
        A_syringe: ligand A concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL. 
        shot_start: first shot to use in fit
        """
        
        self._P_cell = P_cell
        self._P_syringe = P_syringe
        
        self._A_cell = A_cell
        self._A_syringe = A_syringe
            
        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)
        
        self._determine_titration_conc()

    
    def _determine_titration_conc(self):
        """
        Determine the total concentrations of P and A in tn the cell given 
        a set of titration shots and initial concentrations of P and A in
        the cell and syringe.
        """
        
        self._volume  = np.zeros(len(self._shot_volumes)+1)
        self._P_total = np.zeros(len(self._shot_volumes)+1)
        self._A_total = np.zeros(len(self._shot_volumes)+1)
        
        self._volume[0]  = self._cell_volume
        self._P_total[0] = self._P_cell
        self._A_total[0] = self._A_cell
        
        for i in range(len(self._shot_volumes)):
            
            self._volume[i+1] = self._volume[i] + self._shot_volumes[i]
            
            dilution = self._volume[i]/self._volume[i+1]
            added = self._shot_volumes[i]/self._volume[i+1]
            
            self._P_total[i+1] = self._P_total[i]*dilution + self._P_syringe*added
            self._A_total[i+1] = self._A_total[i]*dilution + self._A_syringe*added
            
    def dQ(self,KA,dHA,fx_comp=1.0):
        """
        Calculate the heats that would be observed across shots for a given set of enthalpies
        and binding constants for each reaction.
        """
        
        # ----- Determine mole fractions -----
        P = self._P_total*fx_comp
        b = P + self._A_total + 1/KA
        PA = (b - np.sqrt((b)**2 - 4*P*self._A_total))/2
    
        self._x_pa = PA/P
        self._x_p = 1 - self._x_pa
        
        # ---- Relate mole fractions to heat -----
        A = dHA*(self._x_pa[1:] - self._x_pa[:-1])
    
        to_return = self._cell_volume*(self._P_total[1:]*fx_comp)*A
        
        return to_return

class SingleSiteCompetitor(ITCModel):
    """
    Competition between two ligands for the same site.  Model taken from:

    Sigurskjold BW (2000) Analytical Biochemistry 277(2):260-266
    doi:10.1006/abio.1999.4402
    http://www.sciencedirect.com/science/article/pii/S0003269799944020
    """
 
    def __init__(self,            
                 P_cell=100e-6,P_syringe=0.0,
                 A_cell=0.0,   A_syringe=1000e-6,
                 B_cell=200e-6,B_syringe=0.0,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):
                 
        """
        P_cell: protein concentration in cell in M
        P_syringe: protein concentration in syringe in M
        A_cell: ligand A concentration cell in M
        A_syringe: ligand A concentration syringe in M
        B_cell: ligand B concentration cell in M
        B_syringe: ligand B concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL. 
        shot_start: first shot to use in fit
        """
        
        self._P_cell = P_cell
        self._P_syringe = P_syringe
         
        self._A_cell = A_cell
        self._A_syringe = A_syringe
        
        self._B_cell = B_cell
        self._B_syringe = B_syringe
        
        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)
        
        self._determine_titration_conc()
                 
                
    def _determine_titration_conc(self):
        """
        Determine the total concentrations of P, A, and B in the cell given 
        a set of titration shots and initial concentrations of P, A and B in
        the cell and syringe.
        """
        
        self._volume  = np.zeros(len(self._shot_volumes)+1)
        self._P_total = np.zeros(len(self._shot_volumes)+1)
        self._A_total = np.zeros(len(self._shot_volumes)+1)
        self._B_total = np.zeros(len(self._shot_volumes)+1)
        
        self._volume[0]  = self._cell_volume
        self._P_total[0] = self._P_cell
        self._A_total[0] = self._A_cell
        self._B_total[0] = self._B_cell
        
        for i in range(len(self._shot_volumes)):
            
            self._volume[i+1] = self._volume[i] + self._shot_volumes[i]
            
            dilution = self._volume[i]/self._volume[i+1]
            added = self._shot_volumes[i]/self._volume[i+1]
            
            self._P_total[i+1] = self._P_total[i]*dilution + self._P_syringe*added
            self._A_total[i+1] = self._A_total[i]*dilution + self._A_syringe*added
            self._B_total[i+1] = self._B_total[i]*dilution + self._B_syringe*added


    def dQ(self,KA,KB,dHA,dHB,fx_comp=1.0):
        """
        Calculate the heats that would be observed across shots for a given set of enthalpies
        and binding constants for each reaction.
        """
    
        # ----- Determine mole fractions -----
        P = self._P_total*fx_comp
    
        c_a = KA*P
        c_b = KB*P
        r_a = self._A_total/(P)
        r_b = self._B_total/(P)
        
        alpha = 1/c_a + 1/c_b + r_a + r_b - 1
        beta = (r_a - 1)/c_b + (r_b - 1)/c_a + 1/(c_a*c_b)
        gamma = -1/(c_a*c_b)
        theta = np.arccos((-2*alpha**3 + 9*alpha*beta - 27*gamma)/(2*np.sqrt((alpha**2 - 3*beta)**3)))
    
        self._x_p = (2*np.sqrt(alpha**2 - 3*beta) * np.cos(theta/3) - alpha)/3
        self._x_pa = r_a*self._x_p/(1/c_a + self._x_p)
        self._x_pb = r_b*self._x_p/(1/c_b + self._x_p)
    
        # ---- Relate mole fractions to heat -----
        A = dHA*(self._x_pa[1:] - self._x_pa[:-1])
        B = dHB*(self._x_pb[1:] - self._x_pb[:-1])
        
        to_return = self._cell_volume*P*(A + B)
        
        return to_return
        
