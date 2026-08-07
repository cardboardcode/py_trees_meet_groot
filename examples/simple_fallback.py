import py_trees
import time
import sys

from py_trees_meet_groot import groot_xml
from nodes.bt_action_node import PrintMessage
from nodes.bt_condition_node import SimpleCondition


if __name__ == "__main__":
    all_behaviors = [PrintMessage, SimpleCondition]

    root = groot_xml.load("xml/simple_fallback.xml", behaviors=all_behaviors)

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

        if state == "SUCCESS":
            break
        time.sleep(1)
