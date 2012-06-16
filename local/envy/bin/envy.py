#!/usr/bin/env python

import sys, os
import json
import subprocess
import shutil
import stat

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
    print('envy 0.0.1')
    print('commands are: help list install')

def list():
    resource_file = '%s/local/envy/packages.json' % os.environ['ENVY_HOME']
    #print(resource_file)
    v = json.load(open(resource_file))
    for k,v in v.iteritems():
        print("%s\t\t%s" % (k, v))
    

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
        return filename

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

        

def remove(name):
    work_dir = '%s/local/src/%s' % (os.environ['ENVY_HOME'], name)
    shutil.rmtree(work_dir)

def work_dir(name):
    return '%s/local/src/%s' % (os.environ['ENVY_HOME'], name)

def create_work_dir(name):
    path = work_dir(name)
    try:
        os.mkdir(path)
        return path
    except: pass

def check_work_dir(name):
    path = work_dir(name)
    try:    return len(os.listdir(path)) > 0
    except: return 

def fetch(name):
    create_work_dir(name)
    path = work_dir(name)

    resource_file = '%s/local/envy/packages.json' % os.environ['ENVY_HOME']
    #print(resource_file)
    v = json.load(open(resource_file))
    url = v.get(name)
    package_name = ''
    if url is None: url = name
    # elif type(url) == type({}):
    else: package_name = name

    f = Fetcher(url, path, name)
    return f.fetch()

def deflate(tarball, path='.'):
    curdir = os.getcwd()
    os.chdir(path)

    #if tarball[-6:] == 'tar.gz':
    #elif tarball[-4:] == '.tgz':
    subprocess.call(['tar', 'xzf', tarball])

    return os.chdir(curdir)

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

def find_ball(path):
    for f in os.listdir(path):
        if f[-6:] == 'tar.gz': return f
        elif f[-4:] == '.tgz': return f
        # FIXME: .bz2 case, .zip case
    else:
        raise "No tarball found"


def install(name):
    if not check_work_dir(name): fetch(name) # not yet fetched
    path = work_dir(name)
    tarball = find_ball(path)
    print tarball, path
    deflate(tarball, path)
    print('installing %s' % name)
    
    for f in os.listdir(path):
        srcdir_candidate = os.path.join(path, f)
        if stat.S_ISDIR(os.stat(srcdir_candidate).st_mode):
            return build_and_install(srcdir_candidate)

'''
no upgrade, update, uninstall command
TODO: dependency description and resolution ? is it too much?
'''
if __name__ == '__main__':
    srcdir = get_basedir('local/src')
    try: os.mkdir(srcdir)
    except: pass

    if len(sys.argv) == 1:
        help()
        exit(0)

    cmd = sys.argv[1]

    if   cmd == 'help':  help()
    elif cmd == 'list':  list()

    elif cmd == 'remove':
        for package in sys.argv[2:]: remove(package)

    elif cmd == 'fetch':
        for package in sys.argv[2:]: fetch(package)

    elif cmd == 'install':
        for package in sys.argv[2:]: install(package)

    else:
        print('no such command: %s' % cmd)
        help()
