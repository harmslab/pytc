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

 1. Install python3 either via `anaconda <https://www.continuum.io/downloads>`_ or
    `winpython <https://winpython.github.io/>`_.  
 2. In an anaconda or winpython terminal, type:

    .. sourcecode:: bash

        pip install pytc-fitter

