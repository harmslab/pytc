:orphan:
============
Installation
============

Dependencies
------------
 + `python3 <https://www.python.org/downloads/release/python-3>`_
 + `numpy <http://www.numpy.org/>`_
 + `scipy <https://www.scipy.org/>`_
 + `matplotlib <http://matplotlib.org/>`_
 + `pyqt5 <http://pyqt.sourceforge.net/Docs/PyQt5/installation.html>`_ (for the GUI)
 + `pandas <http://pandas.pydata.org/>`_ (for the GUI)
 + `jupyter <https://jupyter.org/>`_ (useful for fit scripting)

Mac
---

 1. Make sure you have python3 installed.  To see if it is installed, open a
    terminal and type :code:`python3`.  If the command fails, you need to obtain
    python3.  You can either install a python3 scientific computing stack (like
    `anaconda <https://www.continuum.io/downloads>`_) or download and install
    python3.x `directly <https://www.python.org/downloads/release/python-3>`_. 

 2. Install :code:`pip3`.  Open a terminal and type:
    ::
    sudo easy_install pip3

 3. Once this has run, type:
    ::
    sudo pip3 install pytc-fitter

Linux
-----
 
 1. Make sure you have python3 installed.  To see if it is installed, open a
    terminal and type :code:`python3`.  If the command fails, you need to obtain
    python3.  You can either install a python3 scientific computing stack (like
    `anaconda <https://www.continuum.io/downloads>`_), download and install
    python3.x `directly <https://www.python.org/downloads/release/python-3>`_,
    or obtain it via your package manner.  On Ubuntu and other Debian-like
    systems, this would be:
    :: 
    sudo apt-get install python3

 2. Install :code:`pip3`.  Open a terminal and type:
    ::
    sudo easy_install pip3

 3. Once this has run, type:
    ::
    sudo pip3 install pytc-fitter

.. note::
    On some linux distributions, qt5 does not play nice with qt4.  


Windows
-------

1. Make sure you have python3 installed on your machine. To see if it is intalled,
   open the Windows command prompt and type :code:`python` into the terminal. The
   python version currently installed on your machine should print to the terminal.
   If the command fails, you need to obtain python3. You install a python3 
   scientific computing stack (like `anaconda <https://www.continuum.io/downloads>`_).
   The latest version of Anaconda can be installed using the Windows installer from 
   Anaconda, this will include all of the additional packages needed to run pytc,
   including pyqt5. 
2. Once python is installed download the pytc package onto your machine. Using the
   Windows command prompt run :code:`python setup.py install`. 
3. Once install has completed, from the command prompt launch :code:`python gui_main.py`.
   This will launch the gui interface for pytc. 
   
   

