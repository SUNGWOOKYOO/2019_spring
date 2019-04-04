#import matplotlib.pyplot as plt
from cvxopt import matrix, solvers	#import convex optimazation library
import numpy

def identity(a, n): # create and output diagonal matrix with value a 
	m = a * numpy.ones(n)
	m = numpy.diag(m)
	return m

def svm(C, n):
	Q = matrix([[0.0 for i in range(n)] for j in range(n)]) # n*n matrix 
	for i in range(0, n):
		for j in range(0, n):
			Q[i, j] = labels[i] * labels[j] * (x_data[i] * x_data[j] + y_data[i] * y_data[j])
	p = matrix([-1.0 for i in range(n)])
	G = matrix(numpy.vstack((identity(-1.0, n), identity(1.0, n))))
	h = matrix([0.0 for i in range(n)] + [C for i in range(n)])
	A = matrix(labels, (1, n))
	b = matrix(0.0)

	sol = solvers.qp(Q, p, G, h, A, b)
	print sol['x']

	print '\n\nweight:'
	w0 = 0.0
	w1 = 0.0
	for i in range(0, n):
		w0 += sol['x'][i] * labels[i] * x_data[i]
		w1 += sol['x'][i] * labels[i] * y_data[i]
	print w0
	print w1
	
	print '\n\nbias:'
	b = 0.0
	for i in range(0, n):
		if sol['x'][i] <= 0:
			continue
		b += labels[i]
		for j in range(0, n):
			b -= sol['x'][j] * labels[j] * (x_data[j] * x_data[i] + y_data[j] * y_data[i])
		break
	print b

	print '\n\ndecision cost:'
	cost = 0.0
	for i in range(0, n):
		for j in range(0, n):
			cost += sol['x'][j] * labels[j] * (x_data[j] * x_data[i] + y_data[j] * y_data[i])
		cost += b
	print cost

#	x_axis = numpy.arange(-1.0, 5.0, 0.01)
#	d_line = (-b - w0 * x_axis) / w1
	
#	for i in range(0, n):
#		dot_color = chr(106 + int(labels[i]) * 8)
#		plt.scatter(x_data[i], y_data[i], color=dot_color)
#	plt.plot(x_axis, d_line, lw=2)
#	plt.show()


# parsing dataset 
fr = open('data-ex1.txt', 'r')
x_data = []
y_data = []
labels = []
while True:
	line = fr.readline()
	if not line: break
	sp_line = line.split()
	
	x_datum = float(sp_line[1][2:])
	x_data.append(x_datum)
	y_datum = float(sp_line[2][2:])
	y_data.append(y_datum)
	label = int(sp_line[0])
	labels.append(float(label))

#	dot_color = chr(106 + label * 8)
#	plt.scatter(x_datum, y_datum, color=dot_color)
#plt.show()

svm(0.1, len(labels))
svm(10, len(labels))
