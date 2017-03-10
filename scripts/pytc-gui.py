#!/usr/bin/env python3

from pytc.qtgui import Main
import sys
from qtpy.QtWidgets import QApplication

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


if __name__ == '__main__':

	try:
		app = QApplication(sys.argv)
		pytc_run = Main()
		sys.exit(app.exec_())
	except KeyboardInterrupt:
		sys.exit()

