import py_trees
import uuid
import time

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