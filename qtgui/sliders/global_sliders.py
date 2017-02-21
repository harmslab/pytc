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
		#self._fit_object = parent._fit_object
		super().__init__(param_name, parent)

	def bounds(self):
		"""
		update min/max for slider
		"""
		exp_range = self._fitter.param_ranges[0][self._param_name]

		self._slider.setMinimum(exp_range[0])
		self._slider.setMaximum(exp_range[1])