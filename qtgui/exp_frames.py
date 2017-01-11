from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn

from .exp_widgets import *

class Plot(FigureCanvas):
	"""
	create a plot widget
	"""

	def __init__(self, fitter, parent = None, width = 6, height = 6, dpi = 80):

		fig, ax = fitter.plot()

		#self._fig = Figure(figsize = (width, height), dpi = dpi)
		#self._axes = fig.add_subplot(111)

		super().__init__(fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def clear(self, fitter):

		fig, ax = fitter.plot()

class PlotBox(QWidget):
	"""
	hold plot widget and update plot
	"""

	def __init__(self, exp_list):
		super().__init__()

		self._exp_list = exp_list

		self.layout()

	def layout(self):

		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)

		self._plot_layout = QVBoxLayout()
		plot_frame = QFrame()
		plot_frame.setLayout(self._plot_layout)

		main_layout.addWidget(plot_frame)
		
		gen_plot = QPushButton("Generate Plot", self)
		gen_plot.clicked.connect(self.update_plot)
		main_layout.addWidget(gen_plot)

	def update_plot(self):

		if self._exp_list:
			for i in reversed(range(self._plot_layout.count())): 
				self._plot_layout.itemAt(i).widget().setParent(None)

			fitter = self._exp_list["Fitter"]
			plot_figure = Plot(fitter)
			self._plot_layout.addWidget(plot_figure)

class AllExp(QWidget):
	"""
	experiment box widget
	"""

	def __init__(self, exp_list):
		super().__init__()

		self._exp_list = exp_list
		self._labels = {}
		self._global_var = []
		self.layout()

	def layout(self):

		main_layout = QVBoxLayout(self)

		scroll = QScrollArea(self)
		#main_layout.addWidget(scroll)

		exp_content = QWidget()
		self._exp_box = QVBoxLayout(exp_content)
		scroll.setWidget(exp_content)
		scroll.setWidgetResizable(True)

		self._param_box = QTextEdit(self)
		self._param_box.setReadOnly(True)
		#main_layout.addWidget(self._param_box)

		splitter = QSplitter(Qt.Vertical)
		splitter.addWidget(scroll)
		splitter.addWidget(self._param_box)
		splitter.setSizes([200, 200])

		main_layout.addWidget(splitter)

		gen_experiments = QPushButton("Fit Experiments", self)
		gen_experiments.clicked.connect(self.add_exp)
		main_layout.addWidget(gen_experiments)

		print_exp = QPushButton("Print Experiments", self)
		print_exp.clicked.connect(self.print_exp)
		main_layout.addWidget(print_exp)

	def add_exp(self):

		self._fitter = self._exp_list["Fitter"]

		for n, e in self._exp_list["Local"].items():
			if e not in self._labels:
				self._labels[e] = []
				exp = LocalExp(self._fitter, e, n, self._labels, self._global_var, self._exp_list)
				self._exp_box.addWidget(exp)
			else:
				print('already in frame')

		for n, e in self._exp_list["Global"].items():
			self._exp_box.addWidget(e)

		self._fitter.fit()
		self.return_param()

	def return_param(self):
		"""
		"""
		self._param_box.append(self._fitter.fit_as_csv)

	def print_exp(self):

		print(self._labels)

	def remove(self, exp_frame):

		 pass

	def hide(self, exp_frame):

		exp_frame.hide()

	def show(self, exp_frame):

		exp_frame.show()