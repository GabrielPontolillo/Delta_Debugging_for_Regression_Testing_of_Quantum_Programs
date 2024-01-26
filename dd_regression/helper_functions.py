"""This file contains useful functions that are re-used throughout the repo."""
import csv
import random

from qiskit import QuantumCircuit


def get_circuit_register(instruction_arr: list[any]):
    """
    Returns the quantum and classical registers from the circuit instruction list,
    Fails if instruction list is empty.
    """
    assert len(instruction_arr) > 0, "Attempted to get quantum/classical register from an empty circuit"
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
    """
    Converts a list of instructions into a quantum circuit object,
    Fails if list of instruction is empty.
    """
    assert instruction_arr is not None and len(
        instruction_arr) != 0, "Attempted to convert an empty instruction list to a circuit"
    quantum_register, classical_register = get_circuit_register(instruction_arr)
    if classical_register is not None:
        ret_qc = QuantumCircuit(quantum_register.size, classical_register.size)
    else:
        ret_qc = QuantumCircuit(quantum_register.size, quantum_register.size)
    for instruction, qargs, cargs in instruction_arr:
        ret_qc.append(instruction, qargs, cargs)
    return ret_qc


def add_random_chaff(circuit: QuantumCircuit, chaff_length=None):
    """
    Adds semantically equivalent changes to a quantum circuit, by adding pairs of unitary matrices:
    pauli x, y, and z gates.
    """
    # interested in decomposing gates and replacing
    qarg, carg = get_circuit_register(circuit)
    circ_list = [circuitIns for circuitIns in circuit.data]
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
        qc_list = [circuitIns for circuitIns in qc.data]
        # choose where to append the chaff
        insert_location = random.randint(0, len(circ_list))
        circ_list[insert_location:insert_location] = qc_list
    return circ_list


def order_list_by_another_list(sublist, superlist, logging=False):
    """
    Shift the ordering of a sublist to the same order of superlist, (application of deltas expects ordered deltas),

    Args:
        sublist: A smaller list to re-order according to the superlist.
        superlist: The list used as base of reordering

    Returns:
        A re-ordered sublist
    """
    if logging:
        print("sublist:")
        print(sublist)
        print("super-list:")
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


