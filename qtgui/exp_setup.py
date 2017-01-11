import pytc
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import pandas as pd
from inspect import signature

class AddExp(QWidget):
	"""
	add experiment pop-up box
	"""

	def __init__(self, exp_list):
		super().__init__()

		self._models = {"Blank" : pytc.indiv_models.Blank,
                        "Single Site" : pytc.indiv_models.SingleSite,
                        "Single Site Competitor" : pytc.indiv_models.SingleSiteCompetitor,
                        "Binding Polynomial" : pytc.indiv_models.BindingPolynomial}

		self._exp_file = None
		self._shot_start = 1
		self._exp_list = exp_list
		self._fitter = exp_list["Fitter"]

		self.layout()

	def layout(self):
		"""
		"""
		# exp text, model dropdown, shots select

		layout = QGridLayout()
		self.setLayout(layout)

		model_select = QComboBox(self)
		for k, v in self._models.items():
			model_select.addItem(k)

		self._exp_model = self._models[str(model_select.currentText())]
		model_select.activated[str].connect(self.model_select)

		load_exp = QPushButton("Load File", self)
		load_exp.clicked.connect(self.add_file)

		self._exp_label = QLabel("...", self)
		model_label = QLabel("Select Model: ", self)
		shot_label = QLabel("Shot Start: ", self)

		shot_start_text = QLineEdit(self)
		shot_start_text.textChanged[str].connect(self.shot_select)

		gen_widgets = {load_exp : self._exp_label, model_label : model_select, shot_label : shot_start_text}

		sig = signature(self._fitter.add_experiment)
		param = sig.parameters

		self._new_param = {}

		for i in param:
			if "=" not in str(param[i]) and str(param[i]) != "experiment":
				#connect = lambda new: new_param[param[i]] = new

				label_name = str(param[i]).replace("_", " ") + ": "
				new_widget = QLineEdit(self)
				gen_widgets[QLabel(label_name.title(), self)] = new_widget
				#new_widget.textChanged[str].connect(connect)
			else:
				pass

		gen_exp = QPushButton("Generate Experiment", self)
		gen_exp.clicked.connect(self.generate)

		position = 0

		for label, entry in gen_widgets.items():
			layout.addWidget(label, position, 0)
			layout.addWidget(entry, position, 1)

			position += 1

		layout.addWidget(gen_exp, len(gen_widgets)+1, 1)

	def model_select(self, model):
		"""
		"""
		self._exp_model = self._models[model]
		#print(self._exp_model)

	def shot_select(self, shot):
		"""
		"""
		self._shot_start = int(shot)
		#print(self._shot_start, type(self._shot_start))

	def add_file(self):
		"""
		"""
		file_name, _ = QFileDialog.getOpenFileName(self, "Select a file...", "", filter="DH Files (*.DH)")
		self._exp_file = str(file_name)
		self._exp_name = file_name.split("/")[-1]
		self._exp_label.setText(self._exp_name)
		#print(self._exp_file, type(self._exp_file))

	def generate(self):
		"""
		"""
		itc_exp = pytc.ITCExperiment(self._exp_file, self._exp_model, self._shot_start)
		self._exp_list["Local"][self._exp_name] = itc_exp
		self._fitter.add_experiment(itc_exp)
		self.close()

class ChooseFitter(QWidget):
	def __init__(self, exp_list):
		"""
		Choose fitter for current session
		"""
		super().__init__()

		self._fitter_choose = {"Global" : pytc.global_models.GlobalFit(),
                        "Proton Linked" : pytc.global_models.ProtonLinked(),
                        "Temperature Dependence" : pytc.global_models.TempDependence()}

		self._exp_list = exp_list

		self.layout()

	def layout(self):
		"""
		"""
		# exp text, model dropdown, shots select

		layout = QGridLayout()
		self.setLayout(layout)

		fitter_select = QComboBox(self)
		for k, v in self._fitter_choose.items():
			fitter_select.addItem(k)

		self._fitter = self._fitter_choose[str(fitter_select.currentText())]

		fitter_select.activated[str].connect(self.fitter_select)

		gen_fitter = QPushButton("Select Fitter", self)
		gen_fitter.clicked.connect(self.generate)

		layout.addWidget(fitter_select, 0, 1, 1, 2)
		layout.addWidget(gen_fitter, 1, 2)

	def fitter_select(self, fitter):
		"""
		"""
		self._fitter = self._fitter_choose[fitter]

	def generate(self):
		"""
		"""
		if "Fitter" not in self._exp_list:
			self._exp_list["Fitter"] = self._fitter
		else:
			self._exp_list = {}
			self._exp_list["Fitter"] = self._fitter
			print("start over")

		self.close()