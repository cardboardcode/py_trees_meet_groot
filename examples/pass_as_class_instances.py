import operator
import py_trees
import time
from py_trees_meet_groot import groot_xml

# Define Groot Actions and Conditions as py_trees Behaviors
check_door_close = py_trees.behaviours.CheckBlackboardVariableValue(
    name="check_door_close",
    check=py_trees.common.ComparisonExpression(
        variable="door_close",
        value=True,
        operator=operator.eq
    )
)
move_to_door = py_trees.behaviours.Success(name="move_to_door")
open_door = py_trees.behaviours.Failure(name="open_door")
destroy_door = py_trees.behaviours.Success(name="destroy_door")
cross_door = py_trees.behaviours.Success(name="cross_door")
all_behaviors = [
    check_door_close, move_to_door, open_door, destroy_door, cross_door
]

if __name__ == "__main__":
    # Load Groot XML behavior tree
    root = groot_xml.load("xml/test1.xml", behaviors=all_behaviors)

    # DEBUG
    # Visualise parsed BT Groot xml file as py_trees components.
    print(py_trees.display.ascii_tree(root))
    py_trees.display.render_dot_tree(root)  # render behavior tree

    # Play Behavior Tree
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    try:
        root.setup_with_descendants()
        blackboard = py_trees.blackboard.Client(name="main")
        blackboard.register_key(
            "door_close", access=py_trees.common.Access.WRITE
        )
        # Change to False to see how the behavior changes
        blackboard.door_close = True

        root.tick_once()
        time.sleep(0.5)
        print(py_trees.display.ascii_blackboard())
        print("-------------")
        print("-------------")
        print("-------------")

    except KeyboardInterrupt:
        pass
