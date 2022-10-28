import random

from qiskit import QuantumCircuit
from dd_regression.diff_algorithm import print_edit_sequence


def apply_edit_script(edit_script, s1, s2, orig_deltas):
    """
    Apply deltas to the list of circumstances to get a new list of updated circumstances
    :param edit_script:
    :param s1:
    :param s2:
    :param orig_deltas:
    :return:
    """
    print("##############\nin apply edit script\n#############")
    # print_edit_sequence(edit_script, s1, s2)
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
    edit_script = sorted(fixed, key=lambda k: (
        k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    print("edit script")
    # for script in edit_script:
    #     print(script)
    print_edit_sequence(edit_script, s1, s2)
    print("original deltas fixed")
    # print(orig_deltas_fixed)
    # for script in orig_deltas_fixed:
    #     print(script)
    print_edit_sequence(orig_deltas_fixed, s1, s2)
    edit_script = calculate_offset(edit_script, orig_deltas_fixed)
    print("edit script after offset")
    # for script in edit_script:
    #     print(script)
    print_edit_sequence(edit_script, s1, s2)
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
        print(e)
        print_edit_sequence([e], s1, s2)
        print(list_to_circuit(new_sequence))
    while i < len(s1):
        # print(list_to_circuit(new_sequence))
        new_sequence.append(s1[i])
        i = i + 1
    return new_sequence


def calculate_offset(edit_script, orig_deltas):
    """
    Calculate offset to apply to the deltas, when only subsets of the overall deltas are applied
    :param edit_script:
    :param orig_deltas:
    :return:
    """
    print("############\n in calculate offset \n##############")
    for script in orig_deltas:
        print(script)
    print("edit script")
    for script in edit_script:
        print(script)
    modified_script = []
    for delta in edit_script:
        offset = 0
        index = orig_deltas.index(delta)
        # print("id, delta, before, after")
        # print(f"index {index}")
        # print(f"delta {delta}")
        # before = orig_deltas[:index]
        # print(f"before {before}")
        after = orig_deltas[index + 1:]
        # print(f"after {after}")
        # for elem in before:
        # print("elem")
        # print(elem)
        # if elem not in edit_script:
        # print("elem not in script")
        # print(elem)
        # if elem["operation"] == "insert" and elem["position_old"] == delta["position_old"]:
        #     offset += 1
        # if elem["operation"] == "delete":
        #     offset -= 1
        # if elem["operation"] == "delete":
        #     offset -= 1
        # pass
        consec = 0
        for elem in after:
            # print("elem")
            # print(elem)
            if elem not in edit_script:
                # print("elem not in script")
                # print(elem)
                # if elem["operation"] == "insert" and elem["position_old"] == delta["position_old"]:
                #     offset -= 1
                # if elem["operation"] == "delete":
                #     offset -= 1
                # if elem["operation"] == "delete" and elem["position_old"] == delta["position_old"] + consec:
                #     print(f"elem pos {elem['position_old']}")
                #     print(f"delta pos {delta['position_old']}")
                #     print(f"consec {consec}")
                #     offset += 1
                #     consec += 1
                if elem["operation"] == "delete" and elem["position_old"] == delta["position_old"]:
                    print(f"elem pos {elem['position_old']}")
                    print(f"delta pos {delta['position_old']}")
                    print(f"consec {consec}")
                    offset += 1
                    consec += 1
                pass
        delta["offset"] = offset
    # print("edit_script")
    # print(edit_script)
    for elem in edit_script:
        e2 = elem.copy()
        if e2["operation"] != "delete":
            e2["position_old"] = elem["position_old"] + elem["offset"]
        modified_script.append(e2)
    modified_script = sorted(modified_script, key=lambda k: (
        k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    print("modified_script")
    print(modified_script)
    print("\n\n")
    return modified_script


def circuit_to_list(circuit: QuantumCircuit):
    """Converts a circuit into a list of instructions"""
    circuit_instructions = []
    for data in circuit.data:
        circuit_instructions.append((data[0], data[1], data[2]))
    return circuit_instructions


def get_quantum_register(instruction_arr: list[any]):
    """Infers size of a quantum circuit from the instructions"""
    # print(instruction_arr)
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


def add_random_chaff(circuit: QuantumCircuit):
    # print(circuit)
    qarg, carg = get_quantum_register(circuit)
    circ_list = circuit_to_list(circuit)
    # print(circ_list)
    # print(qarg.size)
    qubit_size = qarg.size
    # choose how many to append
    for i in range(random.randint(1, 6)):
        # choose what identities to append
        j = random.randint(0, 5)
        target_qubit = random.randint(0, qubit_size-1)
        # print(target_qubit)
        if j == 0:
            qc = QuantumCircuit(qubit_size)
            qc.x(target_qubit)
            qc.x(target_qubit)
        elif j == 1:
            qc = QuantumCircuit(qubit_size)
            qc.i(target_qubit)
        elif j == 2:
            qc = QuantumCircuit(qubit_size)
            qc.y(target_qubit)
            qc.y(target_qubit)
        elif j == 3:
            qc = QuantumCircuit(qubit_size)
            qc.z(target_qubit)
            qc.z(target_qubit)
        elif j == 4:
            qc = QuantumCircuit(qubit_size)
            qc.h(target_qubit)
            qc.h(target_qubit)
        elif j == 5:
            qc = QuantumCircuit(qubit_size)
            qc.s(target_qubit)
            qc.s(target_qubit)
            qc.s(target_qubit)
            qc.s(target_qubit)
        qc_list = circuit_to_list(qc)
        # choose where to append the chaff
        insert_location = random.randint(0, len(circ_list))
        # print(f"insert location {insert_location}")
        circ_list[insert_location:insert_location] = qc_list
        # print(circ_list)
    # print(list_to_circuit(circ_list))
    return circ_list
