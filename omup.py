#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Console based omploader uploader
#
# No CURL here because it would be too damn boring
# * currently supports python >= 3 *

import sys
import argparse
import http.client
import mimetypes
import re
import os

OMP_URL = "ompldr.org"
OMP_UP = "/upload"

def cmd_parse():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Upload files to omploader.org from the command line.")

    parser.add_argument("-p", "--prompt", action="store_true", default=False,
        help="Prompt before upload.")

    parser.add_argument("-b", "--bbc", action="store_true", default=False,
        help="show BBC code")

    parser.add_argument("file", nargs=1, help="File to upload.")

    return parser.parse_args()


def multipart_encode(filename, data):
    """format multipart message, return body + header"""
    boundary = "----------B0und@ry!"
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    crlf = '\r\n'.encode('latin-1')

    header = "multipart/form-data; boundary={0}".format(boundary)

    content = []
    content.append("--{0}".format(boundary).encode('latin-1'))
    content.append("Content-Type: {0}".format(mime).encode('latin-1'))
    content.append("Content-Disposition: form-data; name=\"file1\"; filename=\"{0}\"".format(filename).encode('latin-1'))
    content.append("".encode('latin-1'))
    content.append(data)
    content.append("--{0}--".format(boundary).encode('latin-1'))

    body = crlf.join(content)

    return header, body


def upload(filename):
    """ust http client module to upload file"""
    try:
        with open(filename, 'rb') as fp:
            data = fp.read()
    except:
        print("Error reading file {0}".format(filename))
        sys.exit(1)

    header, body = multipart_encode(os.path.basename(filename), data)

    # TODO add try block here
    conn = http.client.HTTPConnection(OMP_URL)
    conn.request('POST', OMP_UP, body, {'Content-Type': header})
    response = conn.getresponse()

    if response.status is not http.client.OK:
        print("HTTP returned: {0}. Reason: {1}".format(response.status,
                                                       response.reason))
        sys.exit(1)

    return response.read().decode('UTF-8')


def parse_response(res):
    """parse response page and return bbc code and file uri"""
    # extract bbc code from response
    BBC_RE = re.compile(r'\[url\=.*\[/url\]')
    try:
        bbc = BBC_RE.search(res).group()
    except AttributeError:
        bbc = ''

    # extract file uri from bbc code
    URI_RE = re.compile(r'^\[url\=(?P<uri>.*?)(\].*\[/url])')
    try:
        file_uri = URI_RE.search(bbc).group('uri')
    except AttributeError:
        file_uri = ''

    return bbc, file_uri


if __name__ == '__main__':
    args = cmd_parse()

    if args.prompt is True:
        answer = input("Upload {!r} to omploader? [y/n] > ".format(args.file[0]))
        if answer.lower() not in ('y', 'yes'):
            sys.exit(0)

    response = upload(args.file[0])

    bbc, file_uri = parse_response(response)

    # print urls
    print("{0}/{1}".format(file_uri, os.path.basename(args.file[0])))
    if args.bbc is True:
        print("BBC code: {0}".format(bbc))

    sys.exit(0)
