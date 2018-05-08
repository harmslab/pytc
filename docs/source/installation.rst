:orphan:

============
Installation
============

These instructions are for installing the API.  If you want to install the GUI,
please follow the `instructions <https://pytc-gui.readthedocs.io/en/latest/installation.html>`_.

If you do not already have a Python scientific computing environment set up, we recommend
you follow `these steps <https://python-for-scientists.readthedocs.io/en/latest/_pages/install_python.html>`_.

Dependencies
------------
 + `python3 <https://www.python.org/downloads/release/python-3>`_
 + `numpy <http://www.numpy.org/>`_
 + `scipy <https://www.scipy.org/>`_
 + `matplotlib <http://matplotlib.org/>`_
 + `emcee <http://dan.iel.fm/emcee/current/>`_
 + `jupyter <https://jupyter.org/>`_ (useful for fit scripting)

Mac & Linux
-----------

1. Open a terminal
2. Type the following command:

    .. sourcecode:: bash

        pip3 install pytc-fitter

Windows
-------

1. Open the program *Anaconda prompt*
2. In the prompt, type:

    .. sourcecode:: bash

        python -m pip install pytc-fitter

To test that the program installed correctly:

1. Open a Jupyter notebook
2. Type :code:`import pytc` into a cell and run the cell.  If the cell runs,
   without an error, you have successfully installed the pytc api.
