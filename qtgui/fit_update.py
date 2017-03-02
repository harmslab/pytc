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
		self._main_layout = QVBoxLayout(self)


	def update(self):
		"""
		clear main layout and add new graph to layout
		"""
		self.clear()
		self._figure, self._ax = self._fitter.plot()

		plot_figure = FigureCanvas(self._figure)
		self._main_layout.addWidget(plot_figure)

	def clear(self):
		"""
		"""
		for i in reversed(range(self._main_layout.count())): 
			self._main_layout.itemAt(i).widget().deleteLater()

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

	def load_table(self):
		"""
		load fit data into the table
		"""
		for i, row in enumerate(self._data):
			for j, col in enumerate(row):
				item = QTableWidgetItem(col)
				self._param_table.setItem(i, j, item)

	def csv_to_table(self):
		"""
		convert csv data file to lists to be read by qtablewidget
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
		update the table with updated fit parameters
		"""
		self.csv_to_table()

		self._param_table.setRowCount(len(self._data))
		self._param_table.setColumnCount(len(self._data[0]))
		self._param_table.setHorizontalHeaderLabels(self._col_name)

		self.load_table()

	def clear(self):
		"""
		"""
		self._param_table.clear()
		self._header = []
		self._col_name = []
		self._data = []


class AllExp(QWidget):
	"""
	experiment box widget
	"""

	def __init__(self, parent):

		super().__init__()

		self._fitter = parent._fitter
		self._slider_list = {"Global" : {}, "Local" : {}}
		self._global_var = []
		self._local_appended = []
		self._global_tracker = {}
		self._glob_connect_req = {}
		self._global_connectors = {}
		self._connectors_to_add = {}
		self._connectors_seen = {}
		self._plot_frame = parent._plot_frame

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
		update fit and parameters, update experiments added to fitter
		"""
		self._experiments = self._fitter.experiments

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

			for ex in self._local_appended:
				ex.set_attr()

			try:
				self._fitter.fit()

				for e in self._local_appended:
					e.set_fit_true()

				for n, e in self._global_tracker.items():
					e.set_fit_true()

				self._param_box.update()
			except:
				fit_status = self._fitter.fit_status
				error_message = QMessageBox.warning(self, "warning", "fit failed! " + str(fit_status), QMessageBox.Ok)
		else:
			print("no experiments loaded in fitter")

	def print_sliders(self):
		"""
		testing function, make sure sliders getting added to dictionary
		"""
		print(self._slider_list)

	def clear(self):
		"""
		"""
		for l in self._local_appended:
			self._fitter.remove_experiment(l._exp)

		self._slider_list = {"Global" : {}, "Local" : {}}
		self._global_var = []
		self._connectors_seen = {}
		self._local_appended = []
		self._connectors_to_add = {}
		self._global_tracker = {}
		self._glob_connect_req = {}
		self._global_connectors = {}
		self._param_box.clear()
		for i in reversed(range(self._exp_box.count())): 
			self._exp_box.itemAt(i).widget().deleteLater()

