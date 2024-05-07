from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath

events = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t",
          "y", "u", "i", "o", "p", "[", "]", "\\", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'",
          "z", "x", "c", "v", "b", "n", "m", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9",
          "f10", "f11", "f12", "print_screen",
          "scroll_lock", "backspace", "insert", "home", "page_up", "num_lock",
          "tab", "delete", "end", "page_down", "caps_lock", "enter", "arrow_left",
          "arrow_up", "arrow_down", "arrow_right", "shift", "lshift", "rshift",
          "control", "alt", "lcontrol", "lalt", "space", "ralt", "rcontrol",
          "escape", "`"]


class Component(DirectObject):
    def __init__(self, nodepath: NodePath):
        super().__init__()
        self.nodepath: NodePath = nodepath

        self._tasks = None
        self._accepts = None

        if hasattr(self, "update"):
            self.add_task(self.update)

        if hasattr(self, "input"):
            for event in events:
                self.accept(f"raw-{event}", self.input, extraArgs=[event])
                self.accept(f"raw-{event}-up", self.input, extraArgs=[f"{event}-up"])
                self.accept(f"raw-shift-{event}", self.input, extraArgs=[f"shift-{event}"])
                self.accept(f"raw-control-{event}", self.input, extraArgs=[f"control-{event}"])
                self.accept(f"raw-alt-{event}", self.input, extraArgs=[f"alt-{event}"])
                self.accept(f"raw-shift-control-{event}", self.input, extraArgs=[f"shift-control-{event}"])
                self.accept(f"raw-shift-control-alt-{event}", self.input, extraArgs=[f"shift-control-alt-{event}"])
                self.accept(f"raw-control-alt-{event}", self.input, extraArgs=[f"control-alt-{event}"])
                self.accept(f"raw-shift-alt-{event}", self.input, extraArgs=[f"shift-alt-{event}"])

    def clean_up(self):
        self.ignore_all()
        self.remove_all_tasks()
        self.nodepath.clear_python_tag(self.__class__.__name__)

    def disable(self):
        print(self._taskList)
        self._tasks.update(self._taskList.copy())
        self._accepts = ...
        self.remove_all_tasks()
        print(self._taskList)

    def enable(self):
        # TODO
        if self._tasks:
            for value in self._tasks:
                self.add_task(*value)


    @property
    def node(self) -> NodePath:
        return self.nodepath.node()

    def get_component(self, name):
        for key, obj in self.nodepath.get_python_tags():
            if name == key:
                return obj

    @property
    def components(self):
        components = {}
        for key, value in self.nodepath.get_python_tags().items():
            if Component in value.__class__.__mro__:
                components[key] = value
        return components


def add_component(nodepath: NodePath, component: Component):
    nodepath.set_python_tag(component.__name__, component(nodepath))


def clean_up(nodepath: NodePath):
    print(nodepath.get_python_tags())
    componets = nodepath.get_python_tag_keys()

    for key in componets:
        obj = nodepath.get_python_tag(key)
        if Component in obj.__class__.__mro__:
            obj.clean_up()

    for child in nodepath.get_children():
        clean_up(child)

    nodepath.remove_node()


if __name__ == '__main__':
    from direct.showbase.ShowBase import ShowBase

    s = ShowBase()
    s.accept("q", s.render.ls)


    class Test(Component):
        def __init__(self, nodepath):
            super().__init__(nodepath)

        def input(self, event):
            print(event)
            if event == "delete":
                clean_up(self.nodepath)

            if event == "w":
                print(self.components)

            if event == "e":
                self.clean_up()


            if event == "d":
                self.disable()

        def update(self, task):
            self.nodepath.set_pos(self.nodepath, (0, 0.01, 0))
            return task.cont


    p = s.loader.load_model("panda")
    p.reparent_to(s.render)
    add_component(p, Test)
    s.run()
