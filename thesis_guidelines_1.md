
Your current structure has the right scientific content, but I would reorganize it so that the **logic of the thesis follows the development of the model**:

**physical problem → existing modeling framework → identified limitation → proposed solution → implementation → verification/validation → applications → conclusions.**

In particular, I would avoid introducing the new split too early as if it were already part of the established literature. The literature review should establish the **problem and existing approaches**, then identify the gap that motivates your implementation.

## Proposed thesis structure

### 1. Introduction

#### 1.1 Motivation and scientific context

* Fracture in engineering and natural materials
* Importance of anisotropic materials
* Why anisotropic elasticity matters for fracture
* Examples: composites, crystalline materials, battery electrodes, multiphase materials

#### 1.2 Problem statement

Introduce the central issue:

> Phase-field fracture models provide a powerful framework for modeling crack initiation and propagation, but their treatment of tensile and compressive deformation becomes non-trivial when the elastic response is anisotropic.

Then explain the practical problem:

* Cracks should generally not propagate under purely compressive loading.
* A tension–compression split is therefore required.
* Existing splits are predominantly developed/formulated for isotropic elasticity.
* Their extension to anisotropic elasticity is non-trivial.

#### 1.3 Objectives of the thesis

Clearly state the thesis objectives:

1. Implement the anisotropic tension–compression split proposed by [reference] in Pace3D.
2. Incorporate transverse-anisotropic elasticity into the phase-field fracture framework.
3. Verify the implementation against analytical relations.
4. Validate the tension–compression split using benchmark fracture simulations.
5. Investigate the influence of elastic anisotropy and material orientation on fracture.
6. Demonstrate the approach in a thermoelastic multiphase application.

#### 1.4 Thesis outline

Keep this short.

---

# 2. Theoretical Background and Literature Review

I would make this chapter more systematic than your current "Introduction/Literature Review/Background" idea.

### 2.1 Fundamentals of fracture mechanics

Start broad:

* Brittle fracture
* Crack initiation and propagation
* Griffith criterion / fracture energy
* Mode I, II, III, if relevant
* Limitations of classical sharp-crack descriptions

You don't need a huge fracture-mechanics chapter. Its purpose is to establish the physical concepts needed later.

### 2.2 Phase-field modeling of fracture

Introduce the phase-field approach:

* Sharp crack → diffuse crack representation
* Phase-field/damage variable
* Regularized crack surface
* Total free-energy functional
* Elastic energy + fracture energy
* Governing equations
* Degradation function
* Length-scale parameter

Then introduce the particular model you use.

### 2.3 Phase-field fracture with anisotropic crack resistance

Discuss the model of **Prajapati et al. (2026)**:

* Anisotropic fracture resistance
* Crack-surface energy
* Obstacle/well formulation, if relevant to your implementation
* How anisotropic crack resistance influences crack propagation
* Why this framework is useful for your thesis

This gives the reader the fracture framework **before** introducing anisotropic elasticity.

---

### 2.4 Anisotropic elasticity

Introduce the elastic side separately.

#### 2.4.1 General anisotropic elasticity

* Stress–strain relationship
* Elastic stiffness tensor
* Compliance tensor
* Symmetries

#### 2.4.2 Transverse isotropy

Since this is your primary application:

* Definition
* Material symmetry
* Independent elastic constants
* Representation/orientation of the material symmetry axis

#### 2.4.3 Rotated material coordinate system

This is particularly important for your later parameter studies.

Introduce:

* Material coordinates
* Global coordinates
* Orientation angle \(\theta\)
* Transformation of the stiffness tensor

This makes the later plots of stress versus \(\chi\) and \(\theta\) much easier to understand.

---

# 2.5 Tension–compression decomposition

**This should be a major subsection of the literature review because it is the conceptual core of the thesis.**

### 2.5.1 Motivation for a tension–compression split

Explain the fundamental issue:

The elastic energy is degraded by the phase field. Without a tension–compression decomposition, degradation can also reduce the material's resistance under compression, potentially producing **unphysical crack growth under compressive loading**.

Then introduce:

$$
\psi_e = \psi_e^+ + \psi_e^-
$$

where:

* \(\psi_e^+\): tensile/active part
* \(\psi_e^-\): compressive/inactive part

and typically only \(\psi_e^+\) is degraded.

This gives the reader the "why" before the "how."

---

### 2.5.2 Existing tension–compression splits

Organize them chronologically/conceptually rather than simply listing names.

#### Spectral decomposition — Miehe et al.

