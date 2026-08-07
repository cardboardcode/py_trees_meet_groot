import py_trees
import uuid

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

class SimpleConditionA(py_trees.behaviour.Behaviour):
    def __init__(self, **kwargs):
        allowed_keys = {"ID"}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self, key, value)

        name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:4]}"
        super().__init__(name)

        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="is_A_true", access=py_trees.common.Access.READ)

    def update(self):
        print(
            f"[{self.name}][is_A_true] "
            f"- {self.blackboard.is_A_true}"
        )

        if self.blackboard.is_A_true:
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

        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="is_B_true", access=py_trees.common.Access.READ)

    def update(self):
        print(
            f"[{self.name}][is_B_true] "
            f"- {self.blackboard.is_B_true}"
        )

        if self.blackboard.is_B_true:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

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