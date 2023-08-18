# This code is modified from previous work at https://github.com/GabrielPontolillo/Quantum_Algorithm_Implementations
import warnings
import scipy.stats as sci
import heapq

from qiskit.circuit import ClassicalRegister
from qiskit import execute, Aer

backend = Aer.get_backend('aer_simulator')

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)


# circuit 1 = tested circuit
# circuit 2 = expected value
def assert_equal(circuit_1, qubit_register_1, circuit_2, qubit_register_2, measurements=1000):
    circuit_1.add_register(ClassicalRegister(1))
    c1z = measure_z(circuit_1.copy(), [qubit_register_1])
    c1x = measure_x(circuit_1.copy(), [qubit_register_1])
    c1y = measure_y(circuit_1.copy(), [qubit_register_1])
    z_counts_1 = execute(c1z, backend, shots=measurements, memory=True).result().get_counts()
    x_counts_1 = execute(c1x, backend, shots=measurements, memory=True).result().get_counts()
    y_counts_1 = execute(c1y, backend, shots=measurements, memory=True).result().get_counts()
    z_cleaned_counts_1 = {"z" + k[-1]: v for (k, v) in z_counts_1.items()}
    x_cleaned_counts_1 = {"x" + k[-1]: v for (k, v) in x_counts_1.items()}
    y_cleaned_counts_1 = {"y" + k[-1]: v for (k, v) in y_counts_1.items()}
    merged_counts_1 = z_cleaned_counts_1 | x_cleaned_counts_1 | y_cleaned_counts_1
    for missing in [x for x in ["x0", "x1", "y0", "y1", "z0", "z1"] if x not in merged_counts_1.keys()]:
        merged_counts_1[missing] = 0
    merged_counts_1 = {i: merged_counts_1[i] for i in ["x0", "x1", "y0", "y1", "z0", "z1"]}

    circuit_2.add_register(ClassicalRegister(1))
    c2z = measure_z(circuit_2.copy(), [qubit_register_2])
    c2x = measure_x(circuit_2.copy(), [qubit_register_2])
    c2y = measure_y(circuit_2.copy(), [qubit_register_2])
    z_counts_2 = execute(c2z, backend, shots=measurements, memory=True).result().get_counts()
    x_counts_2 = execute(c2x, backend, shots=measurements, memory=True).result().get_counts()
    y_counts_2 = execute(c2y, backend, shots=measurements, memory=True).result().get_counts()
    z_cleaned_counts_2 = {"z" + k[-1]: v for (k, v) in z_counts_2.items()}
    x_cleaned_counts_2 = {"x" + k[-1]: v for (k, v) in x_counts_2.items()}
    y_cleaned_counts_2 = {"y" + k[-1]: v for (k, v) in y_counts_2.items()}
    merged_counts_2 = z_cleaned_counts_2 | x_cleaned_counts_2 | y_cleaned_counts_2
    for missing in [x for x in ["x0", "x1", "y0", "y1", "z0", "z1"] if x not in merged_counts_2.keys()]:
        merged_counts_2[missing] = 0
    merged_counts_2 = {i: merged_counts_2[i] for i in ["x0", "x1", "y0", "y1", "z0", "z1"]}

    contingency_table_x = [[merged_counts_1.get(x, 0), merged_counts_2.get(x, 0)] for x in ["x0", "x1"]]

    contingency_table_y = [[merged_counts_1.get(x, 0), merged_counts_2.get(x, 0)] for x in ["y0", "y1"]]

    contingency_table_z = [[merged_counts_1.get(x, 0), merged_counts_2.get(x, 0)] for x in ["z0", "z1"]]

    # print("--------------")
    # print(merged_counts_1)
    # print(merged_counts_2)

    # print(contingency_table_x)
    # print(contingency_table_y)
    # print(contingency_table_z)
    # we do a chi square test if we have all values above 5
    # otherwise we do fisher's exact test

    # calculate the chi-squared test statistic
    # _, pvalue = sci.chisquare_gof(f_obs=list(merged_counts_1.values()), f_exp=list(merged_counts_2.values()))
    _, p_value_x = sci.fisher_exact(contingency_table_x)
    _, p_value_y = sci.fisher_exact(contingency_table_y)
    _, p_value_z = sci.fisher_exact(contingency_table_z)
    # print(p_value_x)
    # print(p_value_y)
    # print(p_value_z)
    return p_value_x, p_value_y, p_value_z, merged_counts_1, merged_counts_2


