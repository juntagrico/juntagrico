Documentation
=============

Generating documentation
------------------------

To generate the documentation locally you can run the command below.
After its completion you should see a new folder in the repository
called ``.docs`` in which you can find the generate HTML files. For
example, open the ``index.html`` file with your favorite browser to
brows through the documentation.

.. code:: bash

   # Install sphinx to generate the documentation locally
   pip install sphinx sphinx-rtd-theme
   # Generate the documentation from the docs folder and place it in .docs
   sphinx-build docs .docs
