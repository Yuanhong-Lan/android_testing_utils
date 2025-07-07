# ----------------------
# @Time  : 2021 Dec
# @Author: Yuanhong Lan
# ----------------------
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from enum import Enum
from multiprocessing import Lock

from android_testing_utils.log import my_logger


class ADBSystemOperation:
    @classmethod
    def restart_server(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Restarting adb server")
        cmd = f"adb -s {device_id} kill-server"
        os.system(cmd)
        cmd = f"adb -s {device_id} start-server"
        os.system(cmd)

    @classmethod
    def run_adb_as_root(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Rerunning adb as root")
        cmd = f"adb -s {device_id} root"
        os.system(cmd)

    @classmethod
    def is_root(cls, device_id) -> bool:
        cmd = f"adb -s {device_id} shell whoami"
        cmd_output = os.popen(cmd).read().strip()
        res = cmd_output == "root"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Check if root: {res}")
        return res

    screencap_lock = Lock()

    @classmethod
    def screencap_to_path(cls, device_id, full_path_local):
        with cls.screencap_lock:
            tmp_path = "/sdcard/screen.png"
            cmd = f"adb -s {device_id} shell screencap {tmp_path}"
            my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Screen cap: {cmd}")
            os.system(cmd)
            local_dir, local_file = os.path.split(full_path_local)
            ADBFileOperation.pull(device_id, tmp_path, local_dir)
            my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Move screen.png to: {full_path_local}")
            shutil.move(os.path.join(local_dir, "screen.png"), full_path_local)
            ADBFileOperation.remove(device_id, tmp_path)

    @classmethod
    def screen_record(cls, device_id, save_file_path_device, record_seconds=None):
        cmd = f"adb -s {device_id} shell screenrecord {save_file_path_device}"
        if record_seconds is not None:
            cmd = f"{cmd} --time-limit {record_seconds}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Start screen record: {cmd}")
        os.system(cmd)
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Finish screen record: {cmd}")

    @classmethod
    def sync_system_time(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Sync system time.")

        cmd = f"adb -s {device_id} shell settings put global auto_time 0"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Disable auto time: {cmd}")
        os.system(cmd)

        time.sleep(1)

        current_time_str = datetime.now().strftime("%m%d%H%M%Y.%S")
        cmd = f"adb -s {device_id} shell date -s {current_time_str}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Set system time: {cmd}")
        os.system(cmd)

        time.sleep(1)

        cmd = f"adb -s {device_id} shell settings put global auto_time 1"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Enable auto time: {cmd}")
        os.system(cmd)

        time.sleep(1)

        cmd = f"adb -s {device_id} shell am broadcast -a android.intent.action.TIME_SET"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Broadcast time set action: {cmd}")
        os.system(cmd)


class ADBAppOperation:
    @classmethod
    def install_apk(cls, device_id, apk_file_path):
        cmd = f"adb -s {device_id} install -r '{apk_file_path}'"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Installing app: {cmd}")
        os.system(cmd)

    @classmethod
    def install_apk_with_permissions(cls, device_id, apk_file_path):
        cmd = f"timeout 20s adb -s {device_id} install -r -g '{apk_file_path}'"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Installing app with permission: {cmd}")
        os.system(cmd)

    @classmethod
    def install_apk_with_permissions_allow_downgrade(cls, device_id, apk_file_path):
        cmd = f"timeout 20s adb -s {device_id} install -r -g -d '{apk_file_path}'"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Installing app with permission and allow downgrade: {cmd}")
        os.system(cmd)

    @classmethod
    def start_app_by_am(cls, device_id, package_name, entrance_activity):
        cmd = f"adb -s {device_id} shell am start -S -n {package_name}/{entrance_activity}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Starting app by am: {cmd}")
        os.system(cmd)

    @classmethod
    def start_app_by_monkey(cls, device_id, package_name):
        cmd = f"adb -s {device_id} shell monkey -p {package_name} 1"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Starting app by monkey: {cmd}")
        os.system(cmd)

    @classmethod
    def force_stop_app_by_am(cls, device_id, package_name):
        cmd = f"adb -s {device_id} shell am force-stop {package_name}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Forcing stop app: {cmd}")
        os.system(cmd)

    @classmethod
    def clean_app_data(cls, device_id, package_name):
        cmd = f"adb -s {device_id} shell pm clear {package_name}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Cleaning app data: {cmd}")
        os.system(cmd)

    @classmethod
    def uninstall_apk(cls, device_id, apk_file_path):
        cmd = f"adb -s {device_id} uninstall '{apk_file_path}'"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Uninstall app: {cmd}")
        os.system(cmd)

    @classmethod
    def is_app_installed(cls, device_id, package_name):
        cmd = f"adb -s {device_id} shell pm list packages {package_name}"
        cmd_output = os.popen(cmd).read()
        return cmd_output != ''

    @classmethod
    def get_apk_of_installed_app(cls, device_id, package_name, target_path_local):
        cmd = f"adb -s {device_id} shell pm path {package_name}"
        cmd_output = os.popen(cmd).read().strip()
        if not cmd_output.startswith("package:"):
            my_logger.auto_hint(my_logger.LogLevel.ERROR, cls, True, f"Get apk of installed app failed: {cmd_output}")
            return
        apk_path = cmd_output.split(":")[1]
        ADBFileOperation.pull(device_id, apk_path, target_path_local)
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Get apk of installed app success to: {target_path_local}")


