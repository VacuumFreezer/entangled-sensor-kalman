# 在多个 quantum sensors 之间加 entanglement：已有工作

2026-11-10。接 [claude_direction_A_qa_zh.md](claude_direction_A_qa_zh.md)。回答两件事："关键创新点是在 sensors 之间加 entanglement、实现的还是 distributed Kalman filter"这个概括是否准确；有哪些工作已经在多个 sensors 之间加了 entanglement。

## 结论

1. 这个概括需要改两处。在 sensors 之间加 entanglement 是 distributed quantum sensing 这个领域的定义，不是 A 的创新点。A 也不只是一个 distributed Kalman filter，它在 filter 外面多了一层调度。
2. 在多个 sensors 之间加 entanglement 的理论从 2014 年开始，实验从 2010 年开始，已覆盖 photonic、atomic、ion、NV、optomechanical、superconducting 六类平台。
3. 这些工作有三个共同点：估计的参数是静态的；规模是 2 到 4 个节点；entanglement 是实验前准备好的固定 probe。A 的位置在这三点之外。

## 1　概括是否准确

**不准确，改成下面这样。**

- **已有的第一块：entangled sensor network。** 多个 sensors 共享 entanglement 来估计一个线性泛函，精度超过各自独立测量。见第 2、3 节。
- **已有的第二块：Kalman filter 跟踪时变场。** 都是单个 quantum sensor（Geremia 2003；Jiménez-Martínez 2018；Amorós-Binefa 2021、2025）。
- **A 的创新点：把两块闭环。** Filter 的 error covariance 决定下一步纠缠哪些节点、测多久、何时测；测量结果再更新 filter。目标是跟踪时变场，并回答精度优势随节点数、entanglement 生成速率如何变化。

Filter 的 time update 和 measurement update 公式不变。变化是每一步的 output matrix 和 measurement-noise variance 由调度决定，所以问题属于 sensor scheduling。是否 distributed 是次要的。

一句话：**entangled sensor network 已有，Kalman tracking 已有；我们做的是用 error covariance 在线调度稀缺的 entanglement 去跟踪时变场。**

## 2　理论：纠缠在哪些任务上有用

