# ----------------------
# @Time  : 2021 Dec
# @Author: Yuanhong Lan
# ----------------------

import os
import re
import collections

from typing import List, Tuple, Callable

from android_testing_utils.log import my_logger


class ProcessUtil:
    @staticmethod
    def pull_apk_of_installed_app_and_analysis(package_name, device_id, f: Callable):
        cmd = f"adb -s {device_id} shell pm path {package_name}"
        cmd_output = os.popen(cmd).read()

        source_path = cmd_output.replace("package:", "").strip()
        target_path = os.path.join(os.path.dirname(__file__), f"./{package_name}_temp.apk")
        cmd = f"adb -s {device_id} pull {source_path} {target_path}"
        os.system(cmd)

        res = f(target_path)
        os.remove(target_path)
        return res


class GetComponentName:
    @staticmethod
    def get_EndEmmaBroadcast_receiver_name_by_aapt_dump_xmltree(apk_path):
        cmd = f"aapt dump xmltree '{apk_path}' AndroidManifest.xml | grep EndEmmaBroadcast"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile('android:name\\(\\S+\\)="(\\S+)"')
        return re.findall(pattern, cmd_output)[0]


class GetPackageName:
    @staticmethod
    def get_package_name_from_apk_file_by_aapt_dump_badging(apk_path) -> str:
        cmd = f"aapt dump badging '{apk_path}' | grep package"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile("name='(\\S+)'")
        return re.findall(pattern, cmd_output)[0]

    @staticmethod
    def get_package_name_from_apk_file_by_aapt2_dump_badging(apk_path) -> str:
        cmd = f"aapt2 dump badging '{apk_path}' | grep package"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile("name='(\\S+)'")
        return re.findall(pattern, cmd_output)[0]

    @staticmethod
    def get_package_name_from_apk_file_by_aapt2_dump_packagename(apk_path) -> str:
        cmd = f"aapt2 dump packagename '{apk_path}'"
        cmd_output = os.popen(cmd).read()
        return cmd_output.strip()


class GetAllActivities:
    @staticmethod
    def get_all_activities_from_apk_file_by_aapt_list(apk_path) -> List[str]:
        my_logger.hint(my_logger.LogLevel.INFO, "AAPT", True, f"Start extracting all activities from apk file by aapt list")
        # if package_name is None:
        #     package_name = GetPackageName.get_package_name_from_apk_file_by_aapt2_dump_packagename(apk_path)
        cmd = f"""aapt list -a '{apk_path}' | """ + \
              r"""sed -n '/ activity /{:loop n;s/^.*android:name.*="\([^"]\{1,\}\)".*/\1/;T loop;p;t}'"""
        cmd_output = os.popen(cmd).read()
        activity_list = cmd_output.strip().split('\n')
        # if package_name.endswith(".debug"):
        #     prefix = package_name[:package_name.rfind(".debug")]
        # else:
        #     prefix = package_name
        # for i in range(len(activity_list) - 1, -1, -1):
        #     if not activity_list[i].startswith(prefix):
        #         activity_list.pop(i)
        return activity_list

    @staticmethod
    def get_all_activities_from_installed_app_by_aapt_list_with_apk_pulled(package_name, device_id):
        return ProcessUtil.pull_apk_of_installed_app_and_analysis(
            package_name, device_id,
            GetAllActivities.get_all_activities_from_apk_file_by_aapt_list
        )

    @staticmethod
    def get_all_activities_from_apk_file_by_aapt_dump_xmltree(apk_path) -> List[str]:
        my_logger.hint(my_logger.LogLevel.INFO, "AAPT", True, f"Start extracting all activities from apk file by aapt dump xmltree")
        # if package_name is None:
        #     package_name = GetPackageName.get_package_name_from_apk_file_by_aapt2_dump_packagename(apk_path)
        cmd = f"""aapt dump xmltree '{apk_path}' AndroidManifest.xml | """ + \
              r"""sed -n '/ activity /{:loop n;s/^.*android:name.*="\([^"]\{1,\}\)".*/\1/;T loop;p;t}'"""
        cmd_output = os.popen(cmd).read()
        activity_list = cmd_output.strip().split('\n')
        # if package_name.endswith(".debug"):
        #     prefix = package_name[:package_name.rfind(".debug")]
        # else:
        #     prefix = package_name
        # for i in range(len(activity_list) - 1, -1, -1):
        #     if not activity_list[i].startswith(prefix):
        #         activity_list.pop(i)
        return activity_list


ActivityAliasPair = collections.namedtuple("ActivityAliasPair", ["alias", "target_activity"])
class GetActivityAliasPairs:
    @staticmethod
    def get_all_activity_alias_pair_from_apk_file_by_aapt_dump_xmltree(apk_path) -> List[ActivityAliasPair]:
        my_logger.hint(my_logger.LogLevel.INFO, "AAPT", True, f"Start analyzing all activity alias pairs")
        cmd = f"aapt dump xmltree '{apk_path}' AndroidManifest.xml"
        cmd_output = os.popen(cmd).read()
        cmd_output_lines = cmd_output.split('\n')

        res: List[ActivityAliasPair] = []

        find_alias_flag = False
        temp_alias = None
        temp_target_activity = None

        alias_pattern = re.compile("A: android:name\\(\\S+\\)=\"(\\S+)\"")
        target_activity_pattern = re.compile("A: android:targetActivity\\(\\S+\\)=\"(\\S+)\"")

        for line in cmd_output_lines:
            if find_alias_flag:
                temp_alias_pattern_find = re.findall(alias_pattern, line)
                temp_target_activity_pattern_find = re.findall(target_activity_pattern, line)
                if len(temp_alias_pattern_find) > 0:
                    temp_alias = temp_alias_pattern_find[0]
                if len(temp_target_activity_pattern_find) > 0:
                    temp_target_activity = temp_target_activity_pattern_find[0]
                if (temp_alias is not None) and (temp_target_activity is not None):
                    res.append(ActivityAliasPair(temp_alias, temp_target_activity))
                    find_alias_flag = False
                    temp_alias = None
                    temp_target_activity = None
            elif line.strip().startswith("E: activity-alias"):
                find_alias_flag = True
        return res


