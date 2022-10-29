import time

from abc import ABC, abstractmethod
from dd_regression.dd_algorithm import dd_repeat, filter_artifacts
from dd_regression.helper_functions import circuit_to_list, add_random_chaff, list_to_circuit


class CaseStudyInterface(ABC):
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

    def analyse_results(self):
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
        base_circuit = self.failing_circuit()
        expected_deltas = self.expected_deltas_to_isolate()
        for i in range(1):
            chaff_embedded_circuit_list = add_random_chaff(base_circuit.copy())
            chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
            # deltas, orig_fail_deltas = dd_repeat(self.passing_circuit(), chaff_embedded_circuit, self.test_function)
            # start = time.time()
            # filtered_deltas = filter_artifacts(self.passing_circuit(), chaff_embedded_circuit,
            #                                    deltas, orig_fail_deltas, self.test_function)
            bstart = time.time()
            deltas, passing_deltas, orig_fail_deltas = dd_repeat(self.passing_circuit(), self.failing_circuit(), self.test_function)
            bend = time.time()
            start = time.time()
            filtered_deltas = filter_artifacts(self.passing_circuit(), self.failing_circuit(),
                                               deltas, passing_deltas, orig_fail_deltas, self.test_function)
            end = time.time()
            print(bend - bstart)
            print(end - start)
            print(filtered_deltas)
            print(expected_deltas)

        # filtered_deltas = self.run_dd()
        # need to know what it was before chaff was added
        # compare the position_new parts as those are the ones changed

        # found = 0
        # not_found = 0
        # for delta in filtered_deltas:
        #     if delta[""] == expected_deltas:
        #         found += 1
        #     else:
        #         not_found += 1
        # should never be able to find more than expected deltas
        # assert found <= len(expected_deltas)
        # percent_deltas_isolated = (found/len(expected_deltas)) * 100
        # percent_chaff_isolated = (1 - found/len(filtered_deltas)) * 100
        # return percent_deltas_isolated, percent_chaff_isolated

    def run_dd(self):
        deltas, orig_fail_deltas = dd_repeat(self.passing_circuit(), self.failing_circuit(), self.test_function)
        filtered_deltas = filter_artifacts(self.passing_circuit(), self.failing_circuit(),
                                           deltas, orig_fail_deltas, self.test_function)
        return filtered_deltas

    # def analyse_results(self):
    #     pre_chaff_circuit_list = circuit_to_list(self.failing_circuit())
    #     expected_deltas = self.expected_deltas_to_isolate()
    #     filtered_deltas = self.run_dd()
    #     # need to know what it was before chaff was added
    #     # compare the position_new parts as those are the ones changed
    #     print(filtered_deltas)
    #     print(expected_deltas)
    #     found = 0
    #     not_found = 0
    #     for delta in filtered_deltas:
    #         if delta[""] == expected_deltas:
    #             found += 1
    #         else:
    #             not_found += 1
    #     # should never be able to find more than expected deltas
    #     assert found <= len(expected_deltas)
    #     percent_deltas_isolated = (found/len(expected_deltas)) * 100
    #     percent_chaff_isolated = (1 - found/len(filtered_deltas)) * 100
    #     return percent_deltas_isolated, percent_chaff_isolated

