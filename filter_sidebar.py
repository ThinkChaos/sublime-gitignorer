import os.path
import sublime_plugin

from GitIgnorer.lib.gitignored import is_ignored, ignored_files
from GitIgnorer.lib.path_utils import is_subdirectory


TRIGGER_FILES = ('.gitignore', os.path.basename(__file__))


class GitIgnorer(sublime_plugin.EventListener):

    def on_post_save_async(self, view):
        if os.path.basename(view.file_name()) in TRIGGER_FILES:
            apply_all_ignored(view.window())
        else:
            apply_single_ignored(view.window(), view.file_name())


def update_each_folder(inner):
    def wrapper(window, *args, **kwargs):
        if window is None:
            return

        project_data = window.project_data()

        if project_data is None or 'folders' not in project_data:
            return

        changed = False
        for folder in project_data['folders']:
            to_merge = inner(folder, *args, **kwargs)

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

    return {
        'file_exclude_patterns': list(files),
        'folder_exclude_patterns': list(dirs),
    }
