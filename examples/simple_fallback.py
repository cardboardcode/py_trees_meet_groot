import py_trees
import time
import uuid
import sys

from py_trees_meet_groot import groot_xml


class SimpleCondition(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID", "always_true"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        raw_value = getattr(self, "always_true", True)
        self.always_true = False if raw_value.upper() == "FALSE" else True

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        if self.always_true:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class PrintMessage(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID", "message"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        self.message = getattr(self, "message", "Insert message here.")

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        print(self.message)
        return py_trees.common.Status.SUCCESS


if __name__ == "__main__":
    all_behaviors = [PrintMessage, SimpleCondition]

    root = groot_xml.load("xml/test4.xml", behaviors=all_behaviors)

    if root is None:
        print("Failed to load Groot BT .xml file")
        sys.exit(1)

    # DEBUG
    # Visualise parsed BT Groot xml file as py_trees components.
    # print(py_trees.display.ascii_tree(root))
    # py_trees.display.render_dot_tree(root)  # render behavior tree

    root.setup_with_descendants()
    tree = py_trees.trees.BehaviourTree(root)

    print("--- Ticking BT ---")
    print("Running tree...\n")
    while True:
        root.tick_once()
        state = tree.root.status.value
        print(f"Tree Result: {state}")

        if state == "SUCCESS":
            break
        time.sleep(1)
