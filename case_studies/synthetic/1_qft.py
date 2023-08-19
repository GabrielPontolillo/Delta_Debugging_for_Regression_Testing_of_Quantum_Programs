import random
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer
from qiskit.quantum_info import random_statevector, Statevector

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.assertions.assert_equal import holm_bonferroni_correction, \
    measure_qubits, assert_equal_distributions
from dd_regression.diff_algorithm import Addition, Removal, apply_diffs
from dd_regression.helper_functions import list_to_circuit, get_quantum_register
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QFTSynthetic(CaseStudyInterface):
    def get_algorithm_name(self):
        return "QFT Synthetic"

    # failing circuit without parameter input for length
    # fixed length of 3
    @staticmethod
    def qft_basic():
        qft_circuit = QuantumCircuit(2)
        for i in range(2):
            qft_circuit.h(1 - i)
            phase_ctr = 1 - i
            for j in range(1 - i):
                qft_circuit.cp(np.pi / 2 ** phase_ctr, j, 1 - i)
                phase_ctr -= 1
        return qft_circuit

    @staticmethod
    def qft_update(length):
        qft_circuit = QuantumCircuit(length)
        for i in range(length):
            qft_circuit.h((length - 1) - i)
            phase_ctr = length - i
            for j in range((length - 1) - i):
                qft_circuit.cp(np.pi / 2 ** phase_ctr, j, (length - 1) - i)
                phase_ctr -= 1
        return qft_circuit

    def expected_deltas_to_isolate(self):
        return [Removal(location_index=1), Addition(add_gate_index=1, location_index=2)]

    def passing_circuit(self):
        return self.qft_basic()

    def failing_circuit(self):
        return self.qft_update(2)

    def regression_test(self, circuit_to_test):
        p_values = []
        q_length, c_length = get_quantum_register(circuit_to_test.data)
        for j in range(50):
            rotation = random.randrange(0, 8)
            x_circuit = QuantumCircuit(q_length)
            bin_amt = bin(rotation)[2:]
            for i in range(len(bin_amt)):
                if bin_amt[i] == '1':
                    x_circuit.x(len(bin_amt) - (i + 1))

            inputted_circuit_to_test = x_circuit.compose(circuit_to_test)

            checks = []
            qubits = []

            for i in range(inputted_circuit_to_test.num_qubits):
                checks.append(((360 / (2 ** (i + 1))) * rotation) % 360)
                qubits.append(i)

            pvals = assertPhase(backend, inputted_circuit_to_test, qubits, checks, 1000)
            p_values += pvals

        p_values = sorted(p_values)
        for i in range(len(p_values)):
            if p_values[i] != np.NaN:
                if p_values[i] < 0.01 / (len(p_values) - i):
                    assert False
        assert True

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
        init_qubit_regs = [0, 1]
        self.tests_performed_no_cache += 1

        changed_circuit_list = apply_diffs(passing_circ, failing_circ, deltas, diagnostic=True)

        add = len([x for x in deltas if isinstance(x, Addition)])
        rem = len([x for x in deltas if isinstance(x, Removal)])
        if len(passing_circ) + add - rem != len(changed_circuit_list):
            raise AssertionError(f"apply_diffs has gone wrong pass len {len(passing_circ)}, add {add}, rem {rem}")

        qlength, clength = get_quantum_register(changed_circuit_list)
        changed_circuit = list_to_circuit(changed_circuit_list)
        # generate random input state vector and apply statistical test to expected output
        # here we need to check that qft on an arbitrary statevector, vs upshifted statevector has a phase shift of
        # [1, -i, -, i]
        for j in range(inputs_to_generate):
            # initialize to random state and append the applied delta modified circuit
            init_state = QuantumCircuit(qlength)
            shifted_init_state = QuantumCircuit(qlength)
            init_vector = random_statevector(4)
            # init_vector = Statevector([0, 0, 0, 0])
            vector_dict = init_vector.to_dict()
            shifted_vector = Statevector([vector_dict.get('01', 0), vector_dict.get('10', 0),
                                          vector_dict.get('11', 0), vector_dict.get('00', 0)])

            init_state.initialize(init_vector, init_qubit_regs)
            inputted_circuit_to_test = init_state + changed_circuit

            shifted_init_state.initialize(shifted_vector, init_qubit_regs)
            shifted_circuit_to_test = shifted_init_state + changed_circuit

            base_measurements = measure_qubits(inputted_circuit_to_test, init_qubit_regs)
            shifted_measurements = measure_qubits(shifted_circuit_to_test, init_qubit_regs)

            # base measurements * [1, -i, -, i] = shifted measurements
            modified_measurements = [
                {'z0': base_measurements[0].get('z0'), 'z1': base_measurements[0].get('z1'),
                 'x1': base_measurements[0].get('x0'), 'x0': base_measurements[0].get('x1'),
                 'y1': base_measurements[0].get('y0'), 'y0': base_measurements[0].get('y1')},

                {'z0': base_measurements[1].get('z0'), 'z1': base_measurements[1].get('z1'),
                 'x0': base_measurements[1].get('y0'), 'x1': base_measurements[1].get('y1'),
                 'y0': base_measurements[1].get('x1'), 'y1': base_measurements[1].get('x0')}
            ]
            p_list = assert_equal_distributions(modified_measurements, shifted_measurements)

            # store p_value and input state to get the p_value
            experiments.append((init_vector, p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5],
                                base_measurements, shifted_measurements))

        exp_pairs = []
        for idx, experiment in enumerate(experiments):
            exp_pairs.append((idx, experiment[1]))
            exp_pairs.append((idx, experiment[2]))
            exp_pairs.append((idx, experiment[3]))
            exp_pairs.append((idx, experiment[4]))
            exp_pairs.append((idx, experiment[5]))
            exp_pairs.append((idx, experiment[6]))

        # print(exp_pairs)

        # check if any assert equal failed
        failed = holm_bonferroni_correction(exp_pairs, 0.01)
        #
        # for each failed test, check equality of final state, with initial failing circuit (on same input)
        for failure in failed:
            init_state = QuantumCircuit(qlength)
            init_state.initialize(experiments[failure][0], init_qubit_regs)
            inputted_circuit_to_test = init_state + list_to_circuit(failing_circ)
            new_measurements = measure_qubits(inputted_circuit_to_test, init_qubit_regs)
            p_list = assert_equal_distributions(new_measurements, experiments[failure][7])
            verification_experiments.append(
                (init_vector, p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5],
                 experiments[failure][7], new_measurements))

        verification_pairs = []
        for idx, verification in enumerate(verification_experiments):
            verification_pairs.append((idx, verification[1]))
            verification_pairs.append((idx, verification[2]))
            verification_pairs.append((idx, verification[3]))
            verification_pairs.append((idx, verification[4]))
            verification_pairs.append((idx, verification[5]))
            verification_pairs.append((idx, verification[6]))

        # check if any assert equal failed with initial failing circuit
        verification_failed = holm_bonferroni_correction(verification_pairs, 0.01)

        # print(f"failed {failed}")
        # print(f"verification_failed {verification_failed}")

        # if any state not equal, inconclusive result
        if len(verification_failed) > 0:
            print("return inconclusive")
            self.test_cache[tuple(deltas)] = Inconclusive()
            return Inconclusive()
        elif len(failed) > 0:
            print("return failed")
            self.test_cache[tuple(deltas)] = Failed()
            return Failed()
        else:
            print("return passed")
            self.test_cache[tuple(deltas)] = Passed()
            return Passed()


