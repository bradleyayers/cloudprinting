=============
cloudprinting
=============

A simple interface to Google Cloud Print.

Usage::

    >>> from cloudprinting import *
    >>> auth = ClientLoginAuth("foo@example.com", "password")
    >>> list_jobs(auth=auth)
    [{"id": ...}, ...]
    >>> submit_job(printer="0e506d12-dbe0-54d3-7392-fd69d45ff2fc", content="test.pdf", auth=auth)
    {"id": "abcdefgh", ...}
    >>> delete_job("abcdefgh", auth=auth)




Tests
=====

The test suite requires three environment variables:

- ``GCP_USERNAME`` -- Google Cloud Print username
- ``GCP_PASSWORD` -- password
- ``GCP_PRINTER`` --  printer ID (optional, default: ``__google__docs``)

During the tests a PDF is printed. By default the Google Docs printer is used,
however it I recommend setting up a PDF printer as the
target.

Example::

    GCP_USERNAME=foo@example.com \
    GCP_PASSWORD=bar \
    GCP_PRINTER=0e506d12-dbe0-54d3-a43d-fd69d45ff2fc \
    tox


Change log
==========

0.2.0
=====

- Make `ClientLoginAuth` cache authentication token

0.1.0
=====

- Initial version
