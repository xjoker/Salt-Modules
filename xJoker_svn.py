# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Import python libs
import logging
import os
import re
import subprocess

import salt.utils
from salt import utils, exceptions


__virtualname__ = 'xjoker_svn'
_LOG = logging.getLogger(__name__)
_INI_RE = re.compile(r"^([^:]+):\s+(\S.*)$", re.M)

def __virtual__():
    if salt.utils.is_windows():
        if utils.which('svn') is None:
            return (False,
                'The svn execution module cannot be loaded: svn unavailable.')
        else:
            return True
    else:
        return (False,
                'This modules only run Windows system.')


def _run_svn(cmd, cwd,runasUsername,runasPassword,username, password,certCheck,revision='', opts=''):
    '''
        Execute svn command


    :param cmd: The command to svn.
    :param cwd: The path to the Subversion repository.
    :param username: Connect to Subversion server as another user.
    :param password: Connect to Subversion server with this password.
    :param certCheck: Check Subversion server Cert
    :param opts: Any additional options to add to the command line
    :return: Return the output of the command
    '''

    if runasUsername:
        cmd = ['chcp', '936', '>', 'nul', '&', 'runas','/user:{0}'.format(runasUsername),'"svn', '--non-interactive', cmd, cwd]
    else:
        cmd=['chcp','936', '>', 'nul' ,'&','svn','--non-interactive',cmd,cwd]

    options = list(opts)
    if revision!='':
        options.extend(['-r',str(revision)])

    if username:
        options.extend(['--username',username])
    if password:
        options.extend(['--password',password])

    if not certCheck:
        options.extend(['--trust-server-cert'])

    cmd.extend(options)
    if runasUsername:
        cmd.extend('"')
    _LOG.info(cmd)
    # 设置为简中编码
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,stdin=subprocess.PIPE)

    # 如果有指定RunAS密码在此插入
    if runasPassword:
        p.stdin.write(runasPassword)
        p.stdin.close()

    stdout, stderr = p.communicate()
    if p.returncode==0:
        return stdout.decode('cp936').encode('utf-8')

    raise exceptions.CommandExecutionError(stdout.decode('cp936').encode('utf-8')+ '\n\n')


def update(cwd,
           targets=None,
           runasUsername=None,
           runasPassword=None,
           username=None,
           password=None,
           certCheck=True,
           revision='',
           *opts):
    '''

    Execute svn update command

    '''
    if targets:
        opts += tuple(salt.utils.shlex_split(targets))

    return _run_svn('update', cwd,runasUsername, runasPassword,username, password,certCheck,revision,opts)

def checkout(cwd,
             remote,
             target=None,
             runasUsername=None,
             runasPassword=None,
             username=None,
             password=None,
             certCheck=True,
             revision='',
             *opts):
    opts += (remote,)
    if target:
        opts += (target,)
    if not os.path.exists(cwd):
        os.mkdir(cwd)
    return _run_svn('checkout', cwd, runasUsername, runasPassword,username, password,certCheck,revision,opts)

def info(cwd,
         targets=None,
         runasUsername=None,
         runasPassword=None,
         username=None,
         password=None,
         fmt='str'):
    opts = list()
    if fmt == 'xml':
        opts.append('--xml')
    if targets:
        opts += salt.utils.shlex_split(targets)
    infos = _run_svn('info', cwd, runasUsername, runasPassword, username, password, opts)

    if fmt in ('str', 'xml'):
        return infos

    info_list = []
    for infosplit in infos.split('\n\n'):
        info_list.append(_INI_RE.findall(infosplit))

    if fmt == 'list':
        return info_list
    if fmt == 'dict':
        return [dict(tmp) for tmp in info_list]

def switch(cwd,
           remote,
           target=None,
           runasUsername=None,
           runasPassword=None,
           username=None,
           password=None,
           *opts):
    opts += (remote,)
    if target:
        opts += (target,)
    return _run_svn('switch', cwd, runasUsername, runasPassword, username, password, opts)

def diff(cwd,
         targets=None,
         runasUsername=None,
         runasPassword=None,
         username=None,
         password=None,
         *opts):
    if targets:
        opts += tuple(salt.utils.shlex_split(targets))
    return _run_svn('diff', cwd,  runasUsername, runasPassword,username, password, opts)

def commit(cwd,
           targets=None,
           runasUsername=None,
           runasPassword=None,
           msg=None,
           username=None,
           password=None,
           *opts):
    if msg:
        opts += ('-m', msg)
    if targets:
        opts += tuple(salt.utils.shlex_split(targets))
    return _run_svn('commit', cwd,  runasUsername, runasPassword,username, password, opts)

def add(cwd,
        targets,
        runasUsername=None,
        runasPassword=None,
        username=None,
        password=None,
        *opts):
    if targets:
        opts += tuple(salt.utils.shlex_split(targets))
    return _run_svn('add', cwd,  runasUsername, runasPassword,username, password, opts)

def remove(cwd,
           targets,
           runasUsername=None,
           runasPassword=None,
           msg=None,
           username=None,
           password=None,
           *opts):
    if msg:
        opts += ('-m', msg)
    if targets:
        opts += tuple(salt.utils.shlex_split(targets))
    return _run_svn('remove', cwd,  runasUsername, runasPassword,username, password, opts)

def status(cwd,
           targets=None,
           runasUsername=None,
           runasPassword=None,
           username=None,
           password=None,
           *opts):

    if targets:
        opts += tuple(salt.utils.shlex_split(targets))
    return _run_svn('status', cwd,  runasUsername, runasPassword,username, password, opts)

def export(cwd,
           remote,
           target=None,
           runasUsername=None,
           runasPassword=None,
           username=None,
           password=None,
           revision='HEAD',
           *opts):
    opts += (remote,)
    if target:
        opts += (target,)
    return _run_svn('export', cwd,  runasUsername, runasPassword,username, password,revision, opts)