* Basic concept
* Principal strains/eigenvalues
* Positive and negative spectral components
* Advantages
* Limitations for anisotropic elasticity

#### Alternative splits

Discuss the relevant approaches from your literature, including **Ström/Strom et al.**, depending on the exact references you use.

For each:

* Mathematical idea
* What is decomposed?
* Applicability
* Advantages/limitations

#### Anisotropic splits

Then move specifically to:

* Lubarda/Teichtmeister-type approaches
* Other anisotropic formulations relevant to your work
* What makes anisotropic tension–compression decomposition fundamentally different from the isotropic case

A useful organizing question throughout this section is:

> **What quantity is being split, and with respect to which material/physical directions?**

That makes the literature much easier to compare.

---

# 2.6 The anisotropic tension–compression split of [Reference]

Now introduce the **new split from your reference paper** in its own section.

### 2.6.1 Mathematical formulation

Present the central equations.

### 2.6.2 Physical interpretation

Explain what the split means physically.

### 2.6.3 Expected advantages for anisotropic elasticity

This is where you make the transition toward your research.

Explain why this formulation is expected to overcome the limitations of conventional isotropic splits when the elastic constitutive response is anisotropic.

### 2.6.4 Research gap

End the chapter with something like:

> Although the formulation provides a framework for tension–compression decomposition in anisotropic elasticity, its implementation and systematic numerical assessment within the Pace3D phase-field fracture framework have not yet been established.

Then:

> **This thesis therefore focuses on the implementation, verification, validation, and application of this anisotropic tension–compression split, with particular emphasis on transversely isotropic materials.**

This creates a very clean bridge into Methods.

---

# 3. Methods

This chapter should contain **your model**, not the general literature.

## 3.1 Phase-field fracture formulation

State the governing formulation you actually implement.

* Free-energy functional
* Crack phase field
* Elastic energy
* Fracture energy
* Evolution equation
* Boundary conditions
* Degradation function

Reference Prajapati et al. where appropriate rather than re-deriving everything unnecessarily.

---

## 3.2 Anisotropic crack resistance

Describe the anisotropic crack-resistance model used in your simulations.

For example:

* Isotropic resistance
* Anisotropic resistance
* Obstacle/well formulation
* Parameters controlling anisotropy

Make clear which components come from the literature and which are part of your implementation.

---

## 3.3 Transversely anisotropic elasticity

Now introduce the actual constitutive equations used in your code.

* Constitutive relation
* Stiffness matrix/tensor
* Definition of anisotropy parameter \(\chi\)
* Orientation \(\theta\)
* Transformation between coordinate systems

This section should be sufficiently explicit that another researcher could reproduce your implementation.

---

## 3.4 Anisotropic tension–compression split

Present the equation from the reference paper **as implemented in this thesis**.

Important distinction:

**Literature chapter:** What the proposed split is and why it matters.

**Methods chapter:** Exactly how you incorporated it into your phase-field formulation.

Include:

* Mathematical decomposition
* Modified elastic energy
* Degradation of tensile contribution
* Treatment of compression
* Coupling to anisotropic elasticity

---

# 3.5 Numerical implementation

This is where Pace3D belongs.

### 3.5.1 Pace3D framework

Briefly introduce:

* Multiphysics framework
* C implementation
* Parallelization
* Relevant phase-field module
* Existing capabilities used by your work

Don't spend too much thesis space on the fact that Pace3D has 600k+ lines of code. That is interesting context, but the scientifically relevant point is **where your implementation sits within the framework**.

### 3.5.2 Implementation of anisotropic elasticity

### 3.5.3 Implementation of the tension–compression split

### 3.5.4 Numerical solution procedure

### 3.5.5 Pseudocode

For example:

```text
Initialize material parameters
Initialize phase field
Initialize displacement field

For each load/time step:
    Apply boundary conditions

    Compute strain
    Rotate strain/stiffness into material coordinates

    Compute anisotropic stress
    Compute tension–compression decomposition

    Compute tensile and compressive elastic energies

    Update phase field
    Update degraded stress

    Solve mechanical equilibrium

    Check convergence
End
```

The exact pseudocode should reflect your actual algorithm.

---

# 4. Verification and Validation

I recommend **separating this from the general Results and Discussion**.

Your first study is really **verification**, because you know the expected analytical solution.

This distinction makes the thesis much more rigorous.

## 4.1 Verification of anisotropic elasticity

### 4.1.1 Analytical reference solution

Derive the expected stress components for the prescribed uniaxial strain.

### 4.1.2 Numerical setup

* Geometry
* Boundary conditions
* Applied strain
* Mesh
* Material parameters

