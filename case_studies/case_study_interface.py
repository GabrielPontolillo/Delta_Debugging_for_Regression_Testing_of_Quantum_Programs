import time
import random

from abc import ABC, abstractmethod, abstractproperty

from case_studies.mined.quantum_teleportation.different_paths_same_outcome import DifferentPathsSameOutcomeProperty
from case_studies.mined.quantum_teleportation.equal_output_property import EqualOutputProperty
from case_studies.mined.quantum_teleportation.uniform_superposition_property import UniformSuperpositionProperty
from dd_regression.dd_algorithm import dd_repeat
from dd_regression.helper_functions import circuit_to_list, add_random_chaff, list_to_circuit, \
    determine_delta_application_valid, list_contains_list_in_same_order
from dd_regression.diff_algorithm_r import apply_diffs, diff, Removal, Addition, print_deltas


class CaseStudyInterface(ABC):
    test_cache = {}
    tests_performed = 0
    tests_performed_no_cache = 0

    def __init__(self):
        self.properties = random.sample([EqualOutputProperty, UniformSuperpositionProperty, DifferentPathsSameOutcomeProperty], 1)

    @abstractmethod
    def get_algorithm_name(self):
        pass

    @abstractmethod
    def expected_deltas_to_isolate(self):
        """
        To analyse the data for the paper, we must specify what deltas are expected to be returned
        assuming no artifacts
        """
        pass

    @abstractmethod
    def passing_circuit(self):
        """
        Return a passing version of the quantum circuit (prior to update)
        """
        pass

    @abstractmethod
    def failing_circuit(self):
        """
        Return a failing version of the quantum circuit (prior to update)
        """
        pass

    @abstractmethod
    def regression_test(self, quantum_circuit):
        """
        Return the (property based) regression test that may be used to test each circuit
        """
        pass

    @abstractmethod
    def test_function(self, deltas, src_passing, src_failing, original_deltas):
        """
        Return a test function, similar to regression test that receives a subset of Deltas,
        """
        pass

    def analyse_results(self, chaff_length=None, inputs_to_generate=25):
        """
        -> in for loop
        -> generate random chaff and add it to the circuit
        -> run dd with this chaffed up circuit
        -> evaluate score for this run
        -> check the operation first
        -> if delete = compare position old
        -> if insert = first compare position old, then compare object by looking at prechaff circuit
         and postchaff circuit
        """
        failing_circuit = self.failing_circuit()
        failing_circuit_list = circuit_to_list(self.failing_circuit())
        expected_deltas = self.expected_deltas_to_isolate()
        expected_found = 0
        artifacts_found = 0
        artifacts_added = 0
        tests_with_artifacts = 0
        tests_with_all_deltas_found = 0
        perfect_result = 0
        start = time.time()
        print(expected_deltas)
        print(self.passing_circuit())
        print(failing_circuit)
        loops = 50
        amount_to_find = len(expected_deltas) * loops
        for i in range(loops):
            self.properties = random.sample([EqualOutputProperty, UniformSuperpositionProperty, DifferentPathsSameOutcomeProperty], 1)
            print(f"loop number {i}")
            chaff_embedded_circuit_list = add_random_chaff(failing_circuit.copy(), chaff_length=chaff_length)

            # chaff_embedded_circuit_list = failing_circuit.copy()
            chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
            artifacts_added += len(chaff_embedded_circuit_list) - len(failing_circuit_list)
            print(chaff_embedded_circuit)

            deltas, _ = dd_repeat(self.passing_circuit(), chaff_embedded_circuit, self.test_function, inputs_to_generate=inputs_to_generate)
            # print(f"passing deltas {passing_deltas}")
            print(f"failing deltas {deltas}")
            self.test_cache = {}

            deltas_found = 0
            indexes_found = []
            # need to check deltas to make sure they are the same after diffing with chaff
            for exp in expected_deltas:
                # removal deltas unaffected
                if isinstance(exp, Removal):
                    if exp in deltas:
                        deltas_found += 1
                # addition, we need to modify
                elif isinstance(exp, Addition):
                    # care about gate added and location
                    for idx, delta in enumerate(deltas):
                        # old location unaffected
                        if exp.location_index == delta.location_index:
                            # add gate index affected, compare actual gate in list, if it's the same
                            if chaff_embedded_circuit_list[delta.add_gate_index] == failing_circuit_list[exp.add_gate_index]:
                                # index not already added, we say that it has been found
                                if idx not in indexes_found:
                                    deltas_found += 1
                                    indexes_found.append(idx)
                                    break

            print(f"expected deltas {expected_deltas}")
            print(f"deltas {deltas}")

            expected_found += deltas_found
            assert deltas_found <= len(expected_deltas)
            if deltas_found == len(expected_deltas):
                tests_with_all_deltas_found += 1
                if len(deltas) - deltas_found == 0:
                    perfect_result += 1
            if len(deltas) - deltas_found > 0:
                artifacts_found += len(deltas) - deltas_found
                tests_with_artifacts += 1

        print(f"Total expected deltas found: {expected_found}/{amount_to_find}")
        print(f"Tests with ALL expected deltas found: {tests_with_all_deltas_found}/{loops}, AND no unexpected: {perfect_result}/{loops}")
        print(f"Unexpected deltas: {artifacts_found}/{artifacts_added}, from ({tests_with_artifacts}) tests")
        print(f"Tests called: {self.tests_performed}, tests executed (due to caching): {self.tests_performed_no_cache}")
        print(f"Time taken (minutes): {round(time.time() - start, 2)/60}")

        f = open(f"{self.get_algorithm_name()}_chaff_length{chaff_length}_inputs_to_gen{inputs_to_generate}.txt", "w")
        f.write(f"Expected deltas found: {expected_found}/{amount_to_find}\n")
        # f.write(f"Tests with ALL expected deltas found: {tests_with_all_deltas_found}/{loops}, AND no unexpected: {perfect_result}/{loops}\n")
        # f.write(f"Unexpected deltas: {artifacts_found}/{artifacts_added}, from ({tests_with_artifacts}) tests\n")
        f.write(f"Unexpected deltas: {artifacts_found}/{artifacts_added}\n")
        # f.write(f"Tests called: {self.tests_performed}, tests executed (due to caching): {self.tests_performed_no_cache}\n")
        f.write(f"Time taken (minutes): {round((time.time() - start)/60, 2)}")
        f.close()


