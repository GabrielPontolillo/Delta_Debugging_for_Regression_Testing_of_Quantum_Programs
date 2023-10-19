import random
import time
from abc import ABC, abstractmethod

from dd_regression.dd_algorithm import list_minus, dd
from dd_regression.diff_algorithm import Removal, Addition, diff
from dd_regression.helper_functions import add_random_chaff, list_to_circuit


class CaseStudyInterface(ABC):
    test_cache = {}
    tests_performed = 0
    tests_performed_no_cache = 0

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
    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties,
                      number_of_measurements, significance_level):
        """
        Return a test function, similar to regression test that receives a subset of Deltas,
        """
        pass

    def analyse_results(self, chaff_length, inputs_to_generate, number_of_properties, number_of_measurements, significance_level, test_amount):
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
        log = False
        failing_circuit = self.failing_circuit()
        failing_circuit_list = [circuitIns for circuitIns in self.failing_circuit().data]
        passing_instructions = [circuitIns for circuitIns in self.passing_circuit().data]
        expected_deltas = self.expected_deltas_to_isolate()
        expected_found = 0
        artifacts_found = 0
        artifacts_added = 0
        tests_with_artifacts = 0
        tests_with_all_deltas_found = 0
        perfect_result = 0
        start = time.time()
        if log:
            print("expected deltas")
            print(expected_deltas)
            print("passing circuit")
            print(self.passing_circuit())
        # print(failing_circuit)
        # print(len(expected_deltas))
        # print(test_amount)
        amount_to_find = len(expected_deltas) * test_amount
        for i in range(test_amount):
            selected_properties = random.sample(self.properties, number_of_properties)
            # print(f"loop number {i}")
            chaff_embedded_circuit_list = add_random_chaff(failing_circuit.copy(), chaff_length=chaff_length)

            chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
            artifacts_added += len(chaff_embedded_circuit_list) - len(failing_circuit_list)

            if log:
                print("chaff_embedded_circuit")
                print(chaff_embedded_circuit)

            fail_deltas = diff(passing_instructions, chaff_embedded_circuit_list)
            pass_deltas = []
            # print(passing_instructions)
            # print(chaff_embedded_circuit_list)
            # print(fail_deltas)

            pass_diff, fail_diff = dd(pass_deltas, fail_deltas, self.test_function, passing_instructions, chaff_embedded_circuit_list,
                                      inputs_to_generate=inputs_to_generate, selected_properties=selected_properties,
                                      number_of_measurements=number_of_measurements,
                                      significance_level=significance_level, logging=False)

            deltas = list_minus(fail_diff, pass_diff)

            # deltas, _ = dd_repeat(self.passing_circuit(), chaff_embedded_circuit, self.test_function, inputs_to_generate=inputs_to_generate,
            #                       selected_properties=selected_properties, number_of_measurements=number_of_measurements, significance_level=significance_level)
            # print(f"passing deltas {passing_deltas}")

            # print(f"failing deltas {deltas}")
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
                            if delta.add_gate == exp.add_gate:
                                # index not already added, we say that it has been found
                                if idx not in indexes_found:
                                    deltas_found += 1
                                    indexes_found.append(idx)
                                    break

            # print(f"expected deltas {expected_deltas}")
            # print(f"deltas {deltas}")

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
        print(f"Tests with ALL expected deltas found: {tests_with_all_deltas_found}/{test_amount}, AND no unexpected: {perfect_result}/{test_amount}")
        print(f"Unexpected deltas: {artifacts_found}/{artifacts_added}, from ({tests_with_artifacts}) tests")
        print(f"Tests called: {self.tests_performed}, tests executed (due to caching): {self.tests_performed_no_cache}")
        print(f"Time taken (minutes): {round(time.time() - start, 2)/60}")

        f = open(
            f"{self.get_algorithm_name()}_cl{chaff_length}_in{inputs_to_generate}_prop{number_of_properties}_meas{number_of_measurements}_sig{significance_level}_tests{test_amount}.txt",
            "w")
        f.write(f"Expected deltas found:\n")
        f.write(f"{expected_found}\n")
        f.write(f"{amount_to_find}\n")
        f.write(f"Unexpected deltas:\n")
        f.write(f"{artifacts_found}\n")
        f.write(f"{artifacts_added}\n")
        f.write(f"Time taken (minutes):\n")
        f.write(f"{round((time.time() - start) / 60, 2)}")
        f.close()


