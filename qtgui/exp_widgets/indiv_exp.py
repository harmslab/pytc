from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from .exp_sliders import *

class Experiments(QWidget):
	"""
	experiment box widget
	"""

	def __init__(self, fitter, exp, labels, global_var, exp_list):
		super().__init__()

		self._exp = exp
		self._labels = labels
		self._fitter = fitter
		self._global_var = global_var
		self._exp_list = exp_list

		self.layout()

	def layout(self):
		main_layout = QVBoxLayout(self)

		name_label = QLabel(self._file_name)
		name_stretch = QHBoxLayout()
		name_stretch.addStretch(1)
		name_stretch.addWidget(name_label)
		main_layout.addLayout(name_stretch)

		self._exp_layout = QVBoxLayout()
		self._exp_widget = QFrame()
		self._exp_widget.setLayout(self._exp_layout)

		main_layout.addWidget(self._exp_widget)

		self.exp_widgets()

		divider = QFrame()
		divider.setFrameShape(QFrame.HLine)
		main_layout.addWidget(divider)

		remove = QPushButton("Remove", self)
		remove.clicked.connect(self.remove)

		hide = QPushButton("Hide", self)
		hide.clicked.connect(self.hide)

		show = QPushButton("Show", self)
		show.clicked.connect(self.show)

		stretch = QHBoxLayout()
		stretch.addStretch(1)
		stretch.addWidget(hide)
		stretch.addWidget(show)
		stretch.addWidget(remove)
		main_layout.addLayout(stretch)

	def exp_widgets(self):

		pass

	def remove(self):

		 self._fitter.remove_experiment(self._exp)
		 self._labels.pop(self._exp, None)
		 self.close()

	def hide(self):

		self._exp_widget.hide()

	def show(self):

		self._exp_widget.show()

class LocalExp(Experiments):

	def __init__(self, fitter, exp, file_name, labels, global_var, exp_list):

		self._file_name = file_name

		super().__init__(fitter, exp, labels, global_var, exp_list)

	def exp_widgets(self):

		global_exp = self._exp_list["Global"]
		parameters = self._exp.param_values

		for p, v in parameters.items():
			s = LocalSliders(self._exp, p, v, self._fitter, self._global_var, self._labels, global_exp)
			self._labels[self._exp].append(s)
			self._exp_layout.addWidget(s)

	def remove(self):

		self._exp_list["Local"].remove(self._exp)
		super().remove()

class GlobalExp(Experiments):

	def __init__(self, fitter, exp, labels, global_var, exp_list):
		super().__init__(fitter, exp, labels, global_var, exp_list)

	def exp_widgets(self):

		global_exp = self._exp_list["Global"]

		s = GlobalSliders(self._exp, p, v, self._fitter, self._global_var, self._labels, global_exp)
		self._labels[self._exp].append(s)
		self._exp_layout.addWidget(s)

	def remove(self):

		self._exp_list["Global"].remove(self._exp)
		self._fitter.remove_global(self._labels[self._exp].param_name)
		super().remove()