#!/bin/sh
# run from .. directory

nosetests --ckan --with-pylons=ckanext-etsin/test.ini ckanext-etsin/ckanext/etsin/tests --logging-clear-handlers --logging-filter=ckanext
