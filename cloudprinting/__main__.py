# coding: utf-8
from . import client
from .auth import OAuth2
from argparse import ArgumentParser, FileType
from pprint import pprint
import requests
import sys


def do_authorise(args):
    """
    Provide a CLI interface to OAuth2 authorise an app for Google Cloud Print.
    """
    flow = OAuth2.authorise_device(args.client_id, args.client_secret)
    (url, code) = flow.next()
    print "Browse to *URL* and enter *code*:"
    print
    print "   URL:", url
    print "  code:", code
    print

    while raw_input("Authorisation complete? [y/N] ") != "y":
        continue

    print "Retrieving OAuth2 tokens..."
    tokens = flow.next()

    print
    print "Tokens:"
    pprint(tokens, indent=2)
    print


def do_refresh(args):
    oauth2 = OAuth2(access_token=None,
                    token_type=None,
                    refresh_token=args.refresh_token,
                    client_id=args.client_id,
                    client_secret=args.client_secret)
    oauth2.refresh()
    print "Tokens:"
    print
    print '  token_type:', oauth2.token_type
    print '  access_token:', oauth2.access_token
    print


def do_print(args):
    oauth2 = OAuth2(access_token=args.access_token,
                    token_type=args.token_type)
    r = client.submit_job(args.printer_id, args.path,
                          tags=args.tags.split(','), auth=oauth2)
    sys.exit(not diagnose(r, args.verbose))


def do_list_printers(args):
    oauth2 = OAuth2(access_token=args.access_token,
                    token_type=args.token_type)
    r = client.list_printers(auth=oauth2)
    sys.exit(not diagnose(r, True))


# -----------------------------------------------------------------------------


def diagnose(r, verbose=False):
    if isinstance(r, requests.Response):
        print "Something went wrong:"
        print
        print r.content
        return False
    else:
        if 'message' in r:
            print r['message']
        if verbose:
            pprint(r)
        return r.get('success', True)


# -----------------------------------------------------------------------------


parser = ArgumentParser(prog="python -m cloudprinting")
parser.add_argument(
    '-v', '--verbose',
    action="store_true",
    dest="verbose")

# ----

parser__ = parser.add_subparsers()

# ----

list_printers_ = parser__.add_parser('list-printers')
list_printers_.add_argument(
    '--access-token',
    required=True,
    metavar='<token>',
    dest='access_token')
list_printers_.add_argument(
    '--token-type',
    default='Bearer',
    metavar='<type>',
    dest='token_type')
list_printers_.set_defaults(main=do_list_printers)

# ----

print_ = parser__.add_parser('print')
print_.add_argument(
    '--access-token',
    required=True,
    metavar='<token>',
    dest='access_token')
print_.add_argument(
    '--token-type',
    default='Bearer',
    metavar='<type>',
    dest='token_type')
print_.add_argument(
    '--printer-id',
    required=True,
    metavar='<id>',
    dest='printer_id')
print_.add_argument(
    '--tags',
    dest="tags",
    default='',
    help="comma separated tags")
print_.add_argument(
    'path',
    metavar='<path>')
print_.set_defaults(main=do_print)

# ----

oauth2 = parser__.add_parser('oauth2')
oauth2.add_argument(
    '--client-id',
    metavar='<id>',
    required=True,
    dest='client_id',
    help='application "client id" (Google API)')
oauth2.add_argument(
    '--client-secret',
    metavar='<secret>',
    required=True,
    dest='client_secret',
    help='application "client secret" (Google API)')

# ----

oauth2__ = oauth2.add_subparsers()

# ----

oauth2__authorise = oauth2__.add_parser('authorise')
oauth2__authorise.set_defaults(main=do_authorise)

# ----

oauth2__refresh = oauth2__.add_parser('refresh')
oauth2__refresh.add_argument(
    '--refresh-token',
    required=True,
    metavar='<token>',
    dest='refresh_token')
oauth2__refresh.set_defaults(main=do_refresh)

# ----

args = parser.parse_args()
args.main(args)
