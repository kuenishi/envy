#!/usr/bin/env python

import subprocess, sys, os

e = os.environ['ENVY_HOME']
prefix = '--prefix=%s/local' % e
cmd = ['./configure']
for argv in sys.argv[1:]:
    cmd.append(argv)

cmd.append(prefix)
print(e)
print(cmd)
subprocess.check_call(cmd)
#subprocess.call(['ls'])
