#!/usr/bin/env python3

import unittest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml


class TestActionsConditions(unittest.TestCase):

    def setUp(self):
        self.behaviors = {
            "SayHello": MagicMock(),
            "SayGoodBye": MagicMock(),
            "SimpleCondition": MagicMock()
        }
        self.decorators = {}

    def create_test_xml(self, xml_content):
        """Create a temporary XML file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            tmp_file.write(xml_content.encode('utf-8'))
            tmp_file_path = tmp_file.name
        return tmp_file_path

    def test_action_node(self):
        """Test parsing of Action node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Action ID="SayHello"/>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "SayHello")
        finally:
            os.unlink(xml_file_path)

    def test_condition_node(self):
        """Test parsing of Condition node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Condition ID="SimpleCondition"/>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
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
            with patch('sys.stdout') as mock_stdout:
                doc = ET.parse(xml_file_path)
                behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
                nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
                self.assertEqual(len(nodes), 1)
                self.assertEqual(nodes[0].name, "UnknownBehavior")
                mock_stdout.assert_called_with("Behavior not found:  UnknownBehavior")
        finally:
            os.unlink(xml_file_path)


if __name__ == "__main__":
    unittest.main()