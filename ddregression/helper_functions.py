from qiskit import QuantumCircuit
from diff_algorithm import print_edit_sequence
from dd import listminus


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
        print(e)
        print(list_to_circuit(new_sequence, 2))
        while e["position_old"] > i:
            new_sequence.append(s1[i])
            i = i + 1
        if e["position_old"] == i:
            if e["operation"] == "delete":
                i = i + 1
            elif e["operation"] == "insert":
                new_sequence.append(s2[e["position_new"]])
    while i < len(s1):
        print(list_to_circuit(new_sequence, 2))
        new_sequence.append(s1[i])
        i = i + 1
    return new_sequence


def calculate_offset(edit_script, orig_deltas):
    print("############\n in calculate offset \n##############")
    modified_script = []
    for delta in edit_script:
        offset = 0
        index = orig_deltas.index(delta)
        print("id, delta, before, after")
        print(f"index {index}")
        print(f"delta {delta}")
        before = orig_deltas[:index]
        after = orig_deltas[index + 1:]
        print(f"before {before}")
        print(f"after {after}")
        for elem in before:
            print("elem")
            print(elem)
            if elem not in edit_script:
                print("elem not in script")
                print(elem)
                if elem["operation"] == "insert":
                    offset += 1
                elif elem["operation"] == "delete":
                    offset -= 1
        # if delta["operation"] != "delete":
        delta["offset"] = offset
        # else:
        #     delta["offset"] = 0
    print("edit_script")
    print(edit_script)
    for elem in edit_script:
        e2 = elem.copy()
        if e2["operation"] != "delete":
            e2["position_old"] = elem["position_old"] + elem["offset"]
        modified_script.append(e2)
    print("modified_script")
    print(modified_script)
    print("\n\n")
    modified_script = sorted(modified_script, key=lambda k: (k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    return modified_script


def connect_diffs(deltas):
    for diff in deltas:
        pass


def circuit_to_list(circuit: QuantumCircuit):
    """Converts a circuit into a list of instructions"""
    circuit_instructions = []
    for data in circuit.data:
        circuit_instructions.append((data[0], data[1]))
    return circuit_instructions


def list_to_circuit(instruction_arr: list[any], size: int):
    """Converts a list of instructions into a circuit"""
    ret_qc = QuantumCircuit(size, size)
    for instruction, qargs in instruction_arr:
        ret_qc.append(instruction, qargs)
    return ret_qc