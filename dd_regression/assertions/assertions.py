# This code is from previous work at https://github.com/GabrielPontolillo/Quantum_Algorithm_Implementations
import warnings
import pandas as pd
import math
from math import pi, sqrt, sin, cos
import numpy as np
import scipy.stats as sci
from collections.abc import Callable

from statsmodels.stats.proportion import proportions_ztest

from qiskit import execute
from qiskit.circuit import ClassicalRegister

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)


def assertPhase(backend, quantumCircuit, qubits_to_assert, expected_phases, measurements_to_make):
    ## if "qubits to assert" is just a single value, convert it to a list containing the single value
    if (not isinstance(qubits_to_assert, list)):
        qubits_to_assert = [qubits_to_assert]

    ## if "expected phases" is just a single value, convert it to a list containing the single value
    if (not isinstance(expected_phases, list)):
        expected_phases = [expected_phases]

    resDf = record_xy_data(backend, quantumCircuit, qubits_to_assert, measurements_to_make)

    measurements_to_make = measurements_to_make // 2

    xAmount = resDf['-'].tolist()
    yAmount = resDf['-i'].tolist()

    ## make a dataframe that contains p values of chi square tests to analyse results
    ## if x and y counts are both 25/25/25/25, it means that we cannot calculate a phase
    ## we assume that a qubit that is in |0> or |1> position to have 50% chance to fall
    ## either way, like a coin toss: We treat X and Y results like coin tosses
    # pValues = pd.DataFrame(columns=['X', 'Y'])
    # pValues['X'] = resDf.apply(lambda row: applyChiSquareX(row, measurements_to_make / 2), axis=1)
    # pValues['Y'] = resDf.apply(lambda row: applyChiSquareY(row, measurements_to_make / 2), axis=1)
    #
    # ## check p values on chi square test, we use a low value to be sure that
    # ## we only except if we are certain there is an issue with the x, y results
    # pValues = pValues > 0.00001
    #
    # ## if both pvalues are more than 0.00001, we are pretty certain that the results follow an even distribution
    # ## likely that the qubit is not in the fourier basis (very likely in the |0> or |1> state)
    # pValues.apply(lambda row: assertIfBothTrue(row), axis=1)

    ## this sequence of operations converts from measured results
    ## into an angle for phase:
    ## with 0   (       0 rad) signifying the |+> state
    ## with 90  (    pi/2 rad) signifying the |i> state
    ## with 180 (      pi rad) signifying the |-> state
    ## with 270 (3 * pi/2 rad) signifying the |-i> state
    resDf = resDf / measurements_to_make
    resDf = resDf * 2
    resDf = resDf - 1
    resDf = np.arccos(resDf)
    resDf = resDf * 180
    resDf = resDf / math.pi

    ## to get a final result for phase on each qubit:
    ## we must get the lowest 2 values for each column
    lowestDf = pd.DataFrame(
        columns=['lowest', 'lowest-location', 'second-lowest', 'second-lowest-location', 'estimated-phase'])

    ## store the lowest value as well as what column it is from
    lowestDf['lowest'] = resDf.min(axis=1)
    lowestDf['lowest-location'] = resDf.idxmin(axis=1)

    ## remove the lowest value from the dataframe
    lowestDf = lowestDf.apply(lambda row: setLowestCellToNan(row, resDf), axis=1)

    ## store the second lowest value from the dataframe as well as the column
    lowestDf['second-lowest'] = resDf.min(axis=1)
    lowestDf['second-lowest-location'] = resDf.idxmin(axis=1)

    ## estimate the phase and put it in a new column
    lowestDf['estimated-phase'] = lowestDf.apply(lambda row: setPhaseEstimate(row), axis=1)

    ## calculate what the expected row would be for the expected phase
    expectedX = np.zeros(len(expected_phases)).astype(int)
    expectedY = np.zeros(len(expected_phases)).astype(int)

    for idx, phase in enumerate(expected_phases):
        expectedX[idx], expectedY[idx] = expectedPhaseToRow(expected_phases[idx], measurements_to_make)

    p_values = []

    for i in range(len(qubits_to_assert)):
        ## set observed X values in a table
        observedXtable = [xAmount[i], measurements_to_make - xAmount[i]]
        ## set expected X values in a table
        expectedXtable = [expectedX[i], measurements_to_make - expectedX[i]]

        ## set observed Y values in a table
        observedYtable = [yAmount[i], measurements_to_make - yAmount[i]]
        ## set expected Y values in a table
        expectedYtable = [expectedY[i], measurements_to_make - expectedY[i]]

        xPvalue = sci.chisquare(f_obs=observedXtable, f_exp=expectedXtable)[1]

        yPvalue = sci.chisquare(f_obs=observedYtable, f_exp=expectedYtable)[1]

        p_values.append(xPvalue)
        p_values.append(yPvalue)
    return p_values


