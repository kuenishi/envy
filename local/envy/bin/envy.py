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

class Fetcher:
    def __init__(self, url, destdir, name = ''):
        self.url = url
        self.destdir = destdir
        self.name = name

    def fetch(self):
        if self.url[:7]   == 'http://': return self.fetch_http()
        if self.url[:8]   == 'https://': return self.fetch_http()
        elif self.url[:6] == 'git://' : return self.fetch_git()
        elif self.url[:5] == 'hg://'  : return self.fetch_hg()
        else: return self.fetch_local()

    def fetch_http(self):
        subprocess.call(['wget', self.url, '--directory-prefix=%s'%self.destdir])
        filename = self.url.split('/')[-1]
        return self.deflate(filename)

    def deflate(self,tarball):
        subprocess.call(['tar', 'xzf', '%s/%s' % (self.destdir, tarball),
                         '-C', self.destdir])
        if tarball[-6:] == 'tar.gz':
            basename = tarball[0:-7]
            return '%s/%s' % (self.destdir, basename)
        elif tarball[-4:] == '.tgz':
            basename = tarball[0:-4]
            return '%s/%s' % (self.destdir, basename)
        # FIXME: .bz2 case, .zip case

    def fetch_git(self):
        curdir = os.getcwd()
        os.chdir(self.destdir)
        subprocess.call(['git', 'clone', self.url])
        basename = self.url.split('/')[-1][:-4]
        srcdir = '%s/%s' % (self.destdir, basename)
        os.chdir(curdir)
        return srcdir

    def fetch_hg(self):
        curdir = os.getcwd()
        os.chdir(self.destdir)
        url = 'http%s' % self.url[2:]
        subprocess.call(['hg', 'clone', url, self.name])
        basename = self.name
        if self.name == '':
            basename = self.url.split('/')[-1]
        srcdir = '%s/%s' % (self.destdir, basename)
        os.chdir(curdir)
        return srcdir

def fetch(url, name = ''):
    srcdir = get_basedir('local/src')
    try: os.mkdir(srcdir)
    except: pass
    f = Fetcher(url, srcdir, name)
    return f.fetch()

def build_and_install(srcdir):
    curdir = os.getcwd()
    os.chdir(srcdir)
    print(srcdir)
    prefix = get_basedir('local')
    # FIXME: find one of configure, wscript, setup.py and try 
    try:
        os.stat('configure')
        subprocess.check_call(['./configure', '--prefix=%s'%prefix])
        # run make && make install
        subprocess.check_call(['make'])
        subprocess.check_call(['make', 'install'])
        return os.chdir(curdir)
    except: pass
    try:
        os.stat('wscript')
        subprocess.check_call(['./waf', '--prefix=%s'%prefix])
        # run make && make install
        subprocess.check_call(['./waf'])
        subprocess.check_call(['./waf', 'install'])
        return os.chdir(curdir)
    except: pass
    try:
        os.stat('setup.py')
        # run make && make install
        subprocess.check_call(['python', 'setup.py', 'install', '--prefix=%s'%prefix])
        return os.chdir(curdir)
    except: pass
    print("Failed on build/installing %s. Try yourself." % srcdir )
    exit(-1)

def install(name):
    print('installing %s' % name)
    resource_file = '%s/local/envy/packages.json' % os.environ['ENVY_HOME']
    #print(resource_file)
    v = json.load(open(resource_file))
    url = v.get(name)
    package_name = ''
    if url is None: url = name
    # elif type(url) == type({}):
    else: package_name = name
    # FIXME: if there's tarball or git repository existing , do not fetch again
    path = fetch(url, name)
    return build_and_install(path)


'''
no upgrade, update, uninstall command
TODO: dependency description and resolution ? is it too much?
'''
if __name__ == '__main__':
    cmd = None
    if len(sys.argv) == 1:
        cmd = 'help'
    else:
        cmd = sys.argv[1]

    if cmd == 'help':
        help()
    elif cmd == 'install' and len(sys.argv) > 2:
        # read local/share/envy_resource.json and find what to fetch
        install(sys.argv[2])

    else:
        print('error, assert!')
