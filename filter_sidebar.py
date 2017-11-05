import os.path
import sublime
import sublime_plugin

from .lib.gitignored import is_ignored, ignored_files
from .lib.path_utils import is_subdirectory


TRIGGER_FILES = ('.gitignore', os.path.basename(__file__))


class GitIgnorer(sublime_plugin.EventListener):

    def __init__(self):
        self._known_windows = set()

        sublime.set_timeout_async(self._on_load_async, 0)

    def _on_load_async(self):
        window = None
        for window in sublime.windows():
            self._on_new_window_async(window)

        if window is None:
            sublime.set_timeout_async(self._on_load_async, 50)

    def on_new_async(self, view):
        window = view.window()
        if window is None or window.id() in self._known_windows:
            return

        self._known_windows.add(window.id())
        self._on_new_window_async(window)

    def _on_new_window_async(self, window):
        apply_all_ignored(window)

    def on_post_save_async(self, view):
        window = view.window()

        if window is None:
            return

        file_name = view.file_name()

        if (file_name == window.project_file_name()
                or os.path.basename(file_name) in TRIGGER_FILES):
            apply_all_ignored(window)
        else:
            apply_single_ignored(window, file_name)


def _add_extra_excludes(folder, to_merge, excludes_type):
    excludes_name = '{}_exclude_patterns'.format(excludes_type)
    extra_excludes_name = 'extra_{}'.format(excludes_name)

    should_migrate_folder = extra_excludes_name not in folder
    if should_migrate_folder:
        if excludes_name not in to_merge:
            return False  # delay migration until actually needed

        # migrate user exclude patterns
        folder[extra_excludes_name] = folder.pop(excludes_name, [])

    extra_exclude_patterns = folder[extra_excludes_name]
    if not extra_exclude_patterns:
        return should_migrate_folder

    exclude_patterns = to_merge.get(excludes_name, [])

    to_merge[excludes_name] = exclude_patterns + extra_exclude_patterns
    return True


def update_each_folder(inner):
    def wrapper(window, *args, **kwargs):
        project_data = window.project_data()

        if project_data is None or 'folders' not in project_data:
            return

        changed = False
        for folder in project_data['folders']:
            to_merge = inner(folder, *args, **kwargs)

            for excludes_type in ('file', 'folder'):
                changed |= _add_extra_excludes(folder, to_merge, excludes_type)

            if to_merge:
                changed = True
                folder.update(to_merge)

        if changed:
            window.set_project_data(project_data)

    return wrapper


@update_each_folder
def apply_single_ignored(folder, file_name):
    folder_path = os.path.expanduser(folder['path'])

    if not is_subdirectory(os.path.dirname(file_name), folder_path):
        return {}

    if not is_ignored(file_name):
        return {}

    if os.path.isdir(file_name):
        return {'folder_exclude_patterns': (
            folder.get('folder_exclude_patterns', []) + [file_name]
        )}

    return {'file_exclude_patterns': (
        folder.get('file_exclude_patterns', []) + [file_name]
    )}


@update_each_folder
def apply_all_ignored(folder):
    dirs, files = set(), set()

    folder_path = os.path.expanduser(folder['path'])

    for file in ignored_files(folder_path):
        file = os.path.join(folder_path, file)

        if file.endswith('/'):
            dirs.add(file[:-1])
        else:
            files.add(file)

    to_merge = {}

    if files:
        to_merge['file_exclude_patterns'] = list(files)

    if dirs:
        to_merge['folder_exclude_patterns'] = list(dirs)

    return to_merge