## assert that 2 qubits are equal
def assertEqual(backend, quantumCircuit, qubit1, qubit2, measurements_to_make, alpha):
    ## needs to make at least 2 measurements, one for x axis, one for y axis
    ## realistically we need more for any statistical significance
    if (measurements_to_make < 2):
        raise ValueError("Must make at least 2 measurements")

    ## classical register must be of same length as amount of qubits to assert
    ## if there is no classical register, add one
    if (quantumCircuit.num_clbits == 0):
        quantumCircuit.add_register(ClassicalRegister(2))
    elif (quantumCircuit.num_clbits != 2):
        raise ValueError("QuantumCircuit classical register must be of length 2")

    ## divide measurements to make by 3 as we need to run measurements twice, one for x and one for y
    measurements_to_make = measurements_to_make // 3

    ## copy the circit and set measurement to y axis
    yQuantumCircuit = measure_y(quantumCircuit.copy(), [qubit1, qubit2])

    ## measure the x axis
    xQuantumCircuit = measure_x(quantumCircuit.copy(), [qubit1, qubit2])

    ## measure the z axis
    zQuantumCircuit = measure_z(quantumCircuit, [qubit1, qubit2])

    ## get y axis results
    yJob = execute(yQuantumCircuit, backend, shots=measurements_to_make, memory=True)
    yMemory = yJob.result().get_memory()
    yCounts = yJob.result().get_counts()

    ## get x axis results
    xJob = execute(xQuantumCircuit, backend, shots=measurements_to_make, memory=True)
    xMemory = xJob.result().get_memory()
    xCounts = xJob.result().get_counts()

    ## get z axis results
    zJob = execute(zQuantumCircuit, backend, shots=measurements_to_make, memory=True)
    zMemory = zJob.result().get_memory()
    zCounts = zJob.result().get_counts()

    print(alpha)

    ## make a df to keep track of the predicted angles
    resDf = pd.DataFrame(columns=['0', '1', '+', 'i', '-', '-i'])

    ## fill the df with the x and y results of each qubit that is being asserted
    classical_qubit_index = 1
    for qubit in [qubit1, qubit2]:
        zero_amount, one_amount, plus_amount, i_amount, minus_amount, minus_i_amount = 0, 0, 0, 0, 0, 0
        for experiment in xCounts:
            if (experiment[2 - classical_qubit_index] == '0'):
                plus_amount += xCounts[experiment]
            else:
                minus_amount += xCounts[experiment]
        for experiment in yCounts:
            if (experiment[2 - classical_qubit_index] == '0'):
                i_amount += yCounts[experiment]
            else:
                minus_i_amount += yCounts[experiment]
        for experiment in zCounts:
            if (experiment[2 - classical_qubit_index] == '0'):
                zero_amount += zCounts[experiment]
            else:
                one_amount += zCounts[experiment]
        df = {'0': zero_amount, '1': one_amount,
              '+': plus_amount, 'i': i_amount,
              '-': minus_amount, '-i': minus_i_amount}
        resDf = resDf.append(df, ignore_index=True)
        classical_qubit_index += 1

    ## convert the columns to a strict numerical type
    resDf['+'] = resDf['+'].astype(int)
    resDf['i'] = resDf['i'].astype(int)
    resDf['-'] = resDf['-'].astype(int)
    resDf['-i'] = resDf['-i'].astype(int)
    resDf['0'] = resDf['0'].astype(int)
    resDf['1'] = resDf['1'].astype(int)

    print(resDf.astype(str))

    print(resDf['1'][0].astype(int))
    print(resDf['1'][1].astype(int))

    print(resDf['-'][0].astype(int))
    print(resDf['-'][1].astype(int))

    print(resDf['-i'][0].astype(int))
    print(resDf['-i'][1].astype(int))

    zStat_z, zPvalue = proportions_ztest(count=[resDf['1'][0], resDf['1'][1]],
                                         nobs=[measurements_to_make, measurements_to_make], alternative='two-sided')
    zStat_x, xPvalue = proportions_ztest(count=[resDf['-'][0], resDf['-'][1]],
                                         nobs=[measurements_to_make, measurements_to_make], alternative='two-sided')
    zStat_y, yPvalue = proportions_ztest(count=[resDf['-i'][0], resDf['-i'][1]],
                                         nobs=[measurements_to_make, measurements_to_make], alternative='two-sided')

    print(zPvalue, zStat_z)
    print(xPvalue, zStat_x)
    print(yPvalue, zStat_y)

    if (yPvalue != np.NaN and yPvalue <= alpha):
        raise (AssertionError(
            f"Null hypothesis rejected, there is a significant enough difference in the qubits according to significance level {alpha}"))
    if (xPvalue != np.NaN and xPvalue <= alpha):
        raise (AssertionError(
            f"Null hypothesis rejected, there is a significant enough difference in the qubits according to significance level {alpha}"))
    if (zPvalue != np.NaN and zPvalue <= alpha):
        raise (AssertionError(
            f"Null hypothesis rejected, there is a significant enough difference in the qubits according to significance level {alpha}"))


