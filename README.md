# Entangled quantum sensor networks + Kalman filtering

Tracking a time-varying field with a network of quantum sensors that can share entanglement. A Kalman filter estimates the field and its error covariance; the error covariance decides how long each measurement lasts and, together with the supply of entanglement, which sensors to entangle and when.

用可以共享 entanglement 的 quantum sensor 网络跟踪一个随时间变化的场。Kalman filter 估计场和 error covariance；error covariance 决定每次测量的时长，并和 entanglement 的供给一起决定何时、纠缠哪些 sensors。

## Status: stopped / 状态：已停止

Exploratory notes for a whitepaper direction, November 2026, stopped on 2026-11-14. The toy models found real gains, but each gain is either already known or disappears under a fair benchmark. Numbers come from simplified models; see the "核对深度" section of each analysis for what was and was not checked.

1. **Toy model 1** (one mode, k single-qubit sensors). Network GHZ doubles the MSE exponent ($k^{-1/3}\to k^{-2/3}$), but at k = 2, 3, 4 the MSE is only 11%, 19%, 26% lower. The model is the same as local-oscillator locking in atomic clocks, so the result is known. Tracking a gradient under common-mode noise: unentangled MSE is up to 2.6× higher, the time-varying version of correlation spectroscopy (Nichol et al., Nature 2022).
2. **Toy model 2** (two tracked modes, rate-limited Bell pairs). Entanglement does not add information; it moves information from one mode to the other. Scheduling is necessary (eager use is 2.6× worse than no entanglement; scheduled use is 21–24% better at ρ = 1000 and gives nothing at ρ ≤ 10), but a one-parameter offline schedule is within 1% of the optimum. Online covariance feedback on which sensors to entangle and when adds nothing, so the original claim "the error covariance decides online which sensors to entangle" does not hold.
3. **Toy model 3** (one target mode, strong fast disturbance modes). The gain is set by how many disturbance modes must be cancelled: about 2× for a gradient, 14× for curvature (k = 4, ρ → ∞; 2.3× at ρ = 10). The four-ion GHZ pattern that cancels the uniform field and the gradient is in Megidish et al., PRL 122, 123605 (2019). No platform was found that meets all four conditions: individual readout is forced, only quantum sensors can be used, the target is a higher-order spatial mode, and the low-order disturbance is fast and strong.
4. **Toy model 4** (n qubits per node). When the benchmark may use local entanglement, the network gain does not grow with n: curvature 14× (n = 1), 5.0× (n = 2), about 2.9× (n ≥ 6); gradient 2.4× to 2.0×. When a node holds more qubits than the dephasing-limited GHZ size, the gain goes to 1. Unentangled nodes with about 3 (gradient) or 5–6 (curvature) qubits each beat single-qubit nodes with network GHZ. The remaining 2–3× is the static factor known from Kómár et al. 2014, Proctor et al. 2018, Gessner et al. 2020 and Zhang et al. 2026.

**Conclusion.** Where nodes can hold several qubits, multi-qubit-node sensing is mature and network entanglement adds only the known static factor. Single-qubit-node networks matter only where node size is physically forced, and the platforms where it is forced lack the fast higher-order disturbance that the large gains need. The Kalman filter contributes no advantage of its own: every gain comes from the entangled state, and every allocation rule found is offline.

2026 年 11 月为 whitepaper 方向做的探索笔记，2026-11-14 停止。Toy models 找到了真实的增益，但每一项要么已有文献，要么在公平的 benchmark 下消失。数字来自简化模型，各分析的 "核对深度" 一节说明了核对了什么。

1. **Toy model 1**（一个 mode，k 个单 qubit sensors）。Network GHZ 使 MSE 的指数加倍（$k^{-1/3}\to k^{-2/3}$），但 k = 2, 3, 4 时 MSE 只低 11%、19%、26%。模型与 atomic clock 的 local-oscillator 锁定相同，结论已知。Common-mode 噪声下跟踪 gradient：不纠缠的 MSE 最高是 2.6 倍，是 correlation spectroscopy（Nichol et al., Nature 2022）的时变版本。
2. **Toy model 2**（两个 mode 都要跟踪，Bell pairs 限速供给）。Entanglement 不增加 information，只把它从一个 mode 移到另一个。调度是必需的（pair 一到就用比不纠缠差 2.6 倍；调度后 ρ = 1000 时好 21–24%，ρ ≤ 10 时没有增益），但一个参数的离线规则与最优解相差不到 1%。在线用 covariance 决定纠缠哪些 sensors、何时纠缠没有增益，所以原来的 "error covariance 在线决定纠缠哪些 sensors" 不成立。
3. **Toy model 3**（一个 target mode，强而快的 disturbance modes）。增益由需要抵消的 disturbance mode 个数决定：gradient 约 2 倍，curvature 14 倍（k = 4，ρ → ∞；ρ = 10 时 2.3 倍）。抵消均匀场和 gradient 的四离子 GHZ 已见于 Megidish et al., PRL 122, 123605 (2019)。没有找到同时满足四个条件的平台：必须单独读出、只能用 quantum sensors、target 是高阶空间 mode、低阶 disturbance 快而强。
4. **Toy model 4**（每个 node n 个 qubits）。Benchmark 允许局部纠缠时，网络纠缠的增益不随 n 增长：curvature 从 14 倍（n = 1）降到 5.0 倍（n = 2）、约 2.9 倍（n ≥ 6）；gradient 从 2.4 倍降到 2.0 倍。Node 的 qubit 数超过 dephasing 限制的 GHZ 大小时，增益趋于 1。每个 node 约 3 个（gradient）或 5–6 个（curvature）不纠缠的 qubits 就胜过单 qubit node 加 network GHZ。剩下的 2–3 倍是 Kómár et al. 2014、Proctor et al. 2018、Gessner et al. 2020、Zhang et al. 2026 已知的静态因子。

**结论。** Node 能放多个 qubits 时，多 qubit node 的 sensing 已经成熟，网络纠缠只增加已知的静态因子。单 qubit node 网络只在 node 大小受物理限制时有意义，而这些平台缺少大增益所需的快速高阶 disturbance。Kalman filter 本身不带来优势：所有增益都来自 entangled state，找到的分配规则都是离线的。

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
| `toy_model_A/toy5_multiqubit_nodes_zh.md` | Toy model 4: several qubits per node, local vs network entanglement; when network entanglement still pays, related work |
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
