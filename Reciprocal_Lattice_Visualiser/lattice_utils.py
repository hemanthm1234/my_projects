import numpy as np

def generate_lattice(lattice_type, a, N):
    """Generate real-space lattice points and primitive vectors."""
    if lattice_type == "Simple Cubic":
        a1 = np.array([a, 0, 0])
        a2 = np.array([0, a, 0])
        a3 = np.array([0, 0, a])
        basis = [np.zeros(3)]

    elif lattice_type == "BCC":
        a1 = np.array([a/2, a/2, -a/2])
        a2 = np.array([-a/2, a/2, a/2])
        a3 = np.array([a/2, -a/2, a/2])
        basis = [np.zeros(3)]

    elif lattice_type == "FCC":
        a1 = np.array([0, a/2, a/2])
        a2 = np.array([a/2, 0, a/2])
        a3 = np.array([a/2, a/2, 0])
        basis = [np.zeros(3)]

    points = []
    for i in range(-N, N+1):
        for j in range(-N, N+1):
            for k in range(-N, N+1):
                for atom in basis:
                    R = i*a1 + j*a2 + k*a3 + atom
                    points.append(R)
    return np.array(points), (a1, a2, a3)


def reciprocal_lattice(a_vecs, N):
    """Generate reciprocal lattice points from primitive vectors."""
    a1, a2, a3 = a_vecs
    V = np.dot(a1, np.cross(a2, a3))
    b1 = 2*np.pi * np.cross(a2, a3) / V
    b2 = 2*np.pi * np.cross(a3, a1) / V
    b3 = 2*np.pi * np.cross(a1, a2) / V

    points = []
    for i in range(-N, N+1):
        for j in range(-N, N+1):
            for k in range(-N, N+1):
                G = i*b1 + j*b2 + k*b3
                points.append(G)
    return np.array(points)