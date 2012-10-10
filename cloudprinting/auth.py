# coding: utf-8
import threading
from time import sleep, time
import requests


try:
    from .sample import GetAuthTokens
except (ImportError, SyntaxError):
    pass
else:
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


class OAuth2(object):
    """
    OAuth2 authentication for Google Cloud Print.

    The OAuth2 can be instantiated in two ways.

    - Provide existing valid *access_token* and *token_type*; or/and
    - Provide *refresh_token*, *client_id*, *client_secret*

    It's possible to only provide the former arguments, which will mean that
    once the token expires, the authentication will no longer work.

    Alternatively the later arguments can be provided, which allows then
    authentication tokens to be refreshed when they expire. In this scenario,
    it's not necessary to provide the former arguments.
    """
    token_endpoint = "https://accounts.google.com/o/oauth2/token"
    device_code_endpoint = "https://accounts.google.com/o/oauth2/device/code"
    scope = "https://www.googleapis.com/auth/cloudprint"

    def __init__(self, access_token=None, token_type=None, expires_in=None,
                 refresh_token=None, client_id=None, client_secret=None):
        if not ((access_token and token_type)
                or (refresh_token and client_id and client_secret)):
            raise TypeError("Invalid argument combination. Provide either "
                "<access_token, token_type> or "
                "<refresh_token, client_id, client_secret>.")

        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        # easier to work with a definite time in future, than a delta
        if expires_in is not None:
            self.expires_at = time() + expires_in
        else:
            self.expires_at = None
        self.lock = threading.RLock()

    def __call__(self, r):
        with self.lock:
            if self.expired:
                self.refresh()
            r.headers['Authorization'] = "%s %s" % (self.token_type,
                                                    self.access_token)

            if self.client_id and self.client_secret and self.refresh_token:
                # enable auto refreshing of token
                def hook(response):
                    if response.status_code == requests.codes.forbidden:
                        self.expires_at = 0  # expire token
                        self.refresh()
                        request = response.request
                        request.deregister_hook('response', hook)  # retry one time
                        request.send(anyway=True)
                        return request.response
                    return response
                r.hooks['response'].insert(0, hook)
            return r

    def refresh(self):
        """
        Refresh the ``access_code`` -- this is useful when it expires.
        """
        with self.lock:
            if self.expired:
                return
        r = requests.post(self.token_endpoint, data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"}).json
        self.access_token = r['access_token']
        self.expires_at = r['expires_in'] + time()
        self.token_type = r['token_type']

    @property
    def expired(self):
        if self.expires_at is None:
            # assume the worst
            return True
        return time() < self.expires_at

    @classmethod
    def authorise_device(cls, client_id, client_secret):
        """
        A generator that manages the OAuth2 exchange to authorise an app to access
        Google Cloud Print on behalf of a Google Account.

        :param     client_id: "client ID" of application (Google API)
        :type      client_id: string
        :param client_secret: "client secret"
        :type  client_secret: string
        :raises: RuntimeError if verification URL expires

        This uses Google's "OAuth 2.0 for Devices" API.

        Example::

            >>> flow = OAuth2.authorise_device("abcdefg", "hijklmno")
            >>> (url, code) = flow.next()

            # ... Instruct the user to goto *url* and enter *code* ...

            >>> tokens = flow.next()
            >>> tokens
            {
              "access_token" : "ya29.AHES6ZSuY8f6WFLswSv0HELP2J4cCvFSj-8GiZM0Pr6cgXU",
              "token_type" : "Bearer",
              "expires_in" : 3600,
              "refresh_token" : "1/551G1yXUqgkDGnkfFk6ZbjMLMDIMxo3JFc8lY8CAR-Q"
            }

        """
        r = requests.post(cls.device_code_endpoint, data={
                "client_id": client_id,
                "scope": cls.scope}).json
        yield (r['verification_url'], r['user_code'])

        previous = 0
        interval = r['interval']
        expires_at = time() + r['expires_in']
        device_code = r['device_code']

        while True:
            now = time()
            if now > expires_at:
                raise RuntimeError("URL expired prior to user verification.")
            # honor rate limit
            sleep(max(interval - (now - previous), 0))
            previous = now

            r = requests.post(cls.token_endpoint, data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": device_code,
                    "grant_type": "http://oauth.net/grant_type/device/1.0",
                }).json

            if "error" in r:
                # Either we're polling too fast, or the user hasn't accepted yet.
                continue

            yield r
            break
