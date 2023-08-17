import random
import warnings
import multiprocessing
import csv


import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.quantum_info import random_statevector

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.assertions.assert_equal import assert_equal, assert_equal_state, holm_bonferroni_correction
from dd_regression.helper_functions import circuit_to_list, list_to_circuit, get_quantum_register
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.diff_algorithm import Addition, Removal, diff, apply_diffs, Experiment

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumTeleportationSynthetic(CaseStudyInterface):
    def get_algorithm_name(self):
        return "Quantum Teleportation Synthetic"

    # passing circuit
    @staticmethod
    def quantum_teleportation():
        qc = QuantumCircuit(3)
        qc.x(0)  # d0 remove
        qc.x(0)  # d1 remove
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(0, 1)  # d2 remove
        qc.h(0)
        qc.cx(1, 2)
        qc.cz(0, 2)
        return qc

    # failing circuit
    @staticmethod
    def quantum_teleportation_update():
        qc = QuantumCircuit(3)
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(1, 0)  # d3 insert
        qc.h(0)
        qc.cx(1, 2)
        qc.cz(0, 2)
        return qc

    def expected_deltas_to_isolate(self):
        return [Removal(location_index=4)]

    def passing_circuit(self):
        return self.quantum_teleportation()

    def failing_circuit(self):
        return self.quantum_teleportation_update()

    def regression_test(self, circuit_to_test):
        pass

    # generate circuit, and return if pass or fail
    def test_function(self, deltas, passing_circ, failing_circ, inputs_to_generate=25, measurements=1000):
        self.tests_performed += 1
        # print(f"self.test_cache {self.test_cache}")
        if self.test_cache.get(tuple(deltas), None) is not None:
            # print(f"deltas already tested, returning cache of {deltas}")
            # print(f"cache {self.test_cache.get(tuple(deltas), None)}")
            return self.test_cache.get(tuple(deltas), None)
        # if len(deltas) == 0:
        #     return Passed()
        experiments = []
        verification_experiments = []
        self.tests_performed_no_cache += 1

        changed_circuit_list = apply_diffs(passing_circ, failing_circ, deltas)
        qlength, clength = get_quantum_register(changed_circuit_list)
        changed_circuit = list_to_circuit(changed_circuit_list)
        # print(changed_circuit)
        # generate random input state vector and apply statistical test to expected output
        for j in range(inputs_to_generate):
            # initialize to random state and append the applied delta modified circuit
            init_state = QuantumCircuit(qlength)
            init_vector = random_statevector(2)
            init_state.initialize(init_vector, 0)
            inputted_circuit_to_test = init_state + changed_circuit

            # create a new circuit with just state initialization to compare with
            qc = QuantumCircuit(1)
            qc.initialize(init_vector, 0)

            # get pvalue of test
            p_value_x, p_value_y, p_value_z, measurements_1, measurements_2 = assert_equal(inputted_circuit_to_test, 2,
                                                                                           qc, 0, measurements=measurements)

            # store p_value and input state to get the p_value
            experiments.append((init_vector, p_value_x, p_value_y, p_value_z, measurements_1, measurements_2))

        exp_pairs = []
        for idx, experiment in enumerate(experiments):
            exp_pairs.append((idx, experiment[1]))
            exp_pairs.append((idx, experiment[2]))
            exp_pairs.append((idx, experiment[3]))

        # print(exp_pairs)

        # check if any assert equal failed
        failed = holm_bonferroni_correction(exp_pairs, 0.01)

        # for each failed test, check equality of final state, with initial failing circuit (on same input)
        for failure in failed:
            init_state = QuantumCircuit(qlength)
            init_state.initialize(experiments[failure][0], 0)
            inputted_circuit_to_test = init_state + list_to_circuit(failing_circ)
            # print(inputted_circuit_to_test)
            p_value_x, p_value_y, p_value_z, measurements_1, measurements_2 = assert_equal_state(
                inputted_circuit_to_test, 2, experiments[failure][4], measurements=measurements)
            verification_experiments.append(
                (init_vector, p_value_x, p_value_y, p_value_z, measurements_1, measurements_2))

        verification_pairs = []
        for idx, verification in enumerate(verification_experiments):
            verification_pairs.append((idx, verification[1]))
            verification_pairs.append((idx, verification[2]))
            verification_pairs.append((idx, verification[3]))

        # check if any assert equal failed with initial failing circuit
        verification_failed = holm_bonferroni_correction(verification_pairs, 0.01)

        # print(f"failed {failed}")
        # print(f"verification_failed {verification_failed}")

        # if any state not equal, inconclusive result
        if len(verification_failed) > 0:
            # print("return inconclusive")
            self.test_cache[tuple(deltas)] = Inconclusive()
            return Inconclusive()
        elif len(failed) > 0:
            # print("return failed")
            self.test_cache[tuple(deltas)] = Failed()
            return Failed()
        else:
            # print("return passed")
            self.test_cache[tuple(deltas)] = Passed()
            return Passed()


if __name__ == "__main__":
    qft = QuantumTeleportationSynthetic()
    print(qft.passing_circuit())
    # print(qft.failing_circuit())
    # h_circ = QuantumCircuit(1).h(0) + qft.passing_circuit()
    # print(h_circ)
    # print(execute(h_circ, backend, shots=100, memory=True).result().get_counts())
    # chaff_lengths = [8, 4, 2, 1, 0]
    # inputs_to_generate = [20, 10, 5, 1]
    # qpe_objs = [QuantumTeleportationSynthetic() for _ in range(len(chaff_lengths) * len(inputs_to_generate))]
    # print(qpe_objs)
    # inputs_for_func = [(i1, i2) for i1 in chaff_lengths for i2 in inputs_to_generate]
    # print(inputs_for_func)
    # results = [(qpe_objs[i], inputs_for_func[i][0], inputs_for_func[i][1]) for i in range(len(qpe_objs))]
    # print(results)
    # # qpe.analyse_results(chaff_length=8, inputs_to_generate=50)
    # with multiprocessing.Pool() as pool:
    #     results = [pool.apply_async(qpe_objs[i].analyse_results, kwds={'chaff_length': inputs_for_func[i][0],
    #                                                                    'inputs_to_generate': inputs_for_func[i][1]}) for
    #                i in range(len(qpe_objs))]
    #     for r in results:
    #         r.get()
    #
    # pool.join()
    #
    # rows = []
    # for i in range(len(inputs_to_generate)):
    #     row = []
    #     for j in range(len(chaff_lengths)):
    #         f = open(
    #             f"{qpe_objs[0].get_algorithm_name()}_chaff_length{chaff_lengths[j]}_inputs_to_gen{inputs_to_generate[i]}.txt",
    #             "r")
    #         row.append(f.read())
    #     rows.append(row)
    #
    # with open("test_results.csv", 'w', newline='') as file:
    #     writer = csv.writer(file, dialect='excel')
    #     writer.writerows(rows)
