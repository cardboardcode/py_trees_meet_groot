#!/usr/bin/env python3

import unittest
import os
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from py_trees_meet_groot import groot_xml


class TestDecorators(unittest.TestCase):

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

    def test_timeout_decorator(self):
        """Test parsing of Timeout decorator."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Timeout msec="1000">
              <Action ID="SayHello"/>
            </Timeout>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "timeout")
        finally:
            os.unlink(xml_file_path)

    def test_force_failure_decorator(self):
        """Test parsing of ForceFailure decorator."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <ForceFailure>
              <Action ID="SayHello"/>
            </ForceFailure>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "success_is_failure")
        finally:
            os.unlink(xml_file_path)

    def test_force_success_decorator(self):
        """Test parsing of ForceSuccess decorator."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <ForceSuccess>
              <Action ID="SayHello"/>
            </ForceSuccess>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "failure_is_success")
        finally:
            os.unlink(xml_file_path)

    def test_inverter_decorator(self):
        """Test parsing of Inverter decorator."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root BTCPP_format="3" main_tree_to_execute="BehaviorTree">
          <BehaviorTree ID="BehaviorTree">
            <Inverter>
              <Action ID="SayHello"/>
            </Inverter>
          </BehaviorTree>
        </root>'''

        xml_file_path = self.create_test_xml(xml_content)
        try:
            doc = ET.parse(xml_file_path)
            behavior_tree = doc.getElementsByTagName("BehaviorTree")[0]
            nodes = groot_xml.parse_BehaviourTree(behavior_tree, self.behaviors, self.decorators)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].name, "inverter")
        finally:
            os.unlink(xml_file_path)


if __name__ == "__main__":
    unittest.main()