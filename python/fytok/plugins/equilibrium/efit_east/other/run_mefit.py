#!/usr/bin/env python
# Originally programmed by Chenguang Wan on 2022.06.20 
# Based on Luo Zhengpin's matlab scripts
import subprocess
import sys
import os
import shutil
import time
import numpy as np
import pandas as pd
# from private_modules.EFIT_tools.writek_k import writek
from fytok.plugins.equilibrium.efit.other.writek_k import writek
import multiprocessing as mp
import math
from typing import Optional

def mp_run_mefit_df(shot_times_path, num_workers:int=1, run_efit_dir:Optional[str]=None):
    df = pd.read_csv(shot_times_path)
    shots = np.unique(df.loc[:, "shot"])
    np.random.shuffle(shots)
    pros = []
    per_shot_num = math.ceil(len(shots) / num_workers)
    if run_efit_dir is not None:
        os.chdir(run_efit_dir)
    for i in range(num_workers):
        map_shots = shots[i*per_shot_num:min((i+1) * per_shot_num, len(shots))]
        times_list = []
        for shot in map_shots:
            ids = df.loc[:, "shot"] == shot
            times = df.loc[ids, "time"].tolist()
            times = np.asarray(times, dtype=np.float64)
            times_list.append(times)
        p = mp.Process(target=run_mefit_shots, 
        args=(map_shots, times_list))
        p.start()
        pros.append(p)
    for p in pros:
        p.join()

def run_mefit_df(shot_times_path, run_efit_dir:Optional[str]=None):
    """  shot_times {"shot": List[int], "time": List(float)}
    """
    if run_efit_dir is not None:
        os.chdir(run_efit_dir)
    df = pd.read_csv(shot_times_path)
    shots = np.unique(df.loc[:, "shot"])
    for shot in shots:
        ids = df.loc[:, "shot"] == shot
        times = df.loc[ids, "time"].tolist()
        times = np.asarray(times, dtype=np.float64)
        run_mefit(shot, times)

def run_mefit_shots(shots, times_list):
    """ run mefit on shot batch way.  
    """
    for shot, times in zip(shots, times_list):
        run_mefit(shot, times)

def run_mefit(shot, times, snap_file:Optional[str]=False):
    # snap_filepath = '/ssd01/liuxj_work/workspace_flow/spdb_for_efit/snap_files/'
    # /scratch/liuxj/01_work_2022/sources/efit-service108/EFIT_tools/snap_files
    if (shot <= 44326 and shot > 4774):
        snap_file = snap_filepath + "snap.nam_12"
        efitd = 'efitd129d_east_2010'
    elif (shot > 44326 and shot <= 52804):
        snap_file = snap_filepath + "snap.nam_14"
        efitd = 'efitd129d_east_2014'
    elif (shot > 52804 and shot <= 96915):
        snap_file = snap_filepath + "snap.nam_15"
        efitd = 'efitd129d_east_2015'
    elif (shot > 96915):
        snap_file = snap_filepath + "snap.nam_21"
        efitd = 'efitd129d_east_2021'
    else:
        raise Exception("no such shot")
    
    # retrieving mds+ data for PCS_EAST
    if not os.path.isdir(str(shot)):
        os.mkdir(str(shot))
    else:
        dirname = os.getcwd()
        existed_path = os.path.join(dirname, "%d"%shot)
        print("The %s is already exists \nPlease Check again."%existed_path)
        return
    os.chdir(str(shot))

    writek(shot, times, snap_file)
    runefitm(shot, times, efitd)
    
def run_command(cmd, check=False, timeout=None, shell=False, log=True):

    # @ref: https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
    # if isinstance(cmd, str) and not shell:
    #     cmd = shlex.split(cmd)
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            encoding="utf-8"
        )
        proc_stdout, proc_stderr = process.communicate(timeout=None)
        # for line in proc_stdout :  # b'\n'-separated lines
        #     logger.info(line)

    except subprocess.TimeoutExpired as e:
        os.killpg(process.pid, signal.SIGKILL)
        raise RuntimeError(e.cmd,
                           process.stdout.read(),
                           process.stderr.read(), timeout) from None
        # process_output, _ = command_line_process.communicate()
    completed = subprocess.CompletedProcess(cmd,
                                            returncode=process.returncode,
                                            stdout=proc_stdout,
                                            stderr=proc_stderr)
    if check and process.returncode != 0:
        raise process.subprocessCalledProcessError(completed.args,
                                                   completed.stdout, completed.stderr,
                                                   completed.returncode)
    return completed


