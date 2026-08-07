from xml.dom.minidom import parse, Element

import re
import uuid
import py_trees
import inspect
from .exceptions import UnknownNodeError


def attributes_to_dict(attributes):
    return {
        attributes.item(i).name: attributes.item(i).value
        for i in range(attributes.length)
    }


def load(xml_file_path: str, behaviors: list = [], decorators: dict = {}):
    """Parse XML file into Song Object"""
    dict_bh = {}
    for bh in behaviors:
        if not isinstance(bh, py_trees.behaviour.Behaviour):
            dict_bh[bh.__name__] = bh
        else:
            dict_bh[bh.name] = bh

    doc = parse(xml_file_path)
    root = doc.getElementsByTagName("root")[0]
    main_tree_to_execute = root.getAttribute("main_tree_to_execute")
    behavior_trees = root.getElementsByTagName(main_tree_to_execute)
    ret_array = {}

    subtrees = {}

    for bht in behavior_trees:
        subtree_name = bht.getAttribute("ID")
        if subtree_name != main_tree_to_execute:
            subtrees[subtree_name] = bht

    for bht in behavior_trees:
        if bht.getAttribute("ID") == main_tree_to_execute:
            ret = parse_BehaviourTree(
                bht, dict_bh, decorators, subtrees=subtrees
            )
            ret_array[bht.getAttribute("ID")] = ret

    return ret_array[main_tree_to_execute][0]


