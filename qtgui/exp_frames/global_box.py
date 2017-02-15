from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .base import Experiments
from .. import slider_popup
from .. import sliders

class GlobalBox(Experiments):
	"""
	hold global parameter/sliders
	"""
	def __init__(self, name, global_obj, parent):

		self._linked_list = []
		self._global_obj = global_obj
		self._exp = None

		super().__init__(name, parent)

	def exp_widgets(self):
		"""
		create slider
		"""
		s = sliders.GlobalSliders(self._name, self)
		self._slider_list["Global"][self._name] = s

	def slider_popup(self):
		"""
		hide and show slider window
		"""
		self._slider_window = slider_popup.GlobalPopUp(self)
		self._slider_window.setGeometry(530, 400, 100, 200)
		self._slider_window.show()

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

		self._fitter.remove_global(self._name)
		self._slider_list["Global"].pop(self._name, None)

		for s in self._linked_list:
			s.reset()

		self.close()
