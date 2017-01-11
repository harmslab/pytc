"""
pytc GUI using qtpy bindings
"""
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from .exp_setup import *
from .exp_frames import *

from matplotlib.backends.backend_pdf import PdfPages

class Splitter(QWidget):
	"""
	hold main experiment based widgets
	"""

	def __init__(self, exp_list):
		super().__init__()

		self._exp_list = exp_list
		self.layout()

	def layout(self):
		"""
		"""
		main_frame = QHBoxLayout(self)

		#self.setStyleSheet(open("style.qss", "r").read())

		self._exp_box = AllExp(self._exp_list)
		self._plot_frame = PlotBox(self._exp_list)

		splitter = QSplitter(Qt.Horizontal)
		splitter.addWidget(self._plot_frame)
		splitter.addWidget(self._exp_box)
		splitter.setSizes([200, 200])

		main_frame.addWidget(splitter)
		self.setLayout(main_frame)

	def clear(self):
		"""
		"""
		self._plot_frame.clear()
		self._exp_box.clear()

class Main(QMainWindow):
	"""
	"""
	def __init__(self):
		super().__init__()

		self._exp_list = {"Local" : {}, "Global" : {}}

		self.menu()
		self.new_exp()

	def menu(self):
		"""
		make the menu bar
		"""
		menu = self.menuBar()
		menu.setNativeMenuBar(False)

		file_menu = menu.addMenu("Experiments")
		testing_commands = menu.addMenu("Testing")

		return_exp = QAction("Print Experiments", self)
		return_exp.setShortcut("Ctrl+P")
		return_exp.triggered.connect(self.print_exp)
		testing_commands.addAction(return_exp)

		return_fitter = QAction("Print Fitter", self)
		#return_fitter.setShortcut("Ctrl+P")
		return_fitter.triggered.connect(self.print_fitter)
		testing_commands.addAction(return_fitter)

		new_exp = QAction("New Session", self)
		new_exp.setShortcut("Ctrl+N")
		new_exp.triggered.connect(self.new_exp)
		file_menu.addAction(new_exp)

		file_menu.addSeparator()

		add_exp = QAction("Add Experiment", self)
		add_exp.setShortcut("Ctrl+Shift+N")
		add_exp.triggered.connect(self.add_file)
		file_menu.addAction(add_exp)

		file_menu.addSeparator()

		save_exp = QAction("Save", self)
		save_exp.setShortcut("Ctrl+S")
		save_exp.triggered.connect(self.save_file)
		file_menu.addAction(save_exp)

		export_exp = QAction("Export (not working)", self)
		file_menu.addAction(export_exp)

		open_exp = QAction("Open (not working)", self)
		file_menu.addAction(open_exp)

		file_menu.addSeparator()

		close_window = QAction("Close Window", self)
		close_window.setShortcut("Ctrl+W")
		close_window.triggered.connect(self.close_program)
		file_menu.addAction(close_window)

		self._exp = Splitter(self._exp_list)
		self.setCentralWidget(self._exp)

		self.setGeometry(300, 150, 950, 600)
		self.setWindowTitle('pytc')
		self.show()

	def print_exp(self):
		"""
		testing, check pytc experiments loading
		"""
		print(self._exp_list["Local"])

	def print_fitter(self):
		"""
		testing to make sure fitter selected correctly
		"""
		print(self._exp_list["Fitter"])

	def add_file(self):
		"""
		add a new pytc experiment.
		"""
		self._new_exp = AddExp(self._exp_list)
		self._new_exp.setGeometry(530, 400, 100, 200)
		self._new_exp.show()

	def new_exp(self):
		"""
		choose fitter and start new fit
		"""

		self._choose_fitter = ChooseFitter(self._exp_list, self._exp)
		self._choose_fitter.setGeometry(550, 420, 300, 100)
		self._choose_fitter.show()

	def file_exists(self):
		"""
		working on this...
		"""
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)

		msg.setText("Warning! File already exists. Would you like to overwrite existing files?")
		msg.setStandardButtons(QMessageBox.Save | QMessageBox.Close)

		if msg == QMessageBox.Save: 
			print("save")
		else:
			print("close")

	def save_file(self):
		"""
		save out fit data and plot
		"""
		fitter = self._exp_list["Fitter"]

		file_name = QFileDialog.getSaveFileName(self, "Save File")
		csv_name = file_name[0] + "_fit.csv"
		plot_name = file_name[0] + "_plot.pdf"

		data_file = open(csv_name, "w")
		data_file.write(fitter.fit_as_csv)
		data_file.close()

		plot_save = PdfPages(plot_name)
		fig, ax = fitter.plot()
		plot_save.savefig(fig)
		plot_save.close()

	def close_program(self):
		"""
		close window
		"""
		self.close()