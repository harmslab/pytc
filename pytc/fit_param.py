__description__ = \
"""
Main class for holding fit parameters, including guesses, values, ranges, etc.
"""
__date__ = "2016-09-02"
__author__ = "Michael J. Harms"

import copy
import numpy as np

class FitParameter:
    """
    Class for storing and manipulating generic fit parameters.
    """

    def __init__(self,name,guess=None,guess_range=None,fixed=False,bounds=None,
                 alias=None):
        """
        Initialize class.  Parameters:

        name: name of parameter (string)
        guess: parameter guess (float).  If None, class will guess intelligently
               based on the parameter name.  If no intelligent guess is available,
               guess will be set to 1.0.
        guess_range: range of reasonable guesses (list-like object of 2 floats).
                     If None, class will guess intelligently based on parameter
                     name.  
        fixed: whether or not the parameter is fixed (bool)
        bounds: bounds on fit for parameter (list-like object of 2 floats). If
                None, bounds will be set to (None,None).  If (None,5), no lower
                bound, upper bound of 5.
        alias: alias for parameter name, for linking to global paramter names. (str)
               If None, no alias is made.
        """

        self.name = name
        self.guess = guess
        self.guess_range = guess_range
        self.fixed = fixed
        self.bounds = bounds        
        self.alias = alias
       
        self._initialize_fit_results() 

    def _initialize_fit_results(self):
        """
        Set fit results to start (stdev, ninetyfive, value to guess).
        """
    
        self.value = self.guess
        self._stdev = np.inf
        self._ninetyfive = [-np.inf,np.inf]

    #--------------------------------------------------------------------------
    # parameter name

    @property
    def name(self):
        """
        Name of the parameter.
        """

        return self._name

    @name.setter
    def name(self,n):
        
        self._name = str(n)

    #--------------------------------------------------------------------------
    # parameter value

    @property
    def value(self):
        """
        Value of the parameter.
        """

        return self._value

    @value.setter
    def value(self,v):
        """
        If value is set to None, set value to self.guess value.
        """

        if v != None:
            self._value = v
        else:
            self._value = self.guess

    #--------------------------------------------------------------------------
    # parameter stdev

    @property
    def stdev(self):
        """
        Standard deviation on the parameter.
        """

        return self._stdev

    @stdev.setter
    def stdev(self,s):
        """
        Set the standard deviation of the parameter.
        """

        self._stdev = s

    #--------------------------------------------------------------------------
    # parameter 95% confidence

    @property
    def ninetyfive(self):
        """
        95% confidence interval on the parameter.
        """

        return self._ninetyfive

    @ninetyfive.setter
    def ninetyfive(self,value):
        """
        Set the 95% confidence interval on the parameter.
        """

        if len(value) != 2:
            err = "ninetyfive requires a list-like with length 2.\n"
            raise ValueError(err)

        self._ninetyfive[0] = value[0]
        self._ninetyfive[1] = value[1]

    #--------------------------------------------------------------------------
    # parameter guess

    @property
    def guess(self):
        """
        Guess for the parameter.
        """

        return self._guess

    @guess.setter
    def guess(self,g):
        """
        Set the guess.  If None, choose intelligently based on the name of the
        parameter. 
        """

        if g != None:
            self._guess = g
        else:
            if self.name.startswith("dH"):
                self._guess = 1000.0
            elif self.name.startswith("beta") or self.name.startswith("K"):
                self._guess = 1e6
            elif self.name.startswith("fx"):
                self._guess = 1.0
            else:
                self._guess = 1.0

        self._value = self._guess
        self._initialize_fit_results()

    #--------------------------------------------------------------------------
    # parameter guess_range

    @property
    def guess_range(self):
        """
        Range of reasonable guesses for the parameter. 
        """

        return self._guess_range

    @guess_range.setter
    def guess_range(self,g):
        """
        Set range of reasonable guesses.  If None, choose reasonable guess range
        based on parameter name.
        """

        if g != None:
            try:
                if len(g) != 2:
                    raise TypeError
            except TypeError:
                err = "Guess range must be list-like object of length 2.\n"
                raise ValueError(err)

            self._guess_range = copy.deepcopy(g)
        else:
            if self.name.startswith("dH"):
                self._guess_range = [-10000.0,10000.0]
            elif self.name.startswith("beta") or self.name.startswith("K"):
                self._guess_range = [1.0,1e8]
            elif self.name.startswith("fx"):
                self._guess_range = [0.0,2.0]
            else:
                self._guess_range = [-10000.0,10000.0]

        self._initialize_fit_results()

    #--------------------------------------------------------------------------
    # parameter fixed-ness. 

    @property
    def fixed(self):
        """
        Whether or not the parameter if fixed.
        """

        return self._fixed

    @fixed.setter
    def fixed(self,bool_value):
        """
        Fix or unfix the parameter.
        """
        
        self._fixed = bool(bool_value)
        self._initialize_fit_results()

    #--------------------------------------------------------------------------
    # bounds for fit.

    @property
    def bounds(self):
        """
        Fit bounds.  Either list of bounds or None.
        """

        return self._bounds

    @bounds.setter
    def bounds(self,b):
        """
        Set fit bounds. 
        """

        if b != None:
            try:
                if len(b) != 2:
                    raise TypeError
            except TypeError:
                err = "Bounds must be list-like object of length 2\n"
                raise ValueError(err)
        
            self._bounds = tuple(copy.deepcopy(b))
            
        else:
            self._bounds = (-np.inf,np.inf)

        self._initialize_fit_results()

    #--------------------------------------------------------------------------
    # parameter alias
   
    @property
    def alias(self):
        """
        Parameter alias.  Either string or None.
        """

        return self._alias
    
    @alias.setter
    def alias(self,a):
        """
        Set alias.
        """

        try:
            if self._alias != None and self._alias != a and a != None:
                err = "Could not set alias to {:} because it is already set to {:}".format(a,self._alias)
                raise ValueError(err)
        except AttributeError:
            pass

        self._alias = a

        self._initialize_fit_results()
