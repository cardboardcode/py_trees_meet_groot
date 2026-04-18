import py_trees
import time
import uuid
import sys
from py_trees_meet_groot import groot_xml

class Wait(py_trees.behaviour.Behaviour):
    def __init__(self, name=None, duration=10):
        if name is None:
            name = f"Wait_{uuid.uuid4().hex[:4]}"
        super().__init__(name)
        self.duration = duration
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
            # Reset start_time so the behavior can be reused if ticked again later
            self.start_time = None 
            return py_trees.common.Status.SUCCESS
        
        # While waiting, we return RUNNING
        # We print the remaining time just to show it's working in the console
        remaining = int(self.duration - elapsed)
        print(f"[{self.name}] Waiting... {remaining}s remaining")
        return py_trees.common.Status.RUNNING

class SayHello(py_trees.behaviour.Behaviour):

    def __init__(self, name=None):
        if name is None:
            name = f"SayHello_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

    def update(self):
        print("Hello!")
        return py_trees.common.Status.SUCCESS  # Using common.SUCCESS is more standard

if __name__ == "__main__":

    # say_hello = SayHello()
    # wait = Wait()
    all_behaviors=[SayHello, Wait]

    root = groot_xml.load("test3.xml", behaviors=all_behaviors)

    if root is None:
        print("Failed to load Groot BT .xml file")
        sys.exit(1)

    # DEBUG
    # Visualise parsed BT Groot xml file as py_trees components.
    # print(py_trees.display.ascii_tree(root))
    py_trees.display.render_dot_tree(root) # render behavior tree

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
        
