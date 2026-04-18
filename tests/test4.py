import py_trees
import time
import uuid
import sys
from py_trees_meet_groot import groot_xml

class SimpleCondition(py_trees.behaviour.Behaviour):
    def __init__(self, name="None", always_true=False):
        if name is None:
            name = f"SimpleCondition_{uuid.uuid4().hex[:4]}"
        self.always_true = always_true
        super().__init__(name)

    def update(self):

        if self.always_true:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class SayGoodBye(py_trees.behaviour.Behaviour):

    def __init__(self, name=None):
        if name is None:
            name = f"SayGoodBye_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        print("Goodbye!")
        return py_trees.common.Status.SUCCESS  # Using common.SUCCESS is more standard

class SayHello(py_trees.behaviour.Behaviour):

    def __init__(self, name=None):
        if name is None:
            name = f"SayHello_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        print("Hello!")
        return py_trees.common.Status.SUCCESS  # Using common.SUCCESS is more standard

if __name__ == "__main__":

    all_behaviors=[SayHello, SayGoodBye, SimpleCondition]

    root = groot_xml.load("test4.xml", behaviors=all_behaviors)

    if root is None:
        print("Failed to load Groot BT .xml file")
        sys.exit(1)

    # DEBUG
    # Visualise parsed BT Groot xml file as py_trees components.
    # print(py_trees.display.ascii_tree(root))
    # py_trees.display.render_dot_tree(root) # render behavior tree

    root.setup_with_descendants()
    tree = py_trees.trees.BehaviourTree(root)

    print("--- Ticking BT ---")
    print("Running tree...\n")
    while (True):
        root.tick_once()
        state = tree.root.status.value
        print(f"Tree Result: {state}")

        if state == 'SUCCESS':
            break

        time.sleep(1)
        
