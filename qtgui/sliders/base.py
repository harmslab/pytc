from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import pytc
import inspect

class Sliders(QWidget):
	"""
	create sliders for an experiment
	"""

	def __init__(self, param_name, parent):
		super().__init__()

		self._exp = parent._exp
		self._param_name = param_name
		self._fitter = parent._fitter
		#self._update_fit_func = parent._update_fit_func

		self.layout()

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

		self._min = self._slider.minimum()
		self._max = self._slider.maximum()

		self._fix_int = QLineEdit(self)
		self._main_layout.addWidget(self._fix_int, 1, 3)
		self._fix_int.setText(str(1))
		self._fix_int.textChanged[str].connect(self.fix)
		self._fix_int.hide()

		self._update_min_label = QLabel("min: ", self)
		self._main_layout.addWidget(self._update_min_label, 1, 4)

		self._update_min = QLineEdit(self)
		self._main_layout.addWidget(self._update_min, 1, 5)
		self._update_min.textChanged[str].connect(self.min_bounds)

		self._update_max_label = QLabel("max: ", self)
		self._main_layout.addWidget(self._update_max_label, 1, 6)

		self._update_max = QLineEdit(self)
		self._main_layout.addWidget(self._update_max, 1, 7)
		self._update_max.textChanged[str].connect(self.max_bounds)

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

	def min_bounds(self, value):
		"""
		update the minimum bounds
		"""
		try:
			self._min = int(value)
			self.update()
		except:
			pass

		print("min bound updated: " + value)

	def max_bounds(self, value):
		"""
		update maximum bounds
		"""
		try:
			self._max = int(value)
			self.update_bounds()
		except:
			pass

		print("max bound updated: " + value)

	def update_bounds(self):
		"""
		update min/max bounds and check if range needs to be updated as well
		"""
		pass