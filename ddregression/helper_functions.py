from qiskit import QuantumCircuit

def apply_edit_script(edit_script, s1, s2):
    i, new_sequence = 0, []
    for e in edit_script:
        while e["position_old"] > i:
            new_sequence.append(s1[i])
            i = i + 1
        if e["position_old"] == i:
            if e["operation"] == "delete":
                i = i + 1
            elif e["operation"] == "insert":
                new_sequence.append(s2[e["position_new"]])
    while i < len(s1):
        new_sequence.append(s1[i])
        i = i + 1
    return new_sequence


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
