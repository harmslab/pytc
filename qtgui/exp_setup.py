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

		self._gen_widgets = {}

		sig = signature(self._fitter.add_experiment)
		param = sig.parameters

		for i in param:
			if "=" not in str(param[i]) and str(param[i]) != "experiment":
				self._gen_widgets[param[i]] = QLineEdit(self)
			else:
				pass

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

		gen_exp = QPushButton("Generate Experiment", self)
		gen_exp.clicked.connect(self.generate)

		position = 3

		for name, entry in self._gen_widgets.items():
			label_name = str(name).replace("_", " ") + ": "
			label = QLabel(label_name.title(), self)

			layout.addWidget(label, position, 0)
			layout.addWidget(entry, position, 1)

			position += 1

		layout.addWidget(load_exp, 0, 0)
		layout.addWidget(self._exp_label, 0, 1)
		layout.addWidget(model_label, 1, 0)
		layout.addWidget(model_select, 1, 1)
		layout.addWidget(shot_label, 2, 0)
		layout.addWidget(shot_start_text, 2, 1)
		layout.addWidget(gen_exp, len(self._gen_widgets)+4, 1)

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
		model_param = [int(v.text()) for (k, v) in self._gen_widgets.items()]

		itc_exp = pytc.ITCExperiment(self._exp_file, self._exp_model, self._shot_start)
		self._exp_list["Local"][self._exp_name] = itc_exp
		self._fitter.add_experiment(itc_exp, *model_param)
		
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