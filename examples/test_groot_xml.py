#!/usr/bin/env python3

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml
import py_trees


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
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
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
            groot_xml.load("/nonexistent/path/test.xml", behaviors=[], decorators={})

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

            with patch('py_trees_meet_groot.groot_xml.py_trees.behaviour.Behaviour') as mock_behaviour:
                mock_behaviour_instance = MagicMock()
                mock_behaviour_instance.name = "SayHello"
                mock_behaviour_instance.id = "SayHello"
                mock_behaviour.return_value = mock_behaviour_instance

                nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
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

            with patch('py_trees_meet_groot.groot_xml.py_trees.behaviour.Behaviour') as mock_behaviour:
                mock_behaviour_instance = MagicMock()
                mock_behaviour_instance.name = "SimpleCondition"
                mock_behaviour_instance.id = "SimpleCondition"
                mock_behaviour.return_value = mock_behaviour_instance

                nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
                self.assertEqual(len(nodes), 1)
                self.assertEqual(nodes[0].name, "SimpleCondition")
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
            import sys
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            output = f.getvalue()

            self.assertIn("Behavior not found:  UnknownBehavior", output)
        finally:
            os.unlink(xml_file_path)


if __name__ == '__main__':
    unittest.main()