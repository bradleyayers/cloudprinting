from datetime import datetime
import mimetypes
from os.path import basename
import requests


CLOUDPRINT_URL = "http://www.google.com/cloudprint"


def list_jobs(printer=None, job=None, **kwargs):
    """
    List print jobs.

    :param printer: filter by a printer id
    :type  printer: string
    """
    params = {}
    if printer is not None:
        params["printerid"] = printer
    url = CLOUDPRINT_URL + "/jobs"
    return requests.get(url, params=params, **kwargs).json


def submit_job(printer, content, title=None, capabilities=None, **kwargs):
    """
    Submit a print job.

    :param      printer: the id of the printer to use
    :type       printer: string
    :param      content: what should be printer
    :type       content: ``(name, file-like)`` pair or path
    :param capabilities: capabilities for the printer
    :type  capabilities: list
    :param        title: title of the print job, should be unique to printer
    :type         title: string
    """
    if isinstance(content, (list, tuple)):
        name = content[0]
        data = content[1].read()
    else:
        name = basename(content)
        with open(content, 'rb') as f:
            data = f.read()

    # Make the title unique for each job, since the printer by default will
    # name the print job file the same as the title.
    if title is None:
        title = '%s - %s' % (datetime.now().isoformat(), name)

    files = {"content": (name, data)}
    if capabilities is not None:
        files["capabilities"] = ("data.json",
                                 json.dumps({"capabilities": capabilities}))
    data = {"printerid": printer,
            "title": title,
            "contentType": mimetypes.guess_type(name)[0]}
    url = CLOUDPRINT_URL + "/submit"
    return requests.post(url, data=data, files=files, **kwargs).json
