# -*- coding:utf-8 -*-
# write by Enzo
# mail: Enzohx@163.com


import atexit
from pyVmomi import vim
from pyvim.connect import SmartConnect, Disconnect
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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


def sizeof_fmt(num):
    return "%.1f" % (float(num) / 1024**3)

def ds_beat(host, user, pwd, port):

    si = SmartConnect(
        host=host,
        user=user,
        pwd=pwd,
        port=port)
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    ds_obj_list = get_obj(content, [vim.Datastore], None)
    info_list = []
    for ds_obj in ds_obj_list:
        ds = {}
        summary = ds_obj.summary
        ds_capacity = summary.capacity
        ds_freespace = summary.freeSpace
        ds_uncommitted = summary.uncommitted if summary.uncommitted else 0
        ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
        ds['bk_stora_name'] = summary.name
        ds['bk_stora_cap'] = sizeof_fmt(ds_capacity)
        ds['bk_free_spa'] = sizeof_fmt(ds_freespace)
        ds['bk_prem_spa'] = sizeof_fmt(ds_provisioned)
        ds['bk_stora_path'] = summary.url
        info_list.append(ds)
        #补充数据获取
    objview = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    esxi_hosts = objview.view
    objview.Destroy()
    for esxi_host in esxi_hosts:
        # 遍历所有主机挂载的存储节点
        storage_system = esxi_host.configManager.storageSystem
        host_file_sys_vol_mount_info = storage_system.fileSystemVolumeInfo.mountInfo
        for host_mount_info in host_file_sys_vol_mount_info:
            for ds in info_list:
                if ds['bk_stora_name'] == host_mount_info.volume.name:
                    ds['bk_file_system'] = host_mount_info.volume.type + host_mount_info.volume.version
                    ds['bk_fs_block'] = host_mount_info.volume.blockSizeMb
                    ds['bk_dir_type'] = 'HDD' if host_mount_info.volume.ssd else 'SSD'

    return info_list


if __name__ == '__main__':
    print(ds_beat('192.168.51.20', 'administrator@vsphere.local', '12345.Asd', 443))