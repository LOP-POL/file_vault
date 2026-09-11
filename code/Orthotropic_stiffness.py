#!/usr/bin/env python3
"""
stiffness_tensor.py

Builds the 6x6 Voigt-notation stiffness matrix [C] for either:
  - an isotropic material, given only E and nu, OR
  - a fully orthotropic material, given all 9 independent constants
    (Ea, Eb, Ec, Gbc, Gac, Gab, nu_ab, nu_ac, nu_bc)

If exactly the isotropic pair (E, nu) is supplied and none of the
orthotropic-only arguments are given, this explicitly derives the Lame
constants lambda and mu first (for clarity / traceability) and builds the
isotropic [C] directly from them. Otherwise, all 9 orthotropic constants
must be supplied, and [C] is obtained by inverting the 3x3 normal-strain
compliance block (plus 3 uncoupled shear terms), followed by symmetrizing
the result to remove floating-point asymmetry introduced by the inversion.
"""

import numpy as np


def _build_isotropic(E, nu):
    """
    Explicit isotropic derivation, shown step by step for clarity:

        mu     = E / (2 * (1 + nu))
        lambda = E * nu / ((1 + nu) * (1 - 2*nu))

        C11 = lambda + 2*mu   (= C22 = C33)
        C12 = lambda          (= C13 = C23)
        C44 = mu              (= C55 = C66)
    """
    mu = E / (2.0 * (1.0 + nu))
    lam = E * nu / ((1.0 + nu) * (1.0 - 2.0 * nu))

    print(f"Isotropic input detected (E={E}, nu={nu}).")
    print(f"  Derived Lame constants: lambda = {lam:.6g}, mu = {mu:.6g}")

    C11 = lam + 2.0 * mu
    C12 = lam
    C44 = mu

    C = np.zeros((6, 6))
    C[0, 0] = C[1, 1] = C[2, 2] = C11
    C[0, 1] = C[1, 0] = C12
    C[0, 2] = C[2, 0] = C12
    C[1, 2] = C[2, 1] = C12
    C[3, 3] = C[4, 4] = C[5, 5] = C44

    return C


def _build_orthotropic(Ea, Eb, Ec, Gbc, Gac, Gab, nu_ab, nu_ac, nu_bc):
    """
    Full orthotropic derivation:
      1. Build the 3x3 normal-strain compliance block S_N from
         Ea, Eb, Ec, nu_ab, nu_ac, nu_bc.
      2. Invert it to get the normal-strain stiffness block C_N.
      3. Symmetrize C_N (numpy.linalg.inv on a symmetric matrix is not
         guaranteed to return an exactly symmetric result due to
         floating-point round-off).
      4. Assemble the full 6x6 matrix, with the 3 shear terms
         (Gbc, Gac, Gab) uncoupled from everything else.
    """
    S_N = np.array([
        [1.0 / Ea,   -nu_ab / Ea, -nu_ac / Ea],
        [-nu_ab / Ea, 1.0 / Eb,   -nu_bc / Eb],
        [-nu_ac / Ea, -nu_bc / Eb, 1.0 / Ec  ],
    ])

    C_N = np.linalg.inv(S_N)
    C_N = (C_N + C_N.T) / 2.0  # symmetrize to remove round-off asymmetry

    C = np.zeros((6, 6))
    C[:3, :3] = C_N
    C[3, 3] = Gbc
    C[4, 4] = Gac
    C[5, 5] = Gab

    return C


def build_stiffness(E=None, nu=None,
                     Ea=None, Eb=None, Ec=None,
                     Gbc=None, Gac=None, Gab=None,
                     nu_ab=None, nu_ac=None, nu_bc=None):
    """
    Build the 6x6 stiffness matrix [C], automatically choosing the
    isotropic or orthotropic path based on which arguments are supplied.

    Isotropic path:   pass only E and nu.
    Orthotropic path: pass all of Ea, Eb, Ec, Gbc, Gac, Gab,
                       nu_ab, nu_ac, nu_bc (E and nu left as None).
    """
    isotropic_args_given = (E is not None) and (nu is not None)
    orthotropic_args = [Ea, Eb, Ec, Gbc, Gac, Gab, nu_ab, nu_ac, nu_bc]
    any_orthotropic_given = any(v is not None for v in orthotropic_args)
    all_orthotropic_given = all(v is not None for v in orthotropic_args)

    if isotropic_args_given and not any_orthotropic_given:
        return _build_isotropic(E, nu)

    if all_orthotropic_given and not isotropic_args_given:
        return _build_orthotropic(Ea, Eb, Ec, Gbc, Gac, Gab, nu_ab, nu_ac, nu_bc)

    raise ValueError(
        "Ambiguous or incomplete input: supply either just E and nu "
        "(isotropic), or all nine of Ea, Eb, Ec, Gbc, Gac, Gab, nu_ab, "
        "nu_ac, nu_bc (orthotropic) -- not a mix of the two, and not a "
        "partial orthotropic set."
    )


if __name__ == "__main__":
    np.set_printoptions(precision=4, suppress=True)

    # --- Isotropic example --------------------------------------------------
    print("=== Isotropic example (E=200 GPa, nu=0.3) ===")
    C_iso = build_stiffness(E=200.0, nu=0.3)
    print(C_iso)
    print()

    # --- Orthotropic example: human femur, from Table 8 of Lubarda & Chen ---
    print("=== Orthotropic example (human femur, Lubarda & Chen Table 8) ===")
    C_ortho = build_stiffness(
        Ea=12.01, Eb=13.48, Ec=20.16,
        Gbc=6.23, Gac=5.61, Gab=4.52,
        nu_ab=0.378, nu_ac=0.219, nu_bc=0.233,
    )
    print(C_ortho)
    print("Symmetric?", np.allclose(C_ortho, C_ortho.T))