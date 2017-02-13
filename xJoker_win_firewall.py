# -*- coding: utf-8 -*-
'''
Module for configuring Windows Firewall
'''
from __future__ import absolute_import

# Import python libs
import re
import logging
import subprocess

# Import salt libs
import salt.utils
from salt.ext import six
from salt import exceptions

# Define the module's virtual name
__virtualname__ = 'xjoker_firewall'

log = logging.getLogger(__name__)


# base cmd
cmd = ['chcp','936', '>', 'nul' ,'&','netsh', 'advfirewall']

def __virtual__():
    '''
    Only works on Windows systems
    '''
    if salt.utils.is_windows():
        return __virtualname__
    return (False, "Module win_firewall: module only works on Windows systems")


def _cmd_run(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return stdout.decode('cp936').encode('utf-8')

    raise exceptions.CommandExecutionError(stdout.decode('cp936').encode('utf-8') + '\n\n')

def get_config():
    '''
    Get the status of all the firewall profiles

    CLI Example:

    .. code-block:: bash

        salt '*' firewall.get_config
    '''
    profiles = {}
    curr = None
    cmd.extend(['show', 'allprofiles'])
    for line in _cmd_run(cmd).splitlines():
        if not curr:
            tmp = re.search('(.*) 设置:', line)
            if tmp:
                curr = tmp.group(1)
        elif line.startswith('状态'):
            profiles[curr] = line.split()[1] == '打开'
            curr = None

    return profiles


def disable(profile='allprofiles'):
    '''
    Disable firewall profile :param profile: (default: allprofiles)

    CLI Example:

    .. code-block:: bash

        salt '*' firewall.disable
    '''
    cmd.extend(['set', profile, 'state', 'off'])
    return _cmd_run(cmd) == 'Ok.'


def enable(profile='allprofiles'):
    '''
    Enable firewall profile :param profile: (default: allprofiles)

    .. versionadded:: 2015.5.0

    CLI Example:

    .. code-block:: bash

        salt '*' firewall.enable
    '''
    cmd.extend(['set', profile, 'state', 'on'])
    return _cmd_run(cmd) == 'Ok.'


def get_rule(name='all'):
    '''
    .. versionadded:: 2015.5.0

    Get firewall rule(s) info

    CLI Example:

    .. code-block:: bash

        salt '*' firewall.get_rule 'MyAppPort'
    '''
    ret = {}
    cmd.extend(['firewall','show', 'rule', 'name={0}'.format(name)])
    ret[name] = _cmd_run(cmd)

    if ret[name].strip() == 'No rules match the specified criteria.':
        ret = False

    return ret


def add_rule(name, localport, protocol='tcp', action='allow', dir='in',
             remoteip='any'):
    '''
    .. versionadded:: 2015.5.0

    Add a new firewall rule

    CLI Example:

    .. code-block:: bash

        salt '*' firewall.add_rule 'test' '8080' 'tcp'
        salt '*' firewall.add_rule 'test' '1' 'icmpv4'
        salt '*' firewall.add_rule 'test_remote_ip' '8000' 'tcp' 'allow' 'in' '192.168.0.1'

    '''

    cmd.extend(['firewall', 'add', 'rule',
           'name={0}'.format(name),
           'protocol={0}'.format(protocol),
           'dir={0}'.format(dir),
           'action={0}'.format(action),
           'remoteip={0}'.format(remoteip)])

    if 'icmpv4' not in protocol and 'icmpv6' not in protocol:
        cmd.append('localport={0}'.format(localport))

    ret = _cmd_run(cmd)
    if isinstance(ret, six.string_types):
        return ret.strip() == 'Ok.'
    else:
        log.error('firewall.add_rule failed: {0}'.format(ret))
        return False


def delete_rule(name, localport, protocol='tcp', dir='in', remoteip='any'):
    '''
    .. versionadded:: 2015.8.0

    Delete an existing firewall rule

    CLI Example:

    .. code-block:: bash

        salt '*' firewall.delete_rule 'test' '8080' 'tcp' 'in'
        salt '*' firewall.delete_rule 'test_remote_ip' '8000' 'tcp' 'in' '192.168.0.1'
    '''

    cmd.extend(['firewall', 'delete', 'rule',
           'name={0}'.format(name),
           'protocol={0}'.format(protocol),
           'dir={0}'.format(dir),
           'remoteip={0}'.format(remoteip)])

    if 'icmpv4' not in protocol and 'icmpv6' not in protocol:
        cmd.append('localport={0}'.format(localport))

    ret = _cmd_run(cmd)
    if isinstance(ret, six.string_types):
        return ret.endswith('Ok.')
    else:
        log.error('firewall.delete_rule failed: {0}'.format(ret))
        return False