import math
from math import log, sqrt, atan

from convolution_surface import power_inverse

def vect(A, B):
	return [b - a for a, b in zip(A, B)]
	
def dot(A, B):
	return sum(a*b for a, b in zip(A, B))

def dist2(A, B):
	return sum((b - a)**2 for a, b in zip(A, B))

def dist(A, B):
	return sqrt(dist2(A, B))
	
# |AB| * integral from 0 to 1 of t**k / (|P(A+tAB)|)**i dt
def power_inverse_convolution(k, i, A, B, P):
	discriminant = dist2(A,B) * dist2(A,P) - (dot(vect(A,B), vect(A,P)))**2
		
	if discriminant <= 0:
		return math.inf
	
	if k == 0:
		if i == 1:
			return log((dist(B,A) * dist(B,P) + dot(vect(B,A), vect(B,P))) 	\
				/ (dist(A,B) * dist(A,P) - dot(vect(A,B), vect(A,P))))
		elif i == 2:
			return (atan(dot(vect(B,A), vect(B,P)) / sqrt(discriminant)) 	\
				+ atan(dot(vect(A,B), vect(A,P)) / sqrt(discriminant)))		\
				* dist(A,B) / sqrt(discriminant)
		else: 
			return dist(A,B) / (i-2) / discriminant 								\
				* ((i-3) * dist(A,B)*power_inverse_convolution(0,i-2, A, B, P)		\
				+ dot(vect(B,A), vect(B,P)) / dist(B,P)**(i-2)						\
				+ dot(vect(A,B), vect(A,P)) / dist(A,P)**(i-2))
	elif k == 1:
		if i == 2:
			return dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(0,2, A, B, P)		\
				+ log(dist(B,P) / dist(A,P)) / dist(A,B)
		else:
			return dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(0,i, A, B, P)		\
				+ ((dist(B,P))**(2-i) - (dist(A,P))**(2-i)) / dist(A,B) / (2-i)
	elif k == i - 1: 
		return dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(i-2, i, A, B, P)		\
			+ power_inverse_convolution(i-3,i-2, A, B, P) / dist2(A,B) + (dist(B,P))**(2-i) / (2-i) / dist(A,B)
	else:
		return (i-2*k) / (i-k-1) * dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(k-1,i, A, B, P)	\
			+ (k-1) / (i-k-1) * dist2(A,P) / dist2(A,B) * power_inverse_convolution(k-2,i, A, B, P)						\
			- (dist(B,P))**(2-i) / dist(A,B) / (i-k-1)


def binomial_expansion(n):
	coeff = [1]
	for k in range(n):
		coeff.append((coeff[k] * (n-k)) / (k+1))
	
	return coeff

def get_value(A, B, P, sigma):
	A = [ai / sigma for ai in A]
	B = [bi / sigma for bi in B]
	P = [pi / sigma for pi in P]

	i = 2
	
	tau_0 = 1
	delta_tau = 0
	
	coeff = binomial_expansion(i-1)
	
	# (delta_tau*t + tau_0)**(i-1)
	val = sum(coeff[k] * delta_tau**(k) * tau_0**(i-k-1) * power_inverse_convolution(k, i, A, B, P) for k in range(len(coeff)))

	#print(val)
	return val

def get_field(A, a_rad, B, b_rad, width, height):
	# Initialize a blank field.
	field = [0] * height * width
	return add_to_field(A, a_rad, B, b_rad, width, height, field)	
	
def add_to_field(A, a_rad, B, b_rad, width, height, field):
	for i in range(width*height):
		field[i] += power_inverse(A[0], A[1], a_rad, B[0], B[1], b_rad, i % width, i // height, 1)