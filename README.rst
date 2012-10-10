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

Supports both Python 2 and 3:

- >= Python 2.6
- >= Python 3.2

Tests
=====

The test suite requires three environment variables:

- ``CP_CLIENT_ID`` -- application "client id" (Google API)
- ``CP_CLIENT_SECRET`` -- application "client secret" (Google API)
- ``CP_REFRESH_TOKEN`` -- refresh token for an authorised Google Account
- ``CP_PRINTER_ID`` -- printer ID (optional, default: ``__google__docs``)

During the tests a PDF is printed. By default the Google Docs printer is used,
however it is more forgiving than typical printers, so I don't recommend using
it.

Example::

    CP_CLIENT_ID=1234567890.apps.googleusercontent.com \
    GCP_PASSWORD=asdfghjklzxcvbnmqwertyuiop \
    GCP_PRINTER=0e50ed12-dbe0-54d3-a4bd-fdf9d45ff2fc \
    tox


Command line interface
======================

The module can be used from the command line via::

    python -m cloudprinting ...

See ``--help`` for details.


Change log
==========

0.3.0
=====

- Add ``OAuth2`` authentication
- ``ClientLoginAuth`` only available on Python 2.x
- By default send ``capabilities`` (even if it's ``[{}]``). This fixes some
  issues
- Print jobs now default to using the filename as the title (no more automatic
  inclusion of datetime)
- Added a crude command line interface

0.2.0
=====

- Make ``ClientLoginAuth`` cache authentication token

0.1.0
=====

- Initial version