class ADBLogcat:
    @classmethod
    def empty_logcat_buffer(cls, device_id):
        cmd = f"adb -s {device_id} logcat -c"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Cleaning logcat buffer: {cmd}")
        os.system(cmd)

    @classmethod
    def start_logcat(cls, device_id, log_filter, log_file_path):
        # cmd = f"adb -s {device_id} logcat {log_filter} >> '{log_file_path}' &"
        cmd = f"adb -s {device_id} logcat {log_filter}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Staring logcat: {cmd}")
        # os.system(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=open(log_file_path, 'w'))
        return process


class ADBSendBroadcast:
    @classmethod
    def send_broadcast_by_action(cls, device_id, action):
        cmd = f"adb -s {device_id} shell am broadcast -a {action}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Sending broadcast: {cmd}")
        os.system(cmd)

    @classmethod
    def send_broadcast_by_action_and_explicit(cls, device_id, action, component):
        cmd = f"adb -s {device_id} shell am broadcast -a {action} -n {component}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Sending explicit broadcast: {cmd}")
        os.system(cmd)

    @classmethod
    def send_broadcast_by_action_and_flag(cls, device_id, action, flag):
        cmd = f"adb -s {device_id} shell am broadcast -a {action} -f {flag}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Sending flagged broadcast: {cmd}")
        os.system(cmd)


class ADBFileOperation:
    @classmethod
    def check_existence(cls, device_id, target_path_device, is_dir):
        cmd = f"adb -s {device_id} shell [ {'-d' if is_dir else '-f'} {target_path_device} ] && echo yes || echo no"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Checking existence: {cmd}")
        cmd_output = os.popen(cmd).read().strip()
        return True if cmd_output == "yes" else False

    @classmethod
    def mkdir(cls, device_id, target_path_device):
        cmd = f"adb -s {device_id} shell mkdir -p {target_path_device}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Making dir: {cmd}")
        os.system(cmd)

    @classmethod
    def pull(cls, device_id, source_path_device, target_path_local):
        cmd = f"adb -s {device_id} pull {source_path_device} {target_path_local}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Pulling: {cmd}")
        os.system(cmd)

    @classmethod
    def push(cls, device_id, source_path_local, target_path_device):
        cmd = f"adb -s {device_id} push {source_path_local} {target_path_device}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Pushing: {cmd}")
        os.system(cmd)

    @classmethod
    def remove(cls, device_id, remove_path_device):
        cmd = f"adb -s {device_id} shell rm {remove_path_device}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Removing: {cmd}")
        os.system(cmd)


class ADBMonkey:
    @classmethod
    def run_monkey(cls, device_id, package, times, time_interval=200):
        cmd = f"adb -s {device_id} shell monkey -v --ignore-crashes --ignore-timeouts --ignore-security-exceptions " \
              f"--kill-process-after-error --throttle {time_interval} -p {package} {times}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Start running Monkey: {cmd}")
        os.system(cmd)

    @classmethod
    def run_monkey_normal_test(cls, device_id, package, times, time_interval=200):
        cmd = f"adb -s {device_id} shell monkey -v --ignore-crashes --ignore-timeouts --ignore-security-exceptions " \
              f"--pct-nav 0 --pct-majornav 0 --pct-syskeys 0 --pct-appswitch 0 " \
              f"--kill-process-after-error --throttle {time_interval} -p {package} {times}"
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Start running Monkey: {cmd}")
        os.system(cmd)


