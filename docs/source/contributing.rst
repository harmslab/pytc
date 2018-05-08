:orphan:

============
Contributing
============

I found a bug!
==============

Please let us know and we'll fix it.  To ensure we can understand the problem,
please follow this `quick guide <https://testlio.com/blog/the-ideal-bug-report/>`_
to writing useful bug reports.  Go to `<https://github.com/harmslab/pytc/issues>`_
and create a new issue. If you want to take a crack at fixing the bug yourself,
see the next section.

I fixed a bug/implemented a new feature.
========================================

Great! We love new contributions! Please follow
`this workflow <https://github.com/Zsailer/guide-to-working-as-team-on-github>`_
to contribute code to the project.  This workflow alllows you to get credit for
your work, while allowing us to maintain a clean codebase.  After you make a pull
request, we'll review it and start a conversation with you about incorporating
the change.

Some other important notes:

+ Code should follow the `PEP8 Style Guide <https://www.python.org/dev/peps/pep-0008/>`_.
+ Docstrings should follow the `numpy style guide <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

I implemented a new thermodynamic model.
========================================

Wonderful!  First, make sure you're following the coding guidelines described
above for the code itself.  Second, write up a description of your model.  All
pytc documentation is written in
`restructed text <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_.
The repository contains template .rst files that can be modified for new models

+ :code:`pytc/docs/source/indiv_models/template.rst`
+ :code:`pytc/docs/source/global_connectors/template.rst`

Create a new .rst file describing your model from one of these templates.

Once you have implemented the code and written up the model description, create
a pull request containing both changes and we'll work on incorporating the
model.
