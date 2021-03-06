# -*- coding: utf-8 -*-
'''
Support for Linux LVM2
'''
from __future__ import absolute_import

# Import python libs
import os.path

# Import salt libs
import salt.utils
import six

# Define the module's virtual name
__virtualname__ = 'lvm'


def __virtual__():
    '''
    Only load the module if lvm is installed
    '''
    if salt.utils.which('lvm'):
        return __virtualname__
    return False


def version():
    '''
    Return LVM version from lvm version

    CLI Example:

    .. code-block:: bash

        salt '*' lvm.version
    '''
    cmd = 'lvm version'
    out = __salt__['cmd.run'](cmd).splitlines()
    ret = out[0].split(': ')
    return ret[1].strip()


def fullversion():
    '''
    Return all version info from lvm version

    CLI Example:

    .. code-block:: bash

        salt '*' lvm.fullversion
    '''
    ret = {}
    cmd = 'lvm version'
    out = __salt__['cmd.run'](cmd).splitlines()
    for line in out:
        comps = line.split(':')
    ret[comps[0].strip()] = comps[1].strip()
    return ret


def pvdisplay(pvname=''):
    '''
    Return information about the physical volume(s)

    CLI Examples:

    .. code-block:: bash

        salt '*' lvm.pvdisplay
        salt '*' lvm.pvdisplay /dev/md0
    '''
    ret = {}
    cmd = ['pvdisplay', '-c', pvname]
    cmd_ret = __salt__['cmd.run_all'](cmd, python_shell=False)

    if cmd_ret['retcode'] != 0:
        return {}

    out = cmd_ret['stdout'].splitlines()
    for line in out:
        if 'is a new physical volume' not in line:
            comps = line.strip().split(':')
            ret[comps[0]] = {
                'Physical Volume Device': comps[0],
                'Volume Group Name': comps[1],
                'Physical Volume Size (kB)': comps[2],
                'Internal Physical Volume Number': comps[3],
                'Physical Volume Status': comps[4],
                'Physical Volume (not) Allocatable': comps[5],
                'Current Logical Volumes Here': comps[6],
                'Physical Extent Size (kB)': comps[7],
                'Total Physical Extents': comps[8],
                'Free Physical Extents': comps[9],
                'Allocated Physical Extents': comps[10],
                }
    return ret


def vgdisplay(vgname=''):
    '''
    Return information about the volume group(s)

    CLI Examples:

    .. code-block:: bash

        salt '*' lvm.vgdisplay
        salt '*' lvm.vgdisplay nova-volumes
    '''
    ret = {}
    cmd = ['vgdisplay', '-c', vgname]
    cmd_ret = __salt__['cmd.run_all'](cmd, python_shell=False)

    if cmd_ret['retcode'] != 0:
        return {}

    out = cmd_ret['stdout'].splitlines()
    for line in out:
        comps = line.strip().split(':')
        ret[comps[0]] = {
            'Volume Group Name': comps[0],
            'Volume Group Access': comps[1],
            'Volume Group Status': comps[2],
            'Internal Volume Group Number': comps[3],
            'Maximum Logical Volumes': comps[4],
            'Current Logical Volumes': comps[5],
            'Open Logical Volumes': comps[6],
            'Maximum Logical Volume Size': comps[7],
            'Maximum Physical Volumes': comps[8],
            'Current Physical Volumes': comps[9],
            'Actual Physical Volumes': comps[10],
            'Volume Group Size (kB)': comps[11],
            'Physical Extent Size (kB)': comps[12],
            'Total Physical Extents': comps[13],
            'Allocated Physical Extents': comps[14],
            'Free Physical Extents': comps[15],
            'UUID': comps[16],
            }
    return ret


def lvdisplay(lvname=''):
    '''
    Return information about the logical volume(s)

    CLI Examples:

    .. code-block:: bash

        salt '*' lvm.lvdisplay
        salt '*' lvm.lvdisplay /dev/vg_myserver/root
    '''
    ret = {}
    cmd = ['lvdisplay', '-c', lvname]
    cmd_ret = __salt__['cmd.run_all'](cmd, python_shell=False)

    if cmd_ret['retcode'] != 0:
        return {}

    out = cmd_ret['stdout'].splitlines()
    for line in out:
        comps = line.strip().split(':')
        ret[comps[0]] = {
            'Logical Volume Name': comps[0],
            'Volume Group Name': comps[1],
            'Logical Volume Access': comps[2],
            'Logical Volume Status': comps[3],
            'Internal Logical Volume Number': comps[4],
            'Open Logical Volumes': comps[5],
            'Logical Volume Size': comps[6],
            'Current Logical Extents Associated': comps[7],
            'Allocated Logical Extents': comps[8],
            'Allocation Policy': comps[9],
            'Read Ahead Sectors': comps[10],
            'Major Device Number': comps[11],
            'Minor Device Number': comps[12],
            }
    return ret


def pvcreate(devices, **kwargs):
    '''
    Set a physical device to be used as an LVM physical volume

    CLI Examples:

    .. code-block:: bash

        salt mymachine lvm.pvcreate /dev/sdb1,/dev/sdb2
        salt mymachine lvm.pvcreate /dev/sdb1 dataalignmentoffset=7s
    '''
    if not devices:
        return 'Error: at least one device is required'

    cmd = ['pvcreate']
    for device in devices.split(','):
        if not os.path.exists(device):
            return '{0} does not exist'.format(device)
        cmd.append(device)
    valid = ('metadatasize', 'dataalignment', 'dataalignmentoffset',
             'pvmetadatacopies', 'metadatacopies', 'metadataignore',
             'restorefile', 'norestorefile', 'labelsector',
             'setphysicalvolumesize')
    for var in kwargs:
        if kwargs[var] and var in valid:
            cmd.append('--{0}'.format(var))
            cmd.append(kwargs[var])
    out = __salt__['cmd.run'](cmd, python_shell=False).splitlines()
    return out[0]


