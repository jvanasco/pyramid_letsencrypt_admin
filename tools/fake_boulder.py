"""
fake_boulder

purpose:
    this spins up a server with some simple routes for testing client development
    this crafts endpoints for success


usage:
    0. edit environment.ini and set the following:
        certificate_authority = http://127.0.0.1:7202
        certificate_authority_testing = True
    1. make a folder "fake_boulder_cert/" and place a "cert.crt" in there (der, not pem)
        this folder is ignored by the `.gitignore` file
    2. python fake_boulder.py
"""


from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

import datetime
import base64
import binascii
import textwrap

CERTIFICATE = open('fake_boulder_cert/cert.crt').read()


# ==============================================================================


def directory(request):
    return Response(body='''{"123123123": "https://community.letsencrypt.org/t/adding-random-entries-to-the-directory/33417","key-change": "http://127.0.0.1:7202/acme/key-change","meta": {"caaIdentities": ["letsencrypt.org"],"terms-of-service": "https://letsencrypt.org/documents/LE-SA-v1.2-November-15-2017.pdf","website": "https://letsencrypt.org/docs/staging-environment/"},"new-authz": "http://127.0.0.1:7202/acme/new-authz","new-cert": "http://127.0.0.1:7202/acme/new-cert","new-reg": "http://127.0.0.1:7202/acme/new-reg","revoke-cert": "http://127.0.0.1:7202/acme/revoke-cert"}''',
        status_code=200,
        headers = {'Replay-Nonce': '123123_123123_',
                   'Content-Type': 'application/json',
                   },
    )


def acme_newauthz(request):
    """
    https://tools.ietf.org/html/draft-ietf-acme-acme-03#section-6.4
        6.4.  Identifier Authorization

           GET /acme/authz/1234 HTTP/1.1
             Host: example.com

             HTTP/1.1 200 OK
             Content-Type: application/json
             Link: <https://example.com/acme/some-directory>;rel="directory"

             {
               "status": "pending",

               "identifier": {
                 "type": "dns",
                 "value": "example.org"
               },

               "challenges": [
                 {
                   "type": "http-01",
                   "uri": "https://example.com/authz/asdf/0",
                   "token": "IlirfxKKXAsHtmzK29Pj8A"
                 },
                 {
                   "type": "dns-01",
                   "uri": "https://example.com/authz/asdf/1",
                   "token": "DGyRejmCefe7v4NfDGDKfA"
                 }
               ],

               "combinations": [[0], [1]]
             }
    """
    return Response(body='''{"challenges": [{"type": "http-01", "token": "123123123-12312", "uri": "http://127.0.0.1:7202/acme/CHALLENGE"}]}''', 
                    status_code=201,
                    )


def acme_CHALLENGE(request):
    """
    https://tools.ietf.org/html/draft-ietf-acme-acme-03#section-6.4.1
        6.4.1.  Responding to Challenges

           GET /acme/authz/asdf HTTP/1.1
           Host: example.com

           HTTP/1.1 200 OK

           {
             "status": "valid",
             "expires": "2015-03-01T14:09:00Z",

             "identifier": {
               "type": "dns",
               "value": "example.org"
             },

             "challenges": [
               {
                 "type": "http-01"
                 "status": "valid",
                 "validated": "2014-12-01T12:05:00Z",
                 "token": "IlirfxKKXAsHtmzK29Pj8A",
                 "keyAuthorization": "IlirfxKKXA...vb29HhjjLPSggwiE"
               }
             ]
           }

    """
    return Response(body='''{"status": "valid"}''',
                    status_code=202,
                    )


def acme_newcert(request):
    """
    https://tools.ietf.org/html/draft-ietf-acme-acme-03#section-6.3.1
        6.3.1.  Downloading the Certificate

       GET /acme/cert/asdf HTTP/1.1
       Host: example.com
       Accept: application/pkix-cert

       HTTP/1.1 200 OK
       Content-Type: application/pkix-cert
       Link: <https://example.com/acme/ca-cert>;rel="up";title="issuer"
       Link: <https://example.com/acme/revoke-cert>;rel="revoke"
       Link: <https://example.com/acme/app/asdf>;rel="author"
       Link: <https://example.com/acme/sct/asdf>;rel="ct-sct"
       Link: <https://example.com/acme/some-directory>;rel="directory"

       [DER-encoded certificate]
    """
    return Response(body=CERTIFICATE,
                    status_code=201,
                    headers = {'Link': '<https://acme-v01.api.letsencrypt.org/acme/issuer-cert>;rel="up";title="issuer"',
                               'Date': datetime.datetime.utcnow().isoformat(),
                               'Expires': (datetime.datetime.utcnow() + datetime.timedelta(days=90)).isoformat(),
                               'Content-Type': 'application/pkix-cert',
                               },
                    )


if __name__ == '__main__':
    print "running test server..."
    config = Configurator()
    config.include('pyramid_debugtoolbar')

    config.add_route('/directory', '/directory')
    config.add_view(directory, route_name='/directory')

    config.add_route('/acme/new-authz', '/acme/new-authz')
    config.add_view(acme_newauthz, route_name='/acme/new-authz')

    config.add_route('/acme/CHALLENGE', '/acme/CHALLENGE')
    config.add_view(acme_CHALLENGE, route_name='/acme/CHALLENGE')

    config.add_route('/acme/new-cert', '/acme/new-cert')
    config.add_view(acme_newcert, route_name='/acme/new-cert')


    config.add_request_method(lambda request: request.environ['HTTP_HOST'].split(':')[0], 'active_domain_name', reify=True)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 7202, app)
    server.serve_forever()