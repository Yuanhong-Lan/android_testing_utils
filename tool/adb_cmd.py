# ----------------------
# @Time  : 2021 Dec
# @Author: Yuanhong Lan
# ----------------------
import os
import re
import shutil
from enum import Enum
from multiprocessing import Lock

from android_testing_utils.log import my_logger


def restart_server(device_id):
    cmd = f"adb -s {device_id} kill-server"
    os.system(cmd)
    cmd = f"adb -s {device_id} start-server"
    os.system(cmd)


def run_adb_as_root(device_id):
    cmd = f"adb -s {device_id} root"
    os.system(cmd)


screencap_lock = Lock()
def screencap_to_path(device_id, full_path_local):
    with screencap_lock:
        tmp_path = "/sdcard/screen.png"
        cmd = f"adb -s {device_id} shell screencap {tmp_path}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Screen cap: {cmd}")
        os.system(cmd)
        local_dir, local_file = os.path.split(full_path_local)
        FileOperation.pull(device_id, tmp_path, local_dir)
        shutil.move(os.path.join(local_dir, "screen.png"), full_path_local)
        FileOperation.remove(device_id, tmp_path)


def screen_record(device_id, save_file_path_device, record_seconds=None):
    cmd = f"adb -s {device_id} shell screenrecord {save_file_path_device}"
    if record_seconds is not None:
        cmd = f"{cmd} --time-limit {record_seconds}"
    my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Start screen record: {cmd}")
    os.system(cmd)
    my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Finish screen record: {cmd}")


class AppOperation:
    @staticmethod
    def install_apk(device_id, apk_file_path):
        cmd = f"adb -s {device_id} install -r '{apk_file_path}'"
        os.system(cmd)

    @staticmethod
    def install_apk_with_permissions(device_id, apk_file_path):
        cmd = f"timeout 20s adb -s {device_id} install -r -g '{apk_file_path}'"
        os.system(cmd)

    @staticmethod
    def start_app_by_am(device_id, package_name, entrance_activity):
        cmd = f"adb -s {device_id} shell am start -S -n {package_name}/{entrance_activity}"
        os.system(cmd)

    @staticmethod
    def start_app_by_monkey(device_id, package_name):
        cmd = f"adb -s {device_id} shell monkey -p {package_name} 1"
        os.system(cmd)

    @staticmethod
    def force_stop_app_by_am(device_id, package_name):
        cmd = f"adb -s {device_id} shell am force-stop {package_name}"
        os.system(cmd)

    @staticmethod
    def clean_app_data(device_id, package_name):
        cmd = f"adb -s {device_id} shell pm clear {package_name}"
        os.system(cmd)

    @staticmethod
    def uninstall_apk(device_id, apk_file_path):
        cmd = f"adb -s {device_id} uninstall '{apk_file_path}'"
        os.system(cmd)

    @staticmethod
    def is_app_installed(device_id, package_name):
        cmd = f"adb -s {device_id} shell pm list packages {package_name}"
        cmd_output = os.popen(cmd).read()
        return cmd_output == ''


class Logcat:
    @staticmethod
    def empty_logcat_buffer(device_id):
        cmd = f"adb -s {device_id} logcat -c"
        os.system(cmd)

    @staticmethod
    def start_logcat(device_id, log_filter, log_file_path):
        cmd = f"adb -s {device_id} logcat {log_filter} >> '{log_file_path}' &"
        os.system(cmd)


class SendBroadcast:
    @staticmethod
    def send_broadcast_by_action(device_id, action):
        cmd = f"adb -s {device_id} shell am broadcast -a {action}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Send broadcast: {cmd}")
        os.system(cmd)

    @staticmethod
    def send_broadcast_by_action_and_explicit(device_id, action, component):
        cmd = f"adb -s {device_id} shell am broadcast -a {action} -n {component}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Send explicit broadcast: {cmd}")
        os.system(cmd)

    @staticmethod
    def send_broadcast_by_action_and_flag(device_id, action, flag):
        cmd = f"adb -s {device_id} shell am broadcast -a {action} -f {flag}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Send flagged broadcast: {cmd}")
        os.system(cmd)


