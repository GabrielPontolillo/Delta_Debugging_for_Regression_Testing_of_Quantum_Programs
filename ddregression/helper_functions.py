from qiskit import QuantumCircuit
from diff_algorithm import print_edit_sequence


# def apply_edit_script(edit_script, s1, s2):
#     fixed = []
#     for elem in edit_script:
#         if isinstance(elem, tuple):
#             for e in elem:
#                 fixed.append(e)
#         else:
#             fixed.append(elem)
#     print("fixed")
#     print(fixed)
#     edit_script = sorted(fixed, key=lambda k: (k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
#     i, new_sequence = 0, []
#     for e in edit_script:
#         print(e)
#         print(list_to_circuit(new_sequence, 2))
#         while e["position_old"] > i:
#             new_sequence.append(s1[i])
#             i = i + 1
#         if e["position_old"] == i:
#             if e["operation"] == "delete":
#                 i = i + 1
#             elif e["operation"] == "insert":
#                 new_sequence.append(s2[e["position_new"]])
#     while i < len(s1):
#         print(list_to_circuit(new_sequence, 2))
#         new_sequence.append(s1[i])
#         i = i + 1
#     return new_sequence


def apply_edit_script(edit_script, s1, s2, orig_deltas):
    print("##############\nin apply edit script\n#############")
    print_edit_sequence(edit_script, s1, s2)
    fixed = []
    orig_deltas_fixed = []
    for elem in edit_script:
        if isinstance(elem, tuple):
            for e in elem:
                fixed.append(e)
        else:
            fixed.append(elem)
    for elem in orig_deltas:
        if isinstance(elem, tuple):
            for e in elem:
                orig_deltas_fixed.append(e)
        else:
            orig_deltas_fixed.append(elem)
    edit_script = sorted(fixed, key=lambda k: (k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    print("edit script")
    print(edit_script)
    print("original deltas fixed")
    print(orig_deltas_fixed)
    edit_script = calculate_offset(edit_script, orig_deltas_fixed)
    i, new_sequence = 0, []
    for e in edit_script:
        while e["position_old"] > i:
            if len(s1) > i:
                new_sequence.append(s1[i])
            i = i + 1
        if e["position_old"] == i:
            if e["operation"] == "delete":
                i = i + 1
            elif e["operation"] == "insert":
                new_sequence.append(s2[e["position_new"]])
        # print(e)
        # print(list_to_circuit(new_sequence))
    while i < len(s1):
        # print(list_to_circuit(new_sequence))
        new_sequence.append(s1[i])
        i = i + 1
    return new_sequence


def calculate_offset(edit_script, orig_deltas):
    # print("############\n in calculate offset \n##############")
    modified_script = []
    for delta in edit_script:
        offset = 0
        index = orig_deltas.index(delta)
        # print("id, delta, before, after")
        # print(f"index {index}")
        # print(f"delta {delta}")
        before = orig_deltas[:index]
        # print(f"before {before}")
        # print(f"after {after}")
        for elem in before:
            # print("elem")
            # print(elem)
            if elem not in edit_script:
                # print("elem not in script")
                # print(elem)
                if elem["operation"] == "insert":
                    offset += 1
                elif elem["operation"] == "delete":
                    offset -= 1
        delta["offset"] = offset
    # print("edit_script")
    # print(edit_script)
    for elem in edit_script:
        e2 = elem.copy()
        if e2["operation"] != "delete":
            e2["position_old"] = elem["position_old"] + elem["offset"]
        modified_script.append(e2)
    # print("modified_script")
    # print(modified_script)
    # print("\n\n")
    modified_script = sorted(modified_script, key=lambda k: (k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    return modified_script


# def connect_diffs(deltas):
#     linked_deltas = []
#     linked_indexes = []
#     print("########\n\n\n in connect diffs \n\n\n############")
#     for i in range(len(deltas)):
#         if deltas[i]["operation"] == "delete":
#             del_target = deltas[i]["position_old"]
#             for j in range(len(deltas)):
#                 if deltas[j]["operation"] == "insert" and deltas[j]["position_old"] == del_target:
#                     print((deltas[j], deltas[i]))
#                     linked_deltas.append((deltas[j], deltas[i]))
#                     linked_indexes.append(i)
#                     linked_indexes.append(j)
#                     break
#     linked_indexes = sorted(linked_indexes)
#     for i in range(len(deltas)):
#         if i not in linked_indexes:
#             linked_deltas.append(deltas[i])
#     return linked_deltas


# def connect_diffs(deltas):
#     offset = 0
#     for diff in deltas:
#         if diff["operation"] == "delete":
#             offset -= 1
#         elif diff["operation"] == "insert":
#             offset += 1
#     linked_deltas = []
#     linked_indexes = []
#     print("########\n\n\n in connect diffs \n\n\n############")
#     print(f"offset {offset}")
#     for i in range(len(deltas)):
#         if deltas[i]["operation"] == "delete":
#             additional_offset = 0
#             del_target = deltas[i]["position_old"]
#             dupe = True
#             copy_i = i
#             while dupe and copy_i < len(deltas) - 1:
#                 print(deltas[i])
#                 print("inwhile")
#                 ####################################
#                 # we need to look in the actual circuit rather than deltas for equal instruction
#                 ####################################
#                 if deltas[copy_i] == deltas[copy_i+1]:
#                     additional_offset += 1
#                     copy_i += 1
#                 else:
#                     dupe = False
#                     print("additional")
#                     print(additional_offset)
#             for j in range(len(deltas)):
#                 if deltas[j]["operation"] == "insert" and deltas[j]["position_new"] == del_target + offset + additional_offset:
#                     print((deltas[j], deltas[i]))
#                     linked_deltas.append((deltas[j], deltas[i]))
#                     linked_indexes.append(i)
#                     linked_indexes.append(j)
#                     break
#     linked_indexes = sorted(linked_indexes)
#     for i in range(len(deltas)):
#         if i not in linked_indexes:
#             linked_deltas.append(deltas[i])
#     return linked_deltas


def circuit_to_list(circuit: QuantumCircuit):
    """Converts a circuit into a list of instructions"""
    circuit_instructions = []
    for data in circuit.data:
        circuit_instructions.append((data[0], data[1], data[2]))
    return circuit_instructions


def get_quantum_register(instruction_arr: list[any]):
    """Infers size of a quantum circuit from the instructions"""
    print(instruction_arr)
    qarg_ret = None
    carg_ret = None
    for instruction, qargs, cargs in instruction_arr:
        for qarg in qargs:
            qarg_ret = qarg.register
            break
        for carg in cargs:
            carg_ret = carg.register
            break
        return qarg_ret, carg_ret


def list_to_circuit(instruction_arr: list[any]):
    """Converts a list of instructions into a circuit"""
    if instruction_arr is not None and len(instruction_arr) != 0:
        quantum_register, classical_register = get_quantum_register(instruction_arr)
        if classical_register is not None:
            ret_qc = QuantumCircuit(quantum_register.size, classical_register.size)
        else:
            ret_qc = QuantumCircuit(quantum_register.size, quantum_register.size)
        for instruction, qargs, cargs in instruction_arr:
            ret_qc.append(instruction, qargs, cargs)
        return ret_qc
    else:
        return None
