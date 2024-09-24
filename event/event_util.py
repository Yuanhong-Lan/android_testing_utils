# ----------------------
# @Time  : 2022 May
# @Author: Yuanhong Lan
# ----------------------

class EventUtil:
    @staticmethod
    def is_editable(s: str):
        return (".EditText" in s) or ("AutoCompleteTextView" in s)

    @staticmethod
    def is_seekbar(s: str):
        return ".SeekBar" in s

    @staticmethod
    def is_switch(s: str):
        return ".Switch" in s

    @staticmethod
    def contain_text(s: str):
        return "Text" in s
