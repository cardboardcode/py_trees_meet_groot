import py_trees
import time
import uuid
import sys

from py_trees_meet_groot import groot_xml

blackboard = py_trees.blackboard.Client(name="Global")


class SimpleConditionA(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        print(
            f"[{self.name}][is_A_true] "
            f"- {blackboard.is_A_true}"
        )

        if blackboard.is_A_true:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class SimpleConditionB(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        print(
            f"[{self.name}][is_B_true] "
            f"- {blackboard.is_B_true}"
        )

        if blackboard.is_B_true:
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


class Wait(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID", "seconds"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        raw_value = getattr(self, "seconds", 10)
        self.duration = int(raw_value)

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)
        self.start_time = None

    def update(self):
        # Initialize the start time on the first tick
        if self.start_time is None:
            print(f"[{self.name}] Starting timer for {self.duration}s...")
            self.start_time = time.time()

        # Calculate how much time has passed
        elapsed = time.time() - self.start_time

        if elapsed >= self.duration:
            print(f"[{self.name}] Time elapsed! ({self.duration}s)")
            # Reset start_time so behavior can be reused later
            self.start_time = None
            return py_trees.common.Status.SUCCESS

        # While waiting, we return RUNNING
        # We print the remaining time just to show it's working in the console
        remaining = int(self.duration - elapsed)
        print(f"[{self.name}] Waiting... {remaining}s remaining")
        return py_trees.common.Status.RUNNING


if __name__ == "__main__":
    all_behaviors = [PrintMessage, SimpleConditionA, SimpleConditionB, Wait]

    root = groot_xml.load(
        "xml/test5.xml", behaviors=all_behaviors
    )

    blackboard.register_key(
        key="is_A_true",
        access=py_trees.common.Access.WRITE,
    )
    blackboard.is_A_true = True

    blackboard.register_key(
        key="is_B_true",
        access=py_trees.common.Access.WRITE,
    )
    blackboard.is_B_true = True

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
            # blackboard.is_A_true = False
            blackboard.is_B_true = False

        root.tick_once()
        state = tree.root.status.value
        print(f"Tree Result: {state}")

        if state == "SUCCESS":
            break
        counter = counter + 1
        time.sleep(1)
