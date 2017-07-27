#!/bin/sh
# run from the directory where source folders are

nosetests --ckan --with-pylons=ckanext-etsin/test.ini ckanext-etsin/ckanext/etsin/tests --logging-clear-handlers --logging-filter=ckanext
