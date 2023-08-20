import random
import csv


from qiskit import QuantumCircuit


def circuit_to_list(circuit: QuantumCircuit):
    """Converts a circuit into a list of instructions"""
    circuit_instructions = []
    for data in [circuitIns for circuitIns in circuit.data]:
        circuit_instructions.append((data[0], data[1], data[2]))
    return circuit_instructions


def get_quantum_register(instruction_arr: list[any]):
    """Infers size of a quantum circuit from the instructions"""
    # print(instruction_arr)
    assert len(instruction_arr) > 0
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


def add_random_chaff(circuit: QuantumCircuit, chaff_length=None):
    #interested in decomposing gates and replacing
    qarg, carg = get_quantum_register(circuit)
    circ_list = [circuitIns for circuitIns in circuit.data]
    # print(circ_list)
    # print(qarg.size)
    qubit_size = qarg.size
    # choose how many to append
    if chaff_length is None:
        chaff_length = range(random.randint(1, 8))
    for i in range(chaff_length):
        # choose what identities to append
        j = random.randint(0, 3)
        target_qubit = random.randint(0, qubit_size - 1)
        if j == 0:
            qc = QuantumCircuit(qubit_size)
            qc.x(target_qubit)
            qc.x(target_qubit)
        elif j == 1:
            qc = QuantumCircuit(qubit_size)
            qc.x(target_qubit)
            qc.x(target_qubit)
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
            qc.i(target_qubit)
        elif j == 5:
            qc = QuantumCircuit(qubit_size)
            qc.s(target_qubit)
            qc.s(target_qubit)
            qc.s(target_qubit)
            qc.s(target_qubit)
        qc_list = [circuitIns for circuitIns in qc.data]
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


def order_list_by_another_list(sublist, superlist, logging=False):
    if logging:
        print("sublist:")
        print(sublist)
        print("superlist:")
        print(superlist)
    sublist_modifiable_copy = sublist.copy()
    result = []
    for element in superlist:
        if element in sublist_modifiable_copy:
            result.append(element)
            sublist_modifiable_copy.remove(element)
    if logging:
        print("re-ordered list:")
        print(result)
    return result


def files_to_spreadsheet(algorithm_name, chaff_lengths, inputs_per_properties, number_of_properties, number_of_measurements,
                         significance_level, test_amount):
    output_dict = dict()
    for chaff_length in chaff_lengths:
        for inputs_per_property in inputs_per_properties:
            try:
                f = open(f"{algorithm_name}_cl{chaff_length}_in{inputs_per_property}_prop{number_of_properties}_meas{number_of_measurements}_sig{significance_level}_tests{test_amount}.txt","r")
                output = f.read().split('\n')
                print(output)
                output_dict[(chaff_length, inputs_per_property, "correctly found")] = output[1]
                output_dict[(chaff_length, inputs_per_property, "expected to find")] = output[2]
                output_dict[(chaff_length, inputs_per_property, "artifacts in output")] = output[4]
                output_dict[(chaff_length, inputs_per_property, "artifacts added")] = output[5]
                output_dict[(chaff_length, inputs_per_property, "time")] = output[7]
                f.close()
            except OSError as err:
                output_dict[(chaff_length, inputs_per_property, "correctly found")] = ""
                output_dict[(chaff_length, inputs_per_property, "expected to find")] = ""
                output_dict[(chaff_length, inputs_per_property, "artifacts in output")] = ""
                output_dict[(chaff_length, inputs_per_property, "artifacts added")] = ""
                output_dict[(chaff_length, inputs_per_property, "time")] = ""

    print(output_dict)
    rows = []
    row1 = ["X", ""]
    for i in range(len(chaff_lengths)):
        row1.append(f"{chaff_lengths[i] * 2} inserted deltas")
    rows.append(row1)

    for inputs_per_property in inputs_per_properties:
        for outputs in ["correctly found", "expected to find", "percentage found", "artifacts in output", "artifacts added", "ratio correct/artifact", "time"]:
            row = [""]
            if outputs == "correctly found":
                row[0] = f"{inputs_per_property} inputs/test "
            row.append(outputs)
            for chaff_length in chaff_lengths:
                if outputs == "percentage found":
                    correctly_found = output_dict.get((chaff_length, inputs_per_property, "correctly found"))
                    expected_to_find = output_dict.get((chaff_length, inputs_per_property, "expected to find"))
                    row.append(f"{(int(correctly_found)/int(expected_to_find))*100:.2f}%")
                elif outputs == "ratio correct/artifact":
                    correctly_found = output_dict.get((chaff_length, inputs_per_property, "correctly found"))
                    artifacts_in_output = output_dict.get((chaff_length, inputs_per_property, "artifacts in output"))
                    row.append(f"{(int(correctly_found)/(int(artifacts_in_output)+int(correctly_found)))*100:.2f}%")
                else:
                    print("got")
                    print(output_dict.get((chaff_length, inputs_per_property, outputs)))
                    row.append(output_dict.get((chaff_length, inputs_per_property, outputs)))
            rows.append(row)

    with open("test_results.csv", 'w', newline='') as file:
        writer = csv.writer(file, dialect='excel')
        writer.writerows(rows)
