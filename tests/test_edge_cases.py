#!/usr/bin/env python3

import unittest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml


class TestEdgeCases(unittest.TestCase):

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

    def test_missing_attributes(self):
        """Test handling of missing attributes."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Action></Action>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "Action")
        finally:
            os.unlink(xml_file_path)

    def test_invalid_xml_structure(self):
        """Test handling of malformed XML structure."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Sequence>
              <Condition ID="SimpleCondition">
              <Action ID="SayHello">
            </Sequence>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            with patch('sys.stdout') as mock_stdout:
                doc = ET.parse(xml_file_path)
                behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
                nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
                mock_stdout.assert_called_with("Unknown node Condition")
        finally:
            os.unlink(xml_file_path)

    def test_empty_behavior_tree(self):
        """Test handling of empty behavior tree."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 0)
        finally:
            os.unlink(xml_file_path)

    def test_set_blackboard(self):
        """Test parsing of SetBlackboard node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <SetBlackboard output_key="test_key" value="test_value"></SetBlackboard>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "set_blackboard")
            self.assertEqual(nodes[0].variable_name, "test_key")
            self.assertEqual(nodes[0].variable_value, "test_value")
        finally:
            os.unlink(xml_file_path)


if __name__ == "__main__":
    unittest.main()