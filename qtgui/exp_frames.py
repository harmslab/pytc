from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn

#from .indiv_exp import *
from .exp_sliders import *

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


class PlotBox(QWidget):
	"""
	hold plot widget and update plot
	"""

	def __init__(self, exp_list):
		super().__init__()

		self._exp_list = exp_list

		self.layout()

	def layout(self):
		"""
		"""
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
		"""
		"""
		if self._exp_list:
			for i in reversed(range(self._plot_layout.count())): 
				self._plot_layout.itemAt(i).widget().setParent(None)

			fitter = self._exp_list["Fitter"]
			plot_figure = Plot(fitter)
			self._plot_layout.addWidget(plot_figure)

	def clear(self):
		"""
		"""
		for i in reversed(range(self._plot_layout.count())): 
			self._plot_layout.itemAt(i).widget().setParent(None)

class AllExp(QWidget):
	"""
	experiment box widget
	"""

	def __init__(self, exp_list):
		super().__init__()

		self._exp_list = exp_list
		self._slider_list = {"Global" : {}, "Local" : {}}
		self._global_var = []
		self.layout()

	def layout(self):
		"""
		"""
		main_layout = QVBoxLayout(self)

		scroll = QScrollArea(self)

		exp_content = QWidget()
		self._exp_box = QVBoxLayout(exp_content)
		scroll.setWidget(exp_content)
		scroll.setWidgetResizable(True)

		self._param_box = QTextEdit(self)
		self._param_box.setReadOnly(True)

		splitter = QSplitter(Qt.Vertical)
		splitter.addWidget(scroll)
		splitter.addWidget(self._param_box)
		splitter.setSizes([200, 200])

		main_layout.addWidget(splitter)

		gen_experiments = QPushButton("Fit Experiments", self)
		gen_experiments.clicked.connect(self.add_exp)
		main_layout.addWidget(gen_experiments)

		print_exp = QPushButton("Print Experiments (Testing)", self)
		print_exp.clicked.connect(self.print_exp)
		main_layout.addWidget(print_exp)

	def add_exp(self):
		"""
		update fit and parameters, update sliders as well
		"""
		try:
			self._fitter = self._exp_list["Fitter"]
			self._local_exp = self._exp_list["Local"]
			self._global_exp = self._exp_list["Global"]

			for n, e in self._local_exp.items():
				if e not in self._slider_list["Local"]:
					self._slider_list["Local"][e] = []
					exp = LocalExp(self._fitter, e, n, self._slider_list, self._global_var, self._global_exp, self._local_exp)
					self._exp_box.addWidget(exp)
				else:
					#print('already in frame')
					pass

			for n, e in self._global_exp.items():
				if e not in self._slider_list["Global"]:
					self._exp_box.addWidget(e)

			self._fitter.fit()
			self.return_param()
		except:
			pass

	def return_param(self):
		"""
		update parameter box 
		"""
		self._param_box.clear()
		self._param_box.append(self._fitter.fit_as_csv)

	def print_exp(self):
		"""
		testing function, make sure sliders getting added to dictionary
		"""
		print(self._slider_list)

	def clear(self):
		"""
		"""
		self._slider_list = {"Global" : {}, "Local" : {}}
		self._exp_list = {"Global" : {}, "Local" : {}}
		self._param_box.clear()
		for i in reversed(range(self._exp_box.count())): 
			self._exp_box.itemAt(i).widget().setParent(None)

