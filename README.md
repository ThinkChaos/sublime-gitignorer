# GitIgnorer

A SublimeText 3 plugin to hide Git ignored files from the sidebar.

I wrote this plugin because the [existing similar plugin][other] uses a timer to check for ignored files.  
This plugin uses events, and a couple tricks, to be more efficient.

**Note:** Only works when you are in a project as the plugin modifies the
project's `file_exclude_patterns` and `folder_exclude_patterns` settings.

[other]: https://github.com/ExplodingCabbage/sublime-gitignorer
