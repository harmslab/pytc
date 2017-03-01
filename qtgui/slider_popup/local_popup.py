from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .. import sliders
from .base import SliderPopUp

class LocalPopUp(SliderPopUp):
	"""
	pop-up window for slider widgets
	"""

	def __init__(self, parent):
		"""
		"""
		self._global_var = parent._global_var
		self._connectors_seen = parent._connectors_seen
		self._local_appended = parent._local_appended

		super().__init__(parent)

	def populate(self):
		"""
		"""

		sliders = self._slider_list["Local"][self._exp]
		sliders.sort(key = lambda x: x.name)

		# add sliders to layout
		for s in sliders:
			self._main_layout.addWidget(s)