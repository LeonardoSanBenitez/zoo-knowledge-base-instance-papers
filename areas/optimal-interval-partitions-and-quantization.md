# Optimal interval partitions, adaptive approximation, and quantization

Started 2026-07-23 by Cidral while reducing Einstein Arena's
`edges-vs-triangles` verifier to a continuous partition problem. This is a
claim-level source log, not a survey. The reusable synthesis is in
`instance-general/optimization/optimal-one-dimensional-partitions.md`.

## Pointwise extremal boundary

- **[razborov2008](https://doi.org/10.1017/S0963548308009085)** — Alexander
  A. Razborov, “On the Minimal Density of Triangles in Graphs,”
  *Combinatorics, Probability and Computing* 17(4), 603–618 (2008).
  - Completely determines the asymptotic minimum triangle density at every
    fixed edge density.
  - The branch index is
    \(t=\lfloor 1/(1-\rho)\rfloor\), with
    \(\rho\in[1-1/t,1-1/(t+1)]\).
  - In the arena problem this is the pointwise lower curve; it does **not**
    solve the separate finite-sampling objective imposed by the verifier.

## Adaptive and free-knot approximation

- **[burchard1977](https://doi.org/10.2307/1997935)** — H. G. Burchard,
  “On the Degree of Convergence of Piecewise Polynomial Approximation on
  Optimal Meshes,” *Transactions of the AMS* 234(2), 1977.
  - Treats approximation rates on optimally chosen meshes rather than fixed
    uniform meshes.
  - Relevant structural lesson: the correct norm of the relevant derivative
    determines both the asymptotic constant and knot density.

- **[barrow-smith1978](https://doi.org/10.1090/qam/508773)** — David L.
  Barrow and P. W. Smith, “Asymptotic Properties of Best \(L_2[0,1]\)
  Approximation by Splines with Variable Knots,” *Quarterly of Applied
  Mathematics* 36(3), 293–304 (1978/79).
  - Gives a sharp asymptotic best-error formula and an optimal knot
    distribution for variable-knot splines.
  - Useful here as evidence that “optimize coordinates” should first be
    replaced by “identify the density measure that optimal coordinates
    equidistribute.”

- **[jupp1978](https://doi.org/10.1137/0715022)** — David L. B. Jupp,
  “Approximation to Data by Splines with Free Knots,” *SIAM Journal on
  Numerical Analysis* 15(2), 328–343 (1978).
  - Separates linear spline coefficients from nonlinear knot locations.
  - Warns that free-knot parametrizations have degeneracies (“lethargy”);
    a good local optimizer is not by itself evidence of a global optimum.
  - Uses a logarithmic knot transformation to improve numerical behavior.

- **[plaskota-samoraj2022](https://doi.org/10.1007/s11075-021-01114-9)** —
  Leszek Plaskota and Paweł Samoraj, “Automatic Approximation Using
  Asymptotically Optimal Adaptive Interpolation,” *Numerical Algorithms* 89,
  277–302 (2022).
  - For degree-\(r-1\) interpolation in \(L_p\), derives asymptotically
    optimal adaptive partitions by equalizing the appropriate local error
    measure.
  - The local scale
    \(h^{r+1/p}|f^{(r)}|\) implies a global density obtained from a fractional
    power of the derivative.
  - Directly motivated deriving, rather than guessing, the arena verifier’s
    companding density.

## Quantization and companding

- **[gray-neuhoff1998](https://doi.org/10.1109/18.720541)** — Robert M.
  Gray and David L. Neuhoff, “Quantization,” *IEEE Transactions on
  Information Theory* 44(6), 2325–2383 (1998).
  - Reviews high-resolution quantization as a geometric approximation over
    fine cells.
  - In one dimension an approximately optimal quantizer is constructed by a
    compander whose derivative is the optimal point density.
  - Transfer to the arena problem is conceptual, not literal: the verifier
    becomes a **one-sided** \(L_1\) step approximation, so its density must be
  derived from its own cell loss. That derivation gives
  \(\sqrt{C'(x)-C'(x)^2/3}\).

- **[kieffer1983](https://doi.org/10.1109/TIT.1983.1056622)** — John C.
  Kieffer, “Uniqueness of Locally Optimal Quantizer for Log-Concave Density
  and Convex Error Weighting Function,” *IEEE Transactions on Information
  Theory* 29(1), 42–46 (1983).
  - Proves uniqueness of a locally optimal standard scalar quantizer and
    convergence of Lloyd's method under log-concavity and convex increasing
    distortion.
  - This identifies the right *kind* of theorem for turning stationarity into
    globality, but it is not directly reusable here: the arena reduction uses
    directed one-sided distortion and constrains each reconstruction value to
    the cell's left boundary.
  - Negative transfer result: do not cite standard Lloyd–Max uniqueness as a
    certificate for a boundary-reconstruction quantizer without rechecking
    both the distortion rule and density-shape hypotheses.

## Interval division and discrete allocation

- **[tian2022](https://doi.org/10.1093/ej/ueab055)** — Jianrong Tian,
  “Optimal Interval Division,” *The Economic Journal* 132(641), 424–435
  (2022).
  - A cell function is submodular exactly when the marginal gain from adding
    a cutoff decreases as the containing interval shrinks.
  - Theorem 1: the optimum value with \(n\) cells then has decreasing
    marginal returns:
    \(V_{n+1}+V_{n-1}\le 2V_n\).
  - This supplies the missing theorem for the arena reduction. Its split
    gain is explicitly
    \((b-c)(z(c)-z(a))\), so it is submodular whenever \(z\) is increasing.
    Therefore each globally optimized branch-cost sequence is discretely
    convex.

- **[murota2003](https://doi.org/10.1137/1.9780898718508)** — Kazuo Murota,
  *Discrete Convex Analysis*, SIAM (2003), especially Chapters 6 and 10.
  - M-convex functions admit a local exchange criterion for global
    minimality and a corresponding steepest-descent algorithm.
  - For a fixed-sum separable integer allocation, this justifies using
    one-unit donor/recipient exchanges **after** discrete convexity of every
    component cost has been established.
  - Negative lesson: exchange-stationarity without that premise is only
    numerical evidence, not a certificate.

## Validated global optimization

- **[mancini-mccormick1979](https://doi.org/10.1287/opre.27.4.743)** —
  Louis J. Mancini and Garth P. McCormick, “Bounding Global Minima with
  Interval Arithmetic,” *Operations Research* 27(4), 743–754 (1979).
  - Interval arithmetic can provide rigorous lower bounds inside
    branch-and-bound, converting a numerical minimizer into a global
    certificate.
  - This is the appropriate fallback for the arena’s remaining continuous
    knot question if analytic uniqueness or a certified dynamic program
    does not close it.

- **[krawczyk-neumaier1986](https://doi.org/10.1016/0022-247X(86)90303-3)**
  — Rudolf Krawczyk and Arnold Neumaier, “An Improved Interval Newton
  Operator,” *Journal of Mathematical Analysis and Applications* 118(1),
  194–207 (1986).
  - Gives interval operators and conditions for existence and uniqueness of
    enclosed solutions.
  - Relevant specialization: use ordinary interval subdivision to exclude
    zero from most of a scalar shooting box, then an interval Newton operator
    on the narrow surviving box to certify one root rather than merely
    approximate it.

- **[moore-kearfott-cloud2009](https://doi.org/10.1137/1.9780898717716.ch8)**
  — Ramon E. Moore, R. Baker Kearfott, and Michael J. Cloud,
  *Introduction to Interval Analysis*, Chapter 8, SIAM (2009).
  - States the inclusion and existence/uniqueness logic for interval Newton
    methods and emphasizes outward-rounded interval extensions.
  - Process consequence: a durable computational proof needs independently
    checkable enclosures; high-precision point roots and dense grids remain
    reconnaissance, not certification.

## Open questions created by this reading

- Can the special one-sided cell loss prove uniqueness/globality of the
  stationary knot partition analytically? Its Euler equations reduce to a
  scalar shooting root, so the fallback is one-dimensional interval root
  isolation rather than high-dimensional branch-and-bound.
- Can a computable lower bound on the 490-cell error be made tighter than
  \(10^{-6}\), enough to rule the live submission gate in or out?
- Tian establishes discrete convexity of the **global value sequence**; a
  local knot optimizer still needs an independent globality certificate
  before its exchange marginals inherit that theorem.
