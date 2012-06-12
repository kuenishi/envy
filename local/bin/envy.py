#!/usr/bin/env python

import sys

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

def help():
    print('help: ... ')



if __name__ == '__main__':
    cmd = None
    if len(sys.argv) == 1:
        cmd = 'help'
    else:
        cmd = sys.argv[1]
    print(len(sys.argv))
    if cmd == 'help':
        help()
    elif cmd == 'install' and len(sys.argv) > 2:
        # read local/share/envy_resource.json
        # look for req
        print('envy install <%s>' % sys.argv[2])
    else:
        print('error, assert!')
