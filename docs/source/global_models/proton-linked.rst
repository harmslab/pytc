:orphan:

Proton linked
--------------

This fits a global model to a collection of ITC experiments collected in buffers
of the same pH, but different ionization enthalpies.

`global_connectors\.NumProtons <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/num_protons.py>`_

This is useful for analyzing a binding reaction that involves the gain or loss of
a proton.  The measured enthalpy will have a binding component and an ionization
component.  These can be separated by performing ITC experiments using buffers
with different ionization enthalpies.

Scheme
~~~~~~

.. math::
    \Delta H_{obs,buffer} = \Delta H_{intrinsic} + \Delta H_{ionization,buffer} \times n_{proton},

where :math:`\Delta H_{intrinsic}` is the buffer-independent binding enthalpy,
:math:`\Delta H_{ionization,buffer}` is the buffer ionization enthalpy, and
:math:`n_{proton}` is the number of protons gained or lost.


Parameters
~~~~~~~~~~
+---------------------------------+------------------------------+----------------------------+---------------+
|parameter                        | variable                     | parameter name             | class         |
+=================================+==============================+============================+===============+
|association constant             | :math:`\Delta H_{intrinsic}` | :code:`dH_intrinsic`       | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|binding enthalpy                 | :math:`n_{proton}`           | :code:`num_protons`        | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+

Required data for each experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
+---------------------------------+--------------------------------------+----------------------------+
|data                             | variable                             | data                       |
+=================================+======================================+============================+
|ioinzation enthalpy              | :math:`\Delta H_{ionization,buffer}` | :code:`ionization_enthalpy`|
+---------------------------------+--------------------------------------+----------------------------+