class ADBNetwork:
    @classmethod
    def open_airplane_mode(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Opening airplane mode")
        cmd1 = f"adb -s {device_id} shell settings put global airplane_mode_on 1"
        os.system(cmd1)
        cmd2 = f"adb -s {device_id} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"
        os.system(cmd2)

    @classmethod
    def close_airplane_mode(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Closing airplane mode")
        cmd1 = f"adb -s {device_id} shell settings put global airplane_mode_on 0"
        os.system(cmd1)
        cmd2 = f"adb -s {device_id} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"
        os.system(cmd2)

    @classmethod
    def open_mobile_data(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Opening mobile data")
        cmd = f"adb -s {device_id} shell svc data enable"
        os.system(cmd)

    @classmethod
    def close_mobile_data(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Closing mobile data")
        cmd = f"adb -s {device_id} shell svc data disable"
        os.system(cmd)

    @classmethod
    def open_wifi(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Opening wifi")
        cmd = f"adb -s {device_id} shell svc wifi enable"
        os.system(cmd)

    @classmethod
    def close_wifi(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Closing wifi")
        cmd = f"adb -s {device_id} shell svc wifi disable"
        os.system(cmd)


class VolumeOptions(Enum):
    Up = "volume_up"
    Down = "volume_down"
    Mute = "volume_mute"


class ADBInput:
    @classmethod
    def tap(cls, device_id, x, y):
        cmd = f"adb -s {device_id} shell input tap {x} {y}"
        os.system(cmd)

    @classmethod
    def back(cls, device_id):
        cmd = f"adb -s {device_id} shell input keyevent 4"
        os.system(cmd)

    @classmethod
    def home(cls, device_id):
        cmd = f"adb -s {device_id} shell input keyevent 3"
        os.system(cmd)

    @classmethod
    def menu(cls, device_id):
        cmd = f"adb -s {device_id} shell input keyevent 82"
        os.system(cmd)

    VOLUME_OPTIONS = [
        VolumeOptions.Up,
        VolumeOptions.Down,
        VolumeOptions.Mute,
    ]

    @classmethod
    def volume(cls, device_id, volume_option: VolumeOptions):
        map_dict = {
            VolumeOptions.Up: 24,
            VolumeOptions.Down: 25,
            VolumeOptions.Mute: 164,
        }
        cmd = f"adb -s {device_id} shell input keyevent {map_dict[volume_option]}"
        os.system(cmd)


class ADBGetDeviceInfo:
    @classmethod
    def get_window_resolution_ratio(cls, device_id):
        try:
            cmd = f"adb -s {device_id} shell wm size"
            cmd_output = os.popen(cmd).read()
            pattern = re.compile("size: (\\d+)x(\\d+)")
            x, y = re.findall(pattern, cmd_output)[0]
            my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Get window resolution ratio: x={x}, y={y}")
        except Exception as e:
            my_logger.auto_hint(my_logger.LogLevel.ERROR, cls, True, f"Get window resolution ratio failed: {e}, return default 1080x1920")
            return 1080, 1920
        return int(x), int(y)

    @classmethod
    def get_connected_devices(cls):
        cmd = "adb devices"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile("(\\S+)\\s+device\n")
        devices = re.findall(pattern, cmd_output)
        return devices


class ADBKeyBoard:
    @classmethod
    def disable_keyboard_by_null_keyboard(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Disable keyboard by null keyboard")
        null_keyboard_apk_path = os.path.join(os.path.dirname(__file__), "apk", "null_keyboard.apk")
        ADBAppOperation.install_apk_with_permissions(device_id, null_keyboard_apk_path)
        time.sleep(0.5)
        if not ADBAppOperation.is_app_installed(device_id, "com.wparam.nullkeyboard"):
            my_logger.auto_hint(my_logger.LogLevel.WARNING, cls, True, f"Install null keyboard failed, try again!")
            ADBAppOperation.install_apk_with_permissions(device_id, null_keyboard_apk_path)
            time.sleep(0.5)
        cmd = f"adb -s {device_id} shell ime enable com.wparam.nullkeyboard/.NullKeyboard"
        os.system(cmd)
        cmd = f"adb -s {device_id} shell ime set com.wparam.nullkeyboard/.NullKeyboard"
        os.system(cmd)

    @classmethod
    def disable_keyboard_by_all_disable(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Disable keyboard by all disable")
        cmd = f"adb -s {device_id} shell \"ime list -a | grep \'mId=\' | cut -d= -f2\" | xargs -L1 adb -s {device_id} shell ime disable"
        os.system(cmd)

    @classmethod
    def reset_keyboard(cls, device_id):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f"Reset keyboard")
        cmd = f"adb -s {device_id} shell ime reset"
        os.system(cmd)
