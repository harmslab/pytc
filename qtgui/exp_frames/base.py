from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

class Experiments(QWidget):
	"""
	Experiment box widget
	"""

	def __init__(self, fitter, exp, name, slider_list, global_var, connectors_seen):

		super().__init__()

		self._fitter = fitter
		self._exp = exp
		self._name = name
		self._slider_list = slider_list
		self._global_var = global_var
		self._connectors_seen = connectors_seen

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

		# Create SOMETHING???
		self._req_box = QFrame()
		self._req_layout = QVBoxLayout()
		self._req_box.setLayout(self._req_layout)
		self._main_layout.addWidget(self._req_box)

		# Button to hide and show advanced options for the experiment
		self._show_options_button = QPushButton("Show Options", self)
		self._show_options_button.setCheckable(True)
		self._show_options_button.clicked[bool].connect(self.hide_show)

		# Button to remove experiment
		self._remove_button = QPushButton("Remove", self)
		self._remove_button.clicked.connect(self.remove)

		# Create layout that holds the options and removal buttons
		self._button_stretch = QHBoxLayout()
		self._button_stretch.addStretch(1)
		self._button_stretch.addWidget(self._show_options_button)
		self._button_stretch.addWidget(self._remove_button)
		self._main_layout.addLayout(self._button_stretch)

		# Box that holds the actual fit slider widgets, etc.
		self._exp_layout = QVBoxLayout()
		self._exp_widget = QFrame()
		self._exp_widget.setLayout(self._exp_layout)
		self._exp_widget.hide()
		self._main_layout.addWidget(self._exp_widget)

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

	def hide_show(self, pressed):
		"""
		"""

		if pressed: 
			self._exp_widget.show()
			self._show_options_button.setText("Hide Options")
		else:
			self._exp_widget.hide()
			self._show_options_button.setText("Show Options")
			