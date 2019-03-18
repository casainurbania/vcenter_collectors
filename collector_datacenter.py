#coding=utf-8

import atexit
from pyVmomi import vim, vmodl
from pyvim.connect import SmartConnectNoSSL, Disconnect

def format_size(num,time, decimal):
    return round(num/time, decimal)

def getComputeResource(Folder,computeResourceList): #遍历文件夹
    if hasattr(Folder, 'childEntity'):
        for computeResource in Folder.childEntity:
           getComputeResource(computeResource,computeResourceList)
    else:
        computeResourceList.append(Folder)
    return computeResourceList


def run(host,user,pwd,port):

    try:
        si = SmartConnectNoSSL(host=host, user=user, pwd=pwd, port=port)
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        datacenter_info_list = []
        for datacenter in content.rootFolder.childEntity:
            D = {'name': datacenter.name}
            # print "datacenter =", datacenter.name
            if hasattr(datacenter.hostFolder, 'childEntity'):
                hostFolder = datacenter.hostFolder
                computeResourceList = []
                computeResourceList = getComputeResource(hostFolder, computeResourceList)
                for computeResource in computeResourceList:
                    if isinstance(computeResource, vim.ClusterComputeResource): #只收集集群资源
                        D['cl_name'] = computeResource.name
                        D['cl_cpu_capacity'] = 0
                        D['cl_cpu_used'] = 0
                        D['cl_mem_capacity'] = 0
                        D['cl_mem_used'] = 0
                        D['cl_storage_capacity'] = 0
                        D['cl_storage_used'] = 0
                        for host in computeResource.host:
                            D['cl_cpu_capacity'] += format_size(host.summary.hardware.cpuMhz * host.summary.hardware.numCpuCores, 1000, 2)   # GHz
                            D['cl_cpu_used'] += format_size(host.summary.quickStats.overallCpuUsage, 1000, 2)    # GHz
                            D['cl_mem_capacity'] += format_size(host.summary.hardware.memorySize, 1000, 2)   # GB
                            D['cl_mem_used'] += format_size(host.summary.quickStats.overallMemoryUsage, 1000, 2)  # GB
                        #  计算每个数据中心的存储情况
                        for ds in computeResource.datastore:  #获取该集群下的所有数据存储点名称
                            D['cl_storage_capacity'] += format_size(ds.summary.capacity, 1024**4, 2)    # TB
                            D['cl_storage_used'] += format_size(ds.summary.freeSpace, 1024**4, 2)   # TB
                        D['cl_storage_used'] = D['cl_storage_capacity'] - D['cl_storage_used']
            datacenter_info_list.append(D)
        print datacenter_info_list
#######################################################################################
        # ds_list = []
        # ds_obj_list = get_obj(content, [vim.Datastore],)
        # for ds in ds_obj_list:
        #     ds_list.append({'name':ds.name, 'related':[], 'capacity': ds.summary.capacity / 1024.0**3})
        #     for host in ds.host:
        #         ds_list[-1]['related'].append(host.key.name)
        #
        # #计算每个ESXI关联磁盘总容量
        # for esxi in esxi_list_info:
        #     esxi['capacity'] = 0.00
        #     for ds in ds_list:
        #         for i in ds['related']: #在DS中匹配ESXI
        #             if i == esxi['name']:
        #                 esxi['capacity'] += ds['capacity']  #累加挂载点上的存储容量
        #                 break

        return None

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return False, error.msg


#获取数据中心
if __name__ == "__main__":
    host = "192.168.51.20"
    user = "administrator@vsphere.local"
    pwd = "12345.Asd"
    port = 443

    run(host, user, pwd, port)