# -*- coding:utf-8 -*-
from pyVmomi import vim,vmodl
from pyvim.connect import SmartConnect, Disconnect
import atexit
import sys
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

lb_mode = {
    'failover_explicit': '使用明确故障切换顺序',
    'loadbalance_ip': '基于IP哈希的路由',
    'loadbalance_loadbased': '基于源虚拟端口的路由',
    'loadbalance_srcid': '基于源IP哈希的路由',
    'loadbalance_srcmac': '基于源MAC哈希的路由',
}

class VCenter:
    def __init__(self):
        self.pyVmomi = __import__("pyVmomi")
        self.vcenter_server = '192.168.51.20'
        self.vcenter_username = 'administrator@vsphere.local'
        self.vcenter_password = '12345.Asd'
        self.port = 443
        # self.isDHCP=False,
        # self.vm_ip = '10.7.42.91',
        self.subnet = '255.255.255.0',
        # self.gateway= '10.7.42.40',
        # self.dns= ['company.com', 'company.com'],
        # self.domain= 'esx10g.company.com'

    def connect_to_vcenter(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        self.service_instance = SmartConnect(
                                        host = self.vcenter_server,
                                        user = self.vcenter_username,
                                        pwd = self.vcenter_password,
                                        port = self.port,
                                        sslContext = context)
        self.content = self.service_instance.RetrieveContent()
        atexit.register(Disconnect, self.service_instance)

    def wait_for_task(self, task, actionName='job', hideResult=False):
         while task.info.state == (self.pyVmomi.vim.TaskInfo.State.running or self.pyVmomi.vim.TaskInfo.State.queued):
             time.sleep(2)
         if task.info.state == self.pyVmomi.vim.TaskInfo.State.success:
             if task.info.result is not None and not hideResult:
                 out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                 print out
             else:
                 out = '%s completed successfully.' % actionName
                 print out
         elif task.info.state == self.pyVmomi.vim.TaskInfo.State.error:
             out = 'Error - %s did not complete successfully: %s' % (actionName, task.info.error)
             raise ValueError(out)
         return task.info.result


    def list_obj(self, vimtype):
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimtype, True)
        return container.view

    def get_obj(self, vimtype, name):
        obj = None
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    def get_folder(self, folder_name=''):
        """获取文件夹"""
        folder_list = []
        if folder_name == '':
            listOBJ = self.list_obj([vim.Folder])
        else:
            listOBJ = self.get_obj([vim.Folder],folder_name)
        for each in listOBJ:
            folder_list.append(each)
        return folder_list

    def get_vcenters(self):
        """获取所有数据中心"""
        listOBJ = self.list_obj([vim.Datacenter])
        vcenters_list = []
        for each in listOBJ:
            vcenters_list.append(each)
        return each


    def get_datastore(self, datastore_name=''):
        """获取存储"""
        datastore_list = []
        if datastore_name == '':
            listOBJ = self.list_obj([vim.Datastore])
        else:
            listOBJ = self.get_obj([vim.Datastore],datastore_name)
        for each in listOBJ:
            datastore_list.append(each.name)
        return datastore_list

    def get_clusters(self,clusters_name=''):
        """获取所有的集群"""
        clusters_list = []
        if clusters_name == '':
            listOBJ = self.list_obj([vim.ClusterComputeResource])
        else:
            listOBJ = self.get_obj([vim.ClusterComputeResource],clusters_name)
        for each in listOBJ:
            clusters_list.append(each.name)
        return clusters_list

    def get_resource_pool(self,resource_pool_name=''):
        """获取所有的资源池"""
        resource_pool_list = []
        if resource_pool_name == '':
            listOBJ = self.list_obj([vim.ResourcePool])
        else:
            listOBJ = self.get_obj([vim.ResourcePool],resource_pool_name)
        for each in listOBJ:
            resource_pool_list.append(each.name)
        return resource_pool_list

    def get_hosts(self):
        """获取所有的宿主机"""
        listOBJ = self.list_obj([vim.HostSystem])
        index = 0
        for each in listOBJ:
            tupleVNic=sys._getframe().f_code.co_name, index, each.config.network.vnic
            for eachvnic in tupleVNic[2]:
                index = index + 1
                print sys._getframe().f_code.co_name, \
                    index, \
                    each, \
                    eachvnic.portgroup, \
                    eachvnic.spec.mac, \
                    eachvnic.spec.ip.ipAddress, eachvnic.spec.ip.subnetMask

    def get_pnic(self):
        """获取所有的上行口"""
        listOBJ = self.list_obj([vim.HostSystem])
        index = 0
        for each in listOBJ:
            tuplePNic=sys._getframe().f_code.co_name, index, each.config.network.pnic
            for eachpnic in tuplePNic[2]:
                index = index + 1
                print sys._getframe().f_code.co_name, index, each, eachpnic.device

    def get_vswitchs(self):
        """获取所有的交换机（包括标准交换机和分布式交换机)"""
        return self.list_obj([vim.HostSystem])




    def get_portgroups(self):
        """获取所有的交换机端口组（包括标准交换机和分布式交换机)"""
        listOBJ = self.list_obj([vim.Network])

        for each in listOBJ:

            print sys._getframe().f_code.co_name, each

    def get_vns(self):
        """获取所有的虚拟网络（包括标准交换机端口组和分布式交换机端口组)"""
        try:
            return self.list_obj([vim.Network])

        except Exception as e:
            print e

    def get_dvswitchs(self):
        """获取所有的分布式交换机"""
        return self.list_obj([vim.DistributedVirtualSwitch])


    def get_dvportgroups(self):
        """获取所有的分布式交换机端口组"""
        listOBJ = self.list_obj([vim.DistributedVirtualSwitch])
        index = 0
        for each in listOBJ:
            for eachportgroup in each.portgroup:
                index = index + 1
                print sys._getframe().f_code.co_name,index,eachportgroup

    def get_vnic(self):
        """获取所有的虚拟网卡"""
        listOBJ = self.list_obj([vim.VirtualMachine])
        index = 0
        for each in listOBJ:
            index = index + 1
            vmdeviceList = each.config.hardware.device
            for eachdevice in vmdeviceList:
                index = index + 1
                if isinstance(eachdevice, vim.vm.device.VirtualEthernetCard ):
                    if isinstance( eachdevice.backing,vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo ):
                        print sys._getframe().f_code.co_name,\
                            index, \
                            eachdevice.deviceInfo.label, \
                            eachdevice.macAddress, \
                            eachdevice.deviceInfo.summary, \
                            eachdevice.backing.port.portgroupKey
                    else:
                        print sys._getframe().f_code.co_name,\
                            index, \
                            eachdevice.deviceInfo.label, \
                            eachdevice.macAddress, \
                            eachdevice.backing.deviceName, \
                            eachdevice.backing.network

    def get_allvms(self):
        """获取所有的虚机"""
        listOBJ = self.list_obj([vim.VirtualMachine])
        index = 0
        for each in listOBJ:
            index = index + 1
            print sys._getframe().f_code.co_name,index,each.name

    def print_vm_info(self, virtual_machine, depth=1):
        """打印虚机信息"""
        maxdepth = 10
        if hasattr(virtual_machine, 'childEntity'):
            if depth > maxdepth:
                return
            vmList = virtual_machine.childEntity
            for c in vmList:
                self.print_vm_info(c, depth + 1)
            return
        summary = virtual_machine.summary
        print "Name       : ", summary.config.name
        print "Path       : ", summary.config.vmPathName
        print "Guest      : ", summary.config.guestFullName
        annotation = summary.config.annotation
        if annotation:
            print "Annotation : ", annotation
        print "State      : ", summary.runtime.powerState
        if summary.guest is not None:
            ip_address = summary.guest.ipAddress
            if ip_address:
                print "IP         : ", ip_address
        if summary.runtime.question is not None:
            print "Question  : ", summary.runtime.question.text
        print ""

    def get_acquireTicket(self,virtual_machine):
        """获取主机Console授权"""
        acquireTickets_dict = {}
        listOBJ = self.get_obj([vim.VirtualMachine],virtual_machine)
        try:
            acquireTickets = listOBJ.AcquireTicket('webmks')
        except Exception as err:
            print 'acquireTickets_err:',err
        acquireTickets_dict['host'] = acquireTickets.host
        acquireTickets_dict['port'] = acquireTickets.port
        acquireTickets_dict['ticket'] = acquireTickets.ticket
        print acquireTickets_dict
        return acquireTickets_dict

    def get_hosts_exsi_version(self,virtual_machine):
        """获得主机Esxi版本"""
        try:
            hosts_name = self.get_obj([vim.VirtualMachine],virtual_machine).summary.runtime.host
            for i in self.list_obj([vim.HostSystem]):
                if i == hosts_name:
                    hosts_ip = i.name
            listOBJ = self.get_obj([vim.HostSystem],hosts_ip)
            try:
                exsi_version = listOBJ.summary.config.product.fullName
            except Exception as err:
                print err
                exsi_version = ''
        except Exception as err:
            print err
            exsi_version = ''
        return exsi_version

