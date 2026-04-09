import sympy as sp

I1 = sp.Function('I1')
I2 = sp.Function('I2')
I3 = sp.Function('I3')
D = sp.Function('D')

# Invariants definitions
I1_expr = sp.Sum(sp.Symbol('w_ij') * sp.Symbol('T')**2)
I2_expr = sp.Sum((sp.Symbol('T_next')-sp.Symbol('T'))**2)
I3_expr = 1/(1 + D(sp.Symbol('t')))
