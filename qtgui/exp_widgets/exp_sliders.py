from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from .indiv_exp import *

class SlidersExpanded(QWidget):
	"""
	extra slider options pop-up
	"""

	def __init__(self, exp, fitter):
		super().__init__()

		self._exp = exp
		self._fitter = fitter

		self.layout()

	def layout(self):

		main_layout = QGridLayout(self)

		# update bounds, link???


class Sliders(QWidget):
	"""
	create sliders for an experiment
	"""

	def __init__(self, exp, param_name, value, fitter, exp_list):
		super().__init__()

		self._exp = exp
		self._param_name = param_name
		self._value = value
		self._fitter = fitter
		self._exp_list = exp_list

		self.layout()

	@property
	def param_name(self):

		return self._param_name

	def layout(self):

		layout = QGridLayout(self)
		layout.setVerticalSpacing(40)

		self._name_label = QLabel(self._param_name, self)
		layout.addWidget(self._name_label, 0, 0, 0, 2)

		self._fix = QCheckBox("Fix?", self)
		self._fix.toggle()
		self._fix.setChecked(False)
		self._fix.stateChanged.connect(self.fix)
		layout.addWidget(self._fix, 1, 0)

		exp_range = self._exp.model.param_guess_ranges[self._param_name]

		self._slider = QSlider(Qt.Horizontal)
		self._slider.valueChanged[int].connect(self.update_val)
		self._slider.setMinimum(exp_range[0])
		self._slider.setMaximum(exp_range[1])
		layout.addWidget(self._slider, 1, 1)

		self._fix_int = QLineEdit(self)
		layout.addWidget(self._fix_int, 1, 2)
		self._fix_int.setText(str(1))
		self._fix_int.hide()

		self._link = QComboBox(self)
		self._link.addItem("Unlink")
		self._link.addItem("Add Global Var")

		for i in self._global_list:
			self._link.addItem(i)

		self._link.activated[str].connect(self.link_unlink)
		layout.addWidget(self._link, 1, 3)

		self._expand = QPushButton("...", self)
		self._expand.clicked.connect(self.expanded)
		layout.addWidget(self._expand, 1, 4)

	def expanded(self):

		self._more = SlidersExpanded(self._exp, self._fitter)
		self._more.setGeometry(500, 400, 400, 100)
		self._more.show()

	def fix(self, state):

		if state == Qt.Checked:
			# change widget views
			self._fix_int.show()
			self._slider.hide()

			self._fitter.fix(self._exp, **{self._param_name: int(self._fix_int.text())})
			print(self._fix_int.text())
		else:
			#change widget views
			self._fix_int.hide()
			self._slider.show()

			self._fitter.unfix(*[self._param_name], expt = self._exp)
			print('unfixed')

	def update_val(self, value):

		self._fitter.update_guess(self._param_name, value, self._exp)
		print(value)


class LocalSliders(Sliders):
	"""
	create sliders for an experiment
	"""

	def __init__(self, exp, param_name, value, fitter, global_list, parent_list, exp_list):

		self._global_list = global_list
		self._parent_list = parent_list

		super().__init__(exp, param_name, value, fitter, exp_list)

	def link_unlink(self, status):

		if status == "Unlink":
			self._fitter.unlink_from_global(self._exp, self._param_name)
			print("unlinked")
		elif status == "Add Global Var":
			text, ok = QInputDialog.getText(self, "Add Global Variable", "Var Name: ")
			if ok: 
				self._global_list.append(text)
				for e in self._parent_list.values():
					for i in e:
						i.update_global(text)
		else:
			self._fitter.link_to_global(self._exp, self._param_name, status)
			self._global_exp[status] = GlobalExp(self._fitter, status, self._parent_list, self._global_list, self._exp_list)
			print("linked to " + status)

	def update_global(self, value):

		self._link.addItem(value)

class GlobalSliders(Sliders):
	"""
	create sliders for an experiment
	"""

	def __init__(self, exp, param_name, value, fitter, global_exp):
		super().__init__(exp, param_name, value, fitter, global_exp)

		