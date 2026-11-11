# 方向 A 的三个问题：定位、磁场测量、无 entanglement 的网络

2026-11-10。回答三个问题。[research_and_review_zh.md](research_and_review_zh.md) 和此前的 A/B 审阅（不在本 repo）已列出的工作，这里只引用结论。核对深度见文末。

## 结论

1. A 可以概括为 quantum sensing + distributed Kalman filter，但按字面理解的这个组合已经有人做过。A 的新内容是 entanglement 让 measurement model 成为决策变量。带 entanglement scheduling 的版本，没有找到完全重合的工作。
2. 磁场测量是 quantum sensing 的标准问题。模型最简单，结论可以直接搬到其他物理量。选它不带来新意。
3. 不共享 entanglement 的 quantum sensor network 已有理论、实验和已部署的系统。它相对 classical sensors 的优势是单个器件的常数因子；精度随节点数的 scaling 与 classical 相同。

## 1　A 是不是 quantum sensing + distributed Kalman filter

### 1.1 回答

用 control 的语言，A 是下面这个问题：

$$x_{t+1}=Ax_t+w_t,\qquad y_t=c(S_t)^\top x_t+v_t,\qquad v_t\sim\mathcal N\big(0,\,r(S_t,T_t)\big).$$

- $x_t$ 是场的 modes，例如 offset 和 gradient。节点 $i$ 处的场值是 $h_i^\top x_t$。
- $S_t$ 是这一次纠缠在一起的节点集合，$k=|S_t|$；$T_t$ 是 interrogation time。
- 一个 GHZ probe 只读出 $S_t$ 内各节点场值的平均，所以 $c(S_t)=\frac1k\sum_{i\in S_t}h_i$。
- 理想情况下 $r\propto 1/(k^2T_t^2)$。
- 不纠缠时，同样的 $k$ 个节点给出 $k$ 个独立输出，合成同一个平均值的方差是 $1/(kT_t^2)$。
- $S_t$ 是否可用是随机的，取决于 entanglement generation，等待它要花时间。

所以纠缠是用 output matrix 的秩换一个方向上更低的 measurement noise。Output matrix 和 measurement-noise variance 都由调度决定，调度依赖 error covariance $P_t$。这是 sensor scheduling for Kalman filtering。Distributed fusion 只在节点多、经典通信受限时才成为约束。

"Quantum sensing + distributed Kalman filter" 这个说法里没有 entanglement。按字面理解，它是把 quantum sensors 当作噪声更小的 sensors，接进经典的 distributed Kalman filter。这个问题已有人做过（第 3 节），filter 理论没有变化。

建议的一句话表述：**quantum sensor network 上由 error covariance 驱动的 entanglement scheduling，用于时变场的 state estimation。**

### 1.2 类似工作

