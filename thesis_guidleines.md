
Your current structure has the right technical ingredients, but the logical progression can be made much stronger. In particular, I would separate the thesis into:

    Why fracture modeling needs phase fields

    Why anisotropy creates a specific problem

    What the existing tension–compression splits do

    What the new split contributes

    How you implement it

    How you validate it

    What physical simulations demonstrate that the implementation enables

That gives the thesis a clear narrative: problem → gap → proposed/modeling framework → implementation → verification → application → outlook.
Proposed Thesis Structure

1. Introduction
   1.1 Motivation and scientific context

   Fracture in engineering and natural materials

   Importance of anisotropy in fracture

   Examples of transverse-anisotropic materials

   Limitations of conventional isotropic fracture models

   Motivation for computational fracture modeling

1.2 Research problem

Introduce the central problem explicitly:

    How can phase-field fracture be formulated and implemented such that the tension–compression split is consistent with anisotropic elasticity?

Explain why this is important:

    Cracks should grow primarily under tensile loading.

    Standard phase-field formulations require a distinction between tensile and compressive contributions.

    A split developed for isotropic elasticity may not remain physically consistent when elasticity is anisotropic.

    This becomes particularly relevant for transverse-anisotropic materials.

1.3 Objectives and scope of the thesis

State the objectives clearly, for example:

    Implement the anisotropic tension–compression split proposed by the reference work in Pace3D.

    Incorporate transverse-anisotropic elasticity into the phase-field fracture framework.

    Verify the elastic response against analytical relations.

    Validate the tension–compression behavior using benchmark simulations.

    Investigate the influence of anisotropy and material orientation.

    Demonstrate the model in fracture simulations and a thermoelastic multiphase application.

1.4 Thesis outline

A short paragraph explaining the organization of the thesis.
2. Theoretical Background and Literature Review

I would not call this simply "Background". A combined Theoretical Background and Literature Review makes the progression easier to understand.
2.1 Fundamentals of fracture mechanics

Start from the broadest concept.
2.1.1 Fracture and crack propagation

    Crack initiation

    Crack propagation

    Griffith concept

    Energy-based fracture mechanics

2.1.2 Continuum descriptions of fracture

    Sharp crack descriptions

    Limitations of explicit crack tracking

    Motivation for regularized/continuum descriptions

This section should be relatively concise. You don't need to turn the thesis into a general fracture-mechanics textbook.
2.2 Phase-field modeling of fracture
2.2.1 Basic concept

    Crack phase field/order parameter

    Diffuse crack representation

    Regularization length scale

2.2.2 Variational formulation

    Total free energy

    Elastic energy

    Crack surface energy

    Governing equations

    Evolution equation

2.2.3 Phase-field fracture with anisotropic crack resistance

Introduce Prajapati et al. (2026) here.

Explain:

    Why anisotropic crack resistance is useful

    Crack-surface energy formulation

    Anisotropic obstacle/well formulation

    How anisotropic crack resistance affects crack paths

This provides the foundation for the later simulations.
2.3 Tension–Compression Splitting in Phase-Field Fracture

This deserves its own major section, because it is essentially the central theoretical problem of your thesis.
2.3.1 Why is a tension–compression split required?

Explain the physical and numerical motivation:

    Fracture is generally associated with tensile/deviatoric loading rather than purely compressive loading.

    Without a split, the degradation of elastic energy can also reduce the material's resistance under compression.

    This can result in physically undesirable crack growth or crack evolution under compressive loading.

Then introduce the mathematical concept:

ψel=ψ++ψ−,

where only the appropriate tensile contribution is degraded by the phase field.
2.3.2 Existing tension–compression splits

Rather than discussing the splits as a disconnected list, organize them historically/conceptually.
(a) Spectral decomposition — Miehe et al.

    Basic concept

    Positive and negative eigenvalues of strain

    Advantages

    Limitations

(b) Alternative strain/stress-based splits

    Relevant approaches such as the splits you refer to as Strom's splits

    What quantity is decomposed

    Advantages and limitations

(c) Anisotropic tension–compression splits

Introduce work on anisotropic formulations, including:

    Lubarda / Teichtmeister-type approaches

    Other relevant anisotropic formulations

