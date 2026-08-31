# Modelling Verification Plan

> **Important modelling constraint:**  
> For all studies described below, keep the **crack resistance isotropic** so that the influence of elastic anisotropy can be isolated.
>
> Use:
> - `Crack.Type = obstacle`
>
> Do **not** use:
> - `Crack.Type = obstacle_aniso`
>
> The anisotropic crack-resistance formulation should only be introduced in a later study, after the effects of elastic anisotropy and the tension-compression split have been independently verified.

---

## Tests to conduct

### 1) Uniaxial tension without crack

**Objective:** Verify the anisotropic elastic response and its dependence on `chi` and material orientation.

**Setup:**
- `crack = 0`
- No crack filling
- Apply uniaxial tension in the `x1` direction
- `chi = 0, 1, 2, 5, 10, 20`
- Anisotropy angle = `0, 30, 45, 60, 90 degrees`

**Quantities to analyse:**
- `sigma11`
- `sigma22`
- `sigma12`

For each value of `chi`, plot `sigma11`, `sigma22`, and `sigma12` as a function of anisotropy angle.

Where possible, compare the numerical results with the analytical stress response from the constitutive model. This should verify that the anisotropic stiffness and its rotation are implemented correctly.

The boundary conditions should be chosen carefully, since fully traction-free lateral boundaries may force some stress components to zero and make them unsuitable for verification.

---

### 2a) Uniaxial tension with crack

**Objective:** Study how elastic anisotropy influences the crack driving force while keeping crack resistance isotropic.

**Setup:**
- `crack = 1`
- Apply crack filling / crack preconditioning
- `store.crackdrivingforce = 1`
- `Crack.Type = obstacle`
- Apply the same uniaxial tensile loading as in Test 1
- `chi = 0, 1, 2, 5, 10, 20`
- Anisotropy angle = `0, 30, 45, 60, 90 degrees`

**Quantities to analyse:**
- Crack driving force
- Maximum crack driving force
- Spatial distribution of the crack driving force
- Dependence of the crack driving force on `chi` and anisotropy angle

Generate polar plots of the crack driving force as a function of anisotropy angle for different values of `chi`.

**Main questions:**
- Does increasing `chi` change the magnitude of the crack driving force?
- Does `chi` change the orientation at which the maximum crack driving force occurs?
- Does the anisotropic elastic contribution produce the expected angular dependence?
- Is the isotropic elastic solution recovered for `chi = 0`?

If useful, normalize the crack driving force with respect to the isotropic reference case to distinguish changes in magnitude from changes in directional dependence.

---

### 2b) Uniaxial compression: verification of the tension-compression split

**Objective:** Verify whether the tension-compression split correctly suppresses fracture driving under compressive loading.

Repeat the simulations under uniaxial compression for:

- `chi = 0, 1, 2, 5, 10, 20`
- Anisotropy angle = `0, 30, 45, 60, 90 degrees`
- `Crack.Type = obstacle`

Perform two sets of simulations:

#### A) Without tension-compression split
- Use the complete elastic energy for calculation of the crack driving force.

#### B) With tension-compression split
- Only the tensile / active part of the elastic energy should contribute to the crack driving force.

**Compare:**
- `sigma11`
- `sigma22`
- `sigma12`
- Crack driving force
- Crack evolution, if any

Particular attention should be given to orientations where elastic anisotropy may generate local tensile or shear contributions even though the macroscopic loading is compressive.

The main verification criterion is that the tension-compression split should prevent physically unrealistic crack growth under compression without incorrectly suppressing legitimate anisotropy-induced tensile or shear contributions.

---

## After completion of these tests

Progressively increase the complexity of the elastic anisotropy:

`Current directional anisotropy -> Cubic -> Orthotropic -> Monoclinic -> Triclinic`

For each anisotropy class, repeat the same verification sequence:

1. Verify the elastic stress response against the analytical stiffness tensor.
2. Verify material rotation and orientation dependence.
3. Verify the crack driving force under tension.
4. Verify the tension-compression split under compression.
5. Verify that the expected material symmetry is correctly reproduced.

Throughout these studies, continue using:

- `Crack.Type = obstacle`

This keeps the crack resistance isotropic and ensures that any observed directional dependence originates from the elastic constitutive law rather than from an anisotropic fracture-resistance model.

The triclinic formulation should finally provide the most general elastic framework with 21 independent stiffness components, while cubic, orthotropic, and monoclinic elasticity should be recoverable as special cases through the corresponding symmetry constraints.

---

## Later extension

Only after the elastic anisotropy and tension-compression split have been independently verified should anisotropic crack resistance be introduced.

At that stage, compare:

- `Crack.Type = obstacle`
- `Crack.Type = obstacle_aniso`

This will allow the effects of:

1. Elastic anisotropy
2. Anisotropic crack resistance
3. Their coupling

to be studied separately and then in combination.
