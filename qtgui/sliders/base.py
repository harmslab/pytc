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

	def __init__(self, exp, param_name, fitter):
		super().__init__()

		self._exp = exp
		self._param_name = param_name
		self._fitter = fitter
		#self._global_exp = global_exp

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