def files_to_spreadsheet(algorithm_name, chaff_lengths, inputs_per_properties, numbers_of_properties,
                         number_of_measurements,
                         significance_level, test_amount):
    """
    Collects a set number of predictably named text files containing the results of each configuration,
    and generates a csv file with all aggregated data.

    Args:
        algorithm_name: The algorithm name (as specified in each algorithm case study)
        chaff_lengths: A list of all chaff lengths iterated on for the experiments
        inputs_per_properties: A list of all numbers of inputs generated per properties iterated on for the experiments
        numbers_of_properties: A list the numbers of properties iterated on for the experiments
        number_of_measurements: The number of measurements to make for each property based test
        significance_level: alpha value for the statistical tests (Holm-Bonferroni correction)
        test_amount: The number of times the experiment is repeated (How many times we repeat an experiment)
    Returns:
        Saves all experiment data to a csv file.
    """
    output_dict = dict()
    """
    Iterate over each list of experiment configurations and attempt to read all combinations of files,
    Store the result file contents to a dict.
    """
    for number_of_properties in numbers_of_properties:
        for chaff_length in chaff_lengths:
            for inputs_per_property in inputs_per_properties:
                try:
                    f = open(
                        f"{algorithm_name}_cl{chaff_length}_in{inputs_per_property}_prop{number_of_properties}_meas{number_of_measurements}_sig{significance_level}_tests{test_amount}.txt",
                        "r")
                    output = f.read().split('\n')
                    print(output)
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "correctly found")] = output[
                        1]
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "expected to find")] = output[
                        2]
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "artifacts in output")] = \
                        output[4]
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "artifacts added")] = output[
                        5]
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "time")] = output[7]
                    f.close()
                except OSError as err:
                    """
                    If a result file is not present, save an empty string to csv file.
                    """
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "correctly found")] = ""
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "expected to find")] = ""
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "artifacts in output")] = ""
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "artifacts added")] = ""
                    output_dict[(chaff_length, inputs_per_property, number_of_properties, "time")] = ""

    """
        Store all rows in the csv file in a 2d list, and save to csv file
    """
    rows = [[f"{number_of_measurements} measurements"], [f"{significance_level} alpha"], [f"{test_amount} repetitions"],
            [], []]

    for number_of_properties in numbers_of_properties:

        row1 = [f"{number_of_properties} properties", ""]
        for i in range(len(chaff_lengths)):
            row1.append(f"{chaff_lengths[i] * 2} inserted deltas")
        rows.append(row1)

        for inputs_per_property in inputs_per_properties:
            for outputs in ["correctly found", "expected to find", "percentage found", "artifacts in output",
                            "artifacts added", "ratio correct/artifact", "time"]:
                row = [""]
                if outputs == "correctly found":
                    row[0] = f"{inputs_per_property} inputs/test "
                row.append(outputs)
                for chaff_length in chaff_lengths:
                    if outputs == "percentage found":
                        correctly_found = output_dict.get(
                            (chaff_length, inputs_per_property, number_of_properties, "correctly found"))
                        expected_to_find = output_dict.get(
                            (chaff_length, inputs_per_property, number_of_properties, "expected to find"))
                        if correctly_found != "" and expected_to_find != "":
                            row.append(f"{(int(correctly_found) / int(expected_to_find)) * 100:.2f}%")
                        else:
                            row.append("")
                    elif outputs == "ratio correct/artifact":
                        correctly_found = output_dict.get(
                            (chaff_length, inputs_per_property, number_of_properties, "correctly found"))
                        artifacts_in_output = output_dict.get(
                            (chaff_length, inputs_per_property, number_of_properties, "artifacts in output"))
                        if correctly_found != "" and artifacts_in_output != "":
                            try:
                                row.append(
                                    f"{(int(correctly_found) / (int(artifacts_in_output) + int(correctly_found))) * 100:.2f}%")
                            except ZeroDivisionError as err:
                                row.append(f"N/A")
                        else:
                            row.append("")
                    else:
                        row.append(output_dict.get((chaff_length, inputs_per_property, number_of_properties, outputs)))
                rows.append(row)
        rows.append([])

    with open(
            f"test_results_{algorithm_name}_meas{number_of_measurements}_sig{significance_level}_tests{test_amount}.csv",
            'w', newline='') as file:
        writer = csv.writer(file, dialect='excel')
        writer.writerows(rows)


