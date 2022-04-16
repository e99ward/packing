#__author__ = 'Xinyue'
import cvxpy as cvx
import numpy as np
import matplotlib.pyplot as plt
import dccp

# number of spheres
n = 10
# radius of spheres
#r = np.linspace(1, 5, n)
r = np.array([1 for i in range(n)])
# dimension of space
dim = 2
#2 for circle, 3 for spheres

c = cvx.Variable((n, dim))
constr = []
for i in range(n - 1):
    constr.append(cvx.norm(cvx.reshape(c[i, :], (1, dim)) - c[i + 1: n, :], 2, axis=1) >= r[i] + r[i + 1: n])
prob = cvx.Problem(cvx.Minimize(cvx.max(cvx.max(cvx.abs(c), axis=1) + r)), constr)
prob.solve(method="dccp", solver="ECOS", ep=1e-2, max_slack=1e-2)

fig = plt.figure()

def sphere_at(ax, Px, Py, Pz, R):
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = R * np.cos(u)*np.sin(v) + Px
    y = R * np.sin(u)*np.sin(v) + Py
    z = R * np.cos(v) + Pz
    out = ax.plot_surface(x, y, z, color='g', alpha=0.5)
    return out

def circle_at(ax, Px, Py, R):
    circ = np.linspace(0, 2 * np.pi)
    x = R * np.cos(circ) + Px
    y = R * np.sin(circ) + Py
    out = ax.plot(x, y, 'b')
    return out

if dim == 2:
    ax = fig.add_subplot()
    ax.set_aspect("equal")
    l = cvx.max(cvx.max(cvx.abs(c), axis=1) + r).value * 2
    #l_min = cvx.max(cvx.max(cvx.abs(c), axis=1)).value * 2
    ratio = np.pi * cvx.sum(cvx.square(r)).value / cvx.square(l).value
    print("ratio =", ratio)
    x_border = [-l/2, l/2, l/2, -l/2, -l/2]
    y_border = [-l/2, -l/2, l/2, l/2, -l/2]
    ax.plot(x_border, y_border, 'm')
    #ax.set_xlim([-l / 2, l / 2])
    #ax.set_ylim([-l / 2, l / 2])
    for i in range(n):
        circle_at(ax, c[i, 0].value, c[i, 1].value, r[i])

else:
    ax = fig.add_subplot(projection='3d')
    l = cvx.max(cvx.max(cvx.abs(c), axis=1) + r).value * 2
    ratio = 4/3 * np.pi * np.sum(r**3) / l**3
    print("ratio =", ratio)
    edges_kw = dict(color='0.4', linewidth=1)
    ax.plot([l/2, l/2], [-l/2, l/2], [l/2, l/2], **edges_kw)
    ax.plot([-l/2, l/2], [-l/2, -l/2], [l/2, l/2], **edges_kw)
    ax.plot([l/2, l/2], [-l/2, -l/2], [-l/2, l/2], **edges_kw)
    for i in range(n):
        sphere_at(ax, c[i, 0].value, c[i, 1].value, c[i, 2].value, r[i])

plt.show()