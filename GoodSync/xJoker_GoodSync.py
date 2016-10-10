# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Import python libs
import logging
import os
import subprocess

import salt.utils
from salt import utils, exceptions


__virtualname__ = 'xjoker_goodsync'
_LOG = logging.getLogger(__name__)
_Gsync_path="C:\\Program Files\\Siber Systems\\GoodSync\\gsync.exe"

# D:\Sync\GoodSync\GoodSync.exe

def __virtual__():
    if salt.utils.is_windows():
        if os.path.isfile(_Gsync_path):
            return True
        else:
            return False, "Normal path cannot find gsync"
    else:
        return False, "This modules only run Windows system."


def _run_cmd(cmd):
    base_cmd=[_Gsync_path]
    for i in cmd:
        _LOG.info(i)
        base_cmd.extend([i])

    _LOG.info(base_cmd)
    p = subprocess.Popen(base_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    if p.returncode==0:
        return stdout

    raise exceptions.CommandExecutionError(stdout+ '\n\n')

def sayhi():
    return "Hi xJoker."

def jobnew(jobname,
           f1,
           f2,
           ReadOnlySource=0,
           Direction=1,
           CleanupOldGenerations=0,
           CopyCreateTime=0,
           WaitForLocks=0,
           WaitForLocksMinutes=10,
           exclude='',
           include='',
           LimitChangesPercent=100,
           OnFileChangeAction=2,
           OnTimerAction=2,
           TimerIntervalMinutes=10,
           AutoResolveConflicts=1,
           DetectMovesAndRenames=0,
           UberUnlockedUpload=0):
    '''

    Example :  xjoker_goodsync.jobnew jobname="233" f1="c:\\f1" f2="c:\\f2"

               xjoker_goodsync.jobnew jobname="233" f1="c:\\f1" f2="c:\\f2" ReadOnlySource=0 exclude="*./svn|*.233|*.666" OnFileChangeAction=1 OnTimerAction=1 DetectMovesAndRenames=0
    :param jobname: job name
    :param f1: Left sync folder
    :param f2: Right sync folder
    :param ReadOnlySource: Read-Only source side option. yes=0 no=1 Default=0
    :param Direction: Job direction. 2way=0 ltor=1 rtol=2 Default=1
    :param CleanupOldGenerations: Whether to cleanup old generations of files and folders. yes=0 no=1 Default=0
    :param CopyCreateTime: Copy File/Folder creation time. yes=0 no=1 Default=0
    :param WaitForLocks: Wati for Locks,instead of producing error. yes=0 no=1 Default=0
    :param WaitForLocksMinutes: Waiting for Locks time,in minutes. Default=10
    :param exclude: Exclude filter. Separated by '|'. Example: "*./svn|*.233"
    :param include: Include filter. Separated by '|'. Example: "*./svn|*.233"
    :param LimitChangesPercent: No Sync if to many files changed option. Value is number from 0 to 100. Default=100
    :param OnFileChangeAction: Automatically Analyze/Sync on any file change inside local sync folders. analyze=0 sync=1 no=2 Default=2
    :param OnTimerAction: Automatically Analyze/Sync on Timer (every N minutes). analyze=0 sync=1 no=2 Default=2
    :param TimerIntervalMinutes: Only 'OnTimerAction' setting '0' or '1' . Value is number in minutes. Default=10
    :param AutoResolveConflicts: Auto-Resolve conflicts option. no=0 left=1 right=2 newer=3 Default=1
    :param DetectMovesAndRenames: Detect File/Folder Moves and Renames,instead of doing Copy + Delete. yes=0 no=1 Default=1
    :param UberUnlockedUpload: yes=0 no=1 Default=0
    :return:
    '''

    ReadOnlySource_List=['yes','no']
    Direction_List=['2way','ltor','rtol']
    CleanupOldGenerations_List=['yes','no']
    CopyCreateTime_List=['yes','no']
    WaitForLocks_List=['yes','no']
    OnFileChangeAction_List=['analyze','sync','no']
    OnTimerAction_List=['analyze','sync','no']
    AutoResolveConflicts_List=['no','left','right','newer']
    UberUnlockedUpload_List=['yes','no']



    if jobname==None:
        return "Jobname is null."
    if f1==None or f2==None:
        return "Left folder or right folder is null."

    cmd = ['job-new', str(jobname), '/f1=' + str(f1), '/f2=' + str(f2),
           '/bad-certs1=yes /bad-certs2=yes /hostbased1=yes /hostbased2=yes']

    # 只读设定
    if ReadOnlySource==0 or ReadOnlySource==1:
        cmd.extend(['/readonly-src={0}'.format(ReadOnlySource_List[ReadOnlySource])])

    # 同步模式
    if Direction>=0 or Direction<=2:
        cmd.extend(['/dir={0}'.format(Direction_List[Direction])])

    if CleanupOldGenerations == 0 or CleanupOldGenerations == 1:
        cmd.extend(['/cleanup-old-generations={0}'.format(CleanupOldGenerations_List[CleanupOldGenerations])])

    if CopyCreateTime == 0 or CopyCreateTime == 1:
        cmd.extend(['/copy-create-time={0}'.format(CopyCreateTime_List[CopyCreateTime])])

    if WaitForLocks == 0 or WaitForLocks == 1:
        cmd.extend(['/wait-for-locks={0}'.format(WaitForLocks_List[WaitForLocks])])
        if WaitForLocksMinutes>0:
            cmd.extend(['/timer-period='+str(WaitForLocksMinutes)])
        else:
            cmd.extend(['/timer-period=10'])

    if exclude:
        cmd.extend(['/exclude="{0}"'.format(exclude)])

    if include:
        cmd.extend(['/include="{0}"'.format(include)])

    if LimitChangesPercent>=0 or LimitChangesPercent<=100:
        cmd.extend(['/limit-changes={0}'.format(str(LimitChangesPercent))])


    if OnFileChangeAction>=0 or OnFileChangeAction<=2:
        cmd.extend(['/on-file-change={0}'.format(OnFileChangeAction_List[OnFileChangeAction])])

    if OnTimerAction>=0 or OnTimerAction<=2:
        cmd.extend(['/on-timer={0}'.format(OnTimerAction_List[OnTimerAction])])
        if (OnTimerAction==0 or OnTimerAction==1) and TimerIntervalMinutes>0:
            cmd.extend(['/timer-period='+str(TimerIntervalMinutes)])

    if AutoResolveConflicts>=0 or AutoResolveConflicts<=3:
        cmd.extend(['/autoresolve={0}'.format(AutoResolveConflicts_List[AutoResolveConflicts])])

    if DetectMovesAndRenames == 0:
        cmd.extend(['/detect=folder-moves=yes /detect-moves=yes'])
    elif DetectMovesAndRenames == 1:
        cmd.extend(['/detect=folder-moves=no /detect-moves=no'])

    if UberUnlockedUpload==0 or UberUnlockedUpload==1:
        cmd.extend(['/uber-unlocked={0}'.format(UberUnlockedUpload_List[UberUnlockedUpload])])

    return _run_cmd(cmd)

def joblist():
    '''
     List all job
     Example: salt '*' xjoker_goodsync.joblist
    :return:
    '''
    cmd=['job-list']
    return _run_cmd(cmd)

def jobdelete(jobname):
    '''
    Delete existing job.
    Example: salt '*' xjoker_goodsync.jobdelete jobName
    :param jobname: job name
    :return:
    '''
    if jobname == None:
        return "Jobname is null."
    cmd=['job-delete',str(jobname)]
    return _run_cmd(cmd)

def jobanalyzeall():
    '''
    Analyze all jobs
    :return:
    '''
    cmd=['analyze','/all']
    return _run_cmd(cmd)

def jobsyncall():
    '''
    Synchronize all jobs
    :return:
    '''
    cmd=['sync','/all']
    return _run_cmd(cmd)