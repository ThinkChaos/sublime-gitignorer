import os.path
import subprocess


def is_ignored(file):
    proc = subprocess.Popen(
        ['git', 'check-ignore', '--quiet', file],
        cwd=os.path.dirname(file),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return proc.wait() == 0


def ignored_files(folder_path):
    proc = subprocess.Popen(
        ['git', 'clean', '--dry-run', '-Xd'],
        cwd=folder_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    for line in proc.stdout:
        # line == b'Would remove FILE\n'
        yield line.decode()[13:].rstrip('\r\n')

    proc.wait()