# circuit 1 = tested circuit
# circuit 2 = expected value
def assert_equal_state(circuit_1, qubit_register_1, merged_counts_2, measurements=1000):
    circuit_1.add_register(ClassicalRegister(1))
    c1z = measure_z(circuit_1.copy(), [qubit_register_1])
    c1x = measure_x(circuit_1.copy(), [qubit_register_1])
    c1y = measure_y(circuit_1.copy(), [qubit_register_1])
    z_counts_1 = execute(c1z, backend, shots=measurements, memory=True).result().get_counts()
    x_counts_1 = execute(c1x, backend, shots=measurements, memory=True).result().get_counts()
    y_counts_1 = execute(c1y, backend, shots=measurements, memory=True).result().get_counts()
    z_cleaned_counts_1 = {"z" + k[-1]: v for (k, v) in z_counts_1.items()}
    x_cleaned_counts_1 = {"x" + k[-1]: v for (k, v) in x_counts_1.items()}
    y_cleaned_counts_1 = {"y" + k[-1]: v for (k, v) in y_counts_1.items()}
    merged_counts_1 = z_cleaned_counts_1 | x_cleaned_counts_1 | y_cleaned_counts_1
    for missing in [x for x in ["x0", "x1", "y0", "y1", "z0", "z1"] if x not in merged_counts_1.keys()]:
        merged_counts_1[missing] = 0
    merged_counts_1 = {i: merged_counts_1[i] for i in ["x0", "x1", "y0", "y1", "z0", "z1"]}

    contingency_table_x = [[merged_counts_1.get(x, 0), merged_counts_2.get(x, 0)] for x in ["x0", "x1"]]

    contingency_table_y = [[merged_counts_1.get(x, 0), merged_counts_2.get(x, 0)] for x in ["y0", "y1"]]

    contingency_table_z = [[merged_counts_1.get(x, 0), merged_counts_2.get(x, 0)] for x in ["z0", "z1"]]

    # print(contingency_table_x)
    # print(contingency_table_y)
    # print(contingency_table_z)
    # we do a chi square test if we have all values above 5
    # otherwise we do fisher's exact test

    # calculate the chi-squared test statistic
    # _, pvalue = sci.chisquare_gof(f_obs=list(merged_counts_1.values()), f_exp=list(merged_counts_2.values()))
    _, p_value_x = sci.fisher_exact(contingency_table_x)
    _, p_value_y = sci.fisher_exact(contingency_table_y)
    _, p_value_z = sci.fisher_exact(contingency_table_z)
    # print(p_value_x)
    # print(p_value_y)
    # print(p_value_z)
    return p_value_x, p_value_y, p_value_z, merged_counts_1, merged_counts_2


# circuit 1 = tested circuit
# circuit 2 = expected value
# def measure_qubits(circuit_1, register, measurements=1000):
#     # receives a circuit to measure, and a list of qubit registers to measure
#     # returns a list of measurements for respective qubits
#     results = []
#     circuit_1.add_register(ClassicalRegister(len(register)))
#     c1z = measure_z(circuit_1.copy(), register)
#     c1x = measure_x(circuit_1.copy(), register)
#     c1y = measure_y(circuit_1, register)
#     z_counts_1 = execute(c1z, backend, shots=measurements, memory=True).result().get_counts()
#     x_counts_1 = execute(c1x, backend, shots=measurements, memory=True).result().get_counts()
#     y_counts_1 = execute(c1y, backend, shots=measurements, memory=True).result().get_counts()
#     print(z_counts_1.items())
#     print(x_counts_1.items())
#     print(y_counts_1.items())
#     for i in range(len(register)):
#         z1 = sum([v for (k, v) in z_counts_1.items() if k[-(i + 1)] == '1'])
#         z0 = measurements - z1
#         x1 = sum([v for (k, v) in x_counts_1.items() if k[-(i + 1)] == '1'])
#         x0 = measurements - x1
#         y1 = sum([v for (k, v) in y_counts_1.items() if k[-(i + 1)] == '1'])
#         y0 = measurements - y1
#         results.append({"x0": x0, "x1": x1, "y0": y0, "y1": y1, "z0": z0, "z1": z1})
#
#     return results

