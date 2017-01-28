__description__ = \
"""
Define a class that allows description of individual fitting parameters as some
function of experimental properties and global parameters.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-15"

import inspect
from .. import fit_param

class GlobalConnector:
    """
    Describe simple, individual fitting parameters as an arbitrary collection 
    of other, underlying parameters that depend on experimental properties.
    """

    param_guesses = {"":0.0}

    def __init__(self,name):
        """
        Initialize the class. 

        name: name of the fitter.  will be pre-pended to all parameter names.
        """
    
        self._name = name

        self._param_names = list(self.param_guesses.keys())
        
        methods = [m[0] for m in inspect.getmembers(self, predicate=inspect.ismethod)]
        for p in self._param_names:
            if p in methods:
                err = "param_names cannot have the same names as observable\n"
                err = err + " methods in GlobalConnector subclasses.\n"
                err = err + "Offending parameter: {}\n".format(p)

                raise ValueError(err)

        self._update_name_dicts()

    def _update_name_dicts(self):
        """
        Uses an "int_name" name without the name prefixed to the parameter.
        This is used by __dict__ so the person writing a new connector does not
        use a prefix when referring to the parameter.  There is also an 
        "ext_name" name with the name of the class prefixed to the parameter.
        """

        self._int_to_ext_name = {}
        self._ext_to_int_name = {}

        # If no prefix is specified, the mapping is trival
        if self._name == "":
            self._param_names = list(self.param_guesses.keys())
            for p in self._param_names:
                self._int_to_ext_name[p] = p
                self._ext_to_int_name[p] = p
        else: 
            self._int_to_ext_name = dict([(p,"{}_{}".format(self._name,p))
                                          for p in self._param_names])
            self._ext_to_int_name = dict([("{}_{}".format(self._name,p),p)
                                          for p in self._param_names])

        self._param_dict = {}
        for int_name in self._param_names:
            ext_name = self._int_to_ext_name[int_name] 
            self._param_dict[ext_name] = fit_param.FitParameter(ext_name,
                                                                guess=self.param_guesses[int_name])
            self.__dict__[int_name] = self._param_dict[ext_name].value

    @property
    def name(self):
        """
        Return the name of the global connector (string).
        """

        return self._name

    @name.setter
    def name(self,name):
        """
        Set the name of the connector, updating the parameter names
        """

        self._name = name
        self._update_name_dicts()

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

    @property
    def local_methods(self):
        """
        Return the connector functions defined for this class (things like
        self.dH and self.K).
        """

        output = {}

        # Determine the functions defined in the parent class(es)
        parent_classes = self.__class__.__bases__
        parent_functions = []
        for p in parent_classes:
            for f in inspect.getmembers(p,inspect.isfunction):
                if not f[0].startswith("_"):
                    parent_functions.append(f[0])

        # Determine the methods defined specifically for this class
        child_functions = inspect.getmembers(self.__class__, inspect.isfunction)
        for f in child_functions:
            if not f[0].startswith("_") and f[0] not in parent_functions:
                output["{}.{}".format(self.name,f[0])] = getattr(self,f[0])


        return output 
