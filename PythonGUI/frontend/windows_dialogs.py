from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path


class _OpenFileName(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", ctypes.c_void_p),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]


_OFN_OVERWRITEPROMPT = 0x00000002
_OFN_NOCHANGEDIR = 0x00000008
_OFN_PATHMUSTEXIST = 0x00000800
_OFN_EXPLORER = 0x00080000


def choose_session_zip_path(suggested_name: str) -> Path | None:
    """Show the Windows Save As dialog on the application's UI thread."""
    active_window = ctypes.windll.user32.GetActiveWindow
    active_window.argtypes = []
    active_window.restype = wintypes.HWND

    dialogs = ctypes.windll.comdlg32
    save_as = dialogs.GetSaveFileNameW
    save_as.argtypes = [ctypes.POINTER(_OpenFileName)]
    save_as.restype = wintypes.BOOL
    extended_error = dialogs.CommDlgExtendedError
    extended_error.argtypes = []
    extended_error.restype = wintypes.DWORD

    filename = ctypes.create_unicode_buffer(suggested_name, 32768)
    options = _OpenFileName(
        lStructSize=ctypes.sizeof(_OpenFileName),
        hwndOwner=active_window(),
        lpstrFilter="ZIP archives (*.zip)\0*.zip\0\0",
        nFilterIndex=1,
        lpstrFile=ctypes.cast(filename, wintypes.LPWSTR),
        nMaxFile=len(filename),
        lpstrTitle="Export Session",
        Flags=_OFN_EXPLORER | _OFN_OVERWRITEPROMPT | _OFN_PATHMUSTEXIST | _OFN_NOCHANGEDIR,
        lpstrDefExt="zip",
    )
    if save_as(ctypes.byref(options)):
        return Path(filename.value)
    error = extended_error()
    if error:
        raise OSError(f"Windows Save As dialog failed (0x{error:04X}).")
    return None
