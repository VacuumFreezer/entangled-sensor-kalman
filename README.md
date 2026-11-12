# Entangled quantum sensor networks + Kalman filtering

Tracking a time-varying field with a network of quantum sensors that can share entanglement. A Kalman filter estimates the field and its error covariance; the error covariance decides how long each measurement lasts and, together with the supply of entanglement, which sensors to entangle and when.

用可以共享 entanglement 的 quantum sensor 网络跟踪一个随时间变化的场。Kalman filter 估计场和 error covariance；error covariance 决定每次测量的时长，并和 entanglement 的供给一起决定何时、纠缠哪些 sensors。

## Start here / 从这里开始

- [problem_formulation_en.md](problem_formulation_en.md) — introductory problem formulation, explains the Kalman filter from scratch and summarizes the two toy models.
- [problem_formulation_zh.md](problem_formulation_zh.md) — 同一内容的中文版。

## Contents / 目录

| Path | Content |
|---|---|
| `problem_formulation_en.md`, `problem_formulation_zh.md` | Problem formulation for readers new to Kalman filtering |
| `figures/` | Figures used only by the problem formulation, with the scripts that draw them |
| `toy_model_A/toy_model_analysis_zh.md` | Toy model 1: entangled vs unentangled sensors, one mode (k sensors on one field; gradient under common-mode noise) |
| `toy_model_A/toy3_scheduling_zh.md` | Toy model 2: scheduling rate-limited entanglement when two modes are tracked |
| `toy_model_A/toy4_nuisance_zh.md` | Toy model 3: k sensors, one target mode, strong fast disturbance modes; partial entanglement and allocation of a limited supply of Bell pairs |
| `toy_model_A/code/` | Simulation code (linear Kalman filter, dynamic programming, particle-filter simulation of binary outcomes) and saved results |
| `literature/` | Surveys of prior work: entangled sensor networks, Kalman filtering for quantum sensors, related allocation work (Chinese) |

## Reproduce / 复现

Python 3 with `numpy`, `scipy`, `matplotlib`.

```bash
cd toy_model_A/code
python make_figures.py      # figures 1-3 from saved results (res*.json)
python make_fig4.py         # figure 4
python run4.py              # example: rerun the main toy-model-1 simulations (several minutes)
```

The `run*.py` scripts regenerate the `res*.json` files; the 复现 section at the end of each analysis lists which script produces which result.

## Status / 状态

Exploratory notes for a whitepaper direction, November 2026. The toy-model numbers come from simplified models; see the "核对深度" sections of each analysis for what was and was not checked.
