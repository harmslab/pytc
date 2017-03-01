from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .base import Experiments
from .. import slider_popup
from .. import sliders

class LocalBox(Experiments):
	"""
	hold local parameters/sliders
	"""
	def __init__(self, exp, name, parent):

		self._exp = exp
		self._local_appended = parent._local_appended
		self._required_fields = {}
		self._experiments = parent._experiments
		self._connectors_to_add = parent._connectors_to_add
		self._exp_box = parent._exp_box

		super().__init__(name, parent)

	def exp_widgets(self):
		"""
		create sliders for experiment
		"""
		self._local_appended.append(self)

		parameters = self._exp.param_values

		for p, v in parameters.items():
			s = sliders.LocalSliders(p, v, self)
			self._slider_list["Local"][self._exp].append(s)

	def slider_popup(self):
		"""
		hide and show slider window
		"""
		self._slider_window = slider_popup.LocalPopUp(self)
		self._slider_window.setGeometry(450, 200, 600, 300)
		self._slider_window.show()
				
	def update_req(self):
		"""
		checks if any global connectors are connected and updates to add fields for any required data
		"""
		exp_connectors = self._connectors_seen[self._exp]

		for c in exp_connectors:
			required = c.required_data
			for i in required:
				if i not in self._required_fields:
					label_name = str(i).replace("_", " ") + ": "
					label = QLabel(label_name.title(), self)
					field = QLineEdit(self)
					self._required_fields[i] = field

					stretch = QHBoxLayout()
					stretch.addWidget(label)
					stretch.addWidget(field)
					stretch.addStretch(1)

					self._req_layout.addLayout(stretch)
				else:
					print("already there")

	def set_attr(self):
		"""
		update data from global connector fields
		"""
		for n, v in self._required_fields.items():
			try:
				val = float(v.text())
			except:
				val = v.text()

			setattr(self._exp, n, val)

	def remove(self):
		"""
		"""
		self._fitter.remove_experiment(self._exp)
		self._slider_list["Local"].pop(self._exp, None)
		self.close()
