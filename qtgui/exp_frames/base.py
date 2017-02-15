from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

class Experiments(QWidget):
	"""
	Experiment box widget
	"""

	def __init__(self, name, parent):

		super().__init__()

		self._name = name
		self._fitter = parent._fitter
		self._slider_list = parent._slider_list
		self._global_var = parent._global_var
		self._connectors_seen = parent._connectors_seen
		#self._global_seen = parent._global_seen
		#self._update_fit_func = parent.add_exp()

		self.layout()

	def layout(self):
		"""
		"""
		self._main_layout = QVBoxLayout(self)

		# Construct the header for the experiment
		self._name_stretch = QHBoxLayout()
		self._name_stretch.addStretch(1)
		self._name_label = QLabel(self._name)
		self._name_stretch.addWidget(self._name_label)
		self._main_layout.addLayout(self._name_stretch)

		# Create divider	
		self._divider = QFrame()
		self._divider.setFrameShape(QFrame.HLine)
		self._main_layout.addWidget(self._divider)

		# Create empty box for any required parameters
		self._req_box = QFrame()
		self._req_layout = QVBoxLayout()
		self._req_box.setLayout(self._req_layout)
		self._main_layout.addWidget(self._req_box)

		# Button to hide and show advanced options for the experiment
		self._show_options_button = QPushButton("Show Sliders", self)
		self._show_options_button.clicked.connect(self.slider_popup)

		# Button to remove experiment
		self._remove_button = QPushButton("Remove", self)
		self._remove_button.clicked.connect(self.remove)

		# Create layout that holds the options and removal buttons
		self._button_stretch = QHBoxLayout()
		self._button_stretch.addStretch(1)
		self._button_stretch.addWidget(self._show_options_button)
		self._button_stretch.addWidget(self._remove_button)
		self._main_layout.addLayout(self._button_stretch)

		self.exp_widgets()

	def exp_widgets(self):
		"""
		for changing local/global specific items
		"""
		pass

	def remove(self):
		"""
		"""
		pass

	def slider_popup(self):
		"""
		show window containing sliders
		"""
		pass

			