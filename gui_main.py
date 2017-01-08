import qtgui
import sys
from qtpy.QtWidgets import QApplication

if __name__ == '__main__':

	app = QApplication(sys.argv)
	pytc_run = qtgui.Main()
	sys.exit(app.exec_())