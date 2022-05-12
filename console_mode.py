import ctypes


def quickedit(enabled=1):  # This is a patch to the system that sometimes hangs
    """
    Enable or disable quick edit mode to prevent system hangs,
    sometimes when using remote desktop
    Param (Enabled)
    enabled = 1(default), enable quick edit mode in python console
    enabled = 0, disable quick edit mode in python console
    """
    # -10 is input handle => STD_INPUT_HANDLE (DWORD) -10
    # https://docs.microsoft.com/en-us/windows/console/getstdhandle
    # default = (0x4|0x80|0x20|0x2|0x10|0x1|0x40|0x200)
    # 0x40 is quick edit, #0x20 is insert mode
    # 0x8 is disabled by default
    # https://docs.microsoft.com/en-us/windows/console/setconsolemode
    kernel32 = ctypes.windll.kernel32
    if enabled:
        kernel32.SetConsoleMode(
            kernel32.GetStdHandle(-10),
            (0x4 | 0x80 | 0x20 | 0x2 | 0x10 | 0x1 | 0x40 | 0x100),
        )
        print("Console Quick Edit Enabled")
    else:
        kernel32.SetConsoleMode(
            kernel32.GetStdHandle(-10),
            (0x4 | 0x80 | 0x20 | 0x2 | 0x10 | 0x1 | 0x00 | 0x100),
        )
        print("Console Quick Edit Disabled")


if __name__ == "__main__":
    quickedit(0)