#  TODO:1 在整合到项目时，建议封装成类，引入类使用
#  TODO:2 可根据实际需求重写类方法

if __name__ == '__main__':
    v = VCenter()
    v.connect_to_vcenter()

    vs_list = []

    listOBJ = v.get_vswitchs()
    for each in listOBJ:
        v = each.config.network.vswitch[0]
        vs_list.append({
                'name': v.name,
                'type': '标准交换机' if isinstance(v, vim.host.VirtualSwitch) else '分布式交换机',
                'vlan_id': '-1',
                'MTU': v.mtu,
                'lb_mode': lb_mode[v.spec.policy.nicTeaming.policy],
                'failure_criteria': '信标探测' if v.spec.policy.nicTeaming.failureCriteria.checkBeacon else '仅链路状态',
            })


    v = VCenter()
    v.connect_to_vcenter()
    listOBJ = v.get_dvswitchs()

    for each in listOBJ:
        vs_list.append({
        'name': each.name,
        'type': '标准交换机' if isinstance(each.config, vim.dvs.VmwareDistributedVirtualSwitch.ConfigInfo) else '\n',
        'vlan_id': each.config.defaultPortConfig.vlan.vlanId,
        #  TODO 判断区分vlan 和 trunk类型
        'mtu': each.config.maxMtu,
        'lb_mode': lb_mode[each.config.defaultPortConfig.uplinkTeamingPolicy.policy.value],
        'failure_criteria': '信标探测' if each.config.defaultPortConfig.uplinkTeamingPolicy.failureCriteria.checkBeacon.value
            else '仅链路状态'
        })
    print vs_list
#######################################


if __name__ == '__main__':
    v=VCenter
    print VCenter.get_clusters()
