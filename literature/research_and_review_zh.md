# Quantum sensing 与 distributed estimation：文献调研及 Claude A 审阅

调研日期：2026-11-09。范围包括用户提出的 quantum sensing 联系、Ji Liu publication list，以及 `claude_new_directions_zh.md` 的方向 A。三位独立 agent 分别检查 sensing prior art、Ji Liu 算法接口与 novelty/物理模型，本文汇总核查结果。没有修改 whitepaper 主文。

## 结论

**保留 A，改写为“面向动态场 tracking 的 entanglement scheduling”。评分为创新性 3/5、重要性 4/5、可行性 3/5。**

具体问题是：网络根据当前 estimation uncertainty、可用 entangled links 及其 memory age，决定继续生成 entanglement、立即用 separable probes 测量，或消耗现有 entanglement 测量某个 field mode；在固定物理资源和总时间下，最小化长期 causal tracking MSE。

现有文献已经覆盖 quantum Kalman filtering、动态 quantum sensing、GHZ grouping、entanglement generation stopping，以及 RL sensing allocation。当前可研究的差别是 **stochastic field dynamics 与随机 entanglement supply 共同决定 measurement timing 和 tracking loss**。本轮未找到完整对应的直接论文。

与 Ji Liu 最直接的 estimation 接口是 **Split-Spectrum Based Distributed State Estimation for Linear Systems**。该接口在多维场、local unobservability、neighbor-only communication 时才有实质作用。Claude 的 scalar scheduling 首步主要涉及资源控制和 scalar filtering。

## 已有工作与研究边界