- **[Kómár et al., Nat. Phys. 2014](https://arxiv.org/abs/1310.6045)。** $K$ 个 atomic clocks 共享 GHZ，短 averaging time 内接近 Heisenberg limit。
- **[Eldredge et al., PRA 2018](https://arxiv.org/abs/1607.04646)。** 估计各节点参数的一个线性函数。给出这类非局域量的 Heisenberg limit，GHZ 协议达到该界。
- **[Proctor–Knott–Dunningham, PRL 2018](https://arxiv.org/abs/1707.06252)。** 估计各节点自己的 local parameters 时纠缠几乎没有用；估计 global property 时纠缠有用。
- **[Zhuang–Zhang–Shapiro, PRA 2018](https://arxiv.org/abs/1711.10459)。** Continuous-variable 版本：把一束 squeezed vacuum 用 beam-splitter array 分到 $M$ 个节点。RMS error 按 $1/M$ 下降，不纠缠时是 $1/\sqrt M$。有 loss 时 scaling 优势消失，中等 loss 下仍有常数因子的优势。
- **综述：[Zhang–Zhuang, Distributed quantum sensing, 2021](https://arxiv.org/abs/2010.14744)。**
- 后续理论（多个泛函、噪声、网络资源）已在 [claude_direction_A_qa_zh.md](claude_direction_A_qa_zh.md) 的表里：Bringewatt 2021、2024；Wölk–Sekatski–Dür 2020；Hamann 2025；Van Milligen 2024；Zang 2026；Kazemi Taskooh 2026。

## 3　实验

| 年份 | 工作 | 平台与规模 | 纠缠资源 | 估计的量 | 报告的结果 |
|---|---|---|---|---|---|
| 2010 | [Wasilewski et al., PRL](https://arxiv.org/abs/0907.2453) | 两个 Cs vapor cells，各自有 magnetic shield | 测量产生的 EPR entanglement | RF 磁场脉冲 | 只在脉冲短于 entanglement 寿命（约 4 ms）时有增益 |
| 2020 | [Guo et al., Nat. Phys.](https://arxiv.org/abs/1905.09408) | Photonic，4 个节点 | 4-mode continuous-variable entangled state | 4 个 phase 的平均 | 精度超过 separable probes |
| 2020 | [Xia et al., PRL](https://arxiv.org/abs/1910.08825) | RF-photonic，3 个节点 | 可重构的 continuous-variable multipartite entanglement | RF 场，例如 angle of arrival | 纠缠结构可按任务调整 |
| 2021 | [Liu et al., Nat. Photon.](https://arxiv.org/abs/2102.11679) | Photonic，6 个 entangled photons | Mode 和 particle 上的 entanglement | 单个 phase 和平均 phase | 最多低于 shot-noise limit 2.7 dB，加 multi-pass 后 4.7 dB |
| 2021 | [Zhao et al., PRX](https://arxiv.org/abs/2011.02807) | Photonic，2 个节点，光纤 240 m | Polarization-entangled photon pair | 两个 phase 的线性组合 | 低于 shot-noise limit 0.916 dB；加到 10 km 后没有优势 |
| 2022 | [Malia et al., Nature](https://arxiv.org/abs/2205.06382) | Atomic，最多 4 个 modes | Spin-squeezed 原子分到多个 modes | Clock 和 atom interferometer 的差分 phase | 作者报告比 projection noise limit 好 11.6 dB，比 locally squeezed 网络好 4.5 dB |
| 2022 | [Nichol et al., Nature](https://arxiv.org/abs/2111.10336) | 两个 Sr⁺ ion clocks，相距 2 m | Photonic link 产生的 Bell state | 两个 clock 的 frequency 差 | Uncertainty 降低约 $\sqrt2$ |
| 2023 | [Xia et al., Nat. Photon.](https://arxiv.org/abs/2210.16180) | 两个 optomechanical membranes | 分束后的 squeezed light | 两个 force 的平均 | Shot-noise floor 低 2 dB |
| 2024 | [Kim et al., Nat. Commun.](https://www.nature.com/articles/s41467-023-44204-z) | Photonic，4 个节点，距中心节点 3 km 光纤 | 2 个 polarization-entangled photons | 4 个 phase 的平均 | 比 SQL 好 2.2 dB |
| 2025 | [Kim et al., PRL](https://arxiv.org/abs/2508.02070) | Photonic，4 个 modes | Multi-mode N00N state | 两个 phase 的平均 | 比 SQL 好 2.74 dB |
| 2025 | [Bate et al., PRL](https://arxiv.org/abs/2501.08940) | 3 个 Ca⁺ ions，同一个 trap | Decoherence-free subspace 里的 GHZ 型态 | 磁场的 quadratic 分量 | RMSE 比 separable 协议小 2.6 倍 |
| 2025 | [Rovny–Kolkowitz–de Leon](https://arxiv.org/abs/2504.12533) | 两个 NV centers，相距约 6 nm | 两个 electron spins 的 entanglement | 磁场的两点 correlation | 常规 readout 下 SNR 提高一个量级以上；readout 完美时没有增益 |
| 2026 | [Li et al., Science](https://arxiv.org/abs/2504.08677) | 一团 spin-squeezed BEC 分成 2 到 3 份 | 各份之间的 entanglement | 各份 phase 的和与差，对应场的 mean 和 gradient | 两个参数同时低于 SQL 约 3.5 dB；不利用份间纠缠时是 1.3 dB |
| 2026 | [Zhang et al., Nat. Commun.](https://arxiv.org/abs/2412.18398) | Superconducting modules，用 25 cm cable 连接，2 个 sensor modules | 跨 module 的 Bell state 和 4-qubit GHZ 型态 | Vector field 的三个分量；两个方向的 gradient | Gradient 的总方差比只用 local entanglement 低 3.44 dB |

磁场相关的是 Wasilewski 2010、Bate 2025、Rovny 2025、Li 2026、Zhang 2026 五篇。

**对 Malia 2022 的质疑。** [McGuinness 的 Matters Arising 预印本](https://arxiv.org/abs/2302.00733) 认为该文的 projection noise benchmark 取错，数据不能证明原子之间有 entanglement。引用这篇的 4.5 dB 时要一并说明，或改用 Li 2026 和 Nichol 2022 作为 atomic 平台的证据。

## 4　共同点与空白

- **参数是静态的。** 表中每个实验估计的量在一次实验内固定。处理时变信号的 entangled network 只有理论工作：Kómár 2014、Hamann 2025、Nehra 2026。
- **规模小、距离短。** 节点数是 2 到 4。最远的是 3 km 光纤（Kim 2024）。原子类 sensors 之间跨装置的纠缠只有 Wasilewski 2010（两个 cell）和 Nichol 2022（2 m）。
- **Entanglement 是固定的 probe。** 没有实验根据估计结果在线决定纠缠哪些节点。最接近的是 Xia 2020：它展示了纠缠结构可以按任务重构，重构是每个任务做一次。
- **多节点 entanglement 仍然稀缺。** [Seubert et al. 2026（arXiv 2606.32006）](https://www.alphaxiv.org/abs/2606.32006) 在三个相距 30 到 40 m 的 single-atom 节点之间生成 GHZ：fidelity 77%，实际速率约每分钟 15 个，寿命约 200 μs。

对 A 有两点直接的用处：

- Wasilewski 2010 给出了一个早期的实验证据：纠缠的增益只出现在信号变化快于 entanglement 寿命的区间。这和此前 A/B 审阅（不在本 repo）1.1 节的优势窗口 $k\gamma\tau_c\lesssim1$ 是同一件事。
- Seubert 2026 的速率和寿命说明 entanglement 是要调度的稀缺资源，这是 A 的动机。

## 核对深度

- 表中每一行都核对了摘要。Wasilewski 2010、Zhao 2021、Xia 2023、Rovny 2025、Zhang 2026、Li 2026 核对了正文的相关部分。数字都来自这些摘录。
- Guo 2020 和 Xia 2020 的摘要没有给出增益数值，表中没有填。
- Li 2026 的期刊信息来自新闻稿（Science 391, 374, DOI 10.1126/science.adt2442）。Zhang 2026 的期刊信息来自检索结果里的 Nature Communications 链接，没有打开出版页确认。
- McGuinness 的质疑只读了摘录，没有核对它是否正式发表，也没有判断双方谁对。
