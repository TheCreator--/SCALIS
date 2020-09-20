#include <Python.h>
#include <vector>
#include <cmath>
#include <iostream>
#include <array>

using ::std::pow;
using ::std::sqrt;
using ::std::log;
using ::std::atan;
using ::std::abs;

using Point = std::array<double, 2>;

Point vect(const Point& a, const Point& b) {
	Point v = {b[0] - a[0], b[1] - a[1]};
	return v;
}
	
double dot(const Point& a, const Point& b) {
	return a[0]*b[0] + a[1]*b[1];
}

double dist2(const Point& a, const Point& b) {
	return (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1]);
}

double dist(const Point& A, const Point& B) {
	return sqrt(dist2(A, B));
}

double power_inverse_convolution(int k, int i, const Point& A, const Point& B, const Point& P) {	
	double discriminant = dist2(A,B) * dist2(A,P) - pow(dot(vect(A,B), vect(A,P)), 2);
		
	if (discriminant <= 0) {
		return 0;
	}
		
	if (k == 0) {
		if (i == 1) {
			return log((dist(B,A) * dist(B,P) + dot(vect(B,A), vect(B,P))) 	\
				/ (dist(A,B) * dist(A,P) - dot(vect(A,B), vect(A,P))));
		}
		else if (i == 2) {
			return (atan(dot(vect(B,A), vect(B,P)) / sqrt(discriminant)) 	\
				+ atan(dot(vect(A,B), vect(A,P)) / sqrt(discriminant)))		\
				* dist(A,B) / sqrt(discriminant);
		}
		else { 
			return dist(A,B) / (i-2) / discriminant 								\
				* ((i-3) * dist(A,B)*power_inverse_convolution(0,i-2, A, B, P)		\
				+ dot(vect(B,A), vect(B,P)) / pow(dist(B,P), (i-2))						\
				+ dot(vect(A,B), vect(A,P)) / pow(dist(A,P), (i-2)));
		}
	}
	else if (k == 1) {
		if (i == 2) {
			return dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(0,2, A, B, P)		\
				+ log(dist(B,P) / dist(A,P)) / dist(A,B);
		}
		else {
			return dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(0,i, A, B, P)		\
				+ (pow((dist(B,P)), (2-i)) - pow((dist(A,P)), (2-i))) / dist(A,B) / (2-i);
		}
	}
	else if (k == i - 1) {
		return dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(i-2, i, A, B, P)		\
			+ power_inverse_convolution(i-3,i-2, A, B, P) / dist2(A,B) + pow((dist(B,P)), (2-i)) / (2-i) / dist(A,B);
	}
	else {
		return (i-2*k) / (i-k-1) * dot(vect(A,B), vect(A,P)) / dist2(A,B) * power_inverse_convolution(k-1,i, A, B, P)	\
			+ (k-1) / (i-k-1) * dist2(A,P) / dist2(A,B) * power_inverse_convolution(k-2,i, A, B, P)						\
			- pow((dist(B,P)), (2-i)) / dist(A,B) / (i-k-1);
	}
}

std::vector<int> binomial_expansion(int n) {
	auto coeff = std::vector<int>(n+1);
	
	coeff[0] = 1;
	for (int i = 0; i < n; i++) {
		coeff[i+1] = ((coeff[i] * (n-i)) / (i+1));
	}
	
	return coeff;
}

double normalization_factor(int i, double sigma) {
	if (i == 2) {
		return sigma * sigma * 3.14159265;
	}
	else if (i == 3) {
		return sigma * sigma * sigma * 2;
	}
	else {
		return sigma * sigma * (i-3) / (i-2) * normalization_factor(i-2, sigma);
	}
}

double get_integral_at_point(double A0, double A1, double a_rad, double B0, double B1, double b_rad, double P0, double P1, double sigma) {
	A0 /= sigma;
	A1 /= sigma;
	B0 /= sigma;
	B1 /= sigma;
	P0 /= sigma;
	P1 /= sigma;
	
	Point A = {A0, A1};
	Point B = {B0, B1};
	Point P = {P0, P1};
	
	int i = 3;
	
	// Always go from low weight (radius) to high weight (i.e. delta_tau is positive).
	double tau_0 = a_rad > b_rad ? b_rad : a_rad;
	double delta_tau = abs(a_rad - b_rad);
	
	// Swap points A and B so we go from low to high.
	if (a_rad > b_rad) {
		A[0] = B0; A[1] = B1;
		B[0] = A0; B[1] = A1;
	}
	
	auto coeff = binomial_expansion(i-1);
	
	// (delta_tau*t + tau_0)**(i-1)
	double val = 0;
	for (int k = 0; k < coeff.size(); k++) {
		double convolution = power_inverse_convolution(k, i, A, B, P);
		val += coeff[k] * pow(delta_tau, k) * pow(tau_0, i-k-1) * convolution;
	}
	
	return val / normalization_factor(i, sigma);
}

static PyObject* powerInverse(PyObject* self, PyObject *args) {
	double A0, A1, a_rad, B0, B1, b_rad, P0, P1, sigma;

	if (!PyArg_ParseTuple(args, "ddddddddd", &A0, &A1, &a_rad, &B0, &B1, &b_rad, &P0, &P1, &sigma)) {
		return NULL;
	}
	
	double value = get_integral_at_point(A0, A1, a_rad, B0, B1, b_rad, P0, P1, sigma);
	

	return Py_BuildValue("d", value);
}

static PyMethodDef convolutionSurfaceMethods[] = {
	{ "power_inverse", powerInverse, METH_VARARGS, "Returns value at point using power inverse kernel" },
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef convolutionSurfaceModule = {
	PyModuleDef_HEAD_INIT,
	"convolution_surface",
	"Defines functions for creating convolution surfaces",
	-1,
	convolutionSurfaceMethods
};

PyMODINIT_FUNC PyInit_convolution_surface(void) {
	return PyModule_Create(&convolutionSurfaceModule);
}