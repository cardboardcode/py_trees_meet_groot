import py_trees
import time
import sys

from py_trees_meet_groot import groot_xml
from nodes.bt_action_node import PrintMessage
from nodes.bt_condition_node import SimpleConditionA


if __name__ == "__main__":
    all_behaviors = [PrintMessage, SimpleConditionA]

    root = groot_xml.load(
        "xml/simple_retryutilsuccessful.xml", behaviors=all_behaviors
    )

    # Register is_A_true key to blackboard.
    blackboard = py_trees.blackboard.Client(name="Global")
    blackboard.register_key(
        key="is_A_true",
        access=py_trees.common.Access.WRITE,
    )
    blackboard.is_A_true = True

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
    counter = 1
    while True:
        if counter == 5:
            blackboard.is_A_true = False

        root.tick_once()
        state = tree.root.status.value
        print(f"Tree Result: {state}")

        if state == "SUCCESS" or state == "FAILURE":
            break
        counter = counter + 1
        time.sleep(1)
