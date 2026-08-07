import py_trees
import time
import uuid
import sys

from py_trees_meet_groot import groot_xml


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

class DoesBlackboardValueExist(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID", "key_name"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        self.key_name = getattr(self, "key_name", "Insert key_name here.")

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key=self.key_name, access=py_trees.common.Access.READ)

    def update(self):
        print(f"Checking for blackboard key: [{self.key_name}]...")

        try:
            if hasattr(self.blackboard, self.key_name):
                print(f"[INFO] - Blackboard key [{self.key_name}] does exist...")
                return py_trees.common.Status.SUCCESS
            else:
                return py_trees.common.Status.FAILURE
        except KeyError as error:
            print(f"[ERROR] - {error}")
            return py_trees.common.Status.FAILURE

if __name__ == "__main__":
    all_behaviors = [PrintMessage, DoesBlackboardValueExist]

    root = groot_xml.load(
        "xml/subtree_conditions_actions.xml", behaviors=all_behaviors
    )

    if root is None:
        print("Failed to load Groot BT .xml file")
        sys.exit(1)

    # DEBUG
    # Visualise parsed BT Groot xml file as py_trees components.
    # print(py_trees.display.ascii_tree(root))
    # py_trees.display.render_dot_tree(root)  # render behavior tree

    py_trees.logging.level = py_trees.logging.Level.DEBUG
    root.setup_with_descendants()
    tree = py_trees.trees.BehaviourTree(root)

    print("--- Ticking BT ---")
    print("Running tree...\n")
    while True:
        root.tick_once()
        state = tree.root.status.value
        print(f"Tree Result: {state}")

        if state == "SUCCESS" or state == "FAILURE":
            break
        time.sleep(1)
