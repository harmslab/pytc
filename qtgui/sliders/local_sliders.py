from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

from .. import add_global_connector
from .base import Sliders

class LocalSliders(Sliders):
	"""
	create sliders for a local exp object
	"""

	def __init__(self, exp, param_name, value, fitter, global_list, slider_list, connectors_seen, local_appended):

		self._global_list = global_list
		self._slider_list = slider_list
		self._value = value
		self._connectors_seen = connectors_seen
		self._glob_connect_req = {}
		self._local_appended = local_appended

		super().__init__(exp, param_name, fitter)

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

		for i in self._global_list:
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
				#self._global_exp[status].unlinked(self)
			except:
				pass

		elif status == "Add Global Var":
			text, ok = QInputDialog.getText(self, "Add Global Variable", "Var Name: ")
			if ok: 
				self._global_list.append(text)
				for e in self._slider_list["Local"].values():
					for i in e:
						i.update_global(text)
			else:
				i = self._link.findText("Unlink")
				self._link.setCurrentIndex(i)

		elif status == "Add Connector":
	
			def connector_handler(connector,var_name):
		
				self._global_list.append(connector)

				# Link to the global parameter
				self._fitter.link_to_global(self._exp,self._param_name,connector.local_methods[var_name])

				# Append connector methods to dropbdown lists
				for p, v in connector.local_methods.items():
					for e in self._slider_list["Local"].values():
						for i in e:
							i.update_global(p)

				# Set the dropdown to have the currently selected var_name
				i = self._link.findText(var_name)
				self._link.setCurrentIndex(i)
			
			self.diag = AddGlobalConnectorWindow(connector_handler)
			self.diag.show()

		elif status not in self._glob_connect_req:
			# connect to a simple global variable
			self._fitter.link_to_global(self._exp, self._param_name, status)
			self._slider.hide()
			self._fix.hide()

			if status not in self._global_exp:
				self._global_exp[status] = GlobalExp(self._fitter, None, status, self._slider_list, self._global_list, self._global_exp)

			self._global_exp[status].linked(self)
			print("linked to " + status)
		else:
			# connect to global connector
			self._slider.hide()
			self._fix.hide()

			connector_name = self._link.currentText().split(".")[0]
			curr_connector = self._global_connectors[connector_name]
			self._connectors_seen[self._exp].append(curr_connector)
			self._fitter.link_to_global(self._exp, self._param_name, self._glob_connect_req[status])

			self._slider_list["Global"][curr_connector] = []

			#if status not in self._global_exp:
			#	self._global_exp[status] = GlobalExp(self._fitter, curr_connector, status, self._slider_list, self._global_list, self._global_exp, self._connectors_seen)
			
			#self._global_exp[status].linked(self)
			print("connected to " + status)

			for e in self._local_appended:
				e.update_req()

			#print(curr_connector.params)

	def global_connect(self, name, connector):
		"""
		"""
		#self._glob_connect_req[name] = {}

		parent = inspect.getmembers(pytc.global_connectors.GlobalConnector, inspect.isfunction)
		parent_list = [i[0] for i in parent]
		child = inspect.getmembers(connector, inspect.ismethod)
		child_list = [i[0] for i in child]

		diff = set(child_list).difference(parent_list)
		child_func = [i for i in child if i[0] in diff]

		for i in child_func:
			func_name = name + '.' + i[0]
			self._glob_connect_req[func_name] = i[1]
			self._link.addItem(func_name)

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

		unlink_index = self._link.findText("Unlink", Qt.MatchFixedString)
		self._link.setCurrentIndex(unlink_index)
		