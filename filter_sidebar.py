import os.path
import sublime
import sublime_plugin

from .lib.gitignored import is_ignored, ignored_files
from .lib.path_utils import is_subdirectory


TRIGGER_FILES = ('.gitignore', os.path.basename(__file__))


class GitIgnorer(sublime_plugin.EventListener):

    def on_post_save_async(self, view):
        window = view.window()

        if window is None:
            return

        file_name = view.file_name()

        if (file_name == window.project_file_name() or
                os.path.basename(file_name) in TRIGGER_FILES):
            apply_all_ignored(window)
        else:
            apply_single_ignored(window, file_name)


class RunGitIgnorerCommand(sublime_plugin.WindowCommand):

    settings = sublime.load_settings('GitIgnorer.sublime-settings')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        target = self.timer_run
        if self.run_interval <= 0:
            target = self.run

        sublime.set_timeout_async(target, 0)

    @property
    def run_interval(self):
        return self.settings.get('run_interval') or 5

    def timer_run(self):
        self.run()
        sublime.set_timeout_async(self.timer_run, self.run_interval * 1000)

    def is_enabled(self):
        return self.window.project_data() is not None

    def run(self):
        apply_all_ignored(self.window)


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
            folder_path = os.path.expanduser(folder['path'])

            if not os.path.exists(os.path.join(folder_path, '.git')):
                continue

            to_merge = inner(folder_path, folder, *args, **kwargs)

            for excludes_type in ('file', 'folder'):
                changed |= _add_extra_excludes(folder, to_merge, excludes_type)

            if to_merge:
                changed = True
                folder.update(to_merge)

        if changed:
            window.set_project_data(project_data)

    return wrapper


@update_each_folder
def apply_single_ignored(folder_path, folder, file_name):
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
def apply_all_ignored(folder_path, folder):
    dirs, files = set(), set()

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