### 4.1.3 Stress response as a function of anisotropy

Plot:

$$
\sigma_{11},\quad \sigma_{22},\quad \sigma_{12}
$$

versus \(\chi\).

### 4.1.4 Influence of material orientation

Study:

$$
\theta
$$

and demonstrate that the numerical implementation correctly captures the expected orientation dependence.

### 4.1.5 Verification against analytical relations

This should conclude with quantitative error measures if possible.

For example:

$$
\epsilon_{\mathrm{rel}}
=
\frac{|\sigma_{\mathrm{num}}-\sigma_{\mathrm{analytical}}|}
{|\sigma_{\mathrm{analytical}}|}
$$

This turns "the plots look right" into a genuine numerical verification.

---

# 5. Fracture Results and Discussion

Now move from **no crack → crack**, which is a very natural progression.

## 5.1 Tension–compression split under isotropic crack resistance

### 5.1.1 Benchmark problem

Describe the geometry and loading.

### 5.1.2 Compression without tension–compression split

Show:

* Stress–strain response
* Phase-field evolution
* Crack evolution/path

### 5.1.3 Compression with tension–compression split

Same quantities.

The key comparison becomes:

**Does the split suppress physically inappropriate fracture under compression?**

This is a very important result and should be visually prominent.

---

## 5.2 Influence of anisotropic elasticity under compressive loading

Now introduce:

* \(\chi\)
* \(\theta\)

and examine the effect of anisotropic elasticity on the response.

This logically follows your first verification study.

---

# 5.3 Interaction between anisotropic elasticity and anisotropic crack resistance

This is potentially your most scientifically interesting section.

Use the **single-obstacle anisotropic crack-resistance** case.

### 5.3.1 Tension test with anisotropic crack resistance

Establish the baseline.

### 5.3.2 Isotropic versus anisotropic elasticity

Compare:

* Crack path
* Phase-field distribution
* Stress–strain response
* Possibly crack-driving force

This isolates the effect of the new elastic formulation.

### 5.3.3 Influence of anisotropy parameter \(\chi\)

Systematically vary \(\chi\).

### 5.3.4 Influence of material orientation \(\theta\)

If you have enough simulations, this is worth making a separate subsection.

---

# 5.4 Tension versus compression with anisotropic elasticity and crack resistance

This is where all the components come together:

> anisotropic elasticity + anisotropic crack resistance + tension–compression split.

Compare:

* Tension
* Compression
* Crack evolution
* Stress–strain response
* Dependence on \(\chi\) and/or \(\theta\)

This demonstrates the complete implementation rather than isolated components.

---

# 5.5 Application: Thermoelastic fracture in a multiphase system

Now demonstrate why the implementation is useful beyond artificial benchmark tests.

Discuss:

* Multiphase material
* Thermal loading
* Thermoelastic stresses
* Anisotropic elasticity
* Crack propagation
* Role of phase/material interfaces

This should be presented explicitly as an **application/demonstration**, rather than another validation test.

---

# 5.6 Extended anisotropy studies *(optional)*

Put these at the end so they don't interfere with the core thesis.

Possible extensions:

* Orthotropic materials
* Cubic symmetry
* Triclinic materials
* Stronger anisotropy ratios
* Different orientations
* Parameter sensitivity

I would **not promise all of these in the main thesis structure** unless you already know you will have the results.

You can retain this as an optional section or move it to the Outlook.

---

# 6. General Discussion

I would add a dedicated discussion chapter if the amount of results is substantial.

This lets you move beyond "plot A shows X."

### 6.1 Effect of elastic anisotropy

What changes because of anisotropic elasticity?

### 6.2 Effect of material orientation

How does \(\theta\) influence stress and crack propagation?

### 6.3 Interaction between elastic and fracture anisotropy

This is particularly important.

Distinguish:

$$
\text{elastic anisotropy}
\neq
\text{fracture anisotropy}
$$

and discuss their competing/combined effects.

### 6.4 Performance of the tension–compression split

Discuss:

* Suppression of compressive fracture
* Behavior under mixed loading
* Numerical robustness
* Limitations

### 6.5 Limitations

This section will make the thesis considerably stronger.

Potential topics:

* Restricted material symmetry
* Parameter calibration
* Phase-field length scale
* Computational cost
* Mesh requirements
* Limitations of the constitutive model
* No plasticity, damage mechanisms beyond fracture, etc.

---

# 7. Conclusion and Outlook

## 7.1 Summary of contributions

Be very concrete.

For example:

