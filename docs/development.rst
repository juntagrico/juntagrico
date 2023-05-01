Development
===========

The following list of commands provides an easy way of getting started
with juntagrico. It was tested on macOS 13 and Linux. Contributions for
getting it setup and running under Windows are welcome.

Installing Python and dependencies
----------------------------------

First we need to install Git and Python 3. Under macOS you can use `homebrew <https://docs.brew.sh/Installation>`_ to
easily install Python via the command line.

.. code:: bash

   # Under Linux, e.g Debian based distribution
   sudo apt update && sudo apt install python3 python3-pip git

   # Under mac with homebrew
   brew install python3 git

With the basic dependencies installed we can clone the repository and setup
the project.

.. code:: bash

   # First we need to clone the repository to your local machine.
   git clone https://github.com/juntagrico/juntagrico.git juntagrico
   # Change into the freshly cloned repository
   cd juntagrico
   # Install virtualenv so that we don't pollute the OS installation.
   pip3 install virtualenv
   # Create a virtual environment
   virtualenv .venv
   # Activate the virtual environment
   source .venv/bin/activate
   # Install python dependencies
   pip install -r requirements-local.txt

Getting started
---------------

.. code:: bash

   # Create local database and apply schemas
   python manage.py migrate
   # Start local development server on port 8000
   python manage.py runserver 8000

Generating documentation
------------------------

To generate the documentation locally you can run the command below.
After its completion you should see a new folder in the repository
called ``.docs`` in which you can find the generate HTML files. For
example, open the ``index.html`` file with your favorite browser to
brows through the documentation.

.. code:: bash

   # Install sphinx to generate the documentation locally
   pip install sphinx
   # Generate the documentation from the docs folder and place it in .docs
   sphinx-build -C docs .docs
