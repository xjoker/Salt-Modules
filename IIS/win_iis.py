# -*- coding: utf-8 -*-
'''
Microsoft IIS site management via WebAdministration powershell module

:platform:      Windows

.. versionadded:: 2016.3.0

'''

from __future__ import absolute_import

# Import salt libs
import salt.utils

# Define the module's virtual name
__virtualname__ = 'xjoker_win_iis'


def _get_binding_info(hostheader='', port=80):
    ret = r':{0}:{1}'.format(port, hostheader.replace(' ', ''))
    return ret


def __virtual__():
    '''
    Load only on Windows
    '''
    if salt.utils.is_windows():
        return __virtualname__
    return (False, 'Module xjoker_win_iis: module only works on Windows systems')


def _srvmgr(func):
    '''
    Execute a function from the WebAdministration PS module
    '''

    return __salt__['cmd.run'](
        'Import-Module WebAdministration; {0}'.format(func),
        shell='powershell',
        python_shell=True)


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
    pscmd.append(r' $_.Name,$_.state,$_.physicalPath,($_.bindings.Collection|foreach {$_.bindingInformation})')
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

    pscmd = []
    pscmd.append(r'Get-WebBinding \'{0}\' '.format(name))
    pscmd.append(r' | foreach {')
    pscmd.append(r' $_.bindingInformation')
    pscmd.append(r'};')

    command = ''.join(pscmd)
    return _srvmgr(command)


def create_site(
        name,
        protocol,
        sourcepath,
        port,
        apppool='',
        hostheader='',
        ipaddress=''
        ):
    '''
    Create a basic website in IIS

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.create_site name='My Test Site' protocol='http' sourcepath='c:\\stage' port='80' apppool='TestPool'
    '''

    protocol = str(protocol).lower()
    binding_info = _get_binding_info(hostheader, port)
    site_path = r'IIS:\Sites\{0}'.format(name)
    pscmd = []
    pscmd.append(r"New-Item -Path '{0}' -Bindings".format(site_path))
    pscmd.append(r" @{{ protocol='{0}'; bindingInformation='{1}' }}".format(protocol, binding_info))
    pscmd.append(r"-physicalPath {0};".format(sourcepath))

    if apppool:
        pscmd.append(r"Set-ItemProperty -Path '{0}' ".format(site_path))
        pscmd.append(r" -name applicationPool -value '{0}';".format(apppool))

    command = ''.join(pscmd)
    return _srvmgr(command)

def site_run_as(name,username='',password=''):
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

    pscmd = []
    pscmd.append(r'cd IIS:\Sites\;')
    pscmd.append(r'Remove-WebSite -Name \'{0}\''.format(name))

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


def create_apppool(name):
    '''
    Create IIS Application pools

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.create_apppool name='MyTestPool'
    '''
    apppool_path = r'IIS:\AppPools\{0}'.format(name)

    pscmd = []
    pscmd.append(r"New-Item -Path '{0}'".format(apppool_path))

    command = ''.join(pscmd)
    return _srvmgr(command)


def remove_apppool(name):
    '''
    Removes IIS Application pools

    CLI Example:

    .. code-block:: bash

        salt '*' xjoker_win_iis.remove_apppool name='MyTestPool'
    '''
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

    apppool_path = r'IIS:\AppPools\{0}'.format(name)

    pscmd = []
    if runtime_version:
        pscmd.append("Set-ItemProperty -Path '{0}' -Name managedRuntimeVersion -Value '{1}'"
                     .format(apppool_path,runtime_version))
    if pipeline_mode:
        pscmd.append("Set-ItemProperty -Path '{0}' -Name managedPipelineMode -Value '{1}'"
                     .format(apppool_path,pipeline_mode))
    if auto_start:
        pscmd.append("Set-ItemProperty -Path '{0}' -Name autoStart -Value '{1}'"
                     .format(apppool_path,auto_start))
    if bit_setting:
        pscmd.append("Set-ItemProperty -Path '{0}' -Name enable32BitAppOnWin64 -Value '{1}'"
                     .format(apppool_path,bit_setting))


    command = ''.join(pscmd)
    return _srvmgr(command)