def estimatePhase(backend, quantumCircuit, qubits_to_assert, measurements_to_make):
    resDf = record_xy_data(backend, quantumCircuit, qubits_to_assert, measurements_to_make)

    measurements_to_make = measurements_to_make // 2

    ## make a dataframe that contains p values of chi square tests to analyse results
    ## if x and y counts are both 25/25/25/25, it means that we cannot calculate a phase
    ## we assume that a qubit that is in |0> or |1> position to have 50% chance to fall
    ## either way, like a coin toss: We treat X and Y results like coin tosses
    pValues = pd.DataFrame(columns=['X', 'Y'])
    pValues['X'] = resDf.apply(lambda row: applyChiSquareX(row, measurements_to_make / 2), axis=1)
    pValues['Y'] = resDf.apply(lambda row: applyChiSquareY(row, measurements_to_make / 2), axis=1)

    ## check p values on chi square test, we use a low value to be sure that
    ## we only except if we are certain there is an issue with the x, y results
    pValues = pValues > 0.00001

    ## if both pvalues are more than 0.00001, we are pretty certain that the results follow an even distribution
    ## likely that the qubit is not in the fourier basis (very likely in the |0> or |1> state)
    pValues.apply(lambda row: assertIfBothTrue(row), axis=1)

    ## this sequence of operations converts from measured results
    ## into an angle for phase:
    ## with 0   (       0 rad) signifying the |+> state
    ## with 90  (    pi/2 rad) signifying the |i> state
    ## with 180 (      pi rad) signifying the |-> state
    ## with 270 (3 * pi/2 rad) signifying the |-i> state
    resDf = resDf / measurements_to_make
    resDf = resDf * 2
    resDf = resDf - 1
    resDf = np.arccos(resDf)
    resDf = resDf * 180
    resDf = resDf / math.pi

    ## to get a final result for phase on each qubit:
    ## we must get the lowest 2 values for each column
    lowestDf = pd.DataFrame(
        columns=['lowest', 'lowest-location', 'second-lowest', 'second-lowest-location', 'estimated-phase'])

    ## store the lowest value as well as what column it is from
    lowestDf['lowest'] = resDf.min(axis=1)
    lowestDf['lowest-location'] = resDf.idxmin(axis=1)

    ## remove the lowest value from the dataframe
    lowestDf = lowestDf.apply(lambda row: setLowestCellToNan(row, resDf), axis=1)

    ## store the second lowest value from the dataframe as well as the column
    lowestDf['second-lowest'] = resDf.min(axis=1)
    lowestDf['second-lowest-location'] = resDf.idxmin(axis=1)

    ## estimate the phase and put it in a new column
    lowestDf['estimated-phase'] = lowestDf.apply(lambda row: setPhaseEstimate(row), axis=1)

    return lowestDf


