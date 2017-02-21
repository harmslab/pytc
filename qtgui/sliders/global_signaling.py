from qtpy.QtCore import QObject, pyqtSlot

class GlobalConnectSignal(QObject):
	"""
	link together sliders when connected to the same global variable
	"""

	link_sliders = pyqtSignal

	def connect_sliders(self):
		"""
		"""

		self.link_sliders.connect()

	@pyqtSlot('QSlider')
	def slider_slot(self):

		pass