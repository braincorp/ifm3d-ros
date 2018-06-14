#!/usr/bin/python

import subprocess
import os
import signal
import time
import sys

camera_name_ip = {'left': '192.168.1.2', 'right': '192.168.2.2', 'center': '192.168.0.2'}
camera_name_json = {'left': 'ifm_left.json', 'right': 'ifm_right.json', 'center': 'ifm_center.json'}


def run_shell_command(command, wait_for_return=True, stdin=subprocess.PIPE, get_output=False, debug=True, assert_returncode=True):
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE,
                         stdin=stdin,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
    if debug:
       print("Run command: " + command)
    if wait_for_return is False:
        return p
    output, error = p.communicate()
    return_code = p.returncode
    if (assert_returncode and return_code != 0) or debug:
        print("Command Output: %s" % (output))
        print("Error: %s" % (error))
        print("Return code: %d" % return_code)
        print ("\n")
    else:
        if len(error) > 0:
            print("Error: %s" % (error))
            print ("\n")
    # if assert_returncode or debug:
    #    assert(return_code == 0)
    # return output to user
    if get_output:
        return output, return_code
    return return_code


def find_camera_interface(interface):
    valid_ip = ['192.168.1.2', '192.168.2.2', '192.168.0.69', '192.168.1.69', '192.168.0.2']
    for ip in valid_ip:
        set_interface_config(interface, ip)
        result = ping_interface(ip, assert_returncode=False)
        if result == 0:
            print "Detected camera with IP:={ip}".format(ip=ip)
            return ip
    return None


def ping_interface(ip, assert_returncode=False):
    cmd = 'ping -i 0.5 -q -c1 %s' % ip
    code, result = run_shell_command(cmd, get_output=True,  assert_returncode=assert_returncode)
    return result
 
      
def set_interface_config(name, ip):
    if_ip = ip.split('.')
    if_ip[-1] = '1'   
    cmd = 'sudo ifconfig {name} {ip} up'.format(name=name, ip='.'.join(if_ip))
    run_shell_command(cmd, debug=False)


def update_ifm_settings(old_ip, interface):
    while True:
        side = raw_input("Enter camera side (left or right or center): ").lower()
    	if side in ['left', 'right', 'center']:
            break

    json_file = camera_name_json[side]
    new_ip = camera_name_ip[side] 
    if side in ['left', 'right']:
        cmd='ifm3d --ip={ip} config'.format(ip=old_ip)
        ###ADDED
        print "***RAN LEFT RIGHT CONFIG***"
    else:
        cmd='o3d3xx-config --ip={ip}'.format(ip=old_ip)
        ####ADDED
        print "***RAN CENTER CONFIG***"
    print "IFM json being updated with command", cmd
    result = run_shell_command(cmd, stdin=open(json_file), get_output=True)
    print "IFM IP address:", new_ip
    time.sleep(5.0)
    set_interface_config(interface, new_ip)
    wait_for_interface(new_ip, msg='Waiting after updating json', sleep=1.0)
    return new_ip


def wait_for_command(cmd, msg):
    print "Waiting for ", msg, ":", cmd
    cnt = 0
    while cnt < 5:
        out, res = run_shell_command(cmd, assert_returncode=False, get_output=True)
        if res is False:
            time.sleep(5.0)
        else:
            return res
        cnt = cnt + 1
    return res


