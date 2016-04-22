#!/usr/bin/python
import os
import fnmatch
import sys
import subprocess

if len(sys.argv) > 1:
    version = sys.argv[1]
else:
    print 'No version for SSR SDK specified, aborting'
    sys.exit(1)

if len(sys.argv) > 2:
    print 'Using custom SSR SDK image %s' % sys.argv[2]
    tar = sys.argv[2]
else:
    print 'No custom SSR SDK image specified, using sysbuild image'
    tar = '/home/sysbuild/images/swfeature_int/SEOS-swfeature_int-pkg-SSR-sdk-%s.tar.gz' % version
    if not os.path.exists(tar):
        print 'Image for version %s not found in swfeature_int, looking at REL_IPOS_* directories' % version
        for entry in os.listdir('/home/sysbuild/images'):
            if os.path.isdir('/home/sysbuild/images/%s' % entry) and fnmatch.fnmatchcase(entry, 'REL_IPOS_*'):
                tar_ = '/home/sysbuild/images/%s/SEOS-pkg-SSR-sdk-%s.tar.gz' % (entry, version)
                if os.path.exists(tar_):
                    tar = tar_
                    break
        else:
            print 'No image for version %s found under /home/sysbuild/images/swfeature_int or /home/sysbuild/images/REL_IPOS_*, aborting' % version
            sys.exit(1)
    print 'Image chosen: %s' % tar

base_path = '/ssrsim/%s/ssr-sdk' % os.getenv('USER')
subprocess.call('mkdir -p %s' % base_path, shell=True)

sdk_dir = 'v%s' % version

try:
    os.chdir(base_path)
except OSError, err:
    print 'Unable to cd to %s - %s\nMake sure you have specified a valid SSR-SIM host and the required directories exist' % (base_path, err)
    sys.exit(1)

if sdk_dir in os.listdir('.'):
    print 'The SDK directory %s/%s already exists, skipping prepare' % (base_path, sdk_dir)
else:
    try:
        os.stat(tar)
    except OSError, err:
        print 'Cannot access image file %s' % tar
        sys.exit(1)
    try:
        os.mkdir(sdk_dir)
        os.chdir(sdk_dir)
    except OSError, err:
        print 'Cannot create and cd to %s/%s' % (base_path, sdk_dir)
        sys.exit(1)
    
    subprocess.call('tar -xzf %s' % tar, shell=True)
    subprocess.call('sdk/scripts/ssr-sim prepare', shell=True)
