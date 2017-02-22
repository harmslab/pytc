from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn
from io import StringIO

from .exp_frames import LocalBox, GlobalBox, ConnectorsBox
import pytc

class Plot(FigureCanvas):
	"""
	create a plot widget
	"""

	def __init__(self, fitter, parent = None, width = 6, height = 6, dpi = 80):

		fig, ax = fitter.plot()

		super().__init__(fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

class PlotBox(QWidget):
	"""
	hold plot widget and update plot
	"""

	def __init__(self, parent):
		super().__init__()

		self._fitter = parent._fitter

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

	def update_plot(self):
		"""
		"""
		self.clear()

		plot_figure = Plot(self._fitter)
		self._plot_layout.addWidget(plot_figure)

	def clear(self):
		"""
		"""
		for i in reversed(range(self._plot_layout.count())): 
			self._plot_layout.itemAt(i).widget().setParent(None)

class ParamTable(QWidget):
	"""
	take csv style param string and put into table widget
	"""

	def __init__(self, fitter):
		super().__init__()

		self._fitter = fitter
		self._header = []
		self._col_name = []
		self._data = []

		self.layout()

	def layout(self):
		"""
		"""
		main_layout = QVBoxLayout(self)

		self._param_table = QTableWidget()
		main_layout.addWidget(self._param_table)

		#self.csv_to_table()
		self.load_table()

	def load_table(self):
		"""
		"""
		for i, row in enumerate(self._data):
			for j, col in enumerate(row):
				item = QTableWidgetItem(col)
				self._param_table.setItem(i, j, item)

	def csv_to_table(self):
		"""
		"""
		self._header = []
		self._col_name = []
		self._data = []

		file_data = self._fitter.fit_as_csv
		string_file = StringIO(file_data)

		for i in string_file:
		    if i.startswith("#"):
		        self._header.append(i.rstrip())
		    elif i.startswith("type"):
		        i = i.rstrip().split(',')
		        self._col_name = i
		    else:
		        i = i.rstrip().split(',')
		        self._data.append(i)

	def update(self):
		"""
		"""
		self.csv_to_table()
		self.load_table()

		self._param_table.setRowCount(len(self._data))
		self._param_table.setColumnCount(len(self._data[0]))
		self._param_table.setHorizontalHeaderLabels(self._col_name)


class AllExp(QWidget):
	"""
	experiment box widget
	"""

	def __init__(self, parent):

		super().__init__()

		self._fitter = parent._fitter
		self._slider_list = {"Global" : {}, "Local" : {}}
		self._global_var = []
		self._connectors_seen = {}
		self._local_appended = []
		self._connectors_to_add = {}
		self._global_tracker = {}

		self.layout()

	def layout(self):
		"""
		"""

		self._main_layout = QVBoxLayout(self)

		self._scroll = QScrollArea(self)
		self._exp_content = QWidget()
		self._exp_box = QVBoxLayout(self._exp_content)
		self._scroll.setWidget(self._exp_content)
		self._scroll.setWidgetResizable(True)

		self._param_box = ParamTable(self._fitter)

		self._splitter = QSplitter(Qt.Vertical)
		self._splitter.addWidget(self._scroll)
		self._splitter.addWidget(self._param_box)
		self._splitter.setSizes([200, 200])

		self._main_layout.addWidget(self._splitter)

		# for testing
		print_exp = QPushButton("Print Experiments/Sliders (Testing)", self)
		print_exp.clicked.connect(self.print_sliders)
		self._main_layout.addWidget(print_exp)

	def add_exp(self):
		"""
		update fit and parameters, update sliders as well
		"""
		self._experiments = self._fitter.experiments
		self._global_seen = self._fitter.global_param

		if len(self._experiments) != 0:

			# create local holder if doesn't exist
			for e in self._experiments:

				if e in self._slider_list["Local"]:
					continue

				self._slider_list["Local"][e] = []
				self._connectors_seen[e] = []

				file_name = e.dh_file
				exp_name = file_name.split("/")[-1]

				exp = LocalBox(e, exp_name, self)
				self._exp_box.addWidget(exp)

			# create global holder if doesn't exist
			for n, e in self._global_seen.items():

				curr_name = n.split('_')[0]

				if curr_name in self._slider_list["Global"] or curr_name in self._connectors_to_add:
					continue

				# create global exp object and add to layout
				global_e = GlobalBox(n, e, self)
				self._exp_box.addWidget(global_e)

			# create holder for a global connector item if it doesn't exist
			for n, c in self._connectors_to_add.items():

				if n in self._slider_list["Global"]:
					continue

				self._slider_list["Global"][n] = []

				# create a connector holder and add to layout
				connector_e = ConnectorsBox(n, c, self)
				self._exp_box.addWidget(connector_e)

			for ex in self._local_appended:
				ex.set_attr()

			try:
				self._fitter.fit()
				self._param_box.update()
			except:
				fit_status = self._fitter.fit_status
				error_message = QMessageBox.warning(self, "warning", "fit failed! " + str(fit_status), QMessageBox.Ok)
		else:
			print("failed :(")

	def print_sliders(self):
		"""
		testing function, make sure sliders getting added to dictionary
		"""
		print(self._slider_list)

	def clear(self):
		"""
		"""
		self._slider_list = {"Global" : {}, "Local" : {}}
		self._param_box.clear()
		for i in reversed(range(self._exp_box.count())): 
			self._exp_box.itemAt(i).widget().setParent(None)

