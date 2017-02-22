from qtpy.QtCore import QObject, pyqtSlot

class GlobalConnectSignal(QObject):
	"""
	when fitter is changed, update the GUI (?)
	"""

	fit_update = pyqtSignal

	def update_fit(self):
		"""
		"""
		self.fit_update.connect(self.handle_trigger)

	def handle_trigger(self):
		"""
		"""
		print("fit updated")