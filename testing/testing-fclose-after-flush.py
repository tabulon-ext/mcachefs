#!/bin/env python


import os, sys, subprocess, shlex, time

BASEPATH = "/tmp/mcachefs.testing"
MCACHEFS = os.path.dirname( os.path.abspath(__file__) )+'/../src/mcachefs'

os.system('rm -rf '+BASEPATH+"/")

os.system('mkdir -p '+BASEPATH+"/1")
os.system('mkdir -p '+BASEPATH+"/2")

# just make sure mcachefs is not mounted, in case we're running after a failed try
os.system("fusermount -u %s/2" % BASEPATH)

# run mcachefs in gdb so we can see a stack trace in case it fails!
#cmd='''/bin/sh -c "echo -e 'r\\nbt\\n' | gdb --args %s -f -o -s %s/1 %s/2" ''' % (MCACHEFS, BASEPATH, BASEPATH)
cmd='''/bin/sh -c "%s -f -s %s/1 %s/2 -o cache=%s/cache,metafile=%s/metafile,journal=%s/journal" ''' % (MCACHEFS, BASEPATH, BASEPATH, BASEPATH, BASEPATH, BASEPATH)
p = subprocess.Popen(shlex.split(cmd))

print shlex.split(cmd), p.pid
if not p.pid:
    print "Failed to run %s!" % MCACHEFS
    sys.exit(-1)

# wait a bit mcachefs to mount!
while( not os.path.exists('%s/2/.mcachefs' % BASEPATH) ):
    time.sleep(1)

# time.sleep(10)

print "Create files"
# create 300 files
for n in range(300):
    f=open('%s/2/%s' % (BASEPATH, n),'w').close()

print "Open the last one"
# open the last one!
f=open('%s/2/%s' % (BASEPATH, "last_one"), "w")

print "Apply journal"
os.system('echo apply_journal >  %s/2/.mcachefs/action' % BASEPATH)

time.sleep(5)

print "Flush metadata"
# flush metadata
os.system('echo flush_metadata >  %s/2/.mcachefs/action' % BASEPATH)

# write some stuff in the open file
f.write("Hello world !")

# close the opened file. It should NOT crash!
f.close()

time.sleep(60)

time.sleep(3)
l = os.popen( 'pgrep -fa "%s"' % MCACHEFS ).readlines()
print l
if not l:
	print "mcachefs crashed!"

# unmount mcachefs
os.system("fusermount -u %s/2" % BASEPATH)

# kill gdb if it's still running!
p.poll()
if not p.returncode:
    p.kill()

os.system('rm -rf '+BASEPATH+"/")

