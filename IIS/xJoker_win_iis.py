# -*- coding: utf-8 -*-
'''
Microsoft IIS site management via WebAdministration powershell module

:platform:      Windows

.. versionadded:: 2016.3.0

'''

from __future__ import absolute_import

# Import salt libs
import salt.utils
import os
from salt.exceptions import SaltInvocationError

import logging

# Define the module's virtual name
__virtualname__ = 'xjoker_win_iis'

_LOG = logging.getLogger(__name__)
_VALID_PROTOCOLS = ('ftp', 'http', 'https')  # Allow protocols string

def __virtual__():
    '''
    Load only on Windows
    '''
    if salt.utils.is_windows():
        return __virtualname__
    return (False, 'Module xjoker_win_iis: module only works on Windows systems')


def _srvmgr(func, xml=False):
    '''
    Execute a function from the WebAdministration PS module
    '''

    command = 'Import-Module WebAdministration;'
    appcmd = "$appcmd=$env:windir + \"\system32\\inetsrv\\appcmd\";"
    if xml:
        appcmd_path = os.environ['WINDIR']+"\\system32\\inetsrv\\appcmd.exe"

        if os.path.isfile(appcmd_path):
            command = '{0} {1}'.format(appcmd, func)
        else:
            return False
    else:
        command = '{0} {1}'.format(command, func)

    cmd_ret = __salt__['cmd.run'](command, shell='powershell', python_shell=True)
    return cmd_ret

def _get_binding_info(hostheader='', ipaddress='*', port=80):
    '''
    Combine the host header, IP address, and TCP port into bindingInformation format.
    '''
    ret = r'{0}:{1}:{2}'.format(ipaddress, port, hostheader.replace(' ', ''))

    return ret



def say_hi():
    return "xJoker Hi!"


def list_sites():
    '''
    List all the currently deployed websites

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.list_sites
    '''
    pscmd = []
    pscmd.append(r'Get-WebSite -erroraction silentlycontinue -warningaction silentlycontinue')
    pscmd.append(r' | foreach {')
    pscmd.append(r' $_.Name')
    pscmd.append(r'};')

    command = ''.join(pscmd)
    return _srvmgr(command)


def list_sites_xml():
    '''
    List all the currently deployed websites

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.list_sites_xml
    '''
    pscmd = []
    pscmd.append(r'.$appcmd list site /config /xml')

    command = ''.join(pscmd)
    return _srvmgr(command, xml=True)




def list_sites_status():
    '''
    List all the currently deployed websites

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.list_sites
    '''
    pscmd = []
    pscmd.append(r'Get-WebSite -erroraction silentlycontinue -warningaction silentlycontinue')
    pscmd.append(r' | foreach {')
    pscmd.append(r' $_.Name,$_.state,$_.physicalPath')
    pscmd.append(r'};')

    command = ''.join(pscmd)
    return _srvmgr(command)


def site_binding(name):
    '''
    Get WebBinding (Hostname)

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.site_binding name='sitename'
    '''

    # sites = list_sites()
    #
    # if name not in sites:
    #     _LOG.warning('Site not found: %s', name)
    #     return ""


    pscmd = []
    pscmd.append(r'Get-WebBinding -Name "{0}" '.format(name))
    pscmd.append(r' | foreach {')
    pscmd.append(r' $_.bindingInformation')
    pscmd.append(r'};')

    command = ''.join(pscmd)
    return _srvmgr(command)

def create_binding(site,
                   hostheader='',
                   ipaddress='*',
                   port=80,
                   protocol='http'):
    pscmd = list()
    protocol = str(protocol).lower()
    name = _get_binding_info(hostheader, ipaddress, port)

    if protocol not in _VALID_PROTOCOLS:
        message = ("Invalid protocol '{0}' specified. Valid formats:"
                   ' {1}').format(protocol, _VALID_PROTOCOLS)
        raise SaltInvocationError(message)

    current_bindings = site_binding(site)

    if name in current_bindings:
        _LOG.debug("Binding already present: %s", name)
        return True

    pscmd.append("New-WebBinding -Name '{0}' -HostHeader '{1}'".format(site, hostheader))
    pscmd.append(" -IpAddress '{0}' -Port '{1}'".format(ipaddress, port))
    pscmd.append(" -Protocol '{0}'".format(protocol))

    cmd_ret = _srvmgr(str().join(pscmd))

    new_bindings = site_binding(site)

    if name in new_bindings:
        _LOG.debug('Binding created successfully: %s', name)
        return True
    _LOG.error('Unable to create binding: %s', name)
    return False

def remove_binding(site, hostheader='', ipaddress='*', port=80):
    pscmd = list()
    name = _get_binding_info(hostheader, ipaddress, port)
    current_bindings = site_binding(site)

    if name not in current_bindings:
        _LOG.debug('Binding already absent: %s', name)
        return True

    pscmd.append("Remove-WebBinding -HostHeader '{0}' ".format(hostheader))
    pscmd.append(" -IpAddress '{0}' -Port '{1}'".format(ipaddress, port))

    cmd_ret = _srvmgr(str().join(pscmd))

    new_bindings = site_binding(site)

    if name not in new_bindings:
        _LOG.debug('Binding removed successfully: %s', name)
        return True
    _LOG.error('Unable to remove binding: %s', name)
    return False


