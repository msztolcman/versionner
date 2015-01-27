versionner
==========

`versionner` helps manipulating version of the project.

Current stable version
----------------------

0.2.0

But why?
--------

You can change version manually. But:

* manual changes are prone to errors. And `versionner` guards the compliance
    with [Semantic Versioning](http://semver.org/).
* it's easier to write: `versionner up` instead of open editor, edit and
    save changes ;) 

Some examples
---------------------

Some examples:

    # prints current version info
    % versionner
    
    # increase minor by 1, set patch to 0
    versionner up
    
    # increase patch by 1
    versionner up --patch 
    
    # increase patch by 4
    versionner up --patch 4
     
    # just guess...
    versionner set --minor 3 --patch 2 --build asd3f
        
    # set version to 1.0.0
    versionner set 1.0.0

More
----

Everything is in help :) Just execute:

    versionner --help

Look at result:

    % versionner --help
    usage: versionner [-h] [--file FILE] [--version] {init,up,set} ...
    
    Manipulate version of project
    
    positional arguments:
      {init,up,set}
        init                Create new version file
        up                  Increase version
        set                 Set version to specified one
    
    optional arguments:
      -h, --help            show this help message and exit
      --file FILE, -f FILE  path to file where version is saved
      --version, -v         show program's version number and exit
      
So, there are three commands: `init`, `up` and `set`. We want to look at this:

    % versionner init --help
    usage: versionner init [-h] [value]
    
    positional arguments:
      value       Initial version
    
    optional arguments:
      -h, --help  show this help message and exit

    % versionner up --help
    usage: versionner up [-h] [--major | --minor | --patch] [value]
    
    positional arguments:
      value        Increase version by this value (default: 1)
    
    optional arguments:
      -h, --help   show this help message and exit
      --major, -j  increase major part of version
      --minor, -n  increase minor part of version (default)
      --patch, -p  increase patch part of version

    % versionner set --help
    usage: versionner set [-h] [--major MAJOR] [--minor MINOR] [--patch PATCH]
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

Installation
------------

`subst` should work on any platform where [Python](http://python.org) is available, it means Linux, Windows, MacOS X etc. 

To install, go to [GitHub releases](https://github.com/mysz/versionner/releases), download newest release, unpack and put somewhere in `PATH` (ie. `~/bin` or `/usr/local/bin`).

If You want to install newest unstable version, then just copy file to your PATH, for example:

    curl https://raw.github.com/mysz/subst/master/versionner.py > /usr/local/bin/versionner

or:

    wget https://raw.github.com/mysz/versionner/master/versionner.py -O /usr/local/bin/versionner

Voila!

Authors
-------

Marcin Sztolcman <marcin@urzenia.net>

Contact
-------

If you like or dislike this software, please do not hesitate to tell me about this me via email (marcin@urzenia.net).

If you find bug or have an idea to enhance this tool, please use GitHub's [issues](https://github.com/mysz/versionner/issues).

License
-------

The MIT License (MIT)

Copyright (c) 2015 Marcin Sztolcman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ChangeLog
---------

### v0.2.0

* in progress
