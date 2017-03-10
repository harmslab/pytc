from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .base import Sliders

class GlobalSliders(Sliders):
	"""
	create sliders for a global exp object
	"""

	def __init__(self, param_name, parent):
		"""
		"""
		super().__init__(param_name, parent)

	def bounds(self):
		"""
		update min/max for slider
		"""
		exp_range = self._fitter.param_ranges[0][self._param_name]

		min_range = 0
		max_range = 0

		# transform values based on parameter to allow floats to pass to fitter and 
		# make sliders easier to use, QtSlider only allows integers
		if "fx_competent" in self._param_name:
			min_range = exp_range[0]*10
			max_range = exp_range[1]*10
		elif "K" in self._param_name:
			min_range = exp_range[0]/100000
			max_range = exp_range[1]/100000
		else:
			min_range = exp_range[0]/100
			max_range = exp_range[1]/100

		self._slider.setMinimum(min_range)
		self._slider.setMaximum(max_range)