For each formulation, keep the same structure:

    What is split? → How is it defined? → What physical assumption does it make? → What limitation does it have for anisotropic elasticity?

That will make the literature review much more analytical rather than merely descriptive.
2.4 The New Anisotropic Tension–Compression Split

This should be the culmination of the literature review.
2.4.1 Motivation

Explain the specific problem with applying conventional splits to anisotropic elasticity.
2.4.2 Mathematical formulation

Introduce the split from your reference paper.
2.4.3 Physical interpretation

Explain what the split means in terms of:

    tensile/compressive deformation,

    material anisotropy,

    material orientation,

    energetic degradation.

2.4.4 Expected advantages for anisotropic elasticity

This is where you make the connection to your thesis:

    The new split provides a framework for separating tensile and compressive elastic contributions while accounting for anisotropic elastic behavior.

Then clearly state the research gap:

    Although the formulation has been developed theoretically, its implementation and systematic numerical validation for transverse-anisotropic phase-field fracture have not yet been established in Pace3D.

That sentence—or something equivalent—would give your thesis a very strong reason for existing.
2.5 Research Gap and Contribution

I would actually give this its own short section.

Summarize:

Existing knowledge
→ Phase-field fracture
→ anisotropic crack resistance
→ anisotropic elasticity
→ tension–compression splits
→ proposed new anisotropic split

Remaining gap
→ implementation + validation + application

This thesis
→ fills that gap.

This is much clearer than leaving the reader to infer the research contribution from the literature review.
3. Mathematical Model and Numerical Methods

This chapter should contain everything necessary to reproduce the simulations.
3.1 Phase-field fracture model

Present the model adopted from Prajapati et al. (2026).

    Phase-field variable

    Free-energy functional

    Crack surface energy

    Degradation function

    Governing equations

    Boundary conditions

    Irreversibility/history field, if applicable

3.2 Anisotropic crack resistance

Explain the anisotropic crack resistance model mathematically.

    Anisotropic gradient term

    Material/crack orientation

    Obstacle/well formulation

    Parameters controlling anisotropy

This is where you define quantities such as χ and θ precisely.
3.3 Anisotropic elasticity

Introduce transverse anisotropy.
3.3.1 Constitutive relation

σ=C:ε

with the appropriate transverse-anisotropic stiffness tensor.
3.3.2 Material parameters

Explain:

    isotropic reference case

    anisotropy parameter χ

    material orientation θ

    relationship between model parameters and elastic constants

3.3.3 Coordinate transformation

If the material orientation is represented through a rotation, explain that here.
3.4 Anisotropic tension–compression split

Now introduce the exact equation that you discussed conceptually in Chapter 2.

    Mathematical formulation

    Tensile contribution

    Compressive contribution

    Energy degradation

    Implementation-relevant quantities

This creates a nice distinction:

Chapter 2: Why this split exists and what it contributes.

Chapter 3: Exactly how you use it mathematically.
3.5 Coupled thermoelastic/multiphase formulation

If the thermoelastic multiphase simulation is an important part of the thesis, introduce the relevant equations here.

Otherwise, if it is mainly an application demonstrating the model, keep the detailed formulation relatively short and put the application-specific setup in the Results chapter.
3.6 Numerical Implementation
3.6.1 Pace3D framework

Introduce Pace3D here rather than in the conclusion.

For example:

    Multiphysics simulation framework

    IAM-MMS

    Parallel architecture

    C implementation

    Relevant fracture/elasticity modules

    Position of the new implementation within the existing code

The fact that Pace3D has 600k+ lines of code is useful context, but I would not make the line count a major scientific point. The important point is the complexity and extensibility of the existing multiphysics framework.
3.6.2 Implementation of anisotropic elasticity

    Data structures/parameters

    Constitutive calculations

    Orientation handling

3.6.3 Implementation of the tension–compression split

    Algorithm

    Integration into the phase-field solver

    Interaction with energy degradation

3.6.4 Numerical algorithm

Provide a flowchart and/or pseudocode.

For example:

Initialize material and phase-field parameters
        ↓
Initialize anisotropic elastic properties
        ↓
