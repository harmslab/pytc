
from . import fit_param

class GlobalConnector:
    """
    Describe simple, individual fitting parameters as an arbitrary collection 
    of other, underlying parameters.
    """

    def __init__(self,name):
        """
        """
    
        self.name = name
        self._param_names = [name]
        self._initialize()

    def _initialize(self):
    
        self._param_dict = {}
        for p in self._param_names:
            
            if len(self._param_names) == 1:
                key = p
            else:
                key = "{}_{}".format(self.name,p)

            self._param_dict[key] = fit_param.FitParameter(p)
            self.__dict__[p] = self._param_dict[key].value

    @property
    def params(self):

        return self._param_dict

    def update_values(self,param_dict):
        """
        Update the value of a parameter.
        """
        for p in param_dict.keys():

            if len(self._param_names) == 1:
                key = p
            else:
                key = "{}_{}".format(self.name,p)

            self._param_dict[key].value = param_dict[p]
            self.__dict__[p] = self._param_dict[key].value

class Generic(GlobalConnector):

    pass    


class NumProtons(GlobalConnector):
    
    def __init__(self,name):
        """
        Initialize the NumProtons class, defining the fitting parameters.
        """
        
        self.name = name
        self._param_names = ["num_H","dH_intrinsic"] 

        self._initialize()
           
    def dH(self,experiment):
        """
        Return the change in enthalpy upon binding of buffers with different
        ionization enthalpies. 
        """

        dHion = experiment.ionization_enthalpy

        return self.dH_intrinsic + self.num_H*dHion

class VantHoff(GlobalConnector):
    """
    Fit a collection of ITC experiments at different temperatures to extract the 
    van't Hoff enthalpy.  Assumes constant enthalpy over the temperature range.
    """
    
    def __init__(self,name,reference_temp=298.15,R=1.9872036):
        """
        Initialize the VantHoff class, defining the fitting parameters.
        """
    
        self.reference_temp = reference_temp
        self.R = R

        self._param_names = ["dH","K_ref"]

        self._initialize()

    def K(self,experiment):
        """
        Return the temperature-dependent binding constant, calculated using the
        a fixed enthalpy and shifting K. 
        """

        T = experiment.temperature
        T_ref = self.reference_temp

        a = -(self.dH/self.R)*(1/T - 1/T_ref)

        return self.K_ref*np.exp(a)
       
    def dH(self,experiment):
        """
        Return the van't Hoff enthalpy.
        """

        return self.dH 

class VantHoffExtended(GlobalConnector):
    """
    Fit a collection of ITC experiments at different temperatures to extract the 
    heat capacity change upon binding, as well as the enthalpy and binding 
    constant at at the defined reference temperature.
    """

    def __init__(self,name,reference_temp=298.15,R=1.9872036):
        """
        Initialize the VantHoffExtended class, defining the fitting parameters.
        """

        self.reference_temp = reference_temp
        self.R = R

        self._param_names = ["dCp","dH_ref","K_ref"]

        self._initialize()

          
    def K(self,experiment):
        """
        Return the temperature-dependent binding constant, determined using the
        binding constant at a reference temperature, enthalpy at that reference
        temperature, and the heat capacity change on binding.
        """

        T = experiment.temperature
        T_ref = self.reference_temp

        a = -(self.dH_ref/self.R)*(1/T - 1/T_ref)
        b = (self.dCp/self.R)*(np.log(T/T_ref) + T/T_ref - 1)

        return self.K_ref*np.exp(a + b)

    def dH(self,experiment):
        """
        Return the enthalpy change of binding at a given temperature, determined
        from the enthalpy change at the reference temperature and the heat 
        capacity change on binding.
        """

        return self.dH_ref

