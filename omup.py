#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Console based omploader uploader
#
# No CURL here because it would be too damn boring
# * currently supports python >= 3 *

import sys
import argparse
import http.client
import socket
import mimetypes
import re
import os
from urllib.parse import quote

OMP_URL = "ompldr.org"
OMP_UP = "/upload"

def cmd_parse():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Upload files to omploader.org from the command line.")

    parser.add_argument("-p", "--prompt", action="store_true", default=False,
        help="prompt before upload")

    parser.add_argument("-s", "--short", action="store_true", default=False,
        help="show a shorter file url (strips filename)")

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
    content.append("--{0}".format(boundary))
    content.append("Content-Type: {0}".format(mime))
    content.append(("Content-Disposition: form-data; "
                    "name=\"file1\"; filename=\"{0}\"".format(filename)))
    content.append("")
    content.append(data)
    content.append("--{0}--".format(boundary))

    body = crlf.join(
            c.encode('latin-1') if type(c) is str else c
            for c in content)

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

    try:
        conn = http.client.HTTPConnection(OMP_URL)
        conn.request('POST', OMP_UP, body, {'Content-Type': header})
    except socket.error as e:
        print("Error: cannot connect to {0}".format(OMP_URL))
        sys.exit(1)

    response = conn.getresponse()
    if response.status is not http.client.OK:
        print("HTTP returned: {0}. Reason: {1}".format(response.status,
                                                       response.reason))
        sys.exit(1)

    return response.read().decode('UTF-8')


def parse_response(res):
    """
    parse response page and return the interesting parts:
        * bbc code
        * short file uri
        * full file uri

    we cannot rely too much on the html response so we first
    filter the BBC code string
    """
    # extract bbc code from response
    BBC_RE = re.compile(r'\[url\=.*\[/url\]')
    try:
        bbc = BBC_RE.search(res).group()
    except AttributeError:
        print("Cannot parse response output.")
        sys.exit(1)

    # extract short file uri from bbc code
    SHORT_RE = re.compile(r'^\[url\=(?P<short>.*?)(\].*\[/url])')
    try:
        short_uri = SHORT_RE.search(bbc).group('short')
    except AttributeError:
        print("Cannot parse response output.")
        sys.exit(1)

    # use file uri to extract the href link from response
    # we need to get the href because omploader truncates
    # long names from the <a> contents
    file_id = short_uri.split('/')[-1].strip('/')
    HREF_RE = re.compile('href="(?P<full>.*/{0}/.*?)"'.format(file_id))

    try:
        href = HREF_RE.search(res).group('full')
    except AttributeError:
        print("Cannot parse response output.")
        sys.exit(1)

    full_uri = "http://{0}{1}".format(OMP_URL, quote(href))
    return bbc, short_uri, full_uri


if __name__ == '__main__':
    args = cmd_parse()

    if args.prompt is True:
        answer = input(("Upload {!r} to omploader? "
                        "[y/n] > ".format(args.file[0])))
        if answer.lower() not in ('y', 'yes'):
            sys.exit(0)

    response = upload(args.file[0])

    bbc, file_uri, full_uri = parse_response(response)

    # print urls
    if args.short is True:
        print(file_uri)
    else:
        print(full_uri)

    if args.bbc is True:
        print("BBC code: {0}".format(bbc))

    sys.exit(0)