def select_values(filename, rows=[6, 9, 13, 16, 20, 23, 29, 32, 36, 39, 43, 46, 52, 55, 59, 62, 66, 69], start_column=2, end_column=6):
    with open(filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        rows_to_write = []
        for current_row_index, row in enumerate(csv_reader):
            if current_row_index in rows:
                rows_to_write.append(row[start_column:end_column + 1])

    print(rows_to_write)

    # rows_to_write = [[0, 1, 2, 3], [1,2,3]]

    with open("grouped_" + filename, 'w', newline='') as file:
        writer = csv.writer(file, dialect='excel')
        writer.writerows(rows_to_write)

# def files_to_spreadsheet(algorithm_name, chaff_lengths, inputs_per_properties, numbers_of_properties,
#                          number_of_measurements,
#                          significance_level, test_amount):
#     """
#     Collects a set number of predictably named text files containing the results of each configuration,
#     and generates a csv file with all aggregated data.
#
#     Args:
#         algorithm_name: The algorithm name (as specified in each algorithm case study)
#         chaff_lengths: A list of all chaff lengths iterated on for the experiments
#         inputs_per_properties: A list of all numbers of inputs generated per properties iterated on for the experiments
#         numbers_of_properties: A list the numbers of properties iterated on for the experiments
#         number_of_measurements: The number of measurements to make for each property based test
#         significance_level: alpha value for the statistical tests (Holm-Bonferroni correction)
#         test_amount: The number of times the experiment is repeated (How many times we repeat an experiment)
#     Returns:
#         Saves all experiment data to a csv file.
#     """
#     output_dict = dict()
#     """
#     Iterate over each list of experiment configurations and attempt to read all combinations of files,
#     Store the result file contents to a dict.
#     """
#     for number_of_properties in numbers_of_properties:
#         for chaff_length in chaff_lengths:
#             for inputs_per_property in inputs_per_properties:
#                 try:
#                     f = open(
#                         f"{algorithm_name}_cl{chaff_length}_in{inputs_per_property}_prop{number_of_properties}_meas{number_of_measurements}_sig{significance_level}_tests{test_amount}.txt",
#                         "r")
#                     output = f.read().split('\n')
#                     print(output)
#                     output_dict[(chaff_length, inputs_per_property, number_of_properties, "correctly found")] = output[1]
#                     output_dict[(chaff_length, inputs_per_property, number_of_properties, "artifacts in output")] = output[3]
#                     f.close()
#                 except OSError as err:
#                     """
#                     If a result file is not present, save an empty string to csv file.
#                     """
#                     output_dict[(chaff_length, inputs_per_property, number_of_properties, "correctly found")] = ""
#                     output_dict[(chaff_length, inputs_per_property, number_of_properties, "artifacts in output")] = ""
#
#     """
#         Store all rows in the csv file in a 2d list, and save to csv file
#     """
#     rows = [[f"{number_of_measurements} measurements"], [f"{significance_level} alpha"], [f"{test_amount} repetitions"],
#             [], []]
#
#     for number_of_properties in numbers_of_properties:
#
#         row1 = [f"{number_of_properties} properties", ""]
#         for i in range(len(chaff_lengths)):
#             row1.append(f"{chaff_lengths[i] * 2} inserted deltas")
#         rows.append(row1)
#
#         for inputs_per_property in inputs_per_properties:
#             for outputs in ["correctly found", "artifacts in output"]:
#                 row = [""]
#                 if outputs == "correctly found":
#                     row[0] = f"{inputs_per_property} inputs/test "
#                 row.append(outputs)
#                 for chaff_length in chaff_lengths:
#                     if outputs == "percentage found":
#                         correctly_found = output_dict.get(
#                             (chaff_length, inputs_per_property, number_of_properties, "correctly found"))
#                         expected_to_find = output_dict.get(
#                             (chaff_length, inputs_per_property, number_of_properties, "expected to find"))
#                         if correctly_found != "" and expected_to_find != "":
#                             row.append(f"{(int(correctly_found) / int(expected_to_find)) * 100:.2f}%")
#                         else:
#                             row.append("")
#                     elif outputs == "ratio correct/artifact":
#                         correctly_found = output_dict.get(
#                             (chaff_length, inputs_per_property, number_of_properties, "correctly found"))
#                         artifacts_in_output = output_dict.get(
#                             (chaff_length, inputs_per_property, number_of_properties, "artifacts in output"))
#                         if correctly_found != "" and artifacts_in_output != "":
#                             try:
#                                 row.append(
#                                     f"{(int(correctly_found) / (int(artifacts_in_output) + int(correctly_found))) * 100:.2f}%")
#                             except ZeroDivisionError as err:
#                                 row.append(f"N/A")
#                         else:
#                             row.append("")
#                     else:
#                         row.append(output_dict.get((chaff_length, inputs_per_property, number_of_properties, outputs)))
#                 rows.append(row)
#         rows.append([])
#
#     with open(
#             f"test_results_{algorithm_name}_meas{number_of_measurements}_sig{significance_level}_tests{test_amount}.csv",
#             'w', newline='') as file:
#         writer = csv.writer(file, dialect='excel')
#         writer.writerows(rows)
