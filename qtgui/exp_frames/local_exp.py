from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .base import Experiments
from .. import sliders

class LocalExp(Experiments):
	"""
	hold local parameters/sliders
	"""
	def __init__(self, fitter, exp, name, slider_list, global_var, experiments, connectors_seen, local_appended):

		#self._local_exp = local_exp
		self._local_appended = local_appended
		self._required_fields = {}
		self._experiments = experiments

		super().__init__(fitter, exp, name, slider_list, global_var, connectors_seen)

	def exp_widgets(self):
		"""
		create sliders for experiment
		"""
		self._local_appended.append(self)

		parameters = self._exp.param_values

		for p, v in parameters.items():
			s = sliders.LocalSliders(self._exp, p, v, self._fitter, self._global_var, self._slider_list, self._connectors_seen, self._local_appended)
			self._slider_list["Local"][self._exp].append(s)
			self._exp_layout.addWidget(s)
				
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
