import threading
import requests
from .sample import GetAuthTokens


class ClientLoginAuth(object):
    """
    Authenticates a request using Google's deprecated Client Login API.

    :param caching: cache the authentication token across requests

    When authentication token caching is enabled, the request will be retried
    once if the response status is 'Forbidden'. This handles expired
    authentication tokens.
    """
    def __init__(self, email, password, caching=True):
        self.email = email
        self.password = password
        self.caching = caching
        self.lock = threading.Lock()

    def __call__(self, r):
        r.headers['Authorization'] = 'GoogleLogin auth=%s' % self.token

        if self.caching:
            # Hook the response to retry if the auth token is stale
            def hook(response):
                if response.status_code == requests.codes.forbidden:
                    del self.token  # clear stale token
                    request = response.request
                    request.deregister_hook('response', hook)  # retry one time
                    request.send(anyway=True)
                    return request.response
                return response
            r.hooks['response'].insert(0, hook)
        return r

    @property
    def token(self):
        with self.lock:
            if not self.caching or not hasattr(self, "_token"):
                self._token = GetAuthTokens(self.email, self.password)["Auth"]
                return self._token
            return self._token

    @token.deleter
    def token(self):
        with self.lock:
            del self._token
