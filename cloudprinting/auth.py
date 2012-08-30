from .sample import GetAuthTokens


class ClientLoginAuth(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __call__(self, r):
        tokens = GetAuthTokens(self.email, self.password)
        r.headers['Authorization'] = 'GoogleLogin auth=%s' % tokens['Auth']
        return r
