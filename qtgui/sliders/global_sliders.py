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

	def __init__(self, exp, param_name, fitter):
		super().__init__(exp, param_name, fitter,)

	def bounds(self):
		"""
		update min/max for slider
		"""
		exp_range = self._fitter.param_ranges[1][self._param_name]

		self._slider.setMinimum(exp_range[0])
		self._slider.setMaximum(exp_range[1])