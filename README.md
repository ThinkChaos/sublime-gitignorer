# GitIgnorer

A SublimeText 3 plugin to hide Git ignored files from the sidebar.

I wrote this plugin because the [existing similar plugin][other] uses a timer to check for ignored files.  
This plugin uses both events and a timer to be more efficient.

## FAQ

### GitIgnorer isn't doing anything, why?

GitIgnorer only works when you are in a project as the plugin modifies the
project's `file_exclude_patterns` and `folder_exclude_patterns` settings.

### How do I exclude files, without adding them to .gitignore?

Use the `extra_{file,folder}_exclude_patterns` settings in your project.  
GitIgnorer will automatically add these to the standard exclude patterns when it runs.

**Note:** Existing exclude patterns will automatically be migrated to the "extra_" prefixed versions when needed.

### When does GitIgnorer run?

GitIgnorer runs on the following events:

 - after saving a file
 - when the project window is first activated

There is also a timer that triggers the plugin every 5 seconds by default.  
This is configurable, and can be disabled.

You can also trigger it by selecting "GitIgnorer: Refresh ignored files" in the Command Palette.

[other]: https://github.com/ExplodingCabbage/sublime-gitignorer
