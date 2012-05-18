omup
====

About
-----------
Omup is a simple omploader uploader written in python. It does not depend on PycURL or any other external library. Currently supports Python 3 only.

Dependenies
-----------

* python >= 3

Command line parameters
-----------------------

###Synopsis

omup.py [-h] [-p] [-s] [-b] file

###Parameters
```
positional arguments:
  file          file to upload

optional arguments:
  -h, --help    show help message and exit
  -p, --prompt  prompt before upload
  -s, --short   show a shorter file url (strips filename)
  -b, --bbc     show BBC code

```

Return data
-----------
Omup returns by default the full url of the uploaded file so you can easily get it with `wget`.

e.g.:
`$ omup.py /tmp/foo.png`

returns `http://ompldr.org/vSoMeId/foo.png` while if the `-s` parameter is supplied, returns a shorter version like `http://ompldr.org/vSoMeId`.

License
-------

This program is free software; you can redistribute it and/or modify it under the terms of
the GNU General Public License as published by the Free Software Foundation version 3 of the License.

A copy of theGNU General Public License can be found in [GNU Licence Page](http://www.gnu.org/licenses/gpl.html)

