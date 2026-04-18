#!/usr/bin/env python3

import unittest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml


class TestGrootXMLParsing(unittest.TestCase):

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

    def test_load_valid_xml(self):
        """Test loading a valid Groot XML file."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Sequence>
              <Condition ID="SimpleCondition"/>
              <Action ID="SayHello"/>
            </Sequence>
          </BehaviorTree>
          <TreeNodesModel>
            <Condition ID="SimpleCondition" editable="true"/>
            <Action ID="SayHello" editable="true"/>
          </TreeNodesModel>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            root = groot_xml.load(xml_file_path, behaviors=list(self.behaviors.values()), decorators=self.decorators)
            self.assertIsNotNone(root)
            self.assertEqual(root.name, "sequence")
        finally:
            os.unlink(xml_file_path)

    def test_load_missing_xml(self):
        """Test handling of missing XML file."""
        with self.assertRaises(FileNotFoundError):
            groot_xml.load("/nonexistent/path/test.xml", behaviors=[], decorators={})

    def test_load_empty_xml(self):
        """Test handling of empty XML file."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute=""/>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            root = groot_xml.load(xml_file_path, behaviors=[], decorators={})
            self.assertIsNone(root)
        finally:
            os.unlink(xml_file_path)

    def test_parse_behavior_tree(self):
        """Test parsing of behavior tree nodes."""
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
        finally:
            os.unlink(xml_file_path)


if __name__ == "__main__":
    unittest.main()