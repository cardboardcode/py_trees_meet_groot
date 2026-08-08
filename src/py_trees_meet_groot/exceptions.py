"""Custom exceptions for py_trees_meet_groot package."""


class GrootXMLParserError(Exception):
    """Base exception for XML parsing errors in Groot XML files.

    Attributes:
        node_name (str): The name of the unknown node encountered.
        xml_element (Element): The XML element that caused the error.
        message (str): Detailed error description.

    Args:
        node_name (str): Name of the unknown node.
        xml_element (Element): The XML element instance.
        message (str, optional): Additional error details. Defaults to None.
    """

    def __init__(self, node_name: str, xml_element, message: str = None):
        self.node_name = node_name
        self.xml_element = xml_element
        self.message = message
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format the error message with context about the unknown node.

        Returns:
            str: Formatted error message.
        """
        if self.message:
            return f"Unknown node '{self.node_name}' encountered. {self.message}"
        return f"Unknown node '{self.node_name}' encountered. Node types are not supported by py_trees_meet_groot."


class UnknownNodeError(GrootXMLParserError):
    """Exception raised when an unknown node type is encountered during XML parsing."""


class MissingRequiredAttributeError(GrootXMLParserError):
    """Exception raised when a required XML attribute is missing."""


class InvalidAttributeValueError(GrootXMLParserError):
    """Exception raised when an XML attribute has an invalid value."""


class BehaviourNotFound(GrootXMLParserError):
    """Exception raised when a behavior is not found during XML parsing.

    Attributes:
        behavior_name (str): The name of the behavior that was not found.
    """

    def __init__(self, behavior_name: str, xml_element, message: str = None):
        self.behavior_name = behavior_name
        super().__init__(behavior_name, xml_element, message)


class SubtreeConfigurationError(GrootXMLParserError):
    """Exception raised when a subtree is malformed or improperly configured."""