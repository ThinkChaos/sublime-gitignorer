# GitIgnorer

A SublimeText 3 plugin to hide Git ignored files from the sidebar.

I wrote this plugin because the [existing similar plugin][other] uses a timer to check for ignored files.  
This plugin uses events, and a couple tricks, to be more efficient.

**Note:** Only works when you are in a project as the plugin modifies the
project's `file_exclude_patterns` and `folder_exclude_patterns` settings.

Because this plugin modifies your projects' exclude patterns, if you want to add custom exclude patterns, use the `extra_{file,folder}_exclude_patterns` settings.  
The plugin will automatically add these to the standard exclude patterns.

**Note:** Existing exclude patterns will automatically be migrated to the "extra_" prefixed versions when needed.

[other]: https://github.com/ExplodingCabbage/sublime-gitignorer
