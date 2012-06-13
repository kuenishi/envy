#!/usr/bin/env python

import sys, os
import json
import subprocess

'''
envy_install http://ham.egg.com/spam-0.1.1.tar.gz
->
 wget http://ham.egg.com/spam-0.1.1.tar.gz -P ENVY_HOME/src
 cd ENVY_HOME/src 
 tar xzf spam-0.1.1.tar.gz
 cd spam-0.1.1
 configure.py
 make
 make install


envy_install spam
-> if reference address exists ->
 envy_install http://ham.egg.com/spam-....

envy_install git://github.com/...
->
'''

def get_basedir(relative = None):
    base = os.environ['ENVY_HOME']
    if relative is None: return base
    else:                return '%s/%s' % (base, relative)

def help():
    print('help: ... ')

def fetch(url):
    srcdir = get_basedir('local/src')
    try: os.mkdir(srcdir)
    except: pass
    subprocess.call(['wget', url, '--directory-prefix=%s'%srcdir])
    filename = url.split('/')[-1]
    return filename

def deflate(srcdir, tarball):
    subprocess.call(['tar', 'xzf', '%s/%s' % (srcdir, tarball),
                     '-C', srcdir])
    if tarball[-6:] == 'tar.gz':
        basename = tarball[0:-7]
        return '%s/%s' % (srcdir, basename)
    elif tarball[-4:] == '.tgz':
        basename = tarball[0:-5]
        return '%s/%s' % (srcdir, basename)

def build(srcdir):
    os.chdir(srcdir)
    # run configure.py
    subprocess.call(['configure.py'])
    # run make && make install
    subprocess.call(['make'])
    return subprocess.call(['make', 'install'])

def install(name):
    print('installing %s' % name)
    resource_file = '%s/local/share/packages.json' % os.environ['ENVY_HOME']
    #print(resource_file)
    v = json.load(open(resource_file))
    url = v[name]
    print(url)
    tarball = fetch(url)
    srcdir = get_basedir('local/src')
    srcdir  = deflate(srcdir, tarball)
    return build(srcdir)

if __name__ == '__main__':
    cmd = None
    if len(sys.argv) == 1:
        cmd = 'help'
    else:
        cmd = sys.argv[1]

    if cmd == 'help':
        help()
    elif cmd == 'install' and len(sys.argv) > 2:
        # read local/share/envy_resource.json
        # look for req
        install(sys.argv[2])

    else:
        print('error, assert!')
