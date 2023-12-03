import pprint
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from spdm.utils.logger import logger
from spdm.data.open_entry import open_entry
from spdm.data.Collection import Collection
    # db: Collection = open_db("mdsplus[EAST]://202.127.204.12")


os.environ["SP_DATA_MAPPING_PATH"]="/ssd01/liuxj_work/workspace_flow/fytok/python/fytok/_mapping"

# entry = open_entry("file+mdsplus[EAST]:///scratch/liuxj/01_work_2022/data/fytok_data/mdsplus/~t/?tree_name=efit_east#38300")
# pf_active = entry.get("pf_active")
# magnetics = entry.get("magnetics")
# wall = entry.get("wall")

def read_idsdata(shotnum,treename,idsname):
    DATA_PATH="/ssd01/liuxj_work/workspace_flow/fytok_data"
    mdspath = DATA_PATH+"/mdsplus"
    if treename == None:
        treename ="efit_east"
    # entry = open_entry(f"file+MDSplus[EAST]://{DATA_PATH}/mdsplus/~t/?tree_name=efit_east#70745")
    entry = open_entry("file+MDSplus[EAST]://"+mdspath+"/~t/?tree_name="+treename+"#"+str(shotnum))
    ids = entry.child(idsname)
    
    return ids



def read_idsdata_eq(mdspath,shotnum,treename,time_slice):
    
    entry = open_entry("file+mdsplus[EAST]://"+mdspath+"/~t/?tree_name="+treename+"#"+str(shotnum))
    # ids = entry.get(idsname)
    # time_slice=time_slice
    equilibrium= entry.get(["equilibrium", "time_slice", time_slice]).dump()
    equilibrium["vacuum_toroidal_field"] = {
        "b0": entry.get(["equilibrium", "vacuum_toroidal_field", "b0"])[time_slice],
        "r0": entry.get(["equilibrium", "vacuum_toroidal_field", "r0"])[time_slice],
    }
    
    equilibrium["time"] = entry.get(["equilibrium", "time"])[time_slice]   
    
    return equilibrium

class Data(object):
    def __init__(self):
        pass
    
def get_eastdata_from_spdb_remote(treename,shotnum):
    
    # # shotnum=70758
    # # treename = "pcs_east"
    # mds_server = "202.127.204.12"
    # # entry = open_entry("mdsplus[EAST]://"+mds_server+"#"+str(shotnum))
    # entry = open_entry("mdsplus[EAST]://"+mds_server+"?tree_name="+treename+"#"+str(shotnum))
    mdsdata = Data()
    # fl is flux_loop in magnetics
    mdsdata.fl = []
    ### read from local mds
    # magnetics = read_idsdata(mdspath,shotnum,"pcs_east","magnetics").dump()
    #### read from remote mds
    # magnetics = read_idsdata_remote(shotnum,"pcs_east","magnetics").dump()
    magnetics = read_idsdata(shotnum,"pcs_east","magnetics")
    magnetics = magnetics.fetch()
    nfl = 35 
    if (nfl == len(magnetics['flux_loop'])):
        for i in range(len(magnetics['flux_loop'])):
            # logger.debug(i)
            mdsdata.fl.append(magnetics['flux_loop'][i]["flux"]["data"])
        logger.debug(len(mdsdata.fl))
    else:
        logger.debug("the num of flux_loop less for 35")
    # bp is bpol_probe in magnetics
    mdsdata.bp = []
    nbp = 38
    if (nbp == len(magnetics['bpol_probe'])):
        for i in range(len(magnetics['bpol_probe'])):
            mdsdata.bp.append(magnetics['bpol_probe'][i]["field"]["data"])
    else:
        logger.debug("the num of bpol_probe less for 38")
    
    ## IP
    mdsdata.ip = [magnetics['ip']['data']]
    mdsdata.tmds = magnetics['ip']['time']

    # ifc that is PF(nfs) which = pf current * turnfc in pf_active
    nfc = 12
    mdsdata.ifc = []
    
    ### read from local mds
    # pf_active = read_idsdata(mdspath,shotnum,"pcs_east","pf_active").dump()
    #### read from remote mds
    # pf_active = read_idsdata_remote(shotnum,"pcs_east","pf_active").dump()
    # pf_active = entry.get("pf_active").dump()
    # pf_active = read_idsdata_remote(70754,"pcs_east","pf_active").dump()
    # logger.debug(pf_active.get(["pf_active"]).dump()['coil'][14])
    pf_active = read_idsdata(shotnum,"pcs_east","pf_active")
    pf_active = pf_active.fetch()
    turns=[]
    turns_new = []
    current = []
    if (nfc == (len(pf_active['coil'])-4)):
        for i in range(len(pf_active['coil'])-2):
            turns.append(pf_active['coil'][i]['element']['turns_with_sign'])
            # 
        logger.debug(turns)
        for i in range(len(turns)-2):
            if i<6:
                turns_new.append(turns[i])
            if i==6 or i ==7:
                turns_new.append(turns[i]+turns[i+2])
            if i>7:
                print(i)
                turns_new.append(turns[i+2])
        logger.debug(turns_new) 
        logger.debug(pf_active['coil'][12]['current']['data'])
        for i in range(12):
            logger.debug(i)
            if i <8:
                current = pf_active['coil'][i]['current']['data']
            else:
                logger.debug(i)
                current = pf_active['coil'][i+2]['current']['data']
            logger.debug(current)    
            mdsdata.ifc.append(current * turns_new[i]    )

        logger.debug(len(mdsdata.ifc))
        
    else:
        logger.debug("the num of bpol_probe less for 12")
    logger.debug(mdsdata.ifc)
    ## it is tf current in east tree for tf
    ### for local mds
    # tf = read_idsdata(mdspath,shotnum,"east[t1,t2,t3,t4,t5,t6]","tf").dump()
    ### for remote mds:
    mdsdata.it = 8000
    # tf = entry.get("tf").dump()
    # # tf = read_idsdata_remote(shotnum,"east","tf").dump()
    # ## just for FOCS4 which shot is (shot > 65321 and shot < 75976)
    # it = tf['coil']['current']["data"]
    # idx, = np.where(np.abs(it)>1000)
    # if idx.size:
    #     mdsdata.it = np.mean(it[idx])
    # else:
    #     logger.debug('Waning: cannot get the IT current, set as 8 kA.')
    #     logger.debug('Though EFIT will be running, the results are incorrect.')
    #     mdsdata.it = 8000
    return mdsdata
        
if __name__ == "__main__":
    # mdspath = "/scratch/liuxj/01_work_2022/data/fytok_data/mdsplus"
    # shotnum = 70754
    treename = "pcs_east"
    DATA_PATH="/ssd01/liuxj_work/workspace_flow/fytok_data"
    shotnum = 70754
    mdspath = DATA_PATH+"/mdsplus"
    mdsdata = get_eastdata_from_spdb_remote(mdspath,treename,shotnum)
    logger.debug(len(mdsdata.ifc))
    