def record_xy_data(backend, quantumCircuit, qubits_to_assert, measurements_to_make):
    ## if "qubits to assert" is just a single value, convert it to a list containing the single value
    if not isinstance(qubits_to_assert, list):
        qubits_to_assert = [qubits_to_assert]

    ## needs to make at least 2 measurements, one for x axis, one for y axis
    ## realistically we need more for any statistical significance
    if (measurements_to_make < 2):
        raise ValueError("Must make at least 2 measurements")

    ## classical register must be of same length as amount of qubits to assert
    ## if there is no classical register, add one
    if (quantumCircuit.num_clbits == 0):
        quantumCircuit.add_register(ClassicalRegister(len(qubits_to_assert)))
    elif (quantumCircuit.num_clbits != len(qubits_to_assert)):
        raise ValueError("QuantumCircuit classical register length not equal to qubits to assert")

    ## divide measurements to make by 2 as we need to run measurements twice, one for x and one for y
    measurements_to_make = measurements_to_make // 2

    ## copy the circit and set measurement to y axis
    yQuantumCircuit = measure_y(quantumCircuit.copy(), qubits_to_assert)

    ## measure the x axis
    xQuantumCircuit = measure_x(quantumCircuit, qubits_to_assert)

    ## get y axis results
    yJob = execute(yQuantumCircuit, backend, shots=measurements_to_make, memory=True)
    yCounts = yJob.result().get_counts()

    ## get x axis results
    xJob = execute(xQuantumCircuit, backend, shots=measurements_to_make, memory=True)
    xCounts = xJob.result().get_counts()

    ## make a df to keep track of the predicted angles
    resDf = pd.DataFrame(columns=['+', 'i', '-', '-i'])

    ## fill the df with the x and y results of each qubit that is being asserted
    classical_qubit_index = 1
    for qubit in qubits_to_assert:
        plus_amount, i_amount, minus_amount, minus_i_amount = 0, 0, 0, 0
        for experiment in xCounts:
            if (experiment[len(qubits_to_assert) - classical_qubit_index] == '0'):
                plus_amount += xCounts[experiment]
            else:
                minus_amount += xCounts[experiment]
        for experiment in yCounts:
            if (experiment[len(qubits_to_assert) - classical_qubit_index] == '0'):
                i_amount += yCounts[experiment]
            else:
                minus_i_amount += yCounts[experiment]
        df = {'+': plus_amount, 'i': i_amount,
              '-': minus_amount, '-i': minus_i_amount}
        resDf = resDf.append(df, ignore_index=True)
        classical_qubit_index += 1

    ## convert the columns to a strict numerical type
    resDf['+'] = resDf['+'].astype(int)
    resDf['i'] = resDf['i'].astype(int)
    resDf['-'] = resDf['-'].astype(int)
    resDf['-i'] = resDf['-i'].astype(int)

    return resDf


def measure_x(circuit, qubitIndexes):
    cBitIndex = 0
    for index in qubitIndexes:
        circuit.h(index)
        circuit.measure(index, cBitIndex)
        cBitIndex += 1
    return circuit


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


