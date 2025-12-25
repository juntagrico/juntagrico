Development
===========

.. warning::
    This are the instructions for juntagrico developers. If you want to use juntagrico, follow the :ref:`installation instructions <intro-installation>` instead.

Setup using venv
----------------

The following list of commands provides an easy way of getting started with the development in juntagrico.
It was tested on macOS 13 and Linux. Contributions for
getting it setup and running under Windows are welcome.

Installing Python and dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
   pip install -r requirements.txt

Configure and run
^^^^^^^^^^^^^^^^^

.. code:: bash

   # Create local database and apply schemas
   python -m manage migrate
   # Create a super user account
   python -m manage createadmin
   # Start local development server on port 8000
   python -m manage runserver 8000

you can now open http://localhost:8000 in your browser.

Setup using Docker
------------------

You can also use a docker container instead of installing python directly.

Execute the tests:

.. code:: bash

   docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && export DJANGO_SETTINGS_MODULE=settings.dev && export PYTHONPATH=. && coverage run -m manage test && coverage report"

Execute the linter:

.. code:: bash

   docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "pip install ruff && ruff check juntagrico"

Generate the documentation:

.. code:: bash

    docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "pip install sphinx sphinx-rtd-theme docutils && sphinx-build -b html docs _build/html"

You find the generated documentation in the _build/html folder.

Display an example of all mail texts:

.. code:: bash

    docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && export DJANGO_SETTINGS_MODULE=settings.dev && export PYTHONPATH=. && python -m manage mailtexts"

Start the application (using an integrated sqlite database):

.. code:: bash

   docker run --rm -it -v $(pwd):/app -w /app -p 8000:8000 python:3.11-slim bash -c "pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && export DJANGO_SETTINGS_MODULE=settings.dev && export PYTHONPATH=. && python -m manage migrate && python -m manage createadmin && python -m manage runserver 0.0.0.0:8000"

During the process you can specify the admin credentials. Access the
application under http://localhost:8000
