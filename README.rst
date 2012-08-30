=============
cloudprinting
=============

A simple interface to Google Cloud Print.

Usage::

    >>> from cloudprinting import *
    >>> auth = ClientLoginAuth("foo@example.com", "password")
    >>> list_jobs(auth=auth)
    {...}
    >>> submit_job(printer="0e506d12-dbe0-54d3-7392-fd69d45ff2fc", content="test.pdf", auth=auth)
    {...}
