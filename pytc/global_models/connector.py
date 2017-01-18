
import inspect
import numpy as np
from .. import fit_param

class GlobalConnector:
    """
    Describe simple, individual fitting parameters as an arbitrary collection 
    of other, underlying parameters.
    """

    def __init__(self,name):
        """
        """
    
        self.name = name
        self._param_names = [""]
        self._initialize()

    def _initialize(self):
        """
        Uses an "int_name" name without the name prefixed to the parameter.
        This is used by __dict__ so the person writing a new connector does not
        use a prefix when referring to the parameter.  There is also an 
        "ext_name" name with the name of the class prefixed to the parameter.
        """


        methods = [m[0] for m in inspect.getmembers(self, predicate=inspect.ismethod)]
        for p in self._param_names:
            if p in methods:
                err = "param_names cannot have the same names as observable\n"
                err = err + " methods in GlobalConnector subclasses.\n"
                err = err + "Offending parameter: {}\n".format(p)

                raise ValueError(err)
 
        self._int_to_ext_name = {}
        self._ext_to_int_name = {}

        # If there is only one, unnamed parameter, the mapping is trivial
        if len(self._param_names) == 1 and self._param_names[0] == "":
            self._param_names = [self.name]
            self._int_to_ext_name[self.name] = self.name
            self._ext_to_int_name[self.name] = self.name
        else: 
            self._int_to_ext_name = dict([(p,"{}_{}".format(self.name,p))
                                          for p in self._param_names])
            self._ext_to_int_name = dict([("{}_{}".format(self.name,p),p)
                                          for p in self._param_names])

        self._param_dict = {}
        for int_name in self._param_names:
            ext_name = self._int_to_ext_name[int_name] 
            self._param_dict[ext_name] = fit_param.FitParameter(ext_name)
            self.__dict__[int_name] = self._param_dict[ext_name].value

    @property
    def params(self):
        """
        Return a dictionary of FitParameter instances.  Keys are ext_name 
        names.
        """

        return self._param_dict

    def update_values(self,param_dict):
        """
        Update the value of a parameter.
        """
        for ext_name in param_dict.keys():

            int_name = self._ext_to_int_name[ext_name]

            self._param_dict[ext_name].value = param_dict[ext_name]
            self.__dict__[int_name] = self._param_dict[ext_name].value

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
    
        self.name = name
        self.reference_temp = reference_temp
        self.R = R

        self._param_names = ["dH_vanthoff","K_ref"]

        self._initialize()

    def K(self,experiment):
        """
        Return the temperature-dependent binding constant, calculated using the
        a fixed enthalpy and shifting K. 
        """

        T = experiment.temperature + 273.15
        T_ref = self.reference_temp

        a = -(self.dH_vanthoff/self.R)*(1/T - 1/T_ref)

        return self.K_ref*np.exp(a)
       
    def dH(self,experiment):
        """
        Return the van't Hoff enthalpy.
        """

        return self.dH_vanthoff 

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

        self.name = name
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

        T = experiment.temperature + 273.15
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

        T = experiment.temperature + 273.15
        return self.dH_ref + self.dCp*(T - self.reference_temp)

