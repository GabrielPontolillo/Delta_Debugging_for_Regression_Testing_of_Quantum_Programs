# code from
# https://github.com/Qiskit/platypus/commit/0df3d20746aa442783def305f92000f69879e455

def qiskit_entangle():
    from qiskit import Aer, QuantumCircuit
    from qiskit.quantum_info import Statevector
    backend = Aer.get_backend('aer_simulator')

    MESSAGE = '10'

    qc_alice = QuantumCircuit(2,2)

    # Alice encodes the message
    if MESSAGE[-1] == '1':
        qc_alice.x(0)
    if MESSAGE[-2] == '1':
        qc_alice.x(1)

    # then she creates entangled states
    qc_alice.h(1)
    qc_alice.x(0)
    qc_alice.x(0)
    qc_alice.cx(1,0)

    ket = Statevector(qc_alice)
    ket.draw()

    qc_bob = QuantumCircuit(2,2)
    # Bob unentangles
    qc_bob.cx(0,1)
    qc_bob.h(0)
    # Then measures
    qc_bob.measure([0,1],[0,1])
    return backend.run(qc_alice.compose(qc_bob)).result().get_counts()


def qiskit_entangle_circ():
    from qiskit import Aer, QuantumCircuit
    from qiskit.quantum_info import Statevector
    backend = Aer.get_backend('aer_simulator')

    MESSAGE = '10'

    qc_alice = QuantumCircuit(2,2)

    # Alice encodes the message
    if MESSAGE[-1] == '1':
        qc_alice.x(0)
    if MESSAGE[-2] == '1':
        qc_alice.x(1)

    # then she creates entangled states
    qc_alice.h(1)
    qc_alice.cx(1,0)

    ket = Statevector(qc_alice)
    ket.draw()

    qc_bob = QuantumCircuit(2,2)
    # Bob unentangles
    qc_bob.cx(0,1)
    qc_bob.h(0)
    qc_bob.i(0)
    return qc_alice.compose(qc_bob)

