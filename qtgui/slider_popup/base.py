from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .. import sliders

class SliderPopUp(QWidget):
	"""
	pop-up window for slider widgets
	"""

	def __init__(self, parent):
		"""
		"""
		super().__init__()

		self._name = parent._name
		self._exp = parent._exp
		self._fitter = parent._fitter
		self._slider_list = parent._slider_list

		self.layout()

	def layout(self):
		"""
		"""
		self._main_layout = QVBoxLayout(self)
		self.setWindowTitle(self._name)

		self.populate()

	def populate(self):
		"""
		"""
		pass