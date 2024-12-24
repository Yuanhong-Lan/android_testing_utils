# ----------------------
# @Time  : 2022 May
# @Author: Yuanhong Lan
# ----------------------

class EventUtil:
    @staticmethod
    def is_editable(s: str):
        return ("EditText" in s) or ("AutoCompleteTextView" in s)

    @staticmethod
    def is_seekbar(s: str):
        return "SeekBar" in s

    @staticmethod
    def is_switch(s: str):
        return "Switch" in s

    @staticmethod
    def is_text_presentation(s: str):
        return ("TextView" in s) or ("android.view.View" == s)

    @staticmethod
    def is_list(s: str):
        return ("ListView" in s) or ("RecyclerView" in s)
