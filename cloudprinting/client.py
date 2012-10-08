from datetime import datetime
import json
import mimetypes
from os.path import basename
import requests


CLOUDPRINT_URL = "http://www.google.com/cloudprint"


def get_job(id, printer=None, **kwargs):
    """
    Returns the data for a single job.

    :param      id: print job ID
    :type       id: string
    :param printer: if known, the printer id
    :type  printer: string
    :returns: `dict` expressing a job, or `None`

    This is a convience method that uses `list_jobs`, as there is no "get job"
    API for Google Cloud Print.
    """
    jobs = list_jobs(printer=printer, **kwargs)
    for job in jobs:
        if job['id'] == id:
            return job


def delete_job(id, **kwargs):
    """
    Delete a print job.

    :param id: job ID
    :type  id: string
    """
    url = CLOUDPRINT_URL + "/deletejob"
    r = requests.post(url, data={"jobid": id}, **kwargs)
    return r.json if r.status_code == requests.codes.ok else r


def list_jobs(printer=None, **kwargs):
    """
    List print jobs.

    :param printer: filter by a printer id
    :type  printer: string
    :returns: `list` of `dict`, each `dict` expressing a job
    """
    params = {}
    if printer is not None:
        params["printerid"] = printer
    url = CLOUDPRINT_URL + "/jobs"
    r = requests.get(url, params=params, **kwargs)
    if r.status_code != requests.codes.ok:
        return r
    # At the time of writing, the `/jobs` API returns `Content-Type:
    # text/plain` header
    return (r.json if hasattr(r, "json") else json.loads(r.text))['jobs']


def submit_job(printer, content, title=None, capabilities=None, tags=None,
               **kwargs):
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
    :param         tags: job tags
    :type          tags: list

    See https://developers.google.com/cloud-print/docs/appInterfaces#submit for
    details.

    """
    # normalise *content* to bytes, and *name* to a string
    if isinstance(content, (list, tuple)):
        name = content[0]
        content = content[1].read()
    else:
        name = basename(content)
        with open(content, 'rb') as f:
            content = f.read()

    if title is None:
        title = '%s %s' % (datetime.now().strftime("%d/%m/%y %H:%M"), name)

    files = {"content": (name, content)}
    if capabilities is not None:
        files["capabilities"] = ("data.json",
                                 json.dumps({"capabilities": capabilities}))
    data = {"printerid": printer,
            "title": title,
            "contentType": mimetypes.guess_type(name)[0]}
    if tags:
        data['tag'] = tags

    url = CLOUDPRINT_URL + "/submit"
    r = requests.post(url, data=data, files=files, **kwargs)
    return r.json if r.status_code == requests.codes.ok else r
