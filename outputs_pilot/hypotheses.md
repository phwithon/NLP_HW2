# Hypothesis decisions

## Qwen2.5-1.5B / neutral

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +75.0 [55.0, 95.0] pp -> supported; H2 near-far = +35.0 [15.0, 60.0] pp -> supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +90.0 [75.0, 100.0] pp -> supported; H2 near-far = +35.0 [15.0, 60.0] pp -> supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +75.0 [55.0, 95.0] pp -> supported; H2 near-far = +35.0 [15.0, 60.0] pp -> supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +90.0 [75.0, 100.0] pp -> supported; H2 near-far = +35.0 [15.0, 60.0] pp -> supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero

## Qwen2.5-1.5B / instructed

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +25.0 [10.0, 45.0] pp -> supported; H2 near-far = +10.0 [0.0, 25.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +50.0 [30.0, 70.1] pp -> supported; H2 near-far = +25.0 [10.0, 45.0] pp -> supported
- scope: H1 Delta_near = +95.0 [85.0, 100.0] pp -> supported; H2 near-far = -5.0 [-15.0, 0.0] pp -> not supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +25.0 [10.0, 45.0] pp -> supported; H2 near-far = +10.0 [0.0, 25.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +50.0 [30.0, 70.1] pp -> supported; H2 near-far = +25.0 [10.0, 45.0] pp -> supported
- scope: H1 Delta_near = +95.0 [85.0, 100.0] pp -> supported; H2 near-far = -5.0 [-15.0, 0.0] pp -> not supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero

## Qwen2.5-3B / neutral

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +5.0 [0.0, 15.0] pp -> not supported; H2 near-far = -5.0 [-15.0, 0.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +5.0 [0.0, 15.0] pp -> not supported; H2 near-far = +5.0 [0.0, 15.0] pp -> not supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = +10.0 [0.0, 25.0] pp -> not supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +5.0 [0.0, 15.0] pp -> not supported; H2 near-far = -5.0 [-15.0, 0.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +5.0 [0.0, 15.0] pp -> not supported; H2 near-far = +5.0 [0.0, 15.0] pp -> not supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = +10.0 [0.0, 25.0] pp -> not supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero

## Qwen2.5-3B / instructed

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = +25.0 [5.0, 45.0] pp -> supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = +25.0 [5.0, 45.0] pp -> supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero
