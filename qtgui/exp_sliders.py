from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

class SlidersExpanded(QWidget):
	"""
	extra slider options pop-up
	"""

	def __init__(self, exp, param_name, fitter, slider):
		super().__init__()

		self._exp = exp
		self._param_name = param_name
		self._fitter = fitter
		self._slider = slider
		self._min = slider.minimum()
		self._max = slider.maximum()

		self.layout()

	def layout(self):
		"""
		"""
		main_layout = QGridLayout(self)

		update_min = QLineEdit(self)
		update_max = QLineEdit(self)

		min_label = QLabel("Update Min: ", self)
		max_label = QLabel("Update Max: ", self)

		main_layout.addWidget(min_label, 0, 0)
		main_layout.addWidget(update_min, 0, 1)
		main_layout.addWidget(max_label, 1, 0)
		main_layout.addWidget(update_max, 1, 1)

		self.setWindowTitle("Update Bounds")

	def min_bounds(self, value):
		"""
		update the minimum bounds
		"""
		try:
			self._min = int(value)
			self.update()
		except:
			pass

		print("min bound updated: " + self._min)

	def max_bounds(self, value):
		"""
		update maximum bounds
		"""
		try:
			self._max = int(value)
			self.update()
		except:
			pass

		print("max bound updated: " + self._max)

	def update(self):
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


class Sliders(QWidget):
	"""
	create sliders for an experiment
	"""

	def __init__(self, exp, param_name, fitter, global_exp):
		super().__init__()

		self._exp = exp
		self._param_name = param_name
		self._fitter = fitter
		self._global_exp = global_exp

		self.layout()

	@property
	def param_name(self):
		"""
		"""
		return self._param_name

	def bounds(self):
		"""
		"""
		pass


	def layout(self):
		"""
		"""
		self._main_layout = QGridLayout(self)
		self._main_layout.setVerticalSpacing(40)

		self._name_label = QLabel(self._param_name, self)
		self._main_layout.addWidget(self._name_label, 0, 0, 0, 2)

		self._fix = QCheckBox("Fix?", self)
		self._fix.toggle()
		self._fix.setChecked(False)
		self._fix.stateChanged.connect(self.fix_layout)
		self._main_layout.addWidget(self._fix, 1, 0)

		self._slider = QSlider(Qt.Horizontal)
		self._slider.valueChanged[int].connect(self.update_val)
		self._main_layout.addWidget(self._slider, 1, 1)

		self._param_guess_label = QLabel("", self)
		self._main_layout.addWidget(self._param_guess_label, 1, 2)

		self.bounds()

		self._fix_int = QLineEdit(self)
		self._main_layout.addWidget(self._fix_int, 1, 3)
		self._fix_int.setText(str(1))
		self._fix_int.textChanged[str].connect(self.fix)
		self._fix_int.hide()

		self._expand = QPushButton("...", self)
		self._expand.clicked.connect(self.expanded)
		self._main_layout.addWidget(self._expand, 1, 4)

	def expanded(self):
		"""
		expanded slider options, right now bounds
		"""
		self._more = SlidersExpanded(self._exp, self._param_name, self._fitter, self._slider)
		self._more.setGeometry(500, 400, 400, 100)
		self._more.show()

	def fix_layout(self, state):
		"""
		initial parameter fix and updating whether slider/fixed int is hidden or shown
		"""
		if state == Qt.Checked:
			# change widget views
			self._fix_int.show()
			self._slider.hide()

			self._fitter.update_fixed(self._param_name, int(self._fix_int.text()), self._exp)
			print(self._fix_int.text())
		else:
			#change widget views
			self._fix_int.hide()
			self._slider.show()

			self._fitter.update_fixed(self._param_name, None, self._exp)
			print('unfixed')

	def fix(self, value):
		"""
		update fixed value if changed
		"""
		if value:
			self._fitter.update_fixed(self._param_name, int(value), self._exp)
		else:
			print("unabled to fix")

		print("fixed to value " + value)

	def update_val(self, value):
		"""
		update value for paremter based on slider value
		"""
		self._fitter.update_guess(self._param_name, value, self._exp)
		self._param_guess_label.setText(str(value))
		#print(value)


class LocalSliders(Sliders):
	"""
	create sliders for a local exp object
	"""

	def __init__(self, exp, param_name, value, fitter, global_list, slider_list, global_exp, connectors_seen, local_appended):

		self._global_list = global_list
		self._slider_list = slider_list
		self._value = value
		self._connectors_seen = connectors_seen
		self._glob_connect_req = {}
		self._local_appended = local_appended

		super().__init__(exp, param_name, fitter, global_exp)

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

		for i in self._global_list:
			self._link.addItem(i)

		for n, c in self._global_connectors.items():
			self.global_connect(n, c)

		self._link.activated[str].connect(self.link_unlink)
		self._main_layout.addWidget(self._link, 1, 3)

	def link_unlink(self, status):
		"""
		add global variable, update if parameter is linked or not to a global paremeter
		"""

		if status == "Unlink":
			try:
				self._fitter.unlink_from_global(self._exp, self._param_name)
				self._global_exp[status].unlinked(self)
			except:
				print("failed")

			print("unlinked")
		elif status == "Add Global Var":
			text, ok = QInputDialog.getText(self, "Add Global Variable", "Var Name: ")
			if ok: 
				self._global_list.append(text)
				for e in self._slider_list["Local"].values():
					for i in e:
						i.update_global(text)
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

			if status not in self._global_exp:
				self._global_exp[status] = GlobalExp(self._fitter, curr_connector, status, self._slider_list, self._global_list, self._global_exp, self._connectors_seen)
			
			self._global_exp[status].linked(self)
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

class GlobalSliders(Sliders):
	"""
	create sliders for a global exp object
	"""

	def __init__(self, exp, param_name, fitter, global_exp):
		super().__init__(exp, param_name, fitter, global_exp)

	def bounds(self):
		"""
		update min/max for slider
		"""
		exp_range = self._fitter.param_ranges[0][self._param_name]

		self._slider.setMinimum(exp_range[0])
		self._slider.setMaximum(exp_range[1])
		

class Experiments(QWidget):
	"""
	experiment box widget
	"""

	def __init__(self, fitter, exp, name, slider_list, global_var, global_exp, connectors_seen):
		super().__init__()

		self._fitter = fitter
		self._exp = exp
		self._name = name
		self._slider_list = slider_list
		self._global_var = global_var
		self._global_exp = global_exp
		self._connectors_seen = connectors_seen

		self.layout()

	def layout(self):
		"""
		"""
		main_layout = QVBoxLayout(self)

		name_label = QLabel(self._name)
		name_stretch = QHBoxLayout()
		name_stretch.addStretch(1)
		name_stretch.addWidget(name_label)
		main_layout.addLayout(name_stretch)

		divider = QFrame()
		divider.setFrameShape(QFrame.HLine)
		main_layout.addWidget(divider)

		req_box = QFrame()
		self._req_layout = QVBoxLayout()
		req_box.setLayout(self._req_layout)
		main_layout.addWidget(req_box)

		remove = QPushButton("Remove", self)
		remove.clicked.connect(self.remove)

		hide_show = QPushButton("Hide/Show", self)
		hide_show.setCheckable(True)
		hide_show.clicked[bool].connect(self.hide_show)

		stretch = QHBoxLayout()
		stretch.addStretch(1)
		stretch.addWidget(hide_show)
		stretch.addWidget(remove)
		main_layout.addLayout(stretch)

		self._exp_layout = QVBoxLayout()
		self._exp_widget = QFrame()
		self._exp_widget.setLayout(self._exp_layout)
		self._exp_widget.hide()

		main_layout.addWidget(self._exp_widget)

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
		else:
			self._exp_widget.hide()

class LocalExp(Experiments):
	"""
	hold local parameters/sliders
	"""
	def __init__(self, fitter, exp, name, slider_list, global_var, global_exp, local_exp, connectors_seen, local_appended):

		self._local_exp = local_exp
		self._local_appended = local_appended
		self._required_fields = {}

		super().__init__(fitter, exp, name, slider_list, global_var, global_exp, connectors_seen)

	def exp_widgets(self):
		"""
		create sliders for experiment
		"""
		self._local_appended.append(self)

		parameters = self._exp.param_values

		for p, v in parameters.items():
			s = LocalSliders(self._exp, p, v, self._fitter, self._global_var, self._slider_list, self._global_exp, self._connectors_seen, self._local_appended)
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
			#val = float(v.text()) if v.text().isdigit() else v.text()

			print(self._required_fields, type(val))

			setattr(self._exp, n, val)

	def remove(self):
		"""
		"""
		self._fitter.remove_experiment(self._exp)
		self._local_exp.pop(self._exp, None)
		self._slider_list["Local"].pop(self._exp, None)
		self.close()

class GlobalExp(Experiments):
	"""
	hold global parameter/sliders
	"""
	def __init__(self, fitter, exp, name, slider_list, global_var, global_exp, connectors_seen):

		super().__init__(fitter, exp, name, slider_list, global_var, global_exp, connectors_seen)

		self._linked_list = []

	def exp_widgets(self):
		"""
		create slider
		"""

		# see if global variable is a connector or simple var
		if isinstance(self._exp, pytc.global_connectors.GlobalConnector):
			param = self._exp.params

			for p, v in param.items():
				s = GlobalSliders(None, p, self._fitter, self._global_exp)
				self._slider_list["Global"][self._exp].append(s)
				self._exp_layout.addWidget(s)
		else:
			s = GlobalSliders(None, self._name, self._fitter, self._global_exp)
			self._slider_list["Global"][self._name] = s
			self._exp_layout.addWidget(s)

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
		self._global_exp.pop(self._name, None)
		self._fitter.remove_global(self._name)
		self._slider_list["Global"].pop(self._name, None)

		for s in self._linked_list:
			s.reset()

		self.close()
