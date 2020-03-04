import os.path
import platform

import sublime
import sublime_plugin


def compare_file_names(x, y):
    if platform.system() == "Windows" or platform.system() == "Darwin":
        return x.lower() == y.lower()
    else:
        return x == y


def walk_open_file(name, scope):
    new_path = None
    for root, dirs, files in os.walk(scope):
        if name in files:
            return os.path.join(root, name)
        for dirname in dirs:
            new_path = walk_open_file(name, os.path.join(root, dirname))
            if new_path:
                return new_path
    return new_path


class SwitchFileCommand(sublime_plugin.WindowCommand):
    def switch_file_by_ext(self, extensions=[]):
        base, ext = os.path.splitext(self.fname)
        start = 0
        count = len(extensions)

        if ext != "":
            ext = ext[1:]

            for i in range(0, len(extensions)):
                if compare_file_names(extensions[i], ext):
                    start = i + 1
                    count -= 1
                    break

        for i in range(0, count):
            idx = (start + i) % len(extensions)

            new_path = base + "." + extensions[idx]

            if os.path.exists(new_path):
                self.window.open_file(new_path, flags=sublime.FORCE_GROUP)
                break

    def switch_file_by_name(self, names=[], scope="."):
        base, ext = os.path.splitext(self.fname)
        name = os.path.basename(base)

        start = 0
        count = len(names)
        found = False
        for i in range(0, count):
            change = names[i]
            if compare_file_names(change, name[-len(change) :]):
                name = name[: -len(change)]
                found = True
                start = i + 1
                count -= 1
                break
        if not found:
            return

        for i in range(0, count):
            idx = (start + i) % len(names)
            change = names[idx]
            new_name = name + change + ext
            new_path = walk_open_file(new_name, scope)
            if os.path.exists(new_path):
                self.window.open_file(new_path, flags=sublime.FORCE_GROUP)
                break

    def run(self, extensions=[]):
        if not self.window.active_view():
            return
        self.fname = self.window.active_view().file_name()
        if not self.fname:
            return
        if len(extensions) > 0:
            self.switch_file_by_ext(extensions)
        settings = sublime.load_settings("SublimeDefaultEx.sublime-settings")
        names = settings.get("switch_file_names", [])
        scope = settings.get("switch_file_scope", ".")
        self.switch_file_by_name(names, scope)
