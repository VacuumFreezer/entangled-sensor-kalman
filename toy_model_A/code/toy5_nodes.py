"""Toy 5: nodes with several qubits.  Local-only strategies with mixed local-GHZ sizes per node (no network entanglement); nuisance modes random.
Node j holds units of sizes gs[j] (list); unit u has phase g_u*phi_j - delta_u.  Node likelihood is a Fourier series in
phi_j with frequencies |q| <= G_j = sum(gs[j]).  Immune terms: sum_j q_j F_nuis(z_j) = 0.  A_q = sum_j q_j f_t(z_j)."""
import itertools
import numpy as np


def node_coeffs(bits, gs, deltas):
    G = int(sum(gs))
    c = np.zeros(bits.shape[:-1] + (2 * G + 1,), complex); c[..., G] = 1.0
    for l, g in enumerate(gs):
        b = bits[..., l][..., None]
        ap = b / 4j * np.exp(-1j * deltas[l]); am = -b / 4j * np.exp(1j * deltas[l])
        new = 0.5 * c
        new[..., g:] += ap * c[..., :-g]
        new[..., :-g] += am * c[..., g:]
        c = new
    return c


class MixNet:
    def __init__(self, z, ft, Fn, gs, unit):
        self.k = len(z); self.gs = [list(map(int, x)) for x in gs]; self.G = np.array([sum(x) for x in self.gs])
        self.ft = np.asarray(ft, float); self.Fn = np.asarray(Fn, float); self.unit = np.asarray(unit, float)
        # immune set: enumerate q_1..q_{k-r} freely, solve the rest?  Simple filter is fine for moderate G.
        Q = np.array(list(itertools.product(*[range(-Gj, Gj + 1) for Gj in self.G])), dtype=np.int32)
        ok = np.all(np.abs(Q @ self.Fn) < 1e-9, axis=1)
        self.Q = Q[ok]; self.A = self.Q @ self.ft
        self.nbits = sum(len(x) for x in self.gs)

    def _P_dP(self, C, d):
        W = np.exp(1j * d * self.A)
        prod = np.ones((C[0].shape[0], len(self.Q)), complex)
        for j in range(self.k):
            prod *= C[j][:, self.Q[:, j] + self.G[j]]
        return np.real(prod @ W), np.real(prod @ (1j * self.A * W))

    def fisher_exact(self, deltas, d=0.0):
        outs = [np.array(list(itertools.product((1, -1), repeat=len(g)))) for g in self.gs]
        Cn = [node_coeffs(o, g, dl) for o, g, dl in zip(outs, self.gs, deltas)]
        idx = np.array(list(itertools.product(*[range(len(o)) for o in outs])))
        C = [Cn[j][idx[:, j]] for j in range(self.k)]
        P, dP = self._P_dP(C, d)
        assert abs(P.sum() - 1) < 1e-8
        return float(np.sum(dP ** 2 / np.maximum(P, 1e-300)))

    def fisher_mc(self, deltas, d=0.0, N=100000, seed=0, chunk=10000):
        rng = np.random.default_rng(seed); vals = []
        for s in range(0, N, chunk):
            n = min(chunk, N - s)
            nu = rng.uniform(0, 2 * np.pi, (n, self.Fn.shape[1]))
            phin = nu @ (self.Fn / self.unit).T
            C = []
            for j in range(self.k):
                phi = d * self.ft[j] + phin[:, j]
                g = np.array(self.gs[j]); dl = np.asarray(deltas[j])
                p = (1 + np.sin(g[None, :] * phi[:, None] - dl[None, :])) / 2
                b = np.where(rng.random(p.shape) < p, 1, -1)
                C.append(node_coeffs(b, self.gs[j], dl))
            P, dP = self._P_dP(C, d)
            vals.append(dP ** 2 / P ** 2)
        v = np.concatenate(vals)
        return float(v.mean()), float(v.std() / np.sqrt(len(v)))


def spread_refs(gs, offset):
    """within a node, units of the same size get references spread over [0, pi)."""
    out = np.zeros(len(gs)); gs = np.array(gs)
    for g in np.unique(gs):
        idx = np.where(gs == g)[0]
        out[idx] = offset + np.pi * np.arange(len(idx)) / len(idx)
    return out


def modes(z):
    """Spatial modes at the node positions: uniform b, gradient g, curvature c (mean-subtracted)."""
    z = np.asarray(z, float)
    return {"b": np.ones_like(z), "g": z, "c": z * z - np.mean(z * z)}
