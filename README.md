ckanext-etsin
=============

Etsin is a CKAN extension for coordinating operations used by Etsin harvesters in Metax.

------------
Requirements
------------

* CKAN 2.6
* Some additional Python packages that are installed using `pip install`


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.etsin --cover-inclusive --cover-erase --cover-tests
