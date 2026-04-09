import sympy as sp

# --- SYMBOLS ---
t = sp.Symbol('t')
i = sp.Symbol('i', integer=True)
j = sp.Symbol('j', integer=True)
T = sp.Function('T')  # T(i,j,t)
w = sp.Function('w')  # w(i,j)
D = sp.Function('D')  # D(t)

# --- INVARIANTS (LANGUAGE-AGNOSTIC DEFINITIONS) ---
# I1(t) = S w_ij * T(i,j,t)^2
I1 = sp.Sum(w(i, j) * T(i, j, t)**2, (i, -sp.oo, sp.oo), (j, -sp.oo, sp.oo))

# I2(t) = S[(T(i+1,j)-T(i,j))^2 + (T(i,j+1)-T(i,j))^2]
I2 = sp.Sum((T(i+1, j, t) - T(i, j, t))**2 + (T(i, j+1, t) - T(i, j, t))**2, (i, -sp.oo, sp.oo), (j, -sp.oo, sp.oo))

# I3(t) = 1 / (1 + D(t))
I3 = 1 / (1 + D(t))

# VALID(t) = I1 ? physical_bounds ? I2 ? smoothness_bounds ? I3 ? coherence_bounds
I1_in_bounds = sp.Symbol('I1_in_bounds')
I2_in_bounds = sp.Symbol('I2_in_bounds')
I3_in_bounds = sp.Symbol('I3_in_bounds')
VALID = sp.And(I1_in_bounds, I2_in_bounds, I3_in_bounds)

if __name__ == '__main__':
    print('I1(t) =', I1)
    print('I2(t) =', I2)
    print('I3(t) =', I3)
    print('VALID =', VALID)
