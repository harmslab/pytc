from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .. import sliders
from .base import SliderPopUp

class ConnectorPopUp(SliderPopUp):
	"""
	pop-up window for slider widgets
	"""

	def __init__(self, parent):
		"""
		"""
		self._connector = parent._connector
		self._exp = None

		super().__init__(parent)

	def populate(self):
		"""
		"""
		sliders = self._slider_list["Global"][self._name]

		# add sliders to layout
		for s in sliders:
			self._main_layout.addWidget(s)