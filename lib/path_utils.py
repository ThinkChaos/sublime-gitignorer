"""
Required until ST3 has Python >= 3.4, which comes with pathlib.
"""

import os.path


def os_path_split_asunder(path):
    """
    http://stackoverflow.com/a/4580931
    """
    parts = []
    while True:
        newpath, tail = os.path.split(path)
        if newpath == path:
            assert not tail
            if path:
                parts.append(path)
            break
        parts.append(tail)
        path = newpath
    parts.reverse()
    return parts


def is_subdirectory(potential_subdirectory, expected_parent_directory):
    """
    http://stackoverflow.com/a/17624617
    """
    def _get_normalized_parts(path):
        path = os.path.realpath(os.path.abspath(os.path.normpath(path)))
        return os_path_split_asunder(path)

    # Make absolute and handle symbolic links, split into components
    sub_parts = _get_normalized_parts(potential_subdirectory)
    parent_parts = _get_normalized_parts(expected_parent_directory)

    if len(parent_parts) > len(sub_parts):
        # A parent directory never has more path segments than its child
        return False

    # We expect the zip to end with the short path, which we know to
    # be the parent
    return all(part1 == part2 for part1, part2 in zip(sub_parts, parent_parts))
