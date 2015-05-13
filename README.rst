versionner
==========

``versionner`` helps manipulating version of the project.

With one command you can update all required files and git with new
version.

Current stable version
----------------------

1.0.0

Features
--------

-  ``versionner`` guards the compliance with `Semantic
   Versioning <http://semver.org/>`__
-  manual changes are error-prone, ``versionner`` is error proof
-  it's easier to write: ``versionner up`` instead of open editor, edit
   and save changes ;)
-  ``versionner`` updates also project files (like README or sth)
-  and create vcs (only git currently) tag if requested
-  it's `very easy to install <#installation>`__
-  and it's all in one command...

Some examples
-------------

Some examples:

::

    # initialize new file with version 0.1.0
    % ver init

    # initialize new file with version 1.0.0
    % ver init 1.0.0

    # prints current version info
    % ver

    # increase minor by 1, set patch to 0
    ver up

    # increase patch by 1
    ver up --patch

    # create git tag
    ver tag

    # increase patch by 4
    ver up --patch 4
     
    # just guess...
    ver set --minor 3 --patch 2 --build asd3f
        
    # set version to 1.0.0
    ver set 1.0.0

    # create signed VCS tag
    ver tag --vcs-param -s

More
----

Everything is in help :) Just execute:

::

    ver --help

Look at result:

::

    % ver --help
    usage: ver [-h] [--file VERSION_FILE] [--version] [--date-format DATE_FORMAT]
               [--verbose]
               {init,up,set,tag} ...

    Helps manipulating version of the project

    positional arguments:
      {init,up,set,tag}
        init                Create new version file
        up                  Increase version
        set                 Set version to specified one
        tag                 Create VCS tag with current version

    optional arguments:
      -h, --help            show this help message and exit
      --file VERSION_FILE, -f VERSION_FILE
                            path to file where version is saved
      --version, -v         show program's version number and exit
      --date-format DATE_FORMAT
                            Date format used in project files
      --verbose             Be more verbose if it's possible

So, there are three commands: ``init``, ``up``, ``set`` and ``tag``. We
want to look at this:

::

    % ver init --help
    usage: ver init [-h] [value]

    positional arguments:
      value       Initial version

    optional arguments:
      -h, --help  show this help message and exit

    % ver up --help
    usage: ver up [-h] [--major | --minor | --patch] [value]

    positional arguments:
      value        Increase version by this value (default: 1)

    optional arguments:
      -h, --help   show this help message and exit
      --major, -j  increase major part of version
      --minor, -n  increase minor part of version (project default)
      --patch, -p  increase patch part of version

    % ver set --help
    usage: ver set [-h] [--major MAJOR] [--minor MINOR] [--patch PATCH]
                          [--prerelease PRERELEASE] [--build BUILD]
                          [value]

    positional arguments:
      value                 set version to this value

    optional arguments:
      -h, --help            show this help message and exit
      --major MAJOR, -j MAJOR
                            set major part of version to MAJOR
      --minor MINOR, -n MINOR
                            set minor part of version to MINOR
      --patch PATCH, -p PATCH
                            set patch part of version to PATCH
      --prerelease PRERELEASE, -r PRERELEASE
                            set prerelease part of version to PRERELEASE
      --build BUILD, -b BUILD
                            set build part of version to BUILD
                            
    % ver tag --help
    usage: ver tag [-h] [--vcs-engine VCS_ENGINE] [--vcs-tag-param VCS_TAG_PARAMS]

    optional arguments:
      -h, --help            show this help message and exit
      --vcs-engine VCS_ENGINE
                            Select VCS engine used for tagging (only git is
                            supported currently)
      --vcs-tag-param VCS_TAG_PARAMS
                            Additional params to "tag" command

Configuration
-------------

Configuration is both: user-wide and project-wide.

User-wide is stored in ``~/.versionner.rc`` file, and project-wide is
stored in ``<PROJECT_ROOT>/.versionner.rc``. Projects' configuration is
superior to user-wide.

It allows you also to modify other files specified in configuration.

``.versionner.rc`` is INI file in format:

::

    [versionner]
    file = ./VERSION
    date_format = %Y-%m-%d
    up_part = patch
    ;default_init_version = 1.0.0

    [vcs]
    engine = git
    ;tag_params =
    ;  -f
    ;  --local-user=some-key-id

    [file:some/folder/some_file.py]
    enabled = true
    search = ^\s*__version__\s*=.*$
    replace = __version__ = '%(version)s'
    date_format = %Y-%m-%d
    match = line
    search_flags = 
    encoding = utf-8

Data in '[project]' section are default data for whole project.

Data in '[file:some/folder/some\_file.py]' section are for single file
from project. You can specify here that file 'some/folder/some\_file.py'
have version string (key: ``enabled``), has encoding ``encoding`` and we
have to search for it (``search``) and replace it with value of
``replace``. If ``match`` is 'line', then ``search`` is matched line by
line, and for 'file' whole file is read into memory and matched against
``search``.

Installation
------------

``versionner`` should work on any platform where
`Python <http://python.org>`__ is available, it means Linux, Windows,
MacOS X etc.

Simplest way is to use Python's built-in package system:

::

    pip install versionner

Voila!

Authors
-------

Marcin Sztolcman marcin@urzenia.net

Contact
-------

If you like or dislike this software, please do not hesitate to tell me
about this me via email (marcin@urzenia.net).

If you find bug or have an idea to enhance this tool, please use
GitHub's `issues <https://github.com/mysz/versionner/issues>`__.

License
-------

The MIT License (MIT)

Copyright (c) 2015 Marcin Sztolcman

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ChangeLog
---------

v1.0.0
~~~~~~

-  added ``tag`` command (creates vcs (only git currently) tag)
-  versionner's app now is called 'ver', 'versionner' is deprecated
-  ability to set default value for ``init`` command in
   ``.versionner.rc``

v0.4.3
~~~~~~

-  do not fail when VERSION file is missing
-  automatically use python3 (shebang)
-  updated program description in help

v0.4.2
~~~~~~

-  published on pypi

v0.4.1
~~~~~~

-  copy file permissions to new one when updating project files

v0.4.0
~~~~~~

-  first public version
