#!/usr/bin/env python

import subprocess, sys, os

e = os.environ['ENVY_HOME']
prefix = '--prefix=%s/local' % e
print(prefix)