Set material orientation
        ↓
Apply boundary conditions
        ↓
Calculate strain
        ↓
Calculate anisotropic stress
        ↓
Evaluate tensile/compressive split
        ↓
Calculate elastic energy contributions
        ↓
Update phase field
        ↓
Check convergence
        ↓
Next load/time step

A flowchart would probably be more useful than pseudocode alone.
4. Verification and Validation

I would strongly recommend separating verification from the fracture simulations.

Your first proposed result—no-crack elastic anisotropy—is fundamentally a verification test, not really a fracture result.
4.1 Verification of anisotropic elasticity
4.1.1 Analytical solution/reference relations

Define the analytical expectations for a homogeneous material under uniaxial strain.
4.1.2 Numerical setup

    Geometry

    Boundary conditions

    Material parameters

    χ

    θ

    Mesh/resolution

4.1.3 Stress response

Show:

    σ11 vs. anisotropy parameter

    σ22 vs. anisotropy parameter

    σ12 vs. anisotropy parameter

4.1.4 Influence of anisotropy parameter χ
4.1.5 Influence of material orientation θ
4.1.6 Comparison with analytical results

This is where you demonstrate that the implementation of anisotropic elasticity is correct before introducing cracks.

That's an important methodological point.
5. Fracture Results and Discussion

Now move into the actual scientific results.
5.1 Effect of the tension–compression split under compression
5.1.1 Isotropic crack resistance

Use the simplest configuration first.
5.1.2 Single-obstacle configuration

Explain the benchmark.
5.1.3 Compression test without tension–compression split

Show:

    Stress–strain response

    Phase-field evolution

    Crack path

5.1.4 Compression test with tension–compression split

Same outputs.
5.1.5 Comparison

This should directly demonstrate why the split matters.
5.2 Influence of Anisotropic Crack Resistance

Now isolate the effect of anisotropic crack resistance.
5.2.1 Single anisotropic obstacle

Define the setup.
5.2.2 Tension test

Investigate:

    Crack morphology

    Crack path

    Stress–strain response

5.2.3 Influence of anisotropy parameter χ
5.2.4 Influence of orientation θ

If relevant, combine these into a systematic parameter study rather than showing isolated cases.
5.3 Coupling Anisotropic Elasticity and Anisotropic Crack Resistance

This is probably the scientifically most important results section.

Compare:
Case A

Isotropic elasticity + anisotropic crack resistance
Case B

Transverse-anisotropic elasticity + anisotropic crack resistance

Then examine:

    Crack path

    Crack morphology

    Stress–strain response

    Influence of χ

    Influence of material orientation

This demonstrates why implementing anisotropic elasticity + anisotropic tension–compression splitting is more than simply adding another material parameter.
5.4 Tension versus Compression in the Fully Anisotropic Model

Now perform the direct comparison:

    Tension

    Compression

    With anisotropic elasticity

    With anisotropic crack resistance

    With the new tension–compression split

Focus on whether the model gives physically distinct behavior under tensile and compressive loading.

This section essentially brings together everything developed in the thesis.
5.5 Application: Thermoelastic Fracture in a Multiphase System

This is an excellent final results section because it demonstrates that the development is not merely a benchmark exercise.
5.5.1 Physical motivation

Why thermoelastic fracture in a multiphase material matters.
5.5.2 Model and simulation setup

    Phases

    Elastic properties

    Thermal properties

    Interface properties

    Crack properties

    Thermal loading

5.5.3 Results

    Temperature distribution

    Stress distribution

    Phase-field/crack evolution

    Interaction between phases and cracks

5.5.4 Discussion

Explain what the anisotropic formulation enables that the previous implementation could not represent.
5.6 Extended Anisotropy Studies — Optional

I would not promise these in the main thesis structure unless you already know you will do them.

Potential extensions:

    Orthotropic elasticity

    Cubic anisotropy

    Triclinic anisotropy

These could be a short section if results are strong, but otherwise belong in Outlook, not Results.
6. Conclusions and Outlook
6.1 Summary of the work

Briefly return to the objectives from Chapter 1.