def parse_BehaviourTree(
    bh: Element,
    dict_bh: dict,
    decorators: dict,
    ports: dict = None,
    subtrees: Element = None
) -> list:
    ret = []

    # Filter out the text nodes (whitespace)
    filtered_nodes = [
        node for node in bh.childNodes
        if node.nodeType == node.ELEMENT_NODE
    ]

    for e in filtered_nodes:
        # Control
        if str(e.nodeName) == "Sequence":
            if ports is None:
                nodes = parse_BehaviourTree(
                    e, dict_bh, decorators, subtrees=subtrees
                )
                seq = py_trees.composites.Sequence(
                    name=f"seq_{uuid.uuid4().hex[:4]}",
                    memory=True
                )
                seq.add_children(nodes)
                ret.append(seq)
            else:
                nodes = parse_BehaviourTree(
                    e, dict_bh, decorators, ports=ports, subtrees=subtrees
                )
                seq = py_trees.composites.Sequence(
                    name=f"seq_{uuid.uuid4().hex[:4]}",
                    memory=True
                )
                seq.add_children(nodes)
                ret.append(seq)
        elif str(e.nodeName) == "ReactiveSequence":
            nodes = parse_BehaviourTree(
                e, dict_bh, decorators, subtrees=subtrees
            )
            seq = py_trees.composites.Sequence(
                name=f"rseq_{uuid.uuid4().hex[:4]}",
                memory=False
            )
            seq.add_children(nodes)
            ret.append(seq)
        elif str(e.nodeName) == "Fallback":
            nodes = parse_BehaviourTree(
                e, dict_bh, decorators, subtrees=subtrees
            )
            sel = py_trees.composites.Selector(
                name=f"fall_{uuid.uuid4().hex[:4]}",
                memory=True
            )
            sel.add_children(nodes)
            ret.append(sel)
        elif str(e.nodeName) == "ReactiveFallback":
            nodes = parse_BehaviourTree(
                e, dict_bh, decorators, subtrees=subtrees
            )
            sel = py_trees.composites.Selector(
                name=f"rfall_{uuid.uuid4().hex[:4]}",
                memory=False
            )
            sel.add_children(nodes)
            ret.append(sel)
        elif str(e.nodeName) == "Parallel":
            th = None
            if e.getAttribute("success_threshold") != "":
                th = int(e.getAttribute("success_threshold"))
            if e.getAttribute("success_count") != "":
                th = int(e.getAttribute("success_count"))
            nodes = parse_BehaviourTree(e, dict_bh, decorators)
            if th == 1:
                par = py_trees.composites.Parallel(
                    name=f"parallel_{uuid.uuid4().hex[:4]}",
                    policy=py_trees.common.ParallelPolicy.SuccessOnOne(),
                )
            else:
                par = py_trees.composites.Parallel(
                    name=f"parallel_{uuid.uuid4().hex[:4]}",
                    policy=py_trees.common.ParallelPolicy.SuccessOnAll(),
                )
            par.add_children(nodes)
            ret.append(par)

        # Decorators
        elif str(e.nodeName) == "Timeout":
            node = parse_BehaviourTree(e, dict_bh, decorators, ports=ports)
            dec = py_trees.decorators.Timeout(
                child=node[0],
                name=f"timeout_{uuid.uuid4().hex[:4]}",
                duration=float(e.getAttribute("msec")) / 1000,
            )
            ret.append(dec)
        elif str(e.nodeName) == "ForceFailure":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            dec = py_trees.decorators.SuccessIsFailure(
                child=node[0],
                name=f"success_is_failure_{uuid.uuid4().hex[:4]}"
            )
            ret.append(dec)
        elif str(e.nodeName) == "ForceSuccess":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            dec = py_trees.decorators.FailureIsSuccess(
                child=node[0],
                name=f"failure_is_success_{uuid.uuid4().hex[:4]}"
            )
            ret.append(dec)
        elif str(e.nodeName) == "Inverter":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            dec = py_trees.decorators.Inverter(
                child=node[0],
                name=f"inverter_{uuid.uuid4().hex[:4]}"
            )
            ret.append(dec)
        elif str(e.nodeName) == "Decorator":
            id = e.getAttribute("ID")
            print("id", id)
            print(decorators.keys())
            if id in decorators.keys():
                node = parse_BehaviourTree(e, dict_bh, decorators)
                dec = decorators[id](name=id, child=node[0])
                ret.append(dec)
            else:
                print("Unknown decorator", id)
        elif str(e.nodeName) in decorators:
            id = str(e.nodeName)
            name = id
            if e.getAttribute("name") != "":
                name = e.getAttribute("name")
            node = parse_BehaviourTree(e, dict_bh, decorators)
            dec = decorators[id](name=name, child=node[0])
            ret.append(dec)
        elif str(e.nodeName) == "RetryUntilSuccessful":
            node = parse_BehaviourTree(e, dict_bh, decorators, ports=ports)
            dec = py_trees.decorators.FailureIsRunning(
                child=node[0],
                name=f"failure_is_running_{uuid.uuid4().hex[:4]}"
            )
            ret.append(dec)
        elif str(e.nodeName) == "KeepRunningUntilFailure":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            dec = py_trees.decorators.SuccessIsRunning(
                child=node[0],
                name=f"success_is_running_{uuid.uuid4().hex[:4]}"
            )
            ret.append(dec)
        elif str(e.nodeName) == "Repeat":
            node = parse_BehaviourTree(e, dict_bh, decorators, ports=ports)
            attrs_dict = attributes_to_dict(e.attributes)

            for key, val in attrs_dict.items():
                try:
                    for port_key, port_value in ports.items():
                        if port_key.upper() in val.upper():
                            attrs_dict[key] = port_value
                except Exception:
                    pass

            if e.getAttribute("num_cycles") != "":
                num_cycles = e.getAttribute("num_cycles")
            else:
                # TODO(cardboardcode): Implement exception to raise here
                pass

            dec = py_trees.decorators.Repeat(
                child=node[0],
                name=f"repeat_{uuid.uuid4().hex[:4]}",
                num_success=int(num_cycles)
            )
            ret.append(dec)
        elif str(e.nodeName) == "Delay":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            attrs_dict = attributes_to_dict(e.attributes)

            for key, val in attrs_dict.items():
                try:
                    for port_key, port_value in ports.items():
                        if port_key.upper() in val.upper():
                            attrs_dict[key] = port_value
                except Exception:
                    pass

            if e.getAttribute("delay_msec") != "":
                delay_msec = int(e.getAttribute("delay_msec"))
            else:
                # TODO(cardboardcode): Implement exception to raise here
                pass

            inner_sequence = py_trees.composites.Sequence(
                name=f"timer_seq_{uuid.uuid4().hex[:4]}",
                memory=True
            )
            inner_sequence.add_children([
                py_trees.timers.Timer(
                    name=f"timer_{uuid.uuid4().hex[:4]}",
                    duration=delay_msec/1000
                ),
                node[0]
            ])

            ret.append(inner_sequence)
        # Actions
        elif str(e.nodeName) == "SetBlackboard":
            output_key = e.getAttribute("output_key")
            value = e.getAttribute("value")
            # TODO(cardboardcode): Assign unique id for name.
            set_blackboard = py_trees.behaviours.SetBlackboardVariable(
                name="set_blackboard",
                variable_name=output_key,
                variable_value=value,
                overwrite=True,
            )
            ret.append(set_blackboard)
        elif str(e.nodeName) == "Action" or str(e.nodeName) == "Condition":

            # Check if Action/Condition is in a subtree.
            # If true, map port_value to subtree inputs accordingly.
            if subtrees is not None:
                print(f"inside [Action/Condition] ports = {ports}")

            attrs_dict = attributes_to_dict(e.attributes)

            for key, val in attrs_dict.items():
                try:
                    if ports is not None:
                        # Look for any matching port key of the node itself
                        # to any passed ports from subtree if any.
                        for port_key, port_value in ports.items():
                            if ports["_autoremap"]:
                                if port_key.upper() in val.upper():
                                    attrs_dict[key] = port_value
                except Exception as error:
                    print(f"{error}")
                    pass

            # Assign Action/Condition name based on properties,
            # name or ID as defined in xml.
            if e.getAttribute("name") != "":
                name = e.getAttribute("name")
            else:
                name = e.getAttribute("ID")

            # Iterate through key values in dict_bh
            # As long as key value is a substring in name, append using
            # identified key_value
            is_bh_notfound = True
            for bh_name in dict_bh:
                if bh_name in name:
                    if inspect.isclass(dict_bh[name]):
                        ret.append(dict_bh[name](**attrs_dict))
                    else:
                        ret.append(dict_bh[name])
                    is_bh_notfound = False
                    break
            if is_bh_notfound:
                print("Behavior not found: ", name)
                ret.append(py_trees.behaviours.Success(name=name))

        elif str(e.nodeName) in dict_bh:
            ret.append(dict_bh[str(e.nodeName)])
        elif str(e.nodeName) == "AlwaysSuccess":
            ret.append(py_trees.behaviours.Success())
        elif str(e.nodeName) == "AlwaysFailure":
            ret.append(py_trees.behaviours.Failure())
        elif str(e.nodeName) == "Sleep":

            attrs_dict = attributes_to_dict(e.attributes)

            for key, val in attrs_dict.items():
                try:
                    for port_key, port_value in ports.items():
                        if port_key.upper() in val.upper():
                            attrs_dict[key] = port_value
                except Exception:
                    pass

            if e.getAttribute("msec") != "":
                msec = int(e.getAttribute("msec"))

            ret.append(py_trees.timers.Timer(
                    name=f"timer_{uuid.uuid4().hex[:4]}",
                    duration=msec/1000
                )
            )
        elif str(e.nodeName) == "SubTree":
            if e.getAttribute("name") != "":
                name = e.getAttribute("name")
            else:
                name = e.getAttribute("ID")
            seq = py_trees.composites.Sequence(
                name=f"{name}_SubTree_{uuid.uuid4().hex[:4]}",
                memory=True
            )
            # Extract port values
            attr_map = {}
            for i in range(e.attributes.length):
                attr = e.attributes.item(i)
                attr_map[attr.name] = attr.value

            nodes = parse_BehaviourTree(
                subtrees[name], dict_bh, decorators, ports=attr_map
            )
            seq.add_children(nodes)
            ret.append(seq)
        else:
            print(f"Unknown Node has Node Name:{str(e.nodeName)}")
            raise UnknownNodeError(node_name=str(e.nodeName), xml_element=e)
    return ret
