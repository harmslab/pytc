__description__ = \
"""
assembly_auto_inhibition.py

Model of ligand-mediated protein assembly and autoinhibition of the assembly, 
related to the prozone effect.
"""
__author__ = "Martin L. Rennie"
__date__ = "2018-02-22"

import inspect
import numpy as np
from scipy.optimize import root as solve_mass_balance
from scipy.optimize import OptimizeResult

from pytc.indiv_models.base import ITCModel

class AssemblyAutoInhibition(ITCModel):
    """
    Model of ligand-mediated protein assembly and autoinhibition of the assembly, 
    related to the prozone effect.
    """

    def param_definition(Klig1=1e7,Klig2=1e5,Kolig=1e6,dHlig1=-30.,
                            dHlig2=-30.,dHolig=-210.,n_lig=5.,n_prot=4.,fx_prot_competent=1.0,fx_lig_competent=1.0): 
        """
        Klig1: association constant for binding of the first ligand to the protein (M)
        Klig2: association constant for binding of the second ligand to the protein (M)
        Kolig: "unit normalised" association constant for formation of the protein oligomer (M)
        dHlig1: enthalpy for binding of the first ligand to the protein 
        dHlig2: enthalpy for binding of the second ligand to the protein 
        dHolig: enthalpy for formation of the protein oligomer
        n_lig: stoichiometry of ligands in the protein oligomer
        n_prot: stoichiometry of proteins in the protein oligomer
        """
        
        pass
    
    def __init__(self,
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 is_reverse=False,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):

        """
        S_cell: stationary concentration in cell in M
        S_syringe: stationary concentration in syringe in M
        T_cell: titrant concentration cell in M
        T_syringe: titrant concentration syringe in M
        is_reverse: is the experiment a reverse titration setup, boolean
                 (this will trigger a swapping of the 'titrant' and 'stationary' for the experiment)
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL.
        """
                         
        super().__init__(S_cell,S_syringe,T_cell,T_syringe,cell_volume,shot_volumes)
        
        self._is_reverse = is_reverse
        
        # set initial bounds of certain parameters
        self._params["n_lig"]._bounds = (0.1,100.)
        self._params["n_prot"]._bounds = (0.1,100.)
        
        

    @property
    def dQ(self):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.  
        """

        # if reverse titration setup swap the corrections for competent stationary and competent titrant
        if(self._is_reverse):
            S_conc_corr = self._S_conc*self.param_values["fx_lig_competent"]
            T_conc_corr = self._T_conc*self.param_values["fx_prot_competent"]
        else:
            S_conc_corr = self._S_conc*self.param_values["fx_prot_competent"]
            T_conc_corr = self._T_conc*self.param_values["fx_lig_competent"]
        
        num_shots = len(S_conc_corr)
        
        heat_array = np.zeros((num_shots-1),dtype=float)
        prot_free = np.zeros((num_shots),dtype=float)
        lig_free = np.zeros((num_shots),dtype=float)

        # number of moles of titrant injected
        n_mol_inj = (T_conc_corr[1:] - T_conc_corr[:-1]) * self._cell_volume*1e-6
        
        # call function to compute the free species by numerical solution of the mass balance equations        
        (prot_free, lig_free) = solve_mb(self._is_reverse, num_shots, 
            self.param_values["Klig1"], self.param_values["Klig2"], self.param_values["Kolig"], 
            self.param_values["n_lig"], self.param_values["n_prot"], S_conc_corr, 
            T_conc_corr)
        
        # compute the heat of each injection
        heat_array = self._cell_volume*1e-6 * \
                (self.param_values["dHlig1"] * (self.param_values["Klig1"] * prot_free[1:] * lig_free[1:] -   \
                            self.param_values["Klig1"] * prot_free[:-1] * lig_free[:-1] * (1. - self._shot_volumes/self._cell_volume)) +   \
                (self.param_values["dHlig1"] + self.param_values["dHlig2"]) * (self.param_values["Klig1"] * self.param_values["Klig2"] * prot_free[1:] * lig_free[1:]**2 -   \
                            self.param_values["Klig1"] * self.param_values["Klig2"] * prot_free[:-1] * lig_free[:-1]**2 * (1. - self._shot_volumes/self._cell_volume)) +   \
                self.param_values["dHolig"] * (self.param_values["Kolig"]**(self.param_values["n_lig"] + self.param_values["n_prot"] - 1) * prot_free[1:]**self.param_values["n_prot"] * lig_free[1:]**self.param_values["n_lig"] -   \
                            self.param_values["Kolig"]**(self.param_values["n_lig"] + self.param_values["n_prot"] - 1) * prot_free[:-1]**self.param_values["n_prot"] * lig_free[:-1]**self.param_values["n_lig"] * (1. - self._shot_volumes/self._cell_volume)))
        
        # normalise the heat by the moles of titrant injected and correct for the heats of dilution        
        return heat_array/n_mol_inj + self.dilution_heats


def solve_mb(reverse, N_points, K1, K2, K3, n_oligL, n_oligP, Pt, Lt):
    """
    Solve mass balance equations for the Assembly AutoInhibition model.
    
    Returns a tuple of arrays for the free protein and free ligand concentrations.
    """
                
    p = np.zeros(N_points)
    l = np.zeros(N_points)
    
    # if reverse titration setup swap titrant and stationary    
    if(reverse):
        tmp = Pt
        Pt = Lt
        Lt = tmp
    
    p[0] = Pt[0]
    l[0] = Lt[0]
    
    for i in range(N_points-1):
        
        # mass balance equations
        def equations(x):
            p,l = x
            return [p + K1*p*l + K1*K2*p*l**2. + n_oligP*(K3**(n_oligL+n_oligP-1))*p**n_oligP*l**n_oligL - Pt[i+1], \
                    l + K1*p*l + 2.*K1*K2*p*l**2. + n_oligL*(K3**(n_oligL+n_oligP-1))*p**n_oligP*l**n_oligL - Lt[i+1]]
    
        sol = OptimizeResult(success=False)
        ptmp = -1
        ltmp = -1
        j = 1.
        # try to solve using previous free concentrations as initial guesses. Maximum number of iterations is large as gradient may be very shallow
        sol = solve_mass_balance(equations,(p[i],l[i]),method='lm',options={'maxiter':2000})
        ptmp,ltmp = sol.x
        # if no solution try to solve with different initial conditions and solver options
        if(not sol.success):
            sol = solve_mass_balance(equations,(Pt[i],Lt[i]),method='lm',options={'factor':1,'maxiter':8000})
            ptmp,ltmp = sol.x
            # if still no solution...bugger
            if(not sol.success):
                print("ERROR: Could not find solution...")
    
        l[i+1] = ltmp
        p[i+1] = ptmp
        
    return (p,l)