| Primary source | 已有结果 | 对本方向的影响 |
|---|---|---|
| Geremia et al., *Quantum Kalman Filtering and the Heisenberg Limit in Atomic Magnetometry* (2003), [论文](https://arxiv.org/abs/quant-ph/0306192)；Amorós-Binefa–Kołodyński, *Noisy atomic magnetometry in real time* (2021), [论文](https://doi.org/10.1088/1367-2630/ac3b71) | continuous quantum measurement 与 Kalman estimation 已有直接结合；2021 工作包含随机磁场与 decoherence。 | Kalman 用于 quantum sensing 本身已经成立。 |
| Amorós-Binefa et al., *Tracking time-varying signals with quantum-enhanced atomic magnetometers* (2025), [论文](https://arxiv.org/abs/2503.14793)；Duan et al., *Concurrent spin squeezing and field tracking with machine learning* (2025), [实验](https://www.nature.com/articles/s41567-025-02855-3) | 前者研究 quantum-enhanced fluctuating-field tracking；后者实验结合 continuous squeezing 与时变磁场跟踪。 | 动态 tracking 与 quantum enhancement 已有理论、数值及实验工作。 |
| Guo et al., *Distributed quantum sensing in a continuous-variable entangled network* (2020), [论文](https://arxiv.org/abs/1905.09408) | four-mode continuous-variable entangled optical network 估计 average phase。 | 支持 distributed sensing 的 metrological advantage；它不是 GHZ + Kalman 实验。 |
| Van Milligen et al., *Utilizing probabilistic entanglement between sensors in quantum networks*, PR Applied 22, 064085 (2024), [正文](https://arxiv.org/html/2407.15652v1) | probabilistic star network；比较立即测量、固定等待、达到 link 数门槛后停止；优化每时隙 QFI、GHZ partition、distillation；等待期间可做 separable sensing。 | 生成等待、停止规则、cluster size 已被研究。该文尚未处理 stochastic hidden field 的 recursive tracking，memory decoherence 留作后续。 |
| Zang et al., *Quantum Advantage in Distributed Sensing with Noisy Quantum Networks*, PR Research 8, 033040 (2026), [v5 正文](https://arxiv.org/html/2409.17089v5) | GHZ-diagonal probes、local errors、encoding dephasing、interrogation-time optimization；网络仿真包含 memory aging 和通信延迟。 | 不能把 decoherence、latency 或 sensing-time optimization 本身称作新问题；该文未建立时变 hidden field 的 recursive filter。 |
| Nikoloska et al., *Adaptive Bayesian Single-Shot Quantum Sensing* (2025), [正文](https://arxiv.org/html/2507.16477v1) | 多 quantum agents 的 PQC/POVM 优化、local Bayesian models 与 inverse-variance fusion。 | 多 agent Bayesian fusion 已有。其独立估计融合、训练时真实参数反馈，与无标签、neighbor-only online filtering 有区别。 |
| Nehra et al., *Dynamic distributed quantum sensing of radio-frequency fields via time-bin entanglement* (2026 preprint), [论文](https://arxiv.org/abs/2609.39831) | time-bin entanglement 实现二时刻差分采样，将动态 RF phase 映射为光学相位。 | “已有动态工作都只有一个 sensor”不成立；该工作也没有解决这里的资源调度与 causal recursive filtering。 |
| Kazemi Taskooh et al., *Entanglement Allocation for Quantum Integrated Sensing and Communication* (2026-11-03 preprint), [正文](https://arxiv.org/html/2611.04128v1) | Bell-pair allocation、多个 GHZ cluster 的大小和节点分配、fusion/loss/memory 模型、HC-PPO。§II-D 明确参数在完整 horizon 内固定，跨时隙 QFI 相加。 | 是 A 必须加入的近邻。“RL + GHZ allocation”已有；可区分的是持续变化的目标与 causal tracking loss。 |
| Rahman et al., *Adaptive noise-mitigated distributed variational quantum sensing with federated learning*, PRA accepted 2026-11-03, [出版页](https://journals.aps.org/pra/accepted/10.1103/mphl-ky3z) | personalized federated sensing-circuit learning、Fisher-information objective、bandit 选择 dynamical decoupling。 | 泛称 federated sensing 或 bandit quantum control 不能作为独立新意。 |
| Petersen, *Time Averaged Consensus in a Direct Coupled Distributed Coherent Quantum Observer* (2015), [论文](https://arxiv.org/abs/1503.01457) | quantum harmonic-oscillator network 在 time-average 意义估计 quantum plant observable。 | coherent quantum distributed observer 也已有；它与经典场的 quantum readout fusion 是不同任务。 |

另核查 Iyer–Iyengar 的 [Quantum-Enhanced Distributed Sensor Fusion (2026 preprint)](https://arxiv.org/abs/2605.19327)，其 §5.3 已给出简化的 scalar Kalman fusion。它没有本题的 entanglement inventory/stopping 或 locally unobservable neighbor network。独立审阅发现其一处 QFI-to-error bound 推导的倒数/凸性方向需要重新检查，本文不采用其 claimed bounds。

## Claude A 中需要修正的论证

### 1. 理想 GHZ 精度不能直接成为 Kalman measurement covariance

在每节点一个 qubit、相同 interrogation duration、局部参数可辨识的理想模型下，GHZ 对 arithmetic mean 的 Fisher information 随 k² 增长，separable probes 随 k 增长。真正的 parity readout 是 Bernoulli measurement。以已吸收耦合常数的场为例，

\[
p(m\mid x(\cdot),a)=\frac12\left[1+(-1)^m V_a\cos\left(\sum_{i\in S_a}\int_{t_a}^{t_a+\tau_a} B_i(s)\,ds+\phi_a\right)\right].
\]

其中 S_a 是所用 sensor subset，V_a 是包括备态和 sensing noise 的 visibility，φ_a 是可控 measurement phase。锁定工作点并在合适重复采样条件下，才可得到近似 Gaussian observation。局部静态、相同 field、ν 次重复时的有效方差量级是

\[
r_a\sim\frac{1}{\nu k^2\tau_a^2V_a^2}.
\]

对变化较快的场，观测对应一个时间积分；需将其与 process noise 的相关性纳入 filter。一般 regime 可先用 Bayesian/particle filter，Kalman 作为有明确适用条件的近似。

### 2. 固定总资源后重新判断优势

固定 N 个节点，分成 N/k 个大小为 k 的 GHZ groups，且各组测同一 scalar field。理想总 FI 随 Nk 增长。不能只比较一个 k-node GHZ 与单个 sensor，也不能只让 entangled 策略优化 interrogation time。

一个必须覆盖的 benchmark 是独立 Markovian sensing dephasing。忽略 preparation overhead，并定义 coherence 为 exp(-kγτ)，则局部工作点的 FI rate 为

\[
\mathcal I_{\rm rate}(k,\tau)=Nk\tau e^{-2k\gamma\tau}.
\]

对 τ 优化，τ*=1/(2kγ)，最大 FI rate 为 N/(2eγ)，与 k 无关。这与 [Huelga et al., PRL 1997](https://arxiv.org/abs/quant-ph/9707014) 的 maximally entangled 与 uncorrelated Ramsey comparison 一致。该静态 benchmark 不证明动态 tracking 的全面 no-go，但足以说明理想 k² scaling 不能自动推出本题的优势。

因此应区分 memory decoherence 和 sensing dephasing，固定总 sensing qubits、wall-clock time、总 entanglement-generation capacity，并优化两侧的 sampling policy。研究 N-scaling 时，还需明确 generation capacity 是总量固定还是随 N 增加。

### 3. 定义目标与时序

- 若目标是所有节点共同感受的 scalar field x(t)，任意非零 sensitivity 节点已 locally observable。此时关键是 measurement timing、precision 与资源等待。
- 若目标是不同 local fields 的全网平均，一个 k-node GHZ 只编码其 subset 的场之和。应显式建模 spatial field 或多维 hidden state，再确定哪些 observations 足以恢复目标。
- 若先备态再让 probe 与 field 耦合，备态等待主要降低 sampling cadence。只有 interrogation interval 跨时段或结果延迟到达，才产生时间平均或过期 observation。
- 普通 GHZ 编码给出所选节点的相位和。更一般的 weighted linear functional 需要明确可用的 coupling、control 或组合测量。

### 4. 最小 Riccati calculation 是起点

给定确定周期 Δ 和 Gaussian observation variance r，random-walk field 的 process variance 为 qΔ。scalar steady-state posterior covariance 满足

\[
P=\frac{r(P+q\Delta)}{P+q\Delta+r},\qquad
P=\frac{\sqrt{(q\Delta)^2+4rq\Delta}-q\Delta}{2}.
\]

这是标准 Kalman recurrence 的代数结果。把 r(k)、Δ(k) 代入再扫描 k，可用于模型检查和 baseline。若关心整个时间段的 tracking，确定周期下的平均 prediction MSE 还包括 qΔ/2；只比较 measurement arrival 后的 P 会漏掉等待代价。

值得成为主要成果的是：随机 link generation 与 memory age 下，policy 如何依赖当前 posterior 决定继续等待或立即测量，以及何时 tracking-optimal policy 与 static-QFI-optimal policy 不同。可以先求小网络的 dynamic-programming policy，再研究 threshold structure、近似 policy 与大网络 scaling。RL 是扩展求解手段。

## Ji Liu 的工作怎样接入

身份已通过 [本人 publication list](https://sites.google.com/site/jiliucontrol/publication) 的 Scholar 链接核对为用户给定 ID 对应的 Stony Brook Ji Liu。

| 论文 | 具体接口 | 对 A 的位置 |
|---|---|---|
| Wang–Liu–Anderson–Morse, [Split-Spectrum Based Distributed State Estimation for Linear Systems](https://arxiv.org/html/2210.01232v2), Automatica 2024 | local observable subspace 用 measurement 更新，local unobservable subspace 由 neighbor estimates 补足；原理论是 deterministic observer convergence。 | **首选 estimation 基础。** 扩展到 noisy multimode field 与有限通信，研究 quantum sensing gain 在网络融合后能保留多少。 |
| Wang–Liu–Morse, [A Hybrid Observer for Estimating the State of a Distributed Linear System](https://arxiv.org/abs/2208.02936), Automatica 2022 | continuous local estimation 与每个 event interval 内有限次 distributed iteration。 | 适合处理 sensing interval 与 communication rounds 的配合。属于上项的另一种实现架构。 |
| Zeng–Zhang–Liu–Liu–Yang, [Multi-Entanglement Routing Design Over Quantum Networks Using Greenberger–Horne–Zeilinger Measurements](https://doi.org/10.1109/TON.2025.3608121) | n-fusion、网络 entanglement routing 与多对用户的 rate。 | 资源层基础。内部 GHZ-basis measurement 不等于最终交付任意 sensor subset 的 GHZ probe，需另定义 terminal set、state fidelity、heralding 与生成时间分布。 |
| Lin–Gupta–Liu, [Finite-Time Error Bounds for Distributed Linear Stochastic Approximation](https://arxiv.org/html/2111.12665v2) | geometrically mixing Markov samples、固定 equilibrium、共享 A(X_t) 的 linear SA 与 directed network。 | 可用于 noise/calibration parameter learning；其 theorem 不直接覆盖动态场 tracking。 |
| Zhang et al., [Distributed Learning of Average Belief over Networks Using Sequential Observations](https://arxiv.org/abs/1811.07799), Automatica 2020 | sequential local observations 与网络平均。 | 可借鉴 classical readout fusion；仅将 samples 换成 quantum shots 的新意较低。 |

一个明确的 multimode 起点是 x=[field offset, field gradient]ᵀ，x_{t+1}=ρIx_t+w_t，节点 i 的 field 为 B_i=[1,r_i]x_t。每个节点独自不能区分两个 modes，两个以上不同位置可共同观测。不同 probe subsets 提供不同的线性组合，需要同时考虑观测方向、entanglement 成本与邻居通信。

这一架构使用 quantum sensors 产生数据、classical distributed algorithms 融合数据。若要主张 quantum computational speedup，应另给计算瓶颈和量子子程序；低维 Kalman update 不构成合理的 VQLS/QLSA 应用动机。

## 推荐用于 whitepaper 的问题与评分

**问题。** 在具有随机 entanglement generation、有限 memory lifetime 和 classical communication delay 的 quantum sensor network 中，如何根据当前 posterior 与资源状态选择 probe grouping、measurement timing 和 sensing mode，使动态场的长期 causal tracking error 最小？在相同总资源下，哪些 signal/noise/network regimes 能保留相对 separable sensing 的精度优势，这种优势如何随节点数与通信预算变化？

| 候选范围 | 创新性 | 重要性 | 可行性 | 依据 |
|---|---:|---:|---:|---|
| 上述 tracking-driven entanglement scheduling | 3 | 4 | 3 | 近邻很多，posterior 与随机资源联合决策仍有明确问题；完整物理模型与优势验证有工作量。 |
| Split-spectrum 延伸到 multimode quantum readout 的 neighbor-only estimation | 3 | 4 | 4 | 接口直接，可先从 independent/locally squeezed probes 做起；需得到超出经典 filter 应用的资源—精度结果。 |
| 固定 r(k)、T(k) 的 scalar Kalman calculation | 1 | 2 | 5 | 可快速完成，用于 baseline 和检验，不足独立主方向。 |
| Average-belief 算法直接融合 quantum shots | 2 | 3 | 4 | 容易实现，主要是已有 classical method 的应用。 |
| 直接套用 RL 做 GHZ allocation / DD bandit | 1 | 3 | 4 | 已有直接量子 sensing 先例，需要新的目标、机制或保证。 |

评分均为 5 分制，属于选题判断，不是已完成实验的评价。A 与 whitepaper 的联系是 scalable quantum sensing protocol 和 resource management；如果 whitepaper 的范围严格限定 quantum computational algorithms，则需要明确扩展其研究范围。

## 检索与审阅记录

检索覆盖 quantum Kalman filtering、distributed quantum sensing 的 dynamic/waveform tracking、quantum sensor fusion、decentralized/jointly observable estimation、coherent quantum observer、GHZ resource scheduling，以及 Ji Liu 的 observer、SA、bandit、entanglement routing。按 primary paper 核对，区分预印本和已发表论文；没有将检索未命中写成首创证明。搜索返回的 synthetic research archive 未作为文献依据。

独立审阅一致建议保留 A 并收窄。最重要的修改是补充 2026 年 resource-allocation 近邻、从实际 parity likelihood 建模、固定总资源比较、将 scalar scheduling 与多维 distributed observer 分开，以及把 scalar Riccati sweep 定位为 baseline。
