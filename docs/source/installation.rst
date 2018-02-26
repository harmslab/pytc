:orphan:

============
Installation
============

These instructions are for installing the API.  If you want to install the GUI,
please follow the instructions `here <https://pytc-gui.readthedocs.io/en/latest/installation.html>`_. 

Dependencies
------------
 + `python3 <https://www.python.org/downloads/release/python-3>`_
 + `numpy <http://www.numpy.org/>`_
 + `scipy <https://www.scipy.org/>`_
 + `matplotlib <http://matplotlib.org/>`_
 + `emcee <http://dan.iel.fm/emcee/current/>`_
 + `jupyter <https://jupyter.org/>`_ (useful for fit scripting)

Mac
---

 1. Make sure you have python3 installed.  To see if it is installed, open a
    terminal and type :code:`python3`.  If the command fails, you need to obtain
    python3.  You can either install a python3 scientific computing stack (like
    `anaconda <https://www.continuum.io/downloads>`_) or download and install
    python3.x `directly <https://www.python.org/downloads/release/python-3>`_. 

 2. Install :code:`pip3`.  Open a terminal and type:

    .. sourcecode:: bash
    
        sudo easy_install pip3

 3. Once this has run, type:

    .. sourcecode:: bash

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

    .. sourcecode:: bash

        sudo apt-get install python3 python3-pip

 2. Once this has run, type:

    .. sourcecode:: bash
    
        sudo pip3 install pytc-fitter


Windows
-------

These instructions assume that you do not already have anaconda installed. 

 1. Install the python 3.x version of anaconda `anaconda <https://www.anaconda.com/downloads>`_
 2. Open the :code:`Anaconda prompt` program.
 3. In the prompt, type:

    .. sourcecode:: bash

        python -m pip install pytc-fitter

 4. Open the :code:`Anaconda navigator` program.
 5. Start up a :code:`Jupyter notebook` instance.  
 6. Open a new notebook and type :code:`import pytc` into a cell.  If the cell
    runs, you have successfully installed the pytc api.

