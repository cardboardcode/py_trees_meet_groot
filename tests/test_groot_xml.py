#!/usr/bin/env python3

import unittest
import uuid
import os
import tempfile
import time
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml
import py_trees


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

    def update(self):
        return py_trees.common.Status.SUCCESS


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
        return py_trees.common.Status.SUCCESS


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


class TestGrootXML(unittest.TestCase):

    def setUp(self):
        self.behaviors = {
            "SayHello": MagicMock(spec=py_trees.behaviour.Behaviour),
            "SayGoodBye": MagicMock(spec=py_trees.behaviour.Behaviour),
            "SimpleCondition": MagicMock(spec=py_trees.behaviour.Behaviour)
        }
        self.decorators = {}

        # Set required attributes for mock behaviors
        for name, mock in self.behaviors.items():
            mock.__name__ = name
            mock.name = name
            mock.parent = None
            mock.children = []
            mock.id = name

    def create_test_xml(self, xml_content):
        """Create a temporary XML file for testing."""
        with tempfile.NamedTemporaryFile(
            suffix='.xml', delete=False
        ) as tmp_file:
            tmp_file.write(xml_content.encode('utf-8'))
            tmp_file_path = tmp_file.name
        return tmp_file_path

    def parse_with_minidom(self, xml_file_path):
        """Parse XML using minidom like the actual code."""
        from xml.dom.minidom import parse
        return parse(xml_file_path)

    def test_load_missing_xml(self):
        """Test handling of missing XML file."""
        with self.assertRaises(FileNotFoundError):
            groot_xml.load(
                "/nonexistent/path/test.xml", behaviors=[], decorators={}
            )

    def test_action_node_parsing(self):
        """Test parsing of Action node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Action ID="SayHello"/>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            with patch(
                'py_trees_meet_groot.groot_xml.py_trees.behaviour.Behaviour'
            ) as mock_behaviour:
                mock_behaviour_instance = MagicMock()
                mock_behaviour_instance.name = "SayHello"
                mock_behaviour_instance.id = "SayHello"
                mock_behaviour.return_value = mock_behaviour_instance

                nodes = groot_xml.parse_BehaviourTree(
                    behavior_tree, self.behaviors, self.decorators
                )
                self.assertEqual(len(nodes), 1)
                self.assertEqual(nodes[0].name, "SayHello")
        finally:
            os.unlink(xml_file_path)

    def test_condition_node_parsing(self):
        """Test parsing of Condition node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Condition ID="SimpleCondition"/>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            with patch(
                'py_trees_meet_groot.groot_xml.py_trees.behaviour.Behaviour'
            ) as mock_behaviour:
                mock_behaviour_instance = MagicMock()
                mock_behaviour_instance.name = "SimpleCondition"
                mock_behaviour_instance.id = "SimpleCondition"
                mock_behaviour.return_value = mock_behaviour_instance

                nodes = groot_xml.parse_BehaviourTree(
                    behavior_tree, self.behaviors, self.decorators
                )
                self.assertEqual(len(nodes), 1)
                self.assertEqual(nodes[0].name, "SimpleCondition")
        finally:
            os.unlink(xml_file_path)

    def test_fallback_node_parsing(self):
        """Test parsing of Fallback node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Fallback>
              <Sequence>
                <Condition ID="SimpleCondition"
                           always_true="False"/>
                <Action ID="PrintMessage"
                        message="Success Action"/>
              </Sequence>
              <Action ID="PrintMessage"
                      message="Fallback Action"/>
            </Fallback>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            local_behaviors = [PrintMessage, SimpleCondition]
            dict_bh = {}
            for bh in local_behaviors:
                if not isinstance(bh, py_trees.behaviour.Behaviour):
                    dict_bh[bh.__name__] = bh
                else:
                    dict_bh[bh.name] = bh
            local_decorators = {}

            # Capture print output
            import io
            from contextlib import redirect_stdout

            ret = []

            nodes = groot_xml.parse_BehaviourTree(
                bh=behavior_tree,
                dict_bh=dict_bh,
                decorators=local_decorators
            )
            seq = py_trees.composites.Sequence(name="sequence", memory=True)
            seq.add_children(nodes)
            ret.append(seq)
            root = ret[0]
            root.setup_with_descendants()

            f = io.StringIO()
            with redirect_stdout(f):
                tree = py_trees.trees.BehaviourTree(root)

                print("--- Ticking BT ---")
                print("Running tree...\n")
                while True:
                    root.tick_once()
                    state = tree.root.status.value
                    print(f"Tree Result: {state}")

                    if state == "SUCCESS":
                        break
            output = f.getvalue()

            self.assertIn("Fallback Action", output)

        finally:
            os.unlink(xml_file_path)

    def test_reactive_sequence_node_parsing(self):
        """Test parsing of ReactiveSequence node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <ReactiveSequence>
              <Condition ID="SimpleConditionA"/>
              <Condition ID="SimpleConditionB"/>
              <Action ID="PrintMessage"
                      message="Simulating long-running task..."/>
              <Action ID="Wait"
                      seconds="2"/>
              <Action ID="PrintMessage"
                      message="All conditions met - Success!"/>
            </ReactiveSequence>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            local_behaviors = [
                PrintMessage,
                SimpleConditionA,
                SimpleConditionB,
                Wait
            ]
            dict_bh = {}
            for bh in local_behaviors:
                if not isinstance(bh, py_trees.behaviour.Behaviour):
                    dict_bh[bh.__name__] = bh
                else:
                    dict_bh[bh.name] = bh
            local_decorators = {}

            # Capture print output
            import io
            from contextlib import redirect_stdout

            ret = []

            nodes = groot_xml.parse_BehaviourTree(
                bh=behavior_tree,
                dict_bh=dict_bh,
                decorators=local_decorators
            )
            seq = py_trees.composites.Sequence(
                name="reactive_sequence",
                memory=True
            )
            seq.add_children(nodes)
            ret.append(seq)
            root = ret[0]
            root.setup_with_descendants()

            f = io.StringIO()
            with redirect_stdout(f):
                tree = py_trees.trees.BehaviourTree(root)

                print("--- Ticking BT ---")
                print("Running tree...\n")
                while True:
                    root.tick_once()
                    state = tree.root.status.value
                    print(f"Tree Result: {state}")

                    if state == "SUCCESS":
                        break
            output = f.getvalue()

            self.assertIn("All conditions met - Success!", output)
            self.assertIn("Simulating long-running task", output)

        finally:
            os.unlink(xml_file_path)

    def test_reactive_fallback_node_parsing(self):
        """Test parsing of ReactiveFallback node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <ReactiveFallback>
              <Condition ID="SimpleCondition" always_true="False"/>
              <Condition ID="SimpleCondition" always_true="False"/>
              <Sequence>
                <Action ID="PrintMessage"
                        message="Simulating long-running task..."/>
                <Action ID="Wait"
                        seconds="2"/>
                <Action ID="PrintMessage"
                    message="Task completed because conditions never triggered"
                />
              </Sequence>
            </ReactiveFallback>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            local_behaviors = [
                PrintMessage,
                SimpleCondition,
                Wait
            ]
            dict_bh = {}
            for bh in local_behaviors:
                if not isinstance(bh, py_trees.behaviour.Behaviour):
                    dict_bh[bh.__name__] = bh
                else:
                    dict_bh[bh.name] = bh
            local_decorators = {}

            # Capture print output
            import io
            from contextlib import redirect_stdout

            ret = []

            nodes = groot_xml.parse_BehaviourTree(
                bh=behavior_tree,
                dict_bh=dict_bh,
                decorators=local_decorators
            )
            fallback = py_trees.composites.Selector(
                name="reactive_fallback", memory=True
            )
            fallback.add_children(nodes)
            ret.append(fallback)
            root = ret[0]
            root.setup_with_descendants()

            f = io.StringIO()
            with redirect_stdout(f):
                tree = py_trees.trees.BehaviourTree(root)

                print("--- Ticking BT ---")
                print("Running tree...\n")
                while True:
                    root.tick_once()
                    state = tree.root.status.value
                    print(f"Tree Result: {state}")

                    if state == "SUCCESS":
                        break
            output = f.getvalue()

            self.assertIn(
                "Task completed because conditions never triggered",
                output
            )
            self.assertIn("Simulating long-running task", output)

        finally:
            os.unlink(xml_file_path)

    def test_unknown_behavior(self):
        """Test handling of unknown behavior."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Action ID="UnknownBehavior"/>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            # Capture print output
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                groot_xml.parse_BehaviourTree(
                    behavior_tree, self.behaviors, self.decorators
                )
            output = f.getvalue()

            self.assertIn(
                "Behavior not found:  UnknownBehavior", output
            )
        finally:
            os.unlink(xml_file_path)

    def test_simple_subtree_parsing(self):
        """Test parsing of SubTree node with parameter replacement."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="4"
              main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Sequence>
              <SubTree ID="PrintMessageTree"
                       msg_target_1="Hello Sub-World!"
                       msg_target_2="Goodbye Sub-World!"
                       _autoremap="true"/>
              <SubTree ID="PrintMessageTree"
                       msg_target_1="Hello again, Sub-World!"
                       msg_target_2="Goodbye again, Sub-World!"
                       _autoremap="true"/>
            </Sequence>
          </BehaviorTree>

          <BehaviorTree ID="PrintMessageTree">
            <Sequence>
              <Action ID="PrintMessage"
                      message="{msg_target_1}"/>
              <Action ID="PrintMessage"
                      message="{msg_target_2}"/>
            </Sequence>
          </BehaviorTree>

          <TreeNodesModel>
            <Action ID="PrintMessage"
                    editable="true">
              <input_port name="message"
                          type="std::string"/>
            </Action>
          </TreeNodesModel>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = self.parse_with_minidom(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]

            local_behaviors = [PrintMessage]
            dict_bh = {}
            for bh in local_behaviors:
                if not isinstance(bh, py_trees.behaviour.Behaviour):
                    dict_bh[bh.__name__] = bh
                else:
                    dict_bh[bh.name] = bh
            local_decorators = {}

            # Create subtrees dictionary like the load function does
            subtrees = {}
            for bht in doc.getElementsByTagName("BehaviorTree"):
                subtree_name = bht.getAttribute("ID")
                if subtree_name != "BehaviorTree":
                    subtrees[subtree_name] = bht

            # Capture print output
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                nodes = groot_xml.parse_BehaviourTree(
                    bh=behavior_tree,
                    dict_bh=dict_bh,
                    decorators=local_decorators,
                    subtrees=subtrees
                )
                seq = py_trees.composites.Sequence(
                    name="sequence", memory=True
                    )
                seq.add_children(nodes)

                tree = py_trees.trees.BehaviourTree(seq)
                root = tree.root

                # Setup and run the tree
                root.setup_with_descendants()

                # Tick once to trigger the subtree execution
                root.tick_once()
            output = f.getvalue()

            # Verify that the subtree parameters were replaced correctly
            self.assertIn("Hello Sub-World!", output)
            self.assertIn("Goodbye Sub-World!", output)
            self.assertIn("Hello again, Sub-World!", output)
            self.assertIn("Goodbye again, Sub-World!", output)
        finally:
            os.unlink(xml_file_path)


if __name__ == '__main__':
    unittest.main()