| 类别 | 代表工作 | 已覆盖 | 相对 A 缺什么 |
|---|---|---|---|
| 单个 quantum sensor + Kalman filter | [Geremia 2003](https://arxiv.org/abs/quant-ph/0306192)；[Jiménez-Martínez et al., PRL 2018](https://arxiv.org/abs/1707.08131)；[Amorós-Binefa–Kołodyński, NJP 2021](https://arxiv.org/abs/2103.12025)；[Amorós-Binefa et al. 2025](https://arxiv.org/abs/2503.14793)；[Wang et al. 2026](https://arxiv.org/abs/2605.17784)；综述 [Ma et al. 2022](https://mdpi.com/2073-8994/14/12/2478) | 时变磁场的 real-time tracking，以及 decoherence 下的 quantum limit | 只有一个 sensor |
| Entangled sensor network，静态参数 | [Proctor et al., PRL 2018](https://arxiv.org/abs/1707.06252)；[Bringewatt et al. 2021](https://arxiv.org/abs/2104.09540)、[2024](https://arxiv.org/abs/2401.16472)；[Bugalho–Omar–Markham 2026](https://arxiv.org/abs/2602.12193)；实验 [Malia et al. 2022](https://arxiv.org/abs/2205.06382)、[Bate et al., PRL](https://arxiv.org/abs/2501.08940)、[Li et al. 2025](https://arxiv.org/abs/2504.08677) | 多个线性泛函（mean、gradient、高阶项）的最优 probe 和实验 | 参数不随时间变化 |
| Entangled network + 时变信号 | [Kómár et al., Nat. Phys. 2014](https://arxiv.org/abs/1310.6045)；[Hamann et al., QST 2025](https://arxiv.org/abs/2412.12291)；[Nehra et al. 2026](https://arxiv.org/abs/2609.39831) | Kómár：$K$ 个 clock 用 cascade GHZ 和 feedback 跟踪漂移的 local oscillator。Hamann：用 lock-in 选出 plane wave。Nehra：time-bin entanglement 做二时刻差分采样 | 没有 recursive filter，没有 entanglement 供给模型 |
| Entanglement 供给受限时的分配 | [Van Milligen et al. 2024](https://arxiv.org/abs/2407.15652)；[Zang et al., PRR 2026](https://arxiv.org/abs/2409.17089)；[Kazemi Taskooh et al. 2026](https://arxiv.org/abs/2611.04128) | 等待策略、GHZ partition、noisy GHZ 的优势门槛、RL 分配 | 目标参数在整个 horizon 内固定 |
| Prior 宽度决定 probe | [Wölk–Sekatski–Dür 2020](https://arxiv.org/abs/2003.05341)；[Direkci et al. 2026](https://arxiv.org/abs/2407.06006) | Prior 宽或 interrogation 长时，最优 probe 从 GHZ 变为多能级的态；对任意宽度的 Gaussian prior，可用不同尺寸 GHZ 的乘积态逼近最优 probe | 单次估计，没有网络资源。这是"covariance 决定 GHZ 尺寸"的单步版本 |
| 不带 entanglement 的 quantum sensors + Kalman fusion | [Iyer–Iyengar 2026](https://arxiv.org/abs/2605.19327) §5.3；[Chen et al. 2025](https://arxiv.org/abs/2504.16413)；[Ishizaki et al. 2025](https://arxiv.org/abs/2504.15540) | Scalar random-walk state 加 SQL 噪声 $R/M$ 的 Kalman fusion；原子钟网络上的 decentralized Kalman filter 加 consensus | Entanglement 不进入 filter |
| 经典基础 | Olfati-Saber 2007；Gupta et al. 2006；Vitus et al. 2012 | Distributed Kalman filtering；sensor scheduling | 没有 quantum 的 measurement model |

### 1.3 有没有完全重合的

**带 entanglement scheduling 的版本：没有找到。** 没有论文同时包含"时变 state 的 recursive estimation"和"节点间 entanglement 作为调度对象"。06_quantum_sensing 的一轮检索和本轮约 30 个检索式的结论一致。最接近的三篇各缺一块：

- **Kómár 2014。** 有时变量、GHZ 网络和 feedback。它估计的是单个全局 phase；estimator 是对 parity 结果逐位解码，不是 Kalman filter；性能分析假设 entanglement 随时可用，不含生成速率和 fidelity。
- **Kazemi Taskooh 2026。** 有 entanglement 分配、损耗和 memory 模型、RL。目标是 finite horizon 内累积的 sensing information，参数固定。
- **Direkci 2026。** 有 prior 宽度到 GHZ 尺寸组合的定量对应。对象是单个 ensemble 的单次估计。

A 的第一个结果（scalar Gauss–Markov 场上的最优 cluster size $k^*$）需要以这三篇为 baseline，逐条写清差别。

**不带 entanglement 的版本：已有。** Iyer–Iyengar §5.3 写出了 $x_{t+1}=x_t+w_t$、$z_t=x_t+v_t$、$v_t\sim\mathcal N(0,R/M)$ 的 Kalman fusion，其中 $R$ 是单个 sensor 的 projection noise。原子钟网络已经实现了 decentralized Kalman filter 加 consensus（Chen et al. 2025）。

## 2　磁场测量在 quantum sensing 中的位置

**它是这个领域的标准问题，既简单又通用。**

- **模型最简单。** 一个 spin 在磁场中的 Hamiltonian 是 $H=\tfrac12\gamma B\sigma_z$。Ramsey 序列把 $B$ 变成 phase $\varphi=\gamma BT$，再读出布居数。估计 $B$ 就是估计一个 phase。
- **结论可以搬到其他物理量。** [Degen–Reinhard–Cappellaro, RMP 2017](https://arxiv.org/abs/1611.02427) 用同一个通用协议（初始化、与信号耦合、读出）描述各类 sensors，Ramsey 测量是它的基本形式。Table I 列出的被测量包括 magnetic field、electric field、time and frequency、rotation、temperature、pressure。换一个物理量只是换耦合常数。Kómár 的 clock network 和磁场网络是同一个数学问题。
- **硬件最成熟。** SQUID、atomic vapor magnetometer、NV center 都是磁场 sensor。SERF magnetometer 的 sensitivity 是 160 aT/√Hz（[Dang–Maloof–Romalis 2010](https://arxiv.org/abs/0910.2206)）。
- **Kalman filter 与 quantum sensor 结合的文献几乎都是磁场。** Ma et al. 2022 的综述里，magnetic field estimation 是展开最多的 sensing 应用。
- **网络实验也已经做过场的多个 modes。** Bate et al. 用 3 个 ion 在 constant 和 gradient 噪声磁场下测 quadratic 分量。Li et al. 把一团 spin-squeezed BEC 分成 2 到 3 份，同时估计各份上 phase 的和与差，对应场的 mean 和 gradient。Gradient magnetometry 的精度界见 [Apellaniz et al. 2018](https://arxiv.org/abs/1703.09056)。

所以 offset 加 gradient 的 magnetometry 适合做 A 的第一个例子：审稿人熟悉，结论可推广。它本身不构成贡献。

"简单"只在模型层面成立。Parity readout 是 Bernoulli 的，线性 Gaussian 的 output equation 只在 phase 锁在工作点附近时成立。这一点 06_quantum_sensing 已写明。

## 3　不共享 entanglement 的 quantum sensor network

### 3.1 已有工作

- **已部署的网络。**
  - GNOME：6 个国家 9 个站的 optical magnetometers，GPS 对时，数据经典融合（[Afach et al., Nat. Phys. 2021](https://arxiv.org/abs/2102.13379)）。
  - GPS.DM：GPS 卫星上的 atomic clocks，16 年数据（[Roberts et al., Nat. Commun. 2017](https://arxiv.org/abs/1704.06844)）。
  - 地磁监测：两个站的 optically pumped magnetometers（[Mrozowski et al. 2024](https://arxiv.org/abs/2407.15528)）。
- **Estimation 侧。** GPS composite clock 用的就是 Kalman filter（Ishizaki et al. 2025）。Chen et al. 2025 给出原子钟网络的 decentralized Kalman filter 加 consensus。Iyer–Iyengar §5.3 给出 scalar Kalman fusion。
- **理论侧。**
  - 所有 distributed quantum sensing 论文都把"各节点独立测量、经典融合"当作 baseline。
  - Proctor–Knott–Dunningham 2018 证明：估计各节点自己的 local parameters 时，separable states 加 local measurements 已经最优。
  - [Simmons–Coon–Datta 2017](https://arxiv.org/abs/1707.09166) 分析了"节点内纠缠、节点间只做经典融合"的网络，并指出经典融合环节有噪声时，节点内的量子增益会丢失。

### 3.2 相对 classical sensing 有没有优势

分两层回答。

**器件层面有优势，是常数因子。** 这对应 Degen 分类里的 type I 和 type II（用 quantum object、用 coherence），不涉及 entanglement。
- Sensitivity：SERF 达到 160 aT/√Hz，同一篇文章给出 SQUID 约 1 fT/√Hz。
- Absolute accuracy：原子都相同，各节点共用同一个物理基准。Mrozowski et al. 写明 OPM 有 intrinsic calibration，fluxgate 不是 absolute 的，需要每周校准。这篇工作里野外 OPM 的 sensitivity 是 1 Hz 处 3 pT/√Hz，优势来自校准，不来自 sensitivity。

**网络层面没有 scaling 优势。** $M$ 个节点、每个节点 $n$ 个原子，估计平均场时每次测量的方差是：

| 配置 | 方差 |
|---|---|
| 不纠缠 | $1/(MnT^2)$ |
| 只有节点内纠缠 | $1/(Mn^2T^2)$ |
| 节点间纠缠 | $1/(M^2n^2T^2)$ |

不纠缠时对 $M$ 的依赖是 $1/M$，和 $M$ 个 classical sensors 取平均相同。依据：
- [Yang–Yadin–Xu](https://arxiv.org/abs/2307.07758)：估计 global parameter 时，genuine multipartite entanglement 是 quantum advantage 的必要条件。
- Kómár 2014：按 Allan deviation 计，classical cooperation 比各 clock 独立运行好 $\sqrt K$；quantum cooperation 在短 averaging time 内再好 $\sqrt K$。
- Malia et al. 2022：作者报告 4 节点 mode-entangled 网络比 projection noise limit 好 11.6 dB，比 separable 的 locally squeezed 网络好 4.5 dB。[McGuinness 的 Matters Arising 预印本](https://arxiv.org/abs/2302.00733) 质疑其 benchmark，详见 [claude_entangled_sensor_prior_art_zh.md](claude_entangled_sensor_prior_art_zh.md)。
- [Li et al., Science 2026](https://arxiv.org/abs/2504.08677)：两份 atomic clouds 同时估计两个参数，利用份间纠缠时低于 SQL 约 3.5 dB，不利用时是 1.3 dB。
- [Nichol et al., Nature 2022](https://arxiv.org/abs/2111.10336)：两个相距 2 m 的 Sr⁺ clock，纠缠后 uncertainty 降低约 $\sqrt2$。

节点内纠缠在时变信号下的收益也有限。[Amorós-Binefa 2025](https://arxiv.org/abs/2512.05265) 给出的 quantum limit 表明：有 decoherence 时，单个 magnetometer 的精度随 atom number 至多线性增长，即 scaling 不超过 SQL。

**一个需要区分的结果。** [Xia et al. 2026](https://arxiv.org/abs/2601.14708) 不用 entanglement，估计误差的标准差渐近按 $1/M^2$ 下降，实验做到 9 个节点。做法是让同一束 coherent light 沿正反两个方向依次经过全部节点。节点之间仍然需要保持相干的光学通道，资源按节点数计，没有按光子数计。它不属于"节点间只有经典链路"的情形。

### 3.3 对 A 的含义

- 去掉 entanglement 后，问题是经典 distributed Kalman filtering 加一个给定的 $R$。按 whitepaper 的标准（写明量子优势从哪里来），这个版本不成立。评分：创新性 2 / 重要性 2 / 可行性 5。
- 它的位置是 A 的 baseline。A 的每个结果都要和"同样的节点、同样的总时间、不纠缠、各自取最优 $T$"比较。
- "节点内 squeezing、节点间经典融合"是近期实验能做到的配置，可作为第二个 baseline。

## 建议补进 whitepaper 的引用

- 优势的实验证据：Kómár 2014；Malia 2022；Nichol 2022。
- 磁场多 mode 的 entangled array：Li et al. 2025；Bate et al.；Bugalho–Omar–Markham 2026。
- Covariance 到 GHZ 尺寸：Direkci 2026；Wölk–Sekatski–Dür 2020。
- 时变信号下的 quantum limit：Amorós-Binefa–Kołodyński 2021。

## 核对深度

- 表中文献都核对了摘要。Kómár 2014、Iyer–Iyengar §5.3、Xia 2026、Degen RMP §II 和 §IV、Afach 2021、Zang 2026 核对了正文相关部分。没有逐式复核推导。
- Nehra 2026、Van Milligen 2024、Bringewatt 2021 的定位沿用此前两份文档的核对，本轮只复核了 Nehra 的摘要。
- 核对通过检索工具对摘要或正文的摘录完成，引用的数字都来自这些摘录。
- 3.2 表中的方差是无噪声的理想界，单位已吸收耦合常数。
- Li et al. 的期刊信息（检索结果显示为 Science 2026）和 Yang–Yadin–Xu 的期刊信息没有在出版页上确认，引用时用 arXiv 编号。
- Fluxgate 的典型 sensitivity 没有找一手来源，文中没有给数值。
