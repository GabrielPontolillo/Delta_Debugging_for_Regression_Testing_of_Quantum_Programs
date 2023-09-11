import csv
import multiprocessing
import warnings
import qiskit.quantum_info as qi
from qiskit.circuit.random import random_circuit
import random

import numpy as np
from qiskit import QuantumCircuit, Aer, execute

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.diff_algorithm import diff
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.assertions.assert_equal import measure_qubits

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class DeutschJozsaMined(CaseStudyInterface):
    def __init__(self):
        # self.properties = [EqualOutputProperty, UniformSuperpositionProperty, DifferentPathsSameOutcomeProperty]
        # self.properties = [EqualOutputProperty]
        pass

    def get_algorithm_name(self):
        return "Deutsch_Jozsa_Mined"

    # passing circuit
    @staticmethod
    def deutsch_jozsa():
        qc = []
        return qc

    # failing circuit
    @staticmethod
    def deutsch_jozsa_update():
        qc = []
        return qc

    def expected_deltas_to_isolate(self):
        return diff(self.passing_circuit(), self.failing_circuit())

    def passing_circuit(self):
        return self.deutsch_jozsa()

    def failing_circuit(self):
        return self.deutsch_jozsa_update()

    def regression_test(self, circuit_to_test):
        pass

    def dj(self, oracle, size):
        qc = QuantumCircuit(size)

        # upper register of h's
        for i in range(size-1):
            qc.h(i)

        # lower register to -
        qc.x(size-1)
        qc.h(size-1)

        qc.barrier()

        # apply constant or balanced oracle here (x,y -> x,y+f(x)) where + is xor
        qc = qc.compose(oracle)

        qc.barrier()

        # upper register of h's
        for i in range(size - 1):
            qc.h(i)

        return qc

    def constant_oracle(self, size):
        qc = QuantumCircuit(size)

        for i in range(size-1):
            qc.i(i)

        return qc

    def random_constant_oracle(self, size, max_depth, max_operands):
        depth = random.randint(0, max_depth)
        if size > 1:
            operands = random.randint(1, 2)
        else:
            operands = 1

        qc = random_circuit(size, depth, operands)
        qcdag = qc.inverse()
        qc = qc.compose(qcdag)

        if random.randint(0, 1) == 0:
            qc.x(size-1)

        return qc

    def random_balanced_oracle(self, size):
        qc = QuantumCircuit(size)

        for i in range(size // 2):
            qc.swap(i, size - i - 1)

        random_chosen = []
        for i in range(size-1):
            if random.randint(0, 3) > 0:
                qc.x(i)
                random_chosen.append(1)
            else:
                random_chosen.append(0)

        for i in range(size-1):
            if random.randint(0, 3) > 0:
                qc.cx(i, size-1)

        for i in range(size-1):
            if random_chosen[i] == 1:
                qc.x(i)
                random_chosen.append(1)
            else:
                random_chosen.append(0)
        return qc

    def balanced_oracle(self, size):
        qc = QuantumCircuit(size)

        for i in range(size-1):
            qc.cx(i, size-1)

        return qc

    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties, number_of_measurements, significance_level):
        self.tests_performed += 1
        if self.test_cache.get(tuple(deltas), None) is not None:
            return self.test_cache.get(tuple(deltas), None)
        self.tests_performed_no_cache += 1

        # print(f"chosen properties {selected_properties}")

        oracle_result = TeleportationOracle.test_oracle(src_passing, src_failing, deltas,
                                                        selected_properties,
                                                        inputs_to_generate=inputs_to_generate,
                                                        measurements=number_of_measurements,
                                                        significance_level=significance_level
                                                        )
        if isinstance(oracle_result, Passed):
            self.test_cache[tuple(deltas)] = Passed()
        elif isinstance(oracle_result, Failed):
            self.test_cache[tuple(deltas)] = Failed()
        elif isinstance(oracle_result, Inconclusive):
            self.test_cache[tuple(deltas)] = Inconclusive()
        return oracle_result

    @staticmethod
    def test_vertical():
        size = 4
        size2 = 5

        dj = DeutschJozsaMined()

        oracle_1 = dj.random_balanced_oracle(size)
        qc = dj.dj(oracle_1, size)
        res = measure_qubits(qc, [i for i in range(size - 1)], 1000, ['z'])
        print(oracle_1)
        [print(i) for i in res]

        oracle_2 = dj.random_balanced_oracle(size2)
        qc = dj.dj(oracle_2, size2)
        res = measure_qubits(qc, [i for i in range(size2 - 1)], 1000, ['z'])
        print(oracle_2)
        [print(i) for i in res]

        oracle_3 = QuantumCircuit(size + size2 - 1)
        oracle_1_registers = [i for i in range(size - 1)]
        oracle_1_registers.append(size + size2 - 2)
        oracle_2_registers = [i + size - 1 for i in range(size2 - 1)]
        oracle_2_registers.append(size + size2 - 2)

        print(oracle_1_registers)
        print(oracle_2_registers)

        oracle_3 = oracle_3.compose(oracle_1, qubits=oracle_1_registers)
        oracle_3 = oracle_3.compose(oracle_2, qubits=oracle_2_registers)
        qc = dj.dj(oracle_3, size + size2 - 1)
        res = measure_qubits(qc, [i for i in range(size + size2 - 1 - 1)], 1000, ['z'])
        print(oracle_3)
        [print(i) for i in res]

    @staticmethod
    def test_horizontal():
        size = 2
        size2 = 3

        dj = DeutschJozsaMined()

        oracle_1 = dj.random_balanced_oracle(size)
        qc = dj.dj(oracle_1, size)
        res = measure_qubits(qc, [i for i in range(size - 1)], 1000, ['z'])
        print(oracle_1)
        [print(i) for i in res]

        oracle_2 = dj.random_balanced_oracle(size2)
        qc = dj.dj(oracle_2, size2)
        res = measure_qubits(qc, [i for i in range(size2 - 1)], 1000, ['z'])
        print(oracle_2)
        [print(i) for i in res]

        oracle_3 = QuantumCircuit(max(size, size2))
        oracle_1_registers = [i for i in range(size - 1)]
        oracle_1_registers.append(max(size, size2) - 1)
        oracle_2_registers = [i for i in range(size2 - 1)]
        oracle_2_registers.append(max(size, size2) - 1)

        print(oracle_1_registers)
        print(oracle_2_registers)

        oracle_3 = oracle_3.compose(oracle_1, qubits=oracle_1_registers)
        oracle_3 = oracle_3.compose(oracle_2, qubits=oracle_2_registers)
        qc = dj.dj(oracle_3, max(size, size2))
        res = measure_qubits(qc, [i for i in range(max(size, size2) - 1)], 1000, ['z'])
        print(oracle_3)
        print(qc)
        [print(i) for i in res]


