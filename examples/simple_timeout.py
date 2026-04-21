import py_trees
import time
import uuid
import sys

from py_trees_meet_groot import groot_xml


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
    all_behaviors = [Wait]

    root = groot_xml.load(
        "xml/test8.xml", behaviors=all_behaviors
    )

    if root is None:
        print("Failed to load Groot BT .xml file")
        sys.exit(1)

    # DEBUG
    # Visualise parsed BT Groot xml file as py_trees components.
    # print(py_trees.display.ascii_tree(root))
    py_trees.display.render_dot_tree(root)  # render behavior tree

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
