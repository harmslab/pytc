from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .base import Experiments
from .. import sliders

class GlobalExp(Experiments):
	"""
	hold global parameter/sliders
	"""
	def __init__(self, fitter, exp, name, slider_list, global_var, connectors_seen):

		super().__init__(fitter, exp, name, slider_list, global_var, connectors_seen)

		self._linked_list = []

	def exp_widgets(self):
		"""
		create slider
		"""

		# see if global variable is a connector or simple var
		if isinstance(self._exp, pytc.global_connectors.GlobalConnector):
			param = self._exp.params

			for p, v in param.items():
				s = sliders.GlobalSliders(None, p, self._fitter, self._global_exp)
				self._slider_list["Global"][self._exp].append(s)
				self._exp_layout.addWidget(s)
		else:
			s = sliders.GlobalSliders(None, self._name, self._fitter, self._global_exp)
			self._slider_list["Global"][self._name] = s
			self._exp_layout.addWidget(s)

	def linked(self, loc_slider):
		"""
		update list of sliders linked to global param
		"""
		self._linked_list.append(loc_slider)

	def unlinked(self, loc_slider):
		"""
		remove item from linked list if local param unlinked from global param
		"""
		self._linked_list.remove(loc_slider)

	def remove(self):
		"""
		"""
		#self._global_exp.pop(self._name, None)
		self._fitter.remove_global(self._name)
		self._slider_list["Global"].pop(self._name, None)

		for s in self._linked_list:
			s.reset()

		self.close()
