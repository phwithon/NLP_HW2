# Hypothesis decisions

## Qwen2.5-1.5B / neutral

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +74.2 [65.8, 81.7] pp -> supported; H2 near-far = +17.5 [10.0, 25.8] pp -> supported
- metric: H1 Delta_near = +6.7 [2.5, 11.7] pp -> supported; H2 near-far = +6.7 [2.5, 11.7] pp -> supported
- entity: H1 Delta_near = +85.0 [78.3, 90.8] pp -> supported; H2 near-far = +25.0 [17.5, 32.5] pp -> supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +74.2 [65.8, 81.7] pp -> supported; H2 near-far = +17.5 [10.0, 25.8] pp -> supported
- metric: H1 Delta_near = +6.7 [2.5, 11.7] pp -> supported; H2 near-far = +6.7 [2.5, 11.7] pp -> supported
- entity: H1 Delta_near = +85.0 [78.3, 90.8] pp -> supported; H2 near-far = +25.0 [17.5, 32.5] pp -> supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero

## Qwen2.5-1.5B / instructed

ANS accuracy 98.3% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +33.3 [25.0, 41.7] pp -> supported; H2 near-far = +19.2 [11.7, 26.7] pp -> supported
- metric: H1 Delta_near = +0.8 [0.0, 2.5] pp -> not supported; H2 near-far = +0.8 [0.0, 2.5] pp -> not supported
- entity: H1 Delta_near = +53.3 [44.2, 62.5] pp -> supported; H2 near-far = +30.0 [21.7, 38.3] pp -> supported
- scope: H1 Delta_near = +88.3 [82.5, 93.3] pp -> supported; H2 near-far = -7.5 [-12.5, -3.3] pp -> reversed

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +33.3 [25.0, 41.7] pp -> supported; H2 near-far = +19.2 [11.7, 26.7] pp -> supported
- metric: H1 Delta_near = +0.8 [0.0, 2.5] pp -> not supported; H2 near-far = +0.8 [0.0, 2.5] pp -> not supported
- entity: H1 Delta_near = +53.3 [44.2, 62.5] pp -> supported; H2 near-far = +30.0 [21.7, 38.3] pp -> supported
- scope: H1 Delta_near = +88.3 [82.5, 93.3] pp -> supported; H2 near-far = -7.5 [-12.5, -3.3] pp -> reversed

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero

## Qwen2.5-3B / neutral

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +6.7 [2.5, 11.7] pp -> supported; H2 near-far = -1.7 [-7.5, 5.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +10.0 [5.0, 15.8] pp -> supported; H2 near-far = +10.0 [5.0, 15.8] pp -> supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = +14.2 [8.3, 20.8] pp -> supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +6.7 [2.5, 11.7] pp -> supported; H2 near-far = -1.7 [-7.5, 5.0] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +10.0 [5.0, 15.8] pp -> supported; H2 near-far = +10.0 [5.0, 15.8] pp -> supported
- scope: H1 Delta_near = +100.0 [100.0, 100.0] pp -> supported; H2 near-far = +14.2 [8.3, 20.8] pp -> supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero

## Qwen2.5-3B / instructed

ANS accuracy 100.0% (interpretable)

Baseline IRR (primary):
- period: H1 Delta_near = +0.8 [0.0, 2.5] pp -> not supported; H2 near-far = -0.8 [-3.3, 1.7] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +4.2 [0.8, 8.3] pp -> supported; H2 near-far = +4.2 [0.8, 8.3] pp -> supported
- scope: H1 Delta_near = +94.2 [89.2, 98.3] pp -> supported; H2 near-far = +30.8 [21.7, 39.2] pp -> supported

Baseline IRR_usd (robustness):
- period: H1 Delta_near = +0.8 [0.0, 2.5] pp -> not supported; H2 near-far = -0.8 [-3.3, 1.7] pp -> not supported
- metric: H1 Delta_near = 0.0 [0.0, 0.0] pp -> not supported; H2 near-far = 0.0 [0.0, 0.0] pp -> not supported
- entity: H1 Delta_near = +4.2 [0.8, 8.3] pp -> supported; H2 near-far = +4.2 [0.8, 8.3] pp -> supported
- scope: H1 Delta_near = +94.2 [89.2, 98.3] pp -> supported; H2 near-far = +30.8 [21.7, 39.2] pp -> supported

Presence baselines: substitution IRR 0.0%, IRR_usd 0.0% -> IRR, IRR_usd at floor: Delta equals the raw near-miss substitution rate, and the surface-form contrast cannot be estimated
Surface form (IRR_usd - IRR) = 0.0 [0.0, 0.0] pp -> CI includes zero
