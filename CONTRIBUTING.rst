Contributing
============

Flask-FS is open-source and very open to contributions.

Submitting issues
-----------------

Issues are contributions in a way so don't hesitate
to submit reports on the `official bugtracker`_.

Provide as much informations as possible to specify the issues:

- the flask-fs version used
- a stacktrace
- installed applications list
- a code sample to reproduce the issue
- ...


Submitting patches (bugfix, features, ...)
------------------------------------------

If you want to contribute some code:

1. fork the `official Flask-FS repository`_
2. create a branch with an explicit name (like ``my-new-feature`` or ``issue-XX``)
3. do your work in it
4. rebase it on the master branch from the official repository (cleanup your history by performing an interactive rebase)
5. submit your pull-request

There are some rules to follow:

- your contribution should be documented (if needed)
- your contribution should be tested and the test suite should pass successfully
- your code should be mostly PEP8 compatible with a 120 characters line length
- your contribution should support both Python 2 and 3 (use ``tox`` to test)

You need to install some dependencies to develop on Flask-FS:

.. code-block:: console

    $ pip install -e .[dev]

An Invoke ``tasks.py`` is provided to simplify the common tasks:

.. code-block:: console

    $ inv -l
    Available tasks:

      all      Run tests, reports and packaging
      clean    Cleanup all build artifacts
      cover    Run tests suite with coverage
      dist     Package for distribution
      doc      Build the documentation
      qa       Run a quality report
      start    Start the middlewares (docker)
      stop     Stop the middlewares (docker)
      test     Run tests suite
      tox      Run tests against Python versions

You can launch invoke without any parameters, it will:

- start ``docker`` middlewares containers (ensure docker and docker-compose are installed)
- execute tox to run tests on all supported Python version
- build the documentation
- execute flake8 quality report
- build a distributable wheel

Or you can execute any task on demand.
By exemple, to only run tests in the current Python environment and a quality report:

.. code-block:: console

    $ inv test qa


.. _official Flask-FS repository: https://github.com/noirbizarre/flask-fs
.. _official bugtracker: https://github.com/noirbizarre/flask-fs/issues
