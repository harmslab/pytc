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
	def __init__(self, name, fit_object, parent):

		self._linked_list = []
		self._fit_object = fit_object
		self._exp = None

		super().__init__(name, parent)

	def exp_widgets(self):
		"""
		create slider
		"""
		linked_item = self._global_tracker[self._name]
		self._linked_list.append(linked_item)
		self._global_tracker[self._name] = self

		s = sliders.GlobalSliders(self._name, self)
		self._slider_list["Global"][self._name] = s

	def slider_popup(self):
		"""
		hide and show slider window
		"""
		self._slider_window = slider_popup.GlobalPopUp(self)
		self._slider_window.setGeometry(450, 200, 600, 100)
		self._slider_window.show()

	def linked(self, loc_slider):
		"""
		"""
		self._linked_list.append(loc_slider)
		#print(self._linked_list)

	def unlinked(self, loc_slider):
		"""
		remove item from linked list if local param unlinked from global param
		"""
		self._linked_list.remove(loc_slider)

		# if nothing linked, delete the glob exp object
		if len(self._linked_list) == 0:
			self.remove()

	def remove(self):
		"""
		"""
		try:
			self._fitter.remove_global(self._name)
			self._slider_list["Global"].pop(self._name, None)

			for s in self._linked_list:
				s.reset()
		except:
			pass

		self.close()
