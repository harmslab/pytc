from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .base import Experiments
from .. import slider_popup
from .. import sliders

class ConnectorsBox(Experiments):
	"""
	hold global parameter/sliders
	"""
	def __init__(self, connector, name, parent):

		self._connector = connector
		self._linked_list = []
		self._exp = None

		super().__init__(name, parent)

	def exp_widgets(self):
		"""
		create slider
		"""

		# see if global variable is a connector or simple var
		param = self._connector.params

		for p, v in param.items():
			s = sliders.GlobalSliders(p, self)
			self._slider_list["Global"][self._connector].append(s)

	def slider_popup(self):
		"""
		hide and show slider window
		"""

		self._slider_window = slider_popup.ConnectorPopUp(self)
		self._slider_window.setGeometry(450, 200, 600, 100)
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
		#self._global_seen.pop(self._name, None)
		self._fitter.remove_global(self._name)
		self._slider_list["Global"].pop(self._name, None)

		for s in self._linked_list:
			s.reset()

		self.close()