def setLowestCellToNan(row, resDf):
    for col in row.index:
        resDf.iloc[row.name][row[col]] = np.nan
    return row


def setPhaseEstimate(row):
    overallPhase = 0
    if (row['lowest-location'] == '+'):
        if (row['second-lowest-location'] == 'i'):
            overallPhase = 0 + row['lowest']
        elif (row['second-lowest-location'] == '-i'):
            overallPhase = 360 - row['lowest']
            if (row['lowest'] == 0):
                overallPhase = 0
    elif (row['lowest-location'] == 'i'):
        if (row['second-lowest-location'] == '+'):
            overallPhase = 90 - row['lowest']
        elif (row['second-lowest-location'] == '-'):
            overallPhase = 90 + row['lowest']
    elif (row['lowest-location'] == '-'):
        if (row['second-lowest-location'] == 'i'):
            overallPhase = 180 - row['lowest']
        elif (row['second-lowest-location'] == '-i'):
            overallPhase = 180 + row['lowest']
    elif (row['lowest-location'] == '-i'):
        if (row['second-lowest-location'] == '+'):
            overallPhase = 270 + row['lowest']
        elif (row['second-lowest-location'] == '-'):
            overallPhase = 270 - row['lowest']
    return overallPhase


def expectedPhaseToRow(expected_phase, number_of_measurements):
    # print(expected_phase)
    # print(number_of_measurements)
    expected_phase_y = expected_phase - 90
    expected_phase_y = expected_phase_y * math.pi
    expected_phase_y = expected_phase_y / 180
    expected_phase_y = np.cos(expected_phase_y)
    expected_phase_y = expected_phase_y + 1
    expected_phase_y = expected_phase_y / 2
    expected_phase_y = expected_phase_y * number_of_measurements
    expected_phase = expected_phase * math.pi
    expected_phase = expected_phase / 180
    expected_phase = np.cos(expected_phase)
    expected_phase = expected_phase + 1
    expected_phase = expected_phase / 2
    expected_phase = expected_phase * number_of_measurements
    # print(f"phase + {expected_phase} ---- phase - {number_of_measurements-expected_phase}")
    # print(f"phase i {expected_phase_y} ---- phase -i {number_of_measurements-expected_phase_y}")
    xRes = int(round(number_of_measurements - expected_phase))
    yRes = int(round(number_of_measurements - expected_phase_y))
    return ((xRes, yRes))


def applyChiSquareX(row, expected_amount):
    observed = [row['+'], row['-']]
    expected = [expected_amount, expected_amount]
    return (sci.chisquare(f_obs=observed, f_exp=expected)[1])


def applyChiSquareY(row, expected_amount):
    observed = [row['i'], row['-i']]
    expected = [expected_amount, expected_amount]
    return (sci.chisquare(f_obs=observed, f_exp=expected)[1])


def assertIfBothTrue(row):
    if row.all():
        raise AssertionError("Qubit does not appear to have a phase applied to it!")


def calculate_tensor_product(vectors):
    """
    takes in array of pairs of complex numbers
    returns statevector array
    (recursively)
    """
    if vectors == []:
        return vectors
    elif len(vectors) == 1:
        return vectors
    else:
        v1 = vectors.pop(-1)
        v2 = vectors.pop(-1)
        newvect = []
        for v1_val in v1:
            for v2_val in v2:
                newvect.append(v1_val * v2_val)
        vectors.append(newvect)
        return calculate_tensor_product(vectors)


