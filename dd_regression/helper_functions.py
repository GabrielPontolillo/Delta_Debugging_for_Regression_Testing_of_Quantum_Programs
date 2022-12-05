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
    print("##############in apply edit script#############")
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
    """Removed sorted"""
    edit_script = sorted(fixed, key=lambda k: (
        k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    edit_script = calculate_offset(edit_script, orig_deltas_fixed, s1, s2)

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
        print_edit_sequence([e], s1, s2)
        # print(list_to_circuit(new_sequence))
    while i < len(s1):
        # print(list_to_circuit(new_sequence))
        new_sequence.append(s1[i])
        i = i + 1
    return new_sequence


def calculate_offset(edit_script, orig_deltas, orig_circ, mod_circ):
    """
    Calculate offset to apply to the deltas, when only subsets of the overall deltas are applied
    look at the missing deltas from the original set of deltas, for each delta in the subset of deltas applied,
    we look at the missing deletion deltas after with the same position_old and consecutive deletions thereafter
    we apply an offset for each consecutive deletion after, such that the deltas can be applied correctly
    :param edit_script: the list of deltas that (subset)
    :param orig_deltas: original list of deltas (to compare ordering)
    :return:
    """
    # print("############ in calculate offset ##############")
    # print(edit_script)
    # print(orig_deltas)
    modified_script = []
    for i, delta in enumerate(edit_script):
        # print("\n---")
        # print(delta)
        # print("---\n")
        offset = 0
        consec = 0
        after = listminus(orig_deltas[i + 1:], edit_script)
        # print(after)
        for j, elem in enumerate(after):
            # if delete missing as the same position as the delta in edit script, as well as consequent ones
            # however, if element we need to insert is the same as (need further mod)
            if after[j]["operation"] == "delete" and after[j]["position_old"] == edit_script[i]["position_old"] + consec:
                print("check in calc offset")
                # print(orig_circ[edit_script[i]["position_old"] + consec])
                # print(orig_circ[after[j]["position_old"] + consec])
                # print(mod_circ[edit_script[i]["position_new"]])
            # if after[j]["operation"] == "delete" and (after[j]["position_old"] == edit_script[i]["position_old"] + consec or orig_circ[edit_script[i]["position_old"] + consec] == mod_circ[edit_script[i]["position_new"]]):
                consec += 1
                offset += 1
            #     # print(after[j])
            #     # print(edit_script[i])
            # if after[j]["operation"] == "delete":
            #     offset += 1
        delta["offset"] = offset
        e2 = delta.copy()
        if e2["operation"] != "delete":
            e2["position_old"] = delta["position_old"] + delta["offset"]
        modified_script.append(e2)
    modified_script = sorted(modified_script, key=lambda k: (
        k.get('position_old', None), "position_new" not in k, k.get("position_new", None)))
    print("out of calculate offset")
    # print(modified_script)
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
    # for i in range(random.randint(1, 2)):
    for i in range(2):
        # choose what identities to append
        j = random.randint(0, 4)
        target_qubit = random.randint(0, qubit_size - 1)
        # target_qubit = 1
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
        # insert_location = 5
        # print(f"insert location {insert_location}")
        circ_list[insert_location:insert_location] = qc_list
        # print(circ_list)
    # print(list_to_circuit(circ_list))
    return circ_list


def determine_delta_application_valid(delta_position_old, base_circuit_list, filtered_delta_position_old,
                                      chaff_embedded_circuit_list):
    """To be able to determine whether the delta that we are applying is correct, even after chaff is applied
        We need a way to be able to calculate whether the isolated delta is being applied in the correct location
        (Particularly for insert deltas)
    """
    # check the gates before and after, make sure that filtered deltas after include all before and after
    before_old = base_circuit_list[:delta_position_old]
    print(before_old)
    after_old = base_circuit_list[delta_position_old + 1:]
    print(after_old)
    before_new = chaff_embedded_circuit_list[:filtered_delta_position_old]
    print(before_new)
    after_new = chaff_embedded_circuit_list[filtered_delta_position_old + 1:]
    print(after_new)


def listminus(c1, c2):
    """Return all elements of C1 that are not in C2.
    Assumes elements of C1 are hashable."""
    diffs = []
    for elem in c1:
        found = False
        for elem2 in c2:
            if elem == elem2:
                found = True
        if not found:
            diffs.append(elem)
    return diffs


def list_contains_list_in_same_order(larger_list, smaller_list):
    l = larger_list.copy()
    s = smaller_list.copy()
    for elem in l:
        if len(s) > 0 and elem == s[0]:
            s.pop(0)
    return len(s) == 0

