from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .. import add_global_connector
from .base import Sliders
#from .global_signaling import GlobalConnectSignal

class LocalSliders(Sliders):
	"""
	create sliders for a local exp object
	"""

	def __init__(self, param_name, value, parent):

		self._value = value
		self._global_var = parent._global_var
		self._slider_list = parent._slider_list
		self._connectors_seen = parent._connectors_seen
		self._glob_connect_req = {}
		self._local_appended = parent._local_appended
		self._connectors_to_add = parent._connectors_to_add
		self._global_tracker = parent._global_tracker
		self._if_connected = None

		super().__init__(param_name, parent)

	def bounds(self):
		"""
		update the min max for the slider
		"""
		subclasses = pytc.global_connectors.GlobalConnector.__subclasses__()
		self._global_connectors = {i.__name__: i(i.__name__) for i in subclasses}

		exp_range = self._exp.model.param_guess_ranges[self._param_name]

		self._slider.setMinimum(exp_range[0])
		self._slider.setMaximum(exp_range[1])

		self._link = QComboBox(self)
		self._link.addItem("Unlink")
		self._link.addItem("Add Global Var")
		self._link.addItem("Add Connector")

		for i in self._global_var:
			self._link.addItem(i)

		self._link.activated[str].connect(self.link_unlink)
		self._main_layout.addWidget(self._link, 1, 3)

	def link_unlink(self, status):
		"""
		add global variable, update if parameter is linked or not to a global paremeter
		"""
		if status == "Unlink":
			try:
				self._fitter.unlink_from_global(self._exp, self._param_name)
				self._global_tracker[self._if_connected].unlinked(self)
				self.reset()
				#print(self._fitter.global_param)
			except:
				pass

		elif status == "Add Global Var":
			text, ok = QInputDialog.getText(self, "Add Global Variable", "Var Name: ")
			if ok: 
				self._global_var.append(text)
				for e in self._slider_list["Local"].values():
					for i in e:
						i.update_global(text)
			else:
				i = self._link.findText("Unlink")
				self._link.setCurrentIndex(i)

		elif status == "Add Connector":
	
			def connector_handler(connector,var_names):
		
				self._global_var.append(connector)
				for v in var_names:
					self._glob_connect_req[v] = connector.local_methods[v]
					self._global_connectors[v] = connector

				# Append connector methods to dropbdown lists
				for p, v in connector.local_methods.items():
					for e in self._slider_list["Local"].values():
						for i in e:
							i.update_global(p)
			
			self.diag = add_global_connector.AddGlobalConnectorWindow(connector_handler)
			self.diag.show()

		elif status not in self._glob_connect_req:
			# connect to a simple global variable
			self._fitter.link_to_global(self._exp, self._param_name, status)
			self._slider.hide()
			self._fix.hide()
			self._update_min_label.hide()
			self._update_min.hide()
			self._update_max_label.hide()
			self._update_max.hide()

			self._global_tracker[status] = self
			self._if_connected = status
			print("linked to " + status)
			print(self._fitter.global_param)
			
			#self._update_fit_func
		else:
			# connect to global connector
			self._slider.hide()
			self._fix.hide()
			self._update_min_label.hide()
			self._update_min.hide()
			self._update_max_label.hide()
			self._update_max.hide()

			curr_connector = self._global_connectors[status]
			self._connectors_seen[self._exp].append(curr_connector)
			self._connectors_to_add[curr_connector.name] = curr_connector
			self._fitter.link_to_global(self._exp, self._param_name, self._glob_connect_req[status])
			
			self._global_tracker[curr_connector.name] = self
			self._if_connected = curr_connector.name

			print("connected to " + status)

			for e in self._local_appended:
				e.update_req()

	def update_global(self, value):
		"""
		update the list of global parameters in combobox
		"""
		self._link.addItem(value)

	def reset(self):
		"""
		if global exp object deleted, return local slider object to unlinked state
		"""
		self._slider.show()
		self._fix.show()
		self._update_min_label.show()
		self._update_min.show()
		self._update_max_label.show()
		self._update_max.show()

		unlink_index = self._link.findText("Unlink", Qt.MatchFixedString)
		self._link.setCurrentIndex(unlink_index)
		
	def update_bounds(self):
		"""
		update min/max bounds and check if range needs to be updated as well
		"""
		bounds = [self._min, self._max]
		self._fitter.update_bounds(self._param_name, bounds, self._exp)

		# check if bounds are smaller than range, then update.
		curr_range = self._exp.model.param_guess_ranges[self._param_name]
		curr_bounds = self._exp.model.bounds[self._param_name]

		if curr_range[0] < curr_bounds[0] or curr_range[1] > curr_bounds[1]:
			self._fitter.update_range(self._param_name, bounds, self._exp)