def angle_to_vector(expected_values):
    """
    takes in array of angles (degrees)
    returns pairs of complex numbers
    """
    plus = 1 / sqrt(2)
    minus = -1 / sqrt(2)
    plus_i = complex(0, 1) / sqrt(2)
    minus_i = complex(0, -1) / sqrt(2)

    ret_vector = []

    for angle in expected_values:
        basis_arr = [0, 90, 180, 270, 360]
        closest_basis_arr = [abs(x - angle) for x in basis_arr]

        closest = basis_arr[closest_basis_arr.index(min(closest_basis_arr))]
        closest_angle = closest_basis_arr[closest_basis_arr.index(min(closest_basis_arr))]
        # print("closest " + str(closest))
        # print("closest angle " + str(closest_angle))

        basis_arr.pop(closest_basis_arr.index(min(closest_basis_arr)))
        closest_basis_arr.pop(closest_basis_arr.index(min(closest_basis_arr)))

        second_closest = basis_arr[closest_basis_arr.index(min(closest_basis_arr))]
        second_closest_angle = closest_basis_arr[closest_basis_arr.index(min(closest_basis_arr))]
        # print("second closest " + str(second_closest))
        # print("second closest angle " + str(second_closest_angle))

        if closest == 0:
            if second_closest == 90:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * plus + sin(closest_angle * pi / 180) * plus_i])
            else:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * plus + sin(closest_angle * pi / 180) * minus_i])
        elif closest == 90:
            if second_closest == 180:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * plus_i + sin(closest_angle * pi / 180) * minus])
            else:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * plus_i + sin(closest_angle * pi / 180) * plus])
        elif closest == 180:
            if second_closest == 270:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * minus + sin(closest_angle * pi / 180) * minus_i])
            else:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * minus + sin(closest_angle * pi / 180) * plus_i])
        elif closest == 270:
            if second_closest == 360:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * minus_i + sin(closest_angle * pi / 180) * plus])
            else:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * minus_i + sin(closest_angle * pi / 180) * minus])
        elif closest == 360:
            if second_closest == 90:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * plus + sin(closest_angle * pi / 180) * plus_i])
            else:
                ret_vector.append(
                    [1 / sqrt(2), cos(closest_angle * pi / 180) * plus + sin(closest_angle * pi / 180) * minus_i])
    return ret_vector


def holm_bonferroni_correction(p_value_set, family_wise_alpha):
    print("holm")
    # print(p_value_set)
    valuearr = []
    for tuple in p_value_set:
        for pvalue in tuple[2]:
            if math.isnan(pvalue):
                valuearr.append((tuple[0], tuple[1], 1))
            else:
                valuearr.append((tuple[0], tuple[1], pvalue))

    # p_values = [1 if math.isnan(x) else x for x in p_values]
    valuearr.sort(key=lambda arr: arr[2])
    # print(valuearr)
    # print(p_values)
    for i in range(len(valuearr)):
        if (valuearr[i][2] <= (family_wise_alpha / (len(valuearr) - i))):
            print("failed it !")
            raise (AssertionError(f"Null hypothesis rejected on test {valuearr[i][0]} with inputs {valuearr[i][1]}"))


def run_test(test_method: list[Callable], input_generator: list[Callable], shots_per_test: int, amount_of_tests: int,
             alpha: float):
    if (shots_per_test < 10000):
        print("too few tests, increasing to 10,000 for statistical sig.")
        shots_per_test = 10000
    aggregate_pvalues = []
    vars_to_pass = None
    failed = False
    for i in range(len(test_method)):
        print(f"testing {str(test_method[i])}")
        for j in range(amount_of_tests):
            try:
                pvalues = None
                vars_to_pass = input_generator[i]()
                pvalues = test_method[i](vars_to_pass, shots_per_test)
                # print(str(test_method[i]))
                # print(pvalues)
            except BaseException as err:
                print(err)
                print("Code failed when executed with...")
                print(f"method = {str(test_method[i])}, \ninputs = {vars_to_pass}, \np values = {pvalues}")
                failed = True
                break
                # print("Failed")

            if pvalues != None and not failed:
                aggregate_pvalues.append((str(test_method[i]), vars_to_pass, pvalues))
            else:
                pass
    try:
        holm_bonferroni_correction(aggregate_pvalues, alpha)
    except AssertionError as exception:
        failed = True
        print(exception)

    if failed:
        print("#################")
        print("a test has failed")
        print("#################")
    else:
        print("####################")
        print("all tests successful")
        print("####################")
