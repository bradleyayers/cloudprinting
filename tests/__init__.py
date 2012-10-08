# coding: utf-8
from attest import assert_hook, Tests
from cloudprinting import (ClientLoginAuth, delete_job, get_job, list_jobs,
                           submit_job)
from os import environ
from os.path import dirname, join
import requests
from time import sleep


GCP_USERNAME = environ['GCP_USERNAME']
GCP_PASSWORD = environ['GCP_PASSWORD']
GCP_PRINTER = environ.get('GCP_PRINTER', '__google__docs')
PDF = join(dirname(__file__), "test.pdf")

suite = Tests()


@suite.test
def print_pdf():
    auth = ClientLoginAuth(GCP_USERNAME, GCP_PASSWORD)
    response = submit_job(GCP_PRINTER, PDF, auth=auth)
    assert response['success'] == True

    job = response['job']
    timeout = 0
    delay = 5
    attempts = range(timeout / delay + 1)

    try:
        for _ in attempts:
            sleep(delay)
            latest = get_job(id=job['id'], auth=auth)
            if latest['status'] == 'QUEUED':
                continue
            assert latest['status'] == 'DONE'
        else:
            assert False, "Job never changed from 'QUEUED'"
    finally:
        assert delete_job(job['id'], auth=auth)['success'] == True


@suite.test
def response_is_returned_on_remote_failures():
    r = submit_job("bogus", PDF)
    assert isinstance(r, requests.Response)

    r = delete_job("bogus")
    assert isinstance(r, requests.Response)

    r = list_jobs()
    assert isinstance(r, requests.Response)