class FileOperation:
    @staticmethod
    def check_existence(device_id, target_path_device, is_dir):
        cmd = f"adb -s {device_id} shell [ {'-d' if is_dir else '-f'} {target_path_device} ] && echo yes || echo no"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Check existence: {cmd}")
        cmd_output = os.popen(cmd).read().strip()
        return True if cmd_output == "yes" else False

    @staticmethod
    def mkdir(device_id, target_path_device):
        cmd = f"adb -s {device_id} shell mkdir -p {target_path_device}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Mkdir: {cmd}")
        os.system(cmd)

    @staticmethod
    def pull(device_id, source_path_device, target_path_local):
        cmd = f"adb -s {device_id} pull {source_path_device} {target_path_local}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Pull: {cmd}")
        os.system(cmd)

    @staticmethod
    def push(device_id, source_path_local, target_path_device):
        cmd = f"adb -s {device_id} push {source_path_local} {target_path_device}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Push: {cmd}")
        os.system(cmd)

    @staticmethod
    def remove(device_id, remove_path_device):
        cmd = f"adb -s {device_id} shell rm {remove_path_device}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Remove: {cmd}")
        os.system(cmd)


class Monkey:
    @staticmethod
    def run_monkey(device_id, package, times, time_interval=200):
        cmd = f"adb -s {device_id} shell monkey -v --ignore-crashes --ignore-timeouts --ignore-security-exceptions " \
              f"--kill-process-after-error --throttle {time_interval} -p {package} {times}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Start running Monkey: {cmd}")
        os.system(cmd)

    @staticmethod
    def run_monkey_normal_test(device_id, package, times, time_interval=200):
        cmd = f"adb -s {device_id} shell monkey -v --ignore-crashes --ignore-timeouts --ignore-security-exceptions " \
              f"--pct-nav 0 --pct-majornav 0 --pct-syskeys 0 --pct-appswitch 0 " \
              f"--kill-process-after-error --throttle {time_interval} -p {package} {times}"
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Start running Monkey: {cmd}")
        os.system(cmd)


class Network:
    @staticmethod
    def open_airplane_mode(device_id):
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Open airplane mode")
        cmd1 = f"adb -s {device_id} shell settings put global airplane_mode_on 1"
        os.system(cmd1)
        cmd2 = f"adb -s {device_id} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"
        os.system(cmd2)

    @staticmethod
    def close_airplane_mode(device_id):
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Close airplane mode")
        cmd1 = f"adb -s {device_id} shell settings put global airplane_mode_on 0"
        os.system(cmd1)
        cmd2 = f"adb -s {device_id} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"
        os.system(cmd2)

    @staticmethod
    def open_mobile_data(device_id):
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Open mobile data")
        cmd = f"adb -s {device_id} shell svc data enable"
        os.system(cmd)

    @staticmethod
    def close_mobile_data(device_id):
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Close mobile data")
        cmd = f"adb -s {device_id} shell svc data disable"
        os.system(cmd)

    @staticmethod
    def open_wifi(device_id):
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Open wifi")
        cmd = f"adb -s {device_id} shell svc wifi enable"
        os.system(cmd)

    @staticmethod
    def close_wifi(device_id):
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Close wifi")
        cmd = f"adb -s {device_id} shell svc wifi disable"
        os.system(cmd)


class VolumeOptions(Enum):
    Up = "volume_up"
    Down = "volume_down"
    Mute = "volume_mute"


class Input:
    @staticmethod
    def tap(device_id, x, y):
        cmd = f"adb -s {device_id} shell input tap {x} {y}"
        os.system(cmd)

    @staticmethod
    def back(device_id):
        cmd = f"adb -s {device_id} shell input keyevent 4"
        os.system(cmd)

    @staticmethod
    def home(device_id):
        cmd = f"adb -s {device_id} shell input keyevent 3"
        os.system(cmd)

    @staticmethod
    def menu(device_id):
        cmd = f"adb -s {device_id} shell input keyevent 82"
        os.system(cmd)

    VOLUME_OPTIONS = [
        VolumeOptions.Up,
        VolumeOptions.Down,
        VolumeOptions.Mute,
    ]

    @staticmethod
    def volume(device_id, volume_option: VolumeOptions):
        map_dict = {
            VolumeOptions.Up: 24,
            VolumeOptions.Down: 25,
            VolumeOptions.Mute: 164,
        }
        cmd = f"adb -s {device_id} shell input keyevent {map_dict[volume_option]}"
        os.system(cmd)


class GetDeviceInfo:
    @staticmethod
    def get_window_resolution_ratio(device_id):
        cmd = f"adb -s {device_id} shell wm size"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile("size: (\\d+)x(\\d+)")
        x, y = re.findall(pattern, cmd_output)[0]
        return x, y
