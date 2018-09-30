# -*- coding:utf-8 -*-
import atexit
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
from tools import pchelper
#  IT'S FROM  https://github.com/vmware/pyvmomi-community-samples/tree/master/samples/tools
#  NOT PIP INSTALL!!!
import time

def getComputeResource(Folder,computeResourceList): #递归遍历文件系统
    if hasattr(Folder, 'childEntity'):
        for computeResource in Folder.childEntity:
           getComputeResource(computeResource,computeResourceList)
    else:
        computeResourceList.append(Folder)
    return computeResourceList

def vm_beat(host,user,pwd,port):
    try:
        si = SmartConnectNoSSL(host=host, user=user, pwd=pwd, port=port) #免SSL证书连接
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        view = pchelper.get_container_view(si, obj_type=[vim.VirtualMachine])  #多维度数据需要从不同视图获取
        vm_data = pchelper.collect_properties(si, view_ref=view, obj_type=vim.VirtualMachine, include_mors=True) #path_set=vm_properties
        obj = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True) #多维度数据需要从不同视图获取
        #将vm信息填到字典中
        info = {}
        for vm in obj.view:
            # print(vm.name)
            # print('=' * 100)
            # print ('collecting...')
            info[vm.name] = {}
            info[vm.name]['cpu_MHz'] = vm.summary.quickStats.staticCpuEntitlement / 1024  # GHZ
            info[vm.name]['os'] = vm.summary.config.guestFullName
            info[vm.name]['vm_tools_status'] = vm.summary.guest.toolsStatus
            info[vm.name]['ip'] = vm.summary.guest.ipAddress
            for dev in vm.config.hardware.device:
                if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                    info[vm.name]['mac'] = dev.macAddress
        for vm in vm_data:
            #计算该虚拟机所有磁盘容量之和
            disk_total = 0
            # print vm['name']
            for device in vm["config"].hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    disk_total += int(device.deviceInfo.summary[0:-2].replace(",", ""))
            info[vm["name"]]["disk_GB"] = disk_total / 1024**2  # GB
            info[vm["name"]]["memory_MB"] = (vm["config"].hardware.memoryMB) / 1024  # GB
            info[vm["name"]]["cpu_num"] = vm["config"].hardware.numCPU
    # #TODO 追查具有两个mac地址的虚拟机那个是网卡以及如何赋值
    # overallCpuUsage = 139,（单位MHz）
    # guestMemoryUsage = 327 指标是内存使用情况
    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return False, error.msg
    return info

if __name__ == '__main__':
    host = "192.168.51.20"
    user = "administrator@vsphere.local"
    pwd = "123456.Asd"
    port = 443

    print(vm_beat(host, user, pwd, port))