1. A transversely anisotropic elastic formulation was implemented in Pace3D.
2. The anisotropic tension–compression split of [reference] was implemented and coupled to the phase-field fracture model.
3. The elastic implementation was verified against analytical relations.
4. The fracture formulation was validated using benchmark simulations.
5. The influence of elastic anisotropy and material orientation was investigated.
6. The approach was demonstrated in a thermoelastic multiphase system.

## 7.2 Main findings

This should answer:

> **What did the thesis actually teach us?**

Rather than simply saying that the implementation works.

For example:

* How anisotropy affects stress distributions
* How orientation affects fracture
* Why the tension–compression split matters
* Interaction between elastic and fracture anisotropy

## 7.3 Outlook

Then your proposed extensions:

* Plasticity
* Thermomechanical coupling
* Chemical effects
* Battery electrodes
* Electrochemical–mechanical fracture
* More general anisotropy classes
* Coupling with other multiphysics processes

Your battery-electrode point fits particularly well here:

> Battery electrode materials often exhibit anisotropic mechanical properties, making anisotropic phase-field fracture models potentially relevant for studying mechanically induced degradation and fracture during electrochemical cycling.

---

# The resulting high-level structure

I would therefore structure the thesis as:

```text
1. Introduction
   1.1 Motivation
   1.2 Problem statement
   1.3 Objectives
   1.4 Thesis outline

2. Theoretical Background and Literature Review
   2.1 Fracture mechanics
   2.2 Phase-field fracture
   2.3 Anisotropic crack resistance
   2.4 Anisotropic elasticity
       2.4.1 General anisotropy
       2.4.2 Transverse isotropy
       2.4.3 Material orientation
   2.5 Tension–compression decomposition
       2.5.1 Motivation
       2.5.2 Miehe spectral split
       2.5.3 Other existing splits
       2.5.4 Anisotropic splits
   2.6 New anisotropic tension–compression split
       2.6.1 Formulation
       2.6.2 Physical interpretation
       2.6.3 Advantages/expected behavior
       2.6.4 Research gap

3. Methods
   3.1 Phase-field fracture formulation
   3.2 Anisotropic crack resistance
   3.3 Transversely anisotropic elasticity
   3.4 Anisotropic tension–compression split
   3.5 Numerical implementation
       3.5.1 Pace3D
       3.5.2 Elasticity implementation
       3.5.3 Split implementation
       3.5.4 Solution procedure
       3.5.5 Pseudocode

4. Verification and Validation
   4.1 Verification of anisotropic elasticity
       4.1.1 Analytical relations
       4.1.2 Numerical setup
       4.1.3 Dependence on χ
       4.1.4 Dependence on θ
       4.1.5 Error analysis
   4.2 Verification/validation of tension–compression split
       4.2.1 Compression without split
       4.2.2 Compression with split
       4.2.3 Crack evolution
       4.2.4 Stress–strain response

5. Fracture Results and Discussion
   5.1 Isotropic crack resistance
   5.2 Effect of anisotropic elasticity
   5.3 Anisotropic crack resistance
       5.3.1 Tension
       5.3.2 Isotropic vs anisotropic elasticity
       5.3.3 Effect of χ
       5.3.4 Effect of θ
   5.4 Tension vs compression
   5.5 Thermoelastic fracture in a multiphase system
   5.6 Extended anisotropy studies (optional)

6. General Discussion
   6.1 Elastic anisotropy
   6.2 Material orientation
   6.3 Elastic vs fracture anisotropy
   6.4 Tension–compression split
   6.5 Limitations

7. Conclusions and Outlook
   7.1 Contributions
   7.2 Main findings
   7.3 Outlook
```

### One important conceptual improvement

I would make the thesis revolve around **three separate layers of anisotropy**:

$$
\boxed{\text{Elastic anisotropy}}
$$

$$
\boxed{\text{Fracture/crack-resistance anisotropy}}
$$

$$
\boxed{\text{Tension–compression decomposition}}
$$

Then your results progressively combine them:

**Level 1:**
anisotropic elasticity alone → *Does the constitutive implementation work?*

**Level 2:**
tension–compression split + fracture → *Does the split prevent inappropriate compressive fracture?*

**Level 3:**
anisotropic elasticity + anisotropic fracture resistance → *How do the two anisotropies interact?*

**Level 4:**
full model + thermoelastic multiphase system → *Can the implementation be used in a realistic multiphysics application?*

That progression gives the thesis a very strong narrative. It also prevents the results section from becoming a collection of parameter studies: **each group of simulations answers a specific scientific/implementation question.**