def create_site(
        name,
        sourcepath,
        protocol='http',
        port='80',
        apppool='',
        hostheader='',
        ipaddress='*'
):
    '''
    Create website in IIS

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.create_site name='My Test Site' protocol='http' sourcepath='c:\\stage' port='80' apppool='TestPool'
    '''
    _LOG.debug("create website")
    protocol = str(protocol).lower()
    app=list_apppools()
    current_sites = list_sites()
    pscmd = []

    # Get Site id
    site_id=_srvmgr("dir iis:\sites | foreach {$_.id} | sort -Descending | select -first 1")

    # 判断站点名称是否已经存在
    if name in current_sites:
        _LOG.debug("Site '%s' already present.", name)
        return True

    # 判断传入的协议是不是在允许协议列表内
    # 防止传入其他协议类型导致执行失败
    if protocol not in _VALID_PROTOCOLS:
        message = ("Invalid protocol '{0}' specified. Valid formats:"
                   ' {1}').format(protocol, _VALID_PROTOCOLS)
        raise SaltInvocationError(message)


    # 判断apppool是否存在 不存在则创建和站点名同名的apppool
    if apppool:
        if apppool not in app:
            if name not in app:
                create_apppool(name)
                apppool = name
            else:
                raise SaltInvocationError("Invalid AppPool Name!")
    else:
        if name not in app:
            create_apppool(name)
            apppool = name
        else:
            raise SaltInvocationError("Invalid AppPool Name!")

    # Create site powershell command
    # New-Website -Name "$name" -PhysicalPath "$physicalPath" -ApplicationPool "$applicationPool" -Port "$port" -IPAddress "$IPAddress" -HostHeader "$hostName" -id $id

    pscmd.append("New-Website -Name '{0}'".format(name))
    pscmd.append(" -PhysicalPath '{0}'".format(sourcepath))
    pscmd.append(" -ApplicationPool '{0}'".format(apppool))
    pscmd.append(" -Port '{0}'".format(port))
    pscmd.append(" -IPAddress '{0}'".format(ipaddress))
    pscmd.append(" -HostHeader '{0}'".format(hostheader))
    pscmd.append(" -id '{0}'".format(site_id))

    command = ''.join(pscmd)
    return _srvmgr(command)


def site_log_path(name, path=''):
    # Defalut setting %SystemDrive%\inetpub\logs\LogFiles
    '''
        Setting website logfile path

        CLI Example:

        .. code-block:: bash

            salt '*' xjoker_win_iis.site_log_path name='My Test Site' path='c:\log'

        '''
    site_path = r'IIS:\Sites\{0}'.format(name)
    pscmd = []
    pscmd.append("Set-ItemProperty -Path '{0}' -Name logFile.directory -Value '{1}';"
                 .format(site_path, str(path)))


def site_run_as(name, username='', password=''):
    '''
    Setting website run as user

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.site_run_as name='My Test Site' username='web' password='password'

    '''
    site_path = r'IIS:\Sites\{0}'.format(name)
    pscmd = []
    pscmd.append("Set-ItemProperty -Path '{0}' -Name userName -Value '{1}';"
                 .format(site_path, str(username)))
    pscmd.append("Set-ItemProperty -Path '{0}' -Name password -Value '{1}'"
                 .format(site_path, str(password)))

    command = ''.join(pscmd)
    return _srvmgr(command)