For example:

    Anisotropic elasticity implemented.

    New anisotropic tension–compression split implemented in Pace3D.

    Implementation verified against analytical elastic relations.

    Fracture benchmark cases used for validation.

    Influence of anisotropy and orientation investigated.

    Thermoelastic multiphase application demonstrated.

6.2 Main findings

Rather than simply saying "take-home messages," explicitly state 3–5 findings.

For example:

    The implemented constitutive formulation reproduces the expected analytical response for transverse-anisotropic elasticity.

    The tension–compression split prevents inappropriate degradation of the compressive elastic response.

    Material anisotropy and material orientation affect both the mechanical response and fracture evolution.

    The combination of anisotropic elasticity and anisotropic crack resistance provides a framework for modeling fracture in anisotropic materials within Pace3D.

    The implementation extends the existing capabilities of Pace3D toward more physically realistic fracture simulations.

These should be findings supported by your results, rather than broad claims made before the simulations establish them.
6.3 Limitations

I strongly recommend adding this section.

Potential points:

    Restriction to transverse anisotropy

    Linear elasticity

    Assumptions of the phase-field model

    Mesh/resolution requirements

    Parameter identification

    Limitations of the tension–compression criterion

    Computational cost

A thesis becomes much stronger when it explicitly says what the model does not address.
6.4 Outlook

Then discuss extensions:
Mechanical

    Plasticity

    Large deformation

    More general anisotropy: orthotropic, cubic, triclinic

Multiphysics

    Thermal effects

    Chemical effects

    Thermo-chemo-mechanical coupling

Applications

    Battery electrodes, which can exhibit anisotropic elastic properties

    Composite materials

    Layered materials

    Biological materials, if relevant

Computational

    Parallel performance

    Larger three-dimensional simulations

    Parameter studies

    Coupling with additional Pace3D physics

The Overall Story of the Thesis

I think the most important improvement is to make the thesis follow this chain:

Fracture
   ↓
Why phase-field fracture?
   ↓
Why tension–compression splitting?
   ↓
What existing splits exist?
   ↓
Why are they insufficient for anisotropic elasticity?
   ↓
What does the new anisotropic split provide?
   ↓
What is the mathematical model?
   ↓
How was it implemented in Pace3D?
   ↓
Does the implementation reproduce known analytical behavior?
   ↓
Does the split behave correctly under compression?
   ↓
How do anisotropic elasticity + anisotropic fracture resistance interact?
   ↓
Can the model handle a realistic multiphysics application?
   ↓
What has been enabled and what remains to be done?

That gives you a much stronger thesis narrative than organizing the Results primarily around individual parameter combinations.
Recommended final table of contents

A clean final structure could therefore be:

    Introduction

        Motivation

        Research problem

        Objectives and scope

        Thesis outline

    Theoretical Background and Literature Review

        Fundamentals of fracture mechanics

        Phase-field fracture

        Anisotropic crack resistance

        Tension–compression splitting

        Existing split formulations

        New anisotropic tension–compression split

        Research gap and thesis contribution

    Mathematical Model and Numerical Methods

        Phase-field fracture model

        Anisotropic crack resistance

        Transverse-anisotropic elasticity

        Anisotropic tension–compression split

        Thermoelastic/multiphase formulation

        Pace3D

        Numerical implementation

        Algorithm and pseudocode

    Verification and Validation

        Verification of anisotropic elasticity

        Analytical comparison

        Influence of anisotropy parameter

        Influence of orientation

        Fracture benchmark for tension–compression splitting

    Results and Discussion

        Compression with/without tension–compression split

        Anisotropic crack resistance

        Coupled anisotropic elasticity and crack resistance

        Tension vs. compression

        Thermoelastic fracture in a multiphase system

        Extended anisotropy studies, if applicable

    Conclusions and Outlook

        Summary of contributions

        Main findings

        Limitations

        Outlook and future applications

One further recommendation

I would avoid putting "Literature Review" and "Methods" too close together conceptually. Your key contribution is the new anisotropic tension–compression split, so the reader should encounter it first as a problem and literature gap in Chapter 2, and then encounter its full mathematical implementation in Chapter 3.

That distinction—"What is the problem and why is this formulation needed?" → "Here is
