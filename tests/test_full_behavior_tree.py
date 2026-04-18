#!/usr/bin/env python3

import unittest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml


class TestFullBehaviorTree(unittest.TestCase):

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

    def test_full_behavior_tree(self):
        """Test parsing and execution of a complete behavior tree with nested nodes and decorators."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Fallback>
              <Sequence>
                <Condition ID="SimpleCondition"/>
                <Action ID="SayHello"/>
              </Sequence>
              <Timeout msec="1000">
                <Action ID="SayGoodBye"/>
              </Timeout>
            </Fallback>
          </BehaviorTree>
          <TreeNodesModel>
            <Condition ID="SimpleCondition" editable="true"/>
            <Action ID="SayHello" editable="true"/>
            <Action ID="SayGoodBye" editable="true"/>
          </TreeNodesModel>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            root = groot_xml.load(xml_file_path, behaviors=list(self.behaviors.values()), decorators=self.decorators)
            self.assertIsNotNone(root)
            self.assertEqual(root.name, "selector")
            self.assertEqual(len(root.children), 2)

            # Check first child (Sequence)
            sequence = root.children[0]
            self.assertEqual(sequence.name, "sequence")
            self.assertEqual(len(sequence.children), 2)

            # Check second child (Timeout decorator)
            timeout = root.children[1]
            self.assertEqual(timeout.name, "timeout")
            self.assertEqual(timeout.child.name, "SayGoodBye")
        finally:
            os.unlink(xml_file_path)


if __name__ == "__main__":
    unittest.main()