if __name__ == "__main__":
    qft = QFTSynthetic()
    # diffs = diff(qft.passing_circuit(), qft.failing_circuit())
    # print(diffs)
    # print(qft.test_function([diffs[1]], qft.passing_circuit(), qft.failing_circuit(), inputs_to_generate=1))
    # dd_repeat(qft.passing_circuit(), qft.failing_circuit(), qft.test_function, inputs_to_generate=5)
    # diffs = diff(qft.passing_circuit(), qft.failing_circuit())
    #
    # apply_edit_script([diffs[1]], qft.passing_circuit(), qft.failing_circuit(), diffs)

    # qft.analyse_results(chaff_length=1, inputs_to_generate=3)

    print(qft.passing_circuit())
    print(qft.failing_circuit())

    # chaff_lengths = [8, 4, 2, 1, 0]
    # inputs_to_generate = [20, 10, 5, 1]
    # qpe_objs = [QFTSynthetic() for _ in range(len(chaff_lengths) * len(inputs_to_generate))]
    # print(qpe_objs)
    # inputs_for_func = [(i1, i2) for i1 in chaff_lengths for i2 in inputs_to_generate]
    # print(inputs_for_func)
    # results = [(qpe_objs[i], inputs_for_func[i][0], inputs_for_func[i][1]) for i in range(len(qpe_objs))]
    # print(results)
    #
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
