# -*- coding: utf-8 -*-
'''
Microsoft service management via powershell module

:platform:      Windows

.. versionadded:: 2016.7.14

'''
from __future__ import absolute_import

# Import salt libs
import salt.utils
from salt.exceptions import SaltInvocationError

import logging
import sys

# Define the module's virtual name
__virtualname__ = 'xjoker_win_service'

_LOG = logging.getLogger(__name__)

def __virtual__():
    '''
    Load only on Windows
    '''
    if salt.utils.is_windows():
        return __virtualname__
    return (False, 'Module xjoker_win_service: module only works on Windows systems')


def _srvmgr(func, xml=False):
    '''
    Execute a function from the PS module
    '''
    set_encoding='$OutputEncoding = New-Object -typename System.Text.UTF8Encoding;'
    command = '{0} {1}'.format(set_encoding,func)

    cmd_ret = __salt__['cmd.run'](command, shell='powershell', python_shell=True)
    return cmd_ret


def get_service_status():
    '''
    Use PS module get all service now status

        salt '*' xjoker_win_service.get_service_status
    '''
    pscmd=[]
    pscmd.append(r'get-service | format-list -Property Name,Status,DisplayName')

    command = ''.join(pscmd)
    res=_srvmgr(command)

    return res