# **Quantum Fourier Transform Properties**:

**Let:**
$SHIFT$ be a function that shifts all elements of a column vector up by one, thus $SHIFT(|1\rangle) = |0\rangle$ 

$SHIFT(\begin{pmatrix} x_{0} \\ x_{1} \\ \vdots \\ x_{n-1} \end{pmatrix}) = \begin{pmatrix} x_{1} \\ \vdots \\ x_{n-1} \\ x_{0} \end{pmatrix}$ 

$PHASE\_SHIFT$ is a function that multiplies each element of a column vector by a different phase, according to the equation below:

$PHASE\_SHIFT(\begin{pmatrix} x_{0} \\ x_{1} \\ \vdots \\ x_{n-1} \end{pmatrix}) = \begin{pmatrix} x_{0}w^{n} \\  x_{1}w^{n-1} \\ \vdots \\  x_{n-1}w^{1} \end{pmatrix}$ and $w = e^{\frac{2 \pi i}{n}}$ 

1. **Linear shift induces phase shift.**

  + **Input:** Qubit state $|\psi \rangle$ of size $n$
  + **Precondition:**$| \psi \rangle \in \{| 0 \rangle, ..., | n-1 \rangle\}$
  + **Operation:** \
    $|\psi' \rangle = QFT(|\psi \rangle)$, \
    $|\psi" \rangle = QFT(SHIFT(|\psi \rangle))$
  + **Postcondition:** $PHASE\_SHIFT(|\psi' \rangle ) = |\psi" \rangle $


2. **Phase shift induces linear shift.**

  + **Input:** Qubit state $|\psi \rangle$ of size $n$
  + **Precondition:** \
  $| \phi \rangle \in \{| 0 \rangle, ..., | n-1 \rangle\}$ \
  $| \psi \rangle = QFT(| \phi \rangle)$
  + **Operation:** \
    $|\psi' \rangle = QFT ^{†} (|\psi \rangle)$, \
    $|\psi" \rangle = QFT ^{†} (PHASE\_SHIFT(|\psi \rangle))$
  + **Postcondition:** $SHIFT(|\psi' \rangle )= |\psi" \rangle $ 


3. **Identity property.**

  + **Input:** A random unitary operator $U$
  + **Precondition:** True
  + **Operation:** \
    $|\psi \rangle = QFT( U( H^{\otimes n}(QFT( |0^{\otimes n} \rangle))))$, \
    $|\psi' \rangle = QFT(U(|0^{\otimes n} \rangle))$
  + **Postcondition:** $|\psi \rangle = |\psi' \rangle $



# **Quantum Teleportation Properties:**

1. **Input state = Output state after teleportation.**

  + **Input:** Qubit state $|\psi \rangle$ of size $1$
  + **Precondition:** True
  + **Operation:** $|\psi' \rangle =  QT( | \psi 00 \rangle)$
  + **Postcondition:** $|\psi'_{2} \rangle = |\psi \rangle $


2. **Unitary after teleport = Unitary before teleport.**

  + **Input:** Qubit state $|\psi \rangle$ of size $1$, \
  A random unitary operator $U$
  + **Precondition:** True
  + **Operation:** \
  $|\psi' \rangle = U \otimes I \otimes I ( QT( | \psi 00 \rangle))$, \
  $|\psi" \rangle = QT( U \otimes I \otimes I (| \psi 00 \rangle))$
  + **Postcondition:** $|\psi' \rangle = |\psi" \rangle $


3. **Lower register in $|++\rangle $ after applying quantum teleportation.**

  + **Input:** Qubit state $|\psi \rangle$ of size $1$
  + **Precondition:** True
  + **Operation:** $|\psi' \rangle = QT( | \psi 00 \rangle)$ 
  + **Postcondition:** $|\psi'_{01} \rangle = \frac{1}{2}|++\rangle$


# **Quantum Phase Estimation Properties:**

**Let:**\
$EIG(U,|u\rangle) = True$ iff $U$ is a unitary operator, and $|u \rangle$ is an eigenstate of $U$. \
$VAL(U,|u\rangle)$ yields the eigenvalue of the eigenstate $|u \rangle$ with respect to matrix $U$. \
$QPE(| \phi \rangle, U, n)$ applies quantum phase estimation on unitary $U$ using $n$ estimation qubits (upper register).

1. **The same phase is estimated on the upper register when QPE is applied to two eigenvectors with the same eigenvalue.**

  + **Input:** Qubit states $|u \rangle$, \
  Unitary $U$ of size $n$
  + **Precondition:** \
  $EIG(U, |u \rangle) \land \
  EIG(U, |w \rangle)  \land \ 
  VAL(U, |u \rangle) = VAL(U, |w \rangle)$
  + **Operation:** \
  $|\psi \rangle  = QPE( |0^{\otimes n} \rangle |u \rangle, U, n)$, \
  $|\psi' \rangle = QPE( |0^{\otimes n} \rangle |w \rangle, U, n)$
  + **Postcondition:** $ |\psi_{0,...,n-1} \rangle = |\psi'_{0,...,n-1} \rangle $


2. **A different phase is estimated on the upper register when QPE is applied to two eigenvectors with different eigenvalues.**

  + **Input:** Qubit states $|u \rangle$, \
  Unitary $U$ of size $n$
  + **Precondition:** \
  $EIG(U, |u \rangle) \land \
  EIG(U, |w \rangle)  \land \
  VAL(U, |u \rangle) \neq VAL(U, |w \rangle)$
  + **Operation:** \
  $|\psi \rangle  = QPE( |0^{\otimes n} \rangle |u \rangle, U, n)$, \
  $|\psi' \rangle = QPE( |0^{\otimes n} \rangle |w \rangle, U, n)$
  + **Postcondition:** $ |\psi \rangle \neq |\psi' \rangle $


3. **Lower register is not modified by QPE if it is initialised to an eigenstate $|u \rangle$ that is an eigenvector $U$.**

  + **Input:** Qubit states $|u \rangle$
  + **Precondition:** $EIG(U, |u \rangle)$
  + **Operation:** $|\psi_{0,...,n-1} \rangle |\phi \rangle = QPE( |0^{\otimes n} \rangle |u \rangle, U, n)$
  + **Postcondition:** $ |\phi \rangle = |\phi' \rangle $

