=============================
django-resource-scheduler
=============================

.. image:: https://badge.fury.io/py/django-resource-scheduler.png
    :target: https://badge.fury.io/py/django-resource-scheduler

.. image:: https://travis-ci.org/weijia/django-resource-scheduler.png?branch=master
    :target: https://travis-ci.org/weijia/django-resource-scheduler

.. image:: https://coveralls.io/repos/weijia/django-resource-scheduler/badge.png?branch=master
    :target: https://coveralls.io/r/weijia/django-resource-scheduler?branch=master

A resoruce scehduler

Documentation
-------------

The full documentation is at https://django-resource-scheduler.readthedocs.org.

Quickstart
----------

Install django-resource-scheduler::

    pip install django-resource-scheduler

Then use it in a project::

    import django-resource-scheduler

Features
--------

* Resource creation permission is customizable when the following class attribute is overrided
    class ResourceScheduleTemplateView(TemplateView, ColorSchema):
        resource_permission_id = "resource_daily_scheduler.change_bookableresource"
* TODO
