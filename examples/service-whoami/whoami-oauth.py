"""An example service authenticating with the Hub.

This example service serves `/services/whoami/`,
authenticated with the Hub,
showing the user their own info.
"""
from getpass import getuser
import json
import os
from urllib.parse import urlparse

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import RequestHandler, Application, authenticated

from jupyterhub.services.auth import HubOAuthenticated, HubOAuthCallbackHandler
from jupyterhub.utils import url_path_join

class WhoAmIHandler(HubOAuthenticated, RequestHandler):
    # hub_users is a set of users who are allowed to access the service
    # `getuser()` here means only the user who started the service
    # can access the service:
    hub_users = {getuser()}

    @authenticated
    def get(self):
        user_model = self.get_current_user()
        self.set_header('content-type', 'application/json')
        self.write(json.dumps(user_model, indent=1, sort_keys=True))

def main():
    app = Application([
        (os.environ['JUPYTERHUB_SERVICE_PREFIX'], WhoAmIHandler),
        (url_path_join(os.environ['JUPYTERHUB_SERVICE_PREFIX'], 'oauth_callback'), HubOAuthCallbackHandler),
        (r'.*', WhoAmIHandler),
    ], cookie_secret=os.urandom(32))
    
    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, url.hostname)

    IOLoop.current().start()

if __name__ == '__main__':
    main()
