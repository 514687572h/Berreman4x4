#!/usr/bin/python
# encoding: utf-8

# Berreman4x4 example
# Author: O. Castany, C. Molinaro

# Example of a cholesteric liquid crystal

import numpy, Berreman4x4
from numpy import sin, sqrt, abs
from Berreman4x4 import c, pi, C, D, invC, invD
import matplotlib.pyplot as pyplot

# Materials
glass = Berreman4x4.IsotropicNonDispersiveMaterial(1.55)
front = back = Berreman4x4.IsotropicHalfSpace(glass)

# Liquid crystal oriented along the x direction
(no, ne) = (1.5, 1.6)
Dn = ne-no
n_med = (ne + no)/2
LC = Berreman4x4.UniaxialNonDispersiveMaterial(no, ne)
R = Berreman4x4.rotation_v_theta([0,1,0], pi/2)
LC = LC.rotated(R)
# Cholesteric pitch:
p = 0.65e-6
# One half turn of a right-handed helix:
TN = Berreman4x4.TwistedMaterial(LC, p/2, angle=+pi, div=40)

# Inhomogeneous layer, repeated layer, and structure
IL = Berreman4x4.InhomogeneousLayer(TN)
N = 25      # number half pitch repetitions
h = N * p/2
L = Berreman4x4.RepeatedLayers([IL], N)
s = Berreman4x4.Structure(front, [L], back)

# Normal incidence: 
Kx = 0.0

# Calculation parameters
lbda_min, lbda_max = 0.8e-6, 1.2e-6   # (m)
lbda_B = p * n_med
lbda_list = numpy.linspace(lbda_min, lbda_max, 100)
k0_list = 2*pi/lbda_list

############################################################################
# Analytical calculation for the maximal reflection
R_th = numpy.tanh(Dn/n_med*pi*h/p)**2
lbda_B1, lbda_B2 = p*no, p*ne

############################################################################
# Calculation with Berreman4x4
J = numpy.array([s.getJones(Kx,k0) for k0 in k0_list])
power = abs(J)**2
T_pp = Berreman4x4.extractCoefficient(power, 't_pp')
R_pp = Berreman4x4.extractCoefficient(power, 'r_pp')
T_sp = Berreman4x4.extractCoefficient(power, 't_sp')
R_sp = Berreman4x4.extractCoefficient(power, 'r_sp')
# Note: the expression for T is valid if back and front media are identical

# Reflection and transmission coefficients for unpolarized light:
total_power = power.sum(axis=-1).sum(axis=-1) / 2
(R_np, T_np) = numpy.transpose(total_power)

# Eigenvectors of the transmission matrix in the middle of the stop-band
i = numpy.argmin(abs(lbda_list-lbda_B))     # middle of the stop band
T = J[i,1,:,:]                              # transmission matrix
eigenvalues, eigenvectors = numpy.linalg.eig(T)
numpy.set_printoptions(precision=3)
print("\nTransmission in the middle of the stop-band...\n")
print("Eigenvalues of the Jones transmission matrix:")
print(eigenvalues)
print("Corresponding power transmission:")
print(abs(eigenvalues)**2)
print("Corresponding eigenvectors:")
print(eigenvectors)
# Note: the transformation matrix to the eigenvector basis is
# B = numpy.matrix(eigenvectors), and the matrix B⁻¹ T B is diagonal.
print("Normalization to the 'p' componant:")
print(eigenvectors/eigenvectors[0,:])
print("Ratio 's'/'p':")
print(abs(eigenvectors[1,:]/eigenvectors[0,:]))
print("Ellipticity angle (°) (+90°: L, -90°: R)")
print(180/pi*numpy.angle(eigenvectors[1,:]/eigenvectors[0,:]))

# Jones matrices for the circular wave basis
Jc = Berreman4x4.circularJones(J)
power = abs(Jc)**2

# Right-circular wave is reflected in the stop-band
# R_LR, T_LR close to zero
R_RR = Berreman4x4.extractCoefficient(power, 'r_RR')
T_RR = Berreman4x4.extractCoefficient(power, 't_RR')

# Left-circular wave is transmitted in the full spectrum
# T_RL, R_RL, R_LL close to zero, T_LL close to 1
T_LL = Berreman4x4.extractCoefficient(power, 't_LL')
R_LL = Berreman4x4.extractCoefficient(power, 'r_LL')

############################################################################
# Plotting
fig = pyplot.figure()
ax = fig.add_subplot("111")

# Draw rectangle for λ ∈ [p·no, p·ne], and T ∈ [0, R_th]
rectangle = pyplot.Rectangle((lbda_B1,0), lbda_B2-lbda_B1, R_th, color='cyan')
ax.add_patch(rectangle)

# d1 = numpy.vstack((T_pp, R_pp, T_sp, R_sp)).T
# d2 = numpy.vstack((T_RR, R_RR, T_LR, R_LR)).T

# lines1 = ax.plot(lbda_list, d1)
# lines2 = ax.plot(lbda_list, d2)

# legend1 = ('T_pp', 'R_pp', 'T_sp', 'R_sp')
# legend2 = ('T_RR', 'R_RR', 'T_LR', 'R_LR')

ax.plot(lbda_list, R_RR, label='R_RR')
ax.plot(lbda_list, T_RR, label='T_RR')
ax.legend(loc='center right', bbox_to_anchor=(1.00, 0.50))

ax.set_title("Right-handed Cholesteric Liquid Crystal, " +
             "{:.1f} helix pitches".format(N/2.))
ax.set_xlabel(r"Wavelength $\lambda_0$ (m)")
ax.set_ylabel(r"Power transmission $T$ and reflexion $R$")
fmt = ax.xaxis.get_major_formatter()
fmt.set_powerlimits((-3,3))
pyplot.show()