def remove_site(name):
    '''
    Delete website from IIS

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.remove_site name='My Test Site'

    '''

    current_sites = list_sites()

    # 对于不存在的站点,直接返回已经删除
    # 反正也不存在
    if name not in current_sites:
        _LOG.debug('Site already absent: %s', name)
        return True

    pscmd = []
    pscmd.append(r"Remove-WebSite -Name '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def list_apppools():
    '''
    List all configured IIS Application pools

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.list_apppools
    '''
    pscmd = []
    pscmd.append(r'Get-ChildItem IIS:\AppPools\ -erroraction silentlycontinue -warningaction silentlycontinue')
    pscmd.append(r' | foreach {')
    pscmd.append(r' $_.Name')
    pscmd.append(r'};')

    command = ''.join(pscmd)
    return _srvmgr(command)

def list_apppools_xml():
    '''
    List all configured IIS Application pools
    Output by XML

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.list_apppools_xml
    '''
    pscmd = []
    pscmd.append(r'.$appcmd list apppool /config /xml')

    command = ''.join(pscmd)
    return _srvmgr(command, xml=True)


def create_apppool(name):
    '''
    Create IIS Application pools

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.create_apppool name='MyTestPool'
    '''

    apppool=list_apppools()

    if name in apppool:
        _LOG.warning('AppPool is exist')
        return 'AppPool is exist'

    pscmd = []
    pscmd.append("New-WebAppPool '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def remove_apppool(name):
    '''
    Removes IIS Application pools

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.remove_apppool name='MyTestPool'
    '''

    apppool=list_apppools()

    if name not in apppool:
        _LOG.warning('Apppool is delete')
        return True


    apppool_path = r'IIS:\AppPools\{0}'.format(name)
    pscmd = []
    pscmd.append(r"Remove-Item -Path '{0}' -recurse".format(apppool_path))

    command = ''.join(pscmd)
    return _srvmgr(command)


def start_site(name):
    '''
    Start IIS WebSite

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.start_site name='MyTestPool'
    '''

    sites=list_sites()

    if name not in sites:
        _LOG.warning('Site not exist!')
        return False


    pscmd = []
    pscmd.append(r"Start-WebSite '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def stop_site(name):
    '''
    Stop IIS WebSite

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.stop_site name='MyTestPool'
    '''

    sites = list_sites()

    if name not in sites:
        _LOG.warning('Site not exist!')
        return False

    pscmd = []
    pscmd.append(r"Stop-WebSite '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def restart_site(name):
    '''
    Restart IIS WebSite

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.restart_site name='MyTestPool'
    '''

    sites = list_sites()

    if name not in sites:
        _LOG.warning('Site not exist!')
        return False

    pscmd = []
    pscmd.append(r"Stop-WebSite '{0}'".format(name))
    pscmd.append(r"Start-WebSite '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def restart_apppool(name):
    '''
    Restart IIS Apppool

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.restart_apppool name='MyTestPool'
    '''

    apppool=list_apppools()

    if name not in apppool:
        _LOG.warning('AppPool not exist!')
        return False

    pscmd = []
    pscmd.append(r"Restart-WebAppPool '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def start_apppool(name):
    '''
    Start IIS Apppool

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.start_apppool name='MyTestPool'
    '''

    apppool = list_apppools()

    if name not in apppool:
        _LOG.warning('AppPool not exist!')
        return False

    pscmd = []
    pscmd.append(r"Start-WebAppPool '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def stop_apppool(name):
    '''
    Stop IIS Apppool

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.stop_apppool name='MyTestPool'
    '''

    apppool = list_apppools()

    if name not in apppool:
        _LOG.warning('AppPool not exist!')
        return False

    pscmd = []
    pscmd.append(r"Stop-WebAppPool '{0}'".format(name))

    command = ''.join(pscmd)
    return _srvmgr(command)


def apppool_setting(
        name,
        auto_start='',
        runtime_version='',
        pipeline_mode='',
        bit_setting=''):
    '''
    Change Apppool setting

    CLI Example:

    .. code-block:: bash

    pipeline_mode: Integrated = 0  Classic = 1
    runtime_version: v2.0 or v4.0
    bit_setting; This setting apppool 32bit or 64bit    True = 64bit  False = 32bit
        salt '*' xjoker_win_iis.apppool_setting name='MyTestPool' runtime_version='v2.0' pipeline_mode=0
    '''

    apppool = list_apppools()

    if name not in apppool:
        _LOG.warning('AppPool not exist!')
        return False

    apppool_path = r'IIS:\AppPools\{0}'.format(name)

    pscmd = []
    if runtime_version:
        pscmd.append("Set-ItemProperty -Path '{0}'  'managedRuntimeVersion'  '{1}';"
                     .format(apppool_path, runtime_version))
    if pipeline_mode:
        pscmd.append("Set-ItemProperty -Path '{0}' 'managedPipelineMode' '{1}';"
                     .format(apppool_path, pipeline_mode))
    if auto_start:
        pscmd.append("Set-ItemProperty -Path '{0}' 'autoStart' '{1}';"
                     .format(apppool_path, auto_start))
    if bit_setting == "True" or bit_setting == "False":
        pscmd.append("Set-ItemProperty -Path '{0}' 'enable32BitAppOnWin64' '{1}';"
                     .format(apppool_path, bit_setting))

    # New-Item -Path 'IIS:\AppPools\ttt' | Set-ItemProperty -Name enable32BitAppOnWin64 -Value True | Set-ItemProperty -Name managedPipelineMode -Value 1
    command = ''.join(pscmd)
    return _srvmgr(command)

def iis(fun):
    '''
    Control IIS service statue

    CLI Example:

    .. code-block:: bash
        start : start IIS service
        stop : stop IIS service
        restart : restart IIS service

        salt '*' xjoker_win_iis.iis restart
    '''
    pscmd=[]
    if fun == "restart":
        pscmd.append("invoke-command -scriptblock {iisreset /RESTART}")
    if fun == "start":
        pscmd.append("invoke-command -scriptblock {iisreset /START}")
    if fun == "stop":
        pscmd.append("invoke-command -scriptblock {iisreset /STOP}")

    command = ''.join(pscmd)
    return _srvmgr(command)