class GetEntranceActivity:
    @staticmethod
    def get_entrance_activity_from_apk_file_by_aapt_dump_badging(apk_path) -> str:
        cmd = f"aapt dump badging '{apk_path}' | grep launchable"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile("name='(\\S+)'")
        return re.findall(pattern, cmd_output)[0]

    @staticmethod
    def get_entrance_activity_from_installed_app_by_aapt_dump_badging_with_apk_pulled(package_name, device_id) -> str:
        return ProcessUtil.pull_apk_of_installed_app_and_analysis(
            package_name, device_id,
            GetEntranceActivity.get_entrance_activity_from_apk_file_by_aapt_dump_badging
        )

    @staticmethod
    def get_entrance_activity_from_installed_app_by_dumpsys_package(package_name, device_id) -> str:
        cmd = f"adb -s {device_id} shell dumpsys package {package_name} | grep category.LAUNCHER -B 3"
        cmd_output = os.popen(cmd).read()
        pattern = re.compile(f"{package_name}/(\\S+)")
        entrance_activity = re.findall(pattern, cmd_output)[0]
        if entrance_activity.startswith('.'):
            entrance_activity = package_name + entrance_activity
        return entrance_activity


class GetCurrentPackageAndActivity:
    @staticmethod
    def __handle_cmd_output(cmd_output, pattern, log=True) -> Tuple[str, str]:
        find_result = pattern.findall(cmd_output)
        if len(find_result) == 0:
            if log:
                my_logger.hint(my_logger.LogLevel.WARNING, "ADB", True, f"Dumpsys UNKNOWN! Current output is {cmd_output}")
            current_package = "UNKNOWN"
            current_activity = "UNKNOWN"
        elif len(find_result) == 1:
            current_package, current_activity = find_result[0]
        else:
            if log:
                my_logger.hint(my_logger.LogLevel.WARNING, "ADB", True, f"Dumpsys need attention! Current output is {cmd_output}")
            current_package, current_activity = find_result[-1]
        if current_activity.startswith('.'):
            current_activity = current_package + current_activity

        return current_package, current_activity

    @staticmethod
    def is_dumpsys_window_mCurrentFocus_null(device_id) -> bool:
        cmd = f"adb -s {device_id} shell dumpsys window | grep mCurrentFocus"
        cmd_output = os.popen(cmd).read()
        temp = cmd_output.strip().split('\n')[-1]
        if "mCurrentFocus=null".lower() in temp.lower():
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Catch null! Focus info - mCurrentFocus:{cmd_output}")
            return True
        return False

    @staticmethod
    def is_not_responding(device_id) -> bool:
        cmd = f"adb -s {device_id} shell dumpsys window | grep mCurrentFocus"
        cmd_output = os.popen(cmd).read()
        temp = cmd_output.strip().split('\n')[-1]
        temp = temp.lower()
        if ("Not Responding".lower() in temp) or ("Application Error".lower() in temp):
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Catch not responding! Focus info - mCurrentFocus:{cmd_output}")
            return True
        return False

    @staticmethod
    def is_asking_permission(device_id) -> bool:
        cmd = f"adb -s {device_id} shell dumpsys window | grep mCurrentFocus"
        cmd_output = os.popen(cmd).read()
        temp = cmd_output.strip().split('\n')[-1]
        temp = temp.lower()
        if ("GrantPermissionsActivity".lower() in temp):
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Catch asking permission! Focus info - mCurrentFocus:{cmd_output}")
            return True
        return False

    @staticmethod
    def hint_full_focus_info(device_id):
        cmd = f"adb -s {device_id} shell dumpsys window | grep mCurrentFocus"
        cmd_output = os.popen(cmd).read()
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Focus info - mCurrentFocus:{cmd_output}")
        cmd = f"adb -s {device_id} shell dumpsys window | grep mFocusedApp=AppWindowToken"
        cmd_output = os.popen(cmd).read()
        my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Focus info - mFocusedApp  :{cmd_output}")

    @staticmethod
    def get_current_package_and_activity_by_dumpsys_window_mCurrentFocus(device_id, log=True) -> Tuple[str, str]:
        cmd = f"adb -s {device_id} shell dumpsys window | grep mCurrentFocus"

        cmd_output = os.popen(cmd).read()
        if log:
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Focus info:{cmd_output}")

        pattern = re.compile("(\\S+)/(\\S+)}")
        current_package, current_activity = GetCurrentPackageAndActivity.__handle_cmd_output(cmd_output, pattern, log=log)

        if log:
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"----Current activity is : {current_activity}")
        # TODO: ? SubPanel
        return current_package, current_activity

    @staticmethod
    def get_current_package_and_activity_by_dumpsys_window_mFocusedApp(device_id, log=True) -> Tuple[str, str]:
        cmd = f"adb -s {device_id} shell dumpsys window | grep mFocusedApp"
        cmd_output = os.popen(cmd).read()
        if log:
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"Focus info:{cmd_output}")

        pattern = re.compile("(\\S+)/(\\S+)")
        current_package, current_activity = GetCurrentPackageAndActivity.__handle_cmd_output(cmd_output, pattern, log=log)

        if log:
            my_logger.hint(my_logger.LogLevel.INFO, "ADB", True, f"----Current activity is : {current_activity}")
        # TODO: ? SubPanel
        return current_package, current_activity