def pvremove(devices):
    '''
    Remove a physical device being used as an LVM physical volume

    CLI Examples:

    .. code-block:: bash

        salt mymachine lvm.pvremove /dev/sdb1,/dev/sdb2
    '''
    cmd = ['pvremove', '-y']
    for device in devices.split(','):
        if not __salt__['lvm.pvdisplay'](device):
            return '{0} is not a physical volume'.format(device)
        cmd.append(device)
    out = __salt__['cmd.run'](cmd, python_shell=False).splitlines()
    return out[0]


def vgcreate(vgname, devices, **kwargs):
    '''
    Create an LVM volume group

    CLI Examples:

    .. code-block:: bash

        salt mymachine lvm.vgcreate my_vg /dev/sdb1,/dev/sdb2
        salt mymachine lvm.vgcreate my_vg /dev/sdb1 clustered=y
    '''
    if not vgname or not devices:
        return 'Error: vgname and device(s) are both required'

    cmd = ['vgcreate', vgname]
    for device in devices.split(','):
        cmd.append(device)
    valid = ('clustered', 'maxlogicalvolumes', 'maxphysicalvolumes',
             'vgmetadatacopies', 'metadatacopies', 'physicalextentsize')
    for var in kwargs:
        if kwargs[var] and var in valid:
            cmd.append('--{0}'.format(var))
            cmd.append(kwargs[var])
    out = __salt__['cmd.run'](cmd, python_shell=False).splitlines()
    vgdata = vgdisplay(vgname)
    vgdata['Output from vgcreate'] = out[0].strip()
    return vgdata


def vgextend(vgname, devices):
    '''
    Add physical volumes to an LVM volume group

    CLI Examples:

    .. code-block:: bash

        salt mymachine lvm.vgextend my_vg /dev/sdb1,/dev/sdb2
        salt mymachine lvm.vgextend my_vg /dev/sdb1
    '''
    if not vgname or not devices:
        return 'Error: vgname and device(s) are both required'

    cmd = ['vgextend', vgname]
    for device in devices.split(','):
        cmd.append(device)
    out = __salt__['cmd.run'](cmd, python_shell=False).splitlines()
    vgdata = {'Output from vgextend': out[0].strip()}
    return vgdata


def lvcreate(lvname, vgname, size=None, extents=None, snapshot=None, pv=None, **kwargs):
    '''
    Create a new logical volume, with option for which physical volume to be used

    CLI Examples:

    .. code-block:: bash

        salt '*' lvm.lvcreate new_volume_name vg_name size=10G
        salt '*' lvm.lvcreate new_volume_name vg_name extents=100 /dev/sdb
        salt '*' lvm.lvcreate new_snapshot    vg_name snapshot=volume_name size=3G
    '''
    if size and extents:
        return 'Error: Please specify only size or extents'

    valid = ('activate', 'chunksize', 'contiguous', 'discards', 'stripes',
             'stripesize', 'minor', 'persistent', 'mirrors', 'noudevsync',
             'monitor', 'ignoremonitoring', 'permission', 'poolmetadatasize',
             'readahead', 'regionsize', 'thin', 'thinpool', 'type',
             'virtualsize', 'zero')
    no_parameter = ('noudevsync', 'ignoremonitoring')
    extra_arguments = [
        '--{0}'.format(k) if k in no_parameter else '--{0} {1}'.format(k, v)
        for k, v in six.iteritems(kwargs) if k in valid
    ]

    cmd = ['lvcreate', '-n', lvname]

    if snapshot:
        cmd += ['-s', '{0}/{1}'.format(vgname, snapshot)]
    else:
        cmd.append(vgname)

    if size:
        cmd += ['-L', size]
    elif extents:
        cmd += ['-l', extents]
    else:
        return 'Error: Either size or extents must be specified'

    cmd.append(pv)
    cmd += extra_arguments

    out = __salt__['cmd.run'](cmd, python_shell=False).splitlines()
    lvdev = '/dev/{0}/{1}'.format(vgname, lvname)
    lvdata = lvdisplay(lvdev)
    lvdata['Output from lvcreate'] = out[0].strip()
    return lvdata


def vgremove(vgname):
    '''
    Remove an LVM volume group

    CLI Examples:

    .. code-block:: bash

        salt mymachine lvm.vgremove vgname
        salt mymachine lvm.vgremove vgname force=True
    '''
    cmd = ['vgremove' '-f', vgname]
    out = __salt__['cmd.run'](cmd, python_shell=False)
    return out.strip()


def lvremove(lvname, vgname):
    '''
    Remove a given existing logical volume from a named existing volume group

    CLI Example:

    .. code-block:: bash

        salt '*' lvm.lvremove lvname vgname force=True
    '''
    cmd = ['lvremove', '-f', '{0}/{1}'.format(vgname, lvname)]
    out = __salt__['cmd.run'](cmd, python_shell=False)
    return out.strip()


def lvresize(size, lvpath):
    '''
    Return information about the logical volume(s)

    CLI Examples:

    .. code-block:: bash


        salt '*' lvm.lvresize +12M /dev/mapper/vg1-test
    '''
    ret = {}
    cmd = ['lvresize', '-L', str(size), lvpath]
    cmd_ret = __salt__['cmd.run_all'](cmd, python_shell=False)
    if cmd_ret['retcode'] != 0:
        return {}
    return ret