def check_process_running(process_name):
    p = subprocess.Popen('ps  aux', stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    pids_to_kill = []
    for line in out.splitlines():
        if process_name in line:
            pid = int(line.split()[1])
            if os.getpid() != pid:
                return pid, True
    return None, False
 

def kill_pid(pid):
    os.kill(pid, signal.SIGKILL)
    os.kill(pid, signal.SIGTERM)


def launch_roscore():
    cmd = 'roscore'
    print "Launching %s" % cmd
    run_shell_command(cmd, wait_for_return=False, debug=True)
    result = run_shell_command(cmd, stdin=open(json_file), get_output=True)


def launch_rviz():
    cmd = 'roslaunch ifm3d rviz.launch'
    print "Launching %s" % cmd
    run_shell_command(cmd, wait_for_return=False, debug=True)


def get_ifm_firmware_version(ip):
    cmd = 'ifm3d dump --ip={ip}'.format(ip=ip)
    out, res = run_shell_command(cmd, get_output=True, assert_returncode=False)
    import json
    data = json.loads(out)
    fm_ver = data['ifm3d']['_']['SWVersion']['IFM_Software']
    print 'IFM SW/FW version:', fm_ver
    return fm_ver


def get_ifm_sensor_name(ip):
    cmd = 'ifm3d dump --ip={ip}'.format(ip=ip)
    out, res = run_shell_command(cmd, get_output=True, assert_returncode=False)
    import json
    data = json.loads(out)
    ifm_name = data['ifm3d']['Device']['ArticleNumber']
    print 'IFM name:', ifm_name
    return ifm_name


def launch_ifm_node(ip):
    cmd='roslaunch ifm3d camera.launch ip:={ip}'.format(ip=ip)
    return run_shell_command(cmd, wait_for_return=False)


def wait_for_interface(ip, msg, sleep=20.0):
    cnt = 0
    while cnt < 10:
        res = ping_interface(ip)
        print msg, "..", cnt
        if res is False:
           time.sleep(sleep)
        else:
           time.sleep(sleep)
           break
        cnt = cnt + 1
    return res


def update_ifm_firmware(ip, firmware_fname):
    fw_version = get_ifm_firmware_version(ip)
    if fw_version.strip('.') in firmware_fname.strip('.'):
        print "Firmware version matches existing firmware"

    # skipp firmware update when O3D is configured
    sensor_name = get_ifm_sensor_name(ip)
    if 'O3D' in sensor_name:
        return
    
    out = raw_input("Do you want to update the ifm firmware (y / n) ?")
    if out != 'y':
       return

    if not os.path.exists(firmware_fname):
        print "Unable to find the firmware...: %s" % firmware_fname
        return

    cmd = "ifm3d reboot -r --ip={ip}".format(ip=ip)
    print "Rebooting IFM to recovery..."
    run_shell_command(cmd)
    time.sleep(20.0)
    set_interface_config("eth0", ip)
    wait_for_interface(ip, msg='Waiting after reboot to recovery')
    if res is False:
        print "IFM did not reboot. Stopping !!!"
        return

    cmd = 'ifm3d --ip={ip} swupdate --file={file}'.format(ip=ip, file=firmware_fname)
    print cmd
    os.system(cmd)
    wait_for_interface(ip, 'Waiting after Firmware update interface')
    time.sleep(30.0)
    set_interface_config("eth0", ip)
    cmd = 'ifm3d dump --ip={ip}'.format(ip=ip)
    wait_for_command(cmd, "ifm dump")
    fw_version = get_ifm_firmware_version(ip)
    print "New IFM version:", fw_version


def find_eth_interface():
    return "eth0"
    cmd="ip addr | grep -oh \"^.: \w*en\w*\""
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
    out, err = proc.communicate()
    if proc.returncode != 0:
       print 'Error executing command [%s]' % cmd
       print 'stderr: [%s]' % err
       print 'stdout: [%s]' % out
       exit(-1)
    lines = out.splitlines()
    if len(lines) is 0:
        print 'No ethernet interface found, please make sure the camera is connected to computer by ethernet cable'
        exit(-1)
    i = 0
    while i < len(lines):
        lines[i] = lines[i][3:]
        print ("%d) %s" % (i + 1, lines[i]))
        i += 1
    if(len(lines) == 1):
        sel = 1
    else:
        sel = input("Which ethernet is connected to IFM camera?")
    return lines[sel - 1];

if __name__ == "__main__":
    firmware_fname='O3X_Firmware_1.0.111.swu'
    if(len(sys.argv) == 2):
        firmware_fname = sys.argv[1]
    if not os.path.exists(firmware_fname):
        print "Unable to find the firmware...: %s" % firmware_fname
        exit(-1)
    else:
        print "Found firmware %s" % firmware_fname
    pid, res = check_process_running('ifm3d_node')
    if res is True:
        kill_pid(pid)

    pid, res = check_process_running('rosmaster')
    if res is False:
        launch_roscore()

    interface = find_eth_interface()
    #ip = find_camera_interface(interface)
    #interface='enx00e04c6802b7'
    ip = find_camera_interface(interface)
    assert ip is not None
    #set_interface_config('eth0', ip)
    update_ifm_firmware(ip=ip, firmware_fname=firmware_fname)
    new_ip = update_ifm_settings(ip, interface)
    ifm_proc = launch_ifm_node(new_ip)
    pid, res = check_process_running('rviz.launch')
    if res is False:
        launch_rviz()
#    print "See the result in the rviz window in 5 seconds. Ctrl-C to kill !"
    while True:
        ret = raw_input("See the result in the rviz window in 5 seconds. Enter 'q' to exit...")
        if ret in ['q', 'Q']:
            break
    run_shell_command("sudo ifconfig " + interface + " down", False)


