import numpy as np

M = np.array([ [-0.3748021, -0.6775266, 0.6571839, 1], [0.9050288, -0.5900814, 0.5575801, 1], [0.3260848, -0.0745549,0.0602215, 1], [0.2542186, -0.0603289, 0.0653356, 1] ])
x = np.array([1.74794, -0.871686, -3.26053, -3.00876])
y = np.array([-1.38784, 1.41934, -0.71568, -0.673189])
z = np.array([2.74392,-2.61509, 1.18936, 1.24175])
x_sol = np.linalg.solve(M,x)
y_sol = np.linalg.solve(M,y)
z_sol = np.linalg.solve(M,z)

print(x_sol)
print(y_sol)
print(z_sol)
