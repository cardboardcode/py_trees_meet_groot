#!/usr/bin/env python3

import unittest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml


class TestBehaviorTreeNodes(unittest.TestCase):

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

    def test_sequence_node(self):
        """Test parsing of Sequence node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Sequence>
              <Condition ID="SimpleCondition"/>
              <Action ID="SayHello"/>
            </Sequence>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "sequence")
            self.assertTrue(hasattr(nodes[0], 'add_children'))
        finally:
            os.unlink(xml_file_path)

    def test_fallback_node(self):
        """Test parsing of Fallback node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Fallback>
              <Condition ID="SimpleCondition"/>
              <Action ID="SayGoodBye"/>
            </Fallback>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "selector")
        finally:
            os.unlink(xml_file_path)

    def test_parallel_node(self):
        """Test parsing of Parallel node."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Parallel success_threshold="1">
              <Action ID="SayHello"/>
              <Action ID="SayGoodBye"/>
            </Parallel>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "parallel")
        finally:
            os.unlink(xml_file_path)


if __name__ == "__main__":
    unittest.main()