def measure_qubits(circuit_1, register, measurements=1000, basis=None):
    # receives a circuit to measure, and a list of qubit registers to measure
    # returns a list of measurements for respective qubits
    if basis is None:
        basis = ['x', 'y', 'z']

    results = []
    circuit_1.add_register(ClassicalRegister(len(register)))

    if 'z' in basis:
        c1z = measure_z(circuit_1.copy(), register)
        z_counts_1 = execute(c1z, backend, shots=measurements, memory=True).result().get_counts()

    if 'x' in basis:
        c1x = measure_x(circuit_1.copy(), register)
        x_counts_1 = execute(c1x, backend, shots=measurements, memory=True).result().get_counts()

    if 'y' in basis:
        c1y = measure_y(circuit_1, register)
        y_counts_1 = execute(c1y, backend, shots=measurements, memory=True).result().get_counts()

    for i in range(len(register)):
        res_dict = {}

        if 'x' in basis:
            x1 = sum([v for (k, v) in x_counts_1.items() if k[-(i + 1)] == '1'])
            x0 = measurements - x1
            res_dict["x0"] = x0
            res_dict["x1"] = x1

        if 'y' in basis:
            y1 = sum([v for (k, v) in y_counts_1.items() if k[-(i + 1)] == '1'])
            y0 = measurements - y1
            res_dict["y0"] = y0
            res_dict["y1"] = y1

        if 'z' in basis:
            z1 = sum([v for (k, v) in z_counts_1.items() if k[-(i + 1)] == '1'])
            z0 = measurements - z1
            res_dict["z0"] = z0
            res_dict["z1"] = z1

        results.append(res_dict)
    return results


# compare 2 sets of output distributions, the order of the list of distributions must be the same for both
# i.e. [dist_q1, dist_q2] and [dist2_q1, dist2_q2]
def assert_equal_distributions(distribution_list_1, distribution_list_2, basis=None):
    """inputs:
            distribution_list_1: list containing
       outputs:"""
    if basis is None:
        basis = ['x', 'y', 'z']

    assert len(distribution_list_1) == len(distribution_list_2)

    p_vals = []

    for i, dist_1 in enumerate(distribution_list_1):
        if 'x' in basis:
            contingency_table_x = [[dist_1.get(x, 0), distribution_list_2[i].get(x, 0)] for x in ["x0", "x1"]]
            _, p_value_x = sci.fisher_exact(contingency_table_x)
            p_vals.append(p_value_x)

        if 'y' in basis:
            contingency_table_y = [[dist_1.get(x, 0), distribution_list_2[i].get(x, 0)] for x in ["y0", "y1"]]
            _, p_value_y = sci.fisher_exact(contingency_table_y)
            p_vals.append(p_value_y)

        if 'z' in basis:
            contingency_table_z = [[dist_1.get(x, 0), distribution_list_2[i].get(x, 0)] for x in ["z0", "z1"]]
            _, p_value_z = sci.fisher_exact(contingency_table_z)
            p_vals.append(p_value_z)
    return p_vals


def measure_y(circuit, qubit_indexes):
    cBitIndex = 0
    for index in qubit_indexes:
        circuit.sdg(index)
        circuit.h(index)
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit


def measure_z(circuit, qubit_indexes):
    cBitIndex = 0
    for index in qubit_indexes:
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit


def measure_x(circuit, qubit_indexes):
    cBitIndex = 0
    for index in qubit_indexes:
        circuit.h(index)
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit


# make this return a list of failures p_value, index pairs
def holm_bonferroni_correction(exp_pairs, family_wise_alpha):
    # print(exp_pairs)

    failing_indexes = set()
    exp_pairs.sort(key=lambda x: x[2])
    for i in range(len(exp_pairs)):
        if exp_pairs[i][2] <= (family_wise_alpha / (len(exp_pairs) - i)):
            failing_indexes.add((exp_pairs[i][0], exp_pairs[i][1]))

    # print("failing indexes")
    # print(failing_indexes)
    return failing_indexes


# make this return a list of failures p_value, index pairs
def holm_bonferroni_correction_old(exp_pairs, family_wise_alpha):
    # print(exp_pairs)

    failing_indexes = set()
    exp_pairs.sort(key=lambda x: x[1])
    for i in range(len(exp_pairs)):
        if exp_pairs[i][1] <= (family_wise_alpha / (len(exp_pairs) - i)):
            failing_indexes.add(exp_pairs[i][0])

    # print("failing indexes")
    # print(failing_indexes)
    return failing_indexes
