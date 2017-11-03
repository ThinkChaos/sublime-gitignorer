import os.path
import platform
import subprocess


_startupinfo = None

if platform.system() == 'Windows':
    _startupinfo = subprocess.STARTUPINFO()
    _startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    _startupinfo.wShowWindow = subprocess.SW_HIDE


def is_ignored(file):
    proc = subprocess.Popen(
        ['git', 'check-ignore', '--quiet', file],
        cwd=os.path.dirname(file),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        startupinfo=_startupinfo
    )

    return proc.wait() == 0


def ignored_files(folder_path):
    proc = subprocess.Popen(
        ['git', 'clean', '--dry-run', '-Xd'],
        cwd=folder_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        startupinfo=_startupinfo
    )

    for line in proc.stdout:
        # line == b'Would remove FILE\n'
        yield line.decode()[13:].rstrip('\r\n')

    proc.wait()
