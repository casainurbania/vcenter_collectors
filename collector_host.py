#coding=utf-8

import atexit
from pyVmomi import vim, vmodl
from pyvim.connect import SmartConnectNoSSL, Disconnect

def get_obj(content, vim_type, name=None):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return [obj]
    else:
        return container.view

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
        esxi_list_info = []
        for datacenter in content.rootFolder.childEntity:
            # print "datacenter =", datacenter.name
            if hasattr(datacenter.hostFolder, 'childEntity'):
                hostFolder = datacenter.hostFolder
                computeResourceList = []
                computeResourceList = getComputeResource(hostFolder, computeResourceList)
                for computeResource in computeResourceList:
                    for host in computeResource.host:
                        # print '='*100
                        esxi_list_info.append(
                        {
                            'name': host.name,     #主机名
                            'type': host.summary.hardware.vendor + ' ' + host.summary.hardware.model,  #主机型号
                            'version': host.summary.config.product.fullName,    #管理程序版本
                            'ip': host.name,                    #管理IP地址
                            'logic_core': host.summary.hardware.numCpuThreads,   #cpu逻辑核心数
                            'cpy_type': host.summary.hardware.cpuModel,    #cpu型号
                            'cpu_freq': host.summary.hardware.cpuMhz * host.summary.hardware.numCpuCores /1000.00,  #cpu频率GHz
                            'mem': '%.2f' % (host.summary.hardware.memorySize / 1024.0 ** 3)  #内存GB
                            # host.summary.quickStats  #使用状态简要指标
                            # host.summary.quickStats.overallCpuUsage / 1000.0  #CPU已用频率 GHz
                        })
        ds_list = []
        ds_obj_list = get_obj(content, [vim.Datastore],)
        for ds in ds_obj_list:
            ds_list.append({'name':ds.name, 'related':[], 'capacity': ds.summary.capacity / 1024.0**3})
            for host in ds.host:
                ds_list[-1]['related'].append(host.key.name)
        print ds_list

        #计算每个ESXI关联磁盘总容量
        for esxi in esxi_list_info:
            esxi['capacity'] = 0.00
            for ds in ds_list:
                for i in ds['related']: #在DS中匹配ESXI
                    if i == esxi['name']:
                        esxi['capacity'] += ds['capacity']  #累加挂载点上的存储容量
                        break

        return esxi_list_info

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return False, error.msg



if __name__ == "__main__":
    host = "192.168.51.20"
    user = "administrator@vsphere.local"
    pwd = "12345.Asd"
    port = 443

    print(run(host, user, pwd, port))