def run_mefit_liuxj(shot,times,mdsdata,efit_snap:str|bool=False):
# (shot, times, snap_file:Optional[str]=False):
    snap_filepath = '/ssd01/liuxj_work/workspace_flow/spdb_for_efit/snap_files/'
    # /scratch/liuxj/01_work_2022/sources/efit-service108/EFIT_tools/snap_files
    if (shot <= 44326 and shot > 4774):
        efit_snap = snap_filepath + "snap.nam_12"
        efit_exec = 'efitd129d_east_2010'
    elif (shot > 44326 and shot <= 52804):
        efit_snap = snap_filepath + "snap.nam_14"
        efit_exec = 'efitd129d_east_2014'
    elif (shot > 52804 and shot <= 96915):
        efit_snap = snap_filepath + "snap.nam_15"
        efit_exec = 'efitd129d_east_2015'
    elif (shot > 96915):
        efit_snap = snap_filepath + "snap.nam_21"
        efit_exec = 'efitd129d_east_2021'
    else:
        raise Exception("no such shot")
    
    # retrieving mds+ data for PCS_EAST
    if not os.path.isdir(str(shot)):
        os.mkdir(str(shot))
    else:
        dirname = os.getcwd()
        existed_path = os.path.join(dirname, "%d"%shot)
        print("The %s is already exists \nPlease Check again."%existed_path)
        time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
        new_path = os.path.join(dirname, "%d_%s"%(shot,time_now))
        shutil.move(existed_path, new_path)
        print("The %s is already is moved to %s \nPlease notice it."%(existed_path, new_path))
        os.mkdir(str(shot))
        # return
    os.chdir(str(shot))
    times = eval(times)
    times = np.atleast_1d(times)
    writek(shot, times, efit_snap,mdsdata)
    output_dir = runefitm(shot, times, efit_exec)
    return output_dir
    



    

def runefitm(shot, times, efitcall):
    """Script to run efit in batch mode 
    
    re-WRITTEN by rrzhang 09/06/2015
    Updated by Chenguang Wan 2022.06.20
    Updated by Xiaojuan Liu 2023.09.05"""

    
     
    print('shot number = %d'%shot)
    print('time slices: ', times)
    ntimes = times.size
    print('=================================================================')
    print('Beginning to call EFID129D ......')
    print('the ntimes is : ', ntimes)
    output_dir = []
    for i in range(ntimes):
        try:
            itime = int(times[i]*1000)
            print('the itime1 is : ', itime)
            #efit_snap = 'k%d.%d'%(shot, itime)
            sshot = str(shot).zfill(6)
            stime = str(itime).zfill(5)
            print('the sshot amd stime is : ', sshot, stime)
            efit_snap = 'k' + sshot + '.' + stime
            print('the efit_snap is : ', efit_snap)
            dirname = os.getcwd()
            new_path = os.path.join(dirname, "%s_%s"%(sshot,stime))
            print('the new_path is : ', new_path)
            os.mkdir(new_path)

            print('the efit_snap of efit is ',efit_snap)
            shutil.copyfile(efit_snap, new_path+'/temp')
            print('the exec1 of efit is ',efitcall)
            os.chdir(new_path)
            # os.mkdir(str(shot))
            cmd1 = "source /ssd01/liuxj_work/workspace_flow/spdb_for_efit/EFIT_tools/efit_bash"
            
            cmds = cmd1 + " && " + efitcall
            ## run cmd1 and efitcall togater
            subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print('the exec1 of efit is ',efitcall)
            output_dir.append(new_path)
            os.chdir("..")
        except:
            continue
    dirname = os.path.dirname(os.path.abspath(efit_snap))
    dirname = os.path.dirname(dirname)
    os.chdir(dirname)
    print('the output_dir  is : ', dirname)
    print('=================================================================')
    print('All time slice EQ has been done')
    return output_dir


def run_kfile_shot(shot, kfile):
    """Script to run efit by kfile and shot setting.
    Writen by Chenguang Wan 2022.06.21"""
    if (shot <= 44326 and shot > 4774):
        efitd = 'efitd129d_east_2010'
    elif (shot > 44326 and shot <= 52804):
        efitd = 'efitd129d_east_2014'
    elif (shot > 52804 and shot <= 96915):
        efitd = 'efitd129d_east_2015'
    elif (shot > 96915):
        efitd = 'efitd129d_east_2021'
    else:
        raise Exception("no such shot")
    runKfile(kfile, efitd)

def runKfile(kfile, efitcall):
    """Script to run efit by kfile
    Writen by Chenguang Wan 2022.06.20"""
    shutil.copyfile(kfile, "temp")
    os.system(efitcall)
        
    
    
if __name__ == "__main__":
    import numpy as np
    argv = sys.argv
    # argv = ["run_mefit.py", '66740' ,'3.5']
    if(len(argv) < 2 or len(argv) > 5):
        print("please using:\n  run_mefit.py shot 'timeslices' [snap_file]")
        print("Example: run_mefit.py 66740 '13.5, 14.5'")
    elif len(argv) == 2:
        shot_times_path = argv[1]
        run_mefit_df(shot_times_path)
    else:
        shot = int(eval(argv[1]))
        times = argv[2]
        if ":" in times:
            args = times.split(":")
            args = map(float, args)
            times = np.arange(args[0], args[1], args[2])
        else:
            times = eval(times)
            times = np.atleast_1d(times)
        if (len(argv) == 4):
            snap_file = argv[3]
        else:
            snap_file = False
#        try:
#            run_mefit(shot, times, snap_file)
#        except Exception, e:
#            print(str(e))
#	
        run_mefit(shot, times, snap_file)