if __name__ == "__main__":
    backend = Aer.get_backend('unitary_simulator')

    size = 2

    dj = DeutschJozsaMined()

    oracle_1 = dj.random_balanced_oracle(size)
    print(oracle_1)

    oracle_2 = dj.random_balanced_oracle(size)
    print(oracle_2)

    op = qi.Operator(oracle_1)
    op2 = qi.Operator(oracle_2)

    print(op)
    print(op2)

    # res = measure_qubits(qc, [i for i in range(size - 1)], 1000, ['z'])
    # print(oracle_1)
    # print(qc)
    # [print(i) for i in res]

# if __name__ == "__main__":
#     size = 4
#     size2 = 4
#
#     dj = DeutschJozsaMined()
#
#     oracle_1 = dj.random_balanced_oracle(size)
#     qc = dj.dj(oracle_1, size)
#     res = measure_qubits(qc, [i for i in range(size - 1)], 1000, ['z'])
#     print(oracle_1)
#     [print(i) for i in res]
#
#     oracle_2 = dj.random_balanced_oracle(size2)
#     qc = dj.dj(oracle_2, size2)
#     res = measure_qubits(qc, [i for i in range(size2 - 1)], 1000, ['z'])
#     print(oracle_2)
#     [print(i) for i in res]
#
#     oracle_3 = QuantumCircuit(max(size, size2))
#     oracle_1_registers = [i for i in range(size - 1)]
#     oracle_1_registers.append(max(size, size2) - 1)
#     oracle_2_registers = [i for i in range(size2 - 1)]
#     oracle_2_registers.append(max(size, size2) - 1)
#
#     print(oracle_1_registers)
#     print(oracle_2_registers)
#
#     oracle_3 = oracle_3.compose(oracle_1, qubits=oracle_1_registers)
#     oracle_3 = oracle_3.compose(oracle_2, qubits=oracle_2_registers)
#     qc = dj.dj(oracle_3, max(size, size2))
#     res = measure_qubits(qc, [i for i in range(max(size, size2) - 1)], 1000, ['z'])
#     print(oracle_3)
#     print(qc)
#     [print(i) for i in res]

    # chaff_lengths = [8]
    # inputs_to_generate = [2]
    # numbers_of_properties = [1]
    # number_of_measurements = 4000
    # significance_level = 0.003
    # test_amount = 10
    #
    # qt_objs = [QuantumTeleportationMined() for _ in range(len(chaff_lengths) * len(inputs_to_generate) * len(numbers_of_properties))]
    # print(qt_objs)
    # inputs_for_func = [(i1, i2, i3) for i1 in chaff_lengths for i2 in inputs_to_generate for i3 in numbers_of_properties]
    # print(inputs_for_func)
    # results = [(qt_objs[i], inputs_for_func[i][0], inputs_for_func[i][1], inputs_for_func[i][2]) for i in range(len(qt_objs))]
    # print(results)
    # with multiprocessing.Pool() as pool:
    #     results = [pool.apply_async(qt_objs[i].analyse_results, kwds={'chaff_length': inputs_for_func[i][0],
    #                                                                    'inputs_to_generate': inputs_for_func[i][1],
    #                                                                    'number_of_properties': inputs_for_func[i][2],
    #                                                                    'number_of_measurements': number_of_measurements,
    #                                                                    'significance_level': significance_level,
    #                                                                    'test_amount': test_amount}) for
    #                i in range(len(qt_objs))]
    #     for r in results:
    #         r.get()
    #
    # pool.join()
    #
    # files_to_spreadsheet(
    #     qt_objs[0].get_algorithm_name(), chaff_lengths, inputs_to_generate, numbers_of_properties,
    #     number_of_measurements, significance_level, test_amount
    # )
