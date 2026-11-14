# Toy 5：每个 node 放多个 qubit

2026-11-13。接 [toy4_nuisance_zh.md](toy4_nuisance_zh.md)。按 problem formulation 的编号，这是 toy model 4。

问题：同一个位置的 node 上放 $n$ 个 qubit，node 内的 qubits 可以有**本地纠缠**，不同 node 之间可以用多种方式建立**网络纠缠**。这样的传感器网络会不会表现更好？有没有类似的工作？

公平的 benchmark 是同样的 nodes、同样的 qubit 数、允许本地纠缠、不用网络纠缠，下文简称"只用本地纠缠"。

## 结论

1. **误差的绝对值会下降，但下降的部分不来自网络纠缠。** 一个 node 的 $n$ 个 qubits 做成一个本地 GHZ，就相当于一个 phase 放大 $n$ 倍的 qubit。每个周期的 information 乘 $n^2$，跟踪 MSE 乘 $n^{-2/3}$。全网的 GHZ 也乘 $n^2$。所以要回答的是两者之比怎样随 $n$ 变化。

2. **网络纠缠相对只用本地纠缠的增益不随 $n$ 增长，而是下降。** 二阶情形下降得最多。下表是干扰很强（$\rho\to\infty$）、没有 dephasing、全部 $kn$ 个 qubits 可以放进一个 GHZ 时，"只用本地纠缠的最优做法"与"一个包含全部 qubits 的网络 GHZ"之比（information 取倒数，比值大于 1 表示网络纠缠更好）：

   | 情形 | Information 之比，$n=1$ | $n\ge2$ | MSE 之比，$n=1$ | $n=2$ | $n=4$ | $n=6,8$ |
   |---|---|---|---|---|---|---|
   | A：2 个 node，目标梯度，干扰均匀分量 | 4 | 4 | 2.4 | 2.1 | 2.0 | |
   | A：4 个 node | 5.3 | 5.3 | 1.9 | | | |
   | B：4 个 node，目标曲率，干扰均匀分量和梯度 | 64 | 27 | 14 | 5.0 | 3.2 | 2.9 |
   | B′：3 个 node（$z=-1,0,1$），qubits 按 $1{:}2{:}1$ 分配 | 16 | 13.5 | 7.7 | 3.4 | | |

   空格是没有模拟的。

3. **原因是一个 node 有两个以上 qubit 时，它能读出自己的 phase。** 单 qubit 的 node 每个周期只给一个 bit，要消去随机的干扰 phase，只能把 $s$ 个 node 的结果相乘，振幅降到 $2^{-(s-1)}$。一个 node 有 $m$ 个 qubit、用不同的 reference phase 读出时，这个损失很快消失。情形 B 里，$m=1,2,4,8$ 时保留的 information 是"把干扰也跟住"时的 6%、29%、59%、76%。[Sekatski–Wölk–Dür 2020](https://arxiv.org/abs/1905.06765) 说的"空间纠缠相对乘积态有指数优势"是在每个 sensor 一个 qubit 的例子里算的；node 有多个 qubit 时，这个优势大部分消失。原子干涉仪 gradiometer 用 ellipse fitting 从共模 phase 随机的两团原子中提取差分 phase，靠的是同一个机制。

4. **跟踪 MSE 的差距比 information 的差距缩得更快。** 网络 GHZ 每个周期只给一个 bit，fringe 窄，lock constraint 限制了 $T$。每个 node 多个 bit 时似然没有歧义，$T$ 可以取得更长。情形 B 在 $n\ge4$ 时，MSE 最好的"只用本地纠缠"做法是 node 内**完全不纠缠**，虽然它的 information 不是最高的。网络一方改用两个 GHZ（cascade，例如 $7+1$、$6+2$）都不如一个 GHZ。

5. **Dephasing 限制 GHZ 的大小。这时 node 越大，网络纠缠越没用。** 设 independent dephasing 下最优的 GHZ 大小是 $G^*$。每个 node 有 $n=rG^*$ 个 qubits 时，网络纠缠相对只用本地纠缠的 information 之比：

   | $r=n/G^*$ | 1 | 2 | 4 | 8 |
   |---|---|---|---|---|
   | A，2 个 node | 2.0 | 1.6 | 1.44 | 1.29 |
   | A，4 个 node | 1.66 | 1.42 | 1.28 | 1.19 |
   | B，4 个 node | 6.6 | 3.4 | 1.7 | 1.31 |

   比值随 $r$ 趋于 1。两种做法都只能把 qubits 分成大小约 $G^*$ 的组，网络纠缠省掉的只是"读不出干扰 phase"的损失，而大 node 本来就能读出。**网络纠缠要有明显增益，需要 node 小、coherence 长：全部 $kn$ 个 qubits 放得进一个 coherent 的 GHZ（$kn\lesssim G^*$）。**

6. **多 qubit node 给网络纠缠带来的新东西是结构上的，不是精度上的。**
   - **整数权重。** 每个 node 在网络 GHZ 里的权重可以是 $-n$ 到 $n$ 的任意整数。曲率用 3 个 node（权重 $1,-2,1$）、2 条 link 就能测，单 qubit node 要 4 个 node、3 条 link；三阶 mode 是 4 个 node 对 7 个 node。不等间距或有位置误差的 array 也能抵消干扰，权重的分辨率是 $1/n$。
   - **网络纠缠的成本与 $n$ 无关。** $k-1$ 个 Bell pairs 加 node 内的 CNOT 就把 $kn$ 个 qubits 连成一个 GHZ（[Kómár et al. 2014](https://arxiv.org/abs/1310.6045) 的协议，[Zhang et al. 2026](https://arxiv.org/abs/2412.18398) 的实验）。每个 pair 换来的 information 按 $n^2$ 增长。
   - **只用本地纠缠的 benchmark 同样受益于整数权重。** B′ 里中间 node 做一个两倍大小的本地 GHZ，相乘的只有 3 个 bit，information 的损失从 64 降到 16。

7. **类似工作。** 架构（多 qubit node、本地纠缠加网络 link）和静态参数下增益的上限都已有。Kómár 2014：每个 clock $n$ 个原子，$K-1$ 个 EPR pairs 生成全网 GHZ。[Proctor–Knott–Dunningham 2018](https://arxiv.org/abs/1707.06252)：每个 sensor 多个粒子，估计线性泛函时网络纠缠比"每个 sensor 一个本地 GHZ"的 variance 最多低 $d$ 倍（$d$ 是 sensor 数）。[Gessner–Smerzi–Pezzè 2020](https://doi.org/10.1038/s41467-020-17471-3)：本地 squeezing 对跨 mode 的 squeezing，最多低 $M$ 倍。Zhang 2026：超导 module 每个 4 qubits，梯度比只用本地纠缠低 3.44 dB。没有找到的是：时变目标的跟踪；强而快的干扰下 $n$ 对网络增益的影响；dephasing 下 node 大小的临界条件。详见第 6 节。

8. **对方向 A 的判断。** 多 qubit node 不能加强网络纠缠的论点，它给出了论点的适用范围：每个 node 只有一个或少数几个 qubit（单个 ion、NV center、少原子的 clock node），coherence 容得下全网的 GHZ，目标是高阶 mode。原子气室、BEC、原子云这类大 ensemble node 不在范围内，因为每个 node 自己就能读出 phase，经典相减几乎没有损失。这和之前 SQUID gradiometer 的问题是同一类：只要每个 node 能自己读出场，经典的抵消就很便宜。评分见第 6 节。

## 1　模型

**Nodes。** 沿用 toy 4：$k$ 个 node 等间距排在 $[-1,1]$ 上，modes 是均匀分量 $b$、梯度 $g$、曲率 $c$，目标 mode 的强度是 1，干扰 mode 的强度 $\rho\to\infty$，即每个周期干扰的 phase 完全随机，不跟踪。Node $j$ 有 $n_j$ 个 qubit，它们在同一个位置，看到同一个 phase $\varphi_j$。

**只用本地纠缠。** 每个 node 把自己的 qubits 分成若干单元，每个单元是一个 $g$ 个 qubit 的本地 GHZ（$g=1$ 就是不纠缠的 qubit），phase 是 $g\varphi_j$，读出一个 bit，reference phase 各自选择。Node 的似然是 $\varphi_j$ 的 Fourier 级数，频率不超过 node 的 qubit 数。对随机的干扰 phase 平均后，只剩对干扰免疫的项：

$$P(\mathbf b\mid d)=\sum_{\mathbf q\in\mathcal Q}\prod_j c_{j,q_j}(\mathbf b_j)\,e^{i d A_{\mathbf q}},\qquad \mathcal Q=\Big\{\mathbf q:\ \sum_j q_jF_{\text{干扰}}(z_j)=0\Big\},\quad A_{\mathbf q}=\sum_j q_j f_{\text{目标}}(z_j).$$

$d$ 是目标 phase 与 feedback phase 之差，$c_{j,q}(\mathbf b_j)$ 是 node $j$ 的读出结果对应的 Fourier 系数。这是 toy 4 第 1 节公式的推广，单 qubit node 时两者相同。

**网络纠缠。** 全部 qubits 组成一个 GHZ 型态，node $j$ 的权重 $m_j$ 是该 node 内正、负符号的 qubit 数之差，$|m_j|\le n_j$。这个态积累 $\sum_j m_j\varphi_j$，选 $m$ 使它对干扰免疫。生成它需要 $k-1$ 个网络 Bell pairs，其余靠 node 内的 CNOT。

**缩放关系。** 每个 node 做一个大小为 $n$ 的本地 GHZ 时，问题与单 qubit node 完全相同，只是所有 phase 乘 $n$。所以单 qubit node 的任何做法都可以搬到 $n$ 个 qubit 的 node，information 乘 $n^2$，跟踪 MSE 乘 $n^{-2/3}$；权重为 $\pm n$ 的网络 GHZ 也一样。由此，只要 $n=1$ 时的网络 pattern 已经是最优的（A、B 都是），网络纠缠相对只用本地纠缠的比值就不会随 $n$ 增大。它会不会减小，取决于只用本地纠缠时有没有比"每个 node 一个本地 GHZ"更好的分法。

**计算。** Fisher information 用上式精确计算（总 bit 数不超过 12 时遍历全部结果，更多时 Monte Carlo），reference phases 在每类单元内均匀分布在 $[0,\pi)$，各 node 的 offset 数值优化。跟踪误差用 toy 4 的精确模拟（particle filter），lock 参数 $c$ 逐一扫描。

## 2　每周期的 information

### 2.1　一个 node 读出自己的 phase

每个 node $m$ 个不纠缠的 qubits，干扰 phase 随机。下表是对目标的 information 占"把干扰也跟住、每个 qubit 都在最优工作点"时的比例：

| 每个 node 的 qubit 数 $m$ | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|
| A，2 个 node | 0.50 | 0.63 | 0.66 | 0.69 | 0.74 | 0.78 |
| A，4 个 node | 0.60 | 0.70 | 0.75 | 0.78 | 0.81 | 0.84 |
| B，4 个 node | 0.06 | 0.29 | 0.45 | 0.59 | 0.71 | 0.76 |
| B′，3 个 node（每个 node $m$ 个） | 0 | 0.10 | 0.23 | 0.40 | 0.60 | 0.72 |

- **情形 B 的损失主要是单 bit 的问题。** $m=1$ 时只有 4 个 node 的乘积对干扰免疫，振幅 1/8，保留 6%。$m=2$ 时每个 node 已经能大致定出自己的 phase，跳到 29%。
- **$m$ 大时比例趋于 1。** Visibility 为 1 时，一个 qubit 的 Fisher information 在任何 phase 上都是 1，所以 phase 未知只影响能不能唯一地定出它，不影响精度。Node 内 qubits 越多，越容易定出。
- **B′ 在 $m=1$ 时是 0。** 3 个 node 消去均匀分量和梯度需要权重 $1,-2,1$，单 bit 做不到。

### 2.2　只用本地纠缠的最优分法

把 node 的 $n$ 个 qubits 分成本地 GHZ 单元的各种方式，information 除以 $n^2$：

| 情形 | $n$ | 一个大小 $n$ 的本地 GHZ | 全部不纠缠 | Information 最高的分法 |
|---|---|---|---|---|
| A，2 个 node | 4 | 1.00 | 0.35 | 一个本地 GHZ：1.00 |
| A，2 个 node | 8 | 1.00 | 0.19 | 一个本地 GHZ：1.00 |
| B，4 个 node | 2 | 0.049 | 0.115 | 不纠缠：0.115 |
| B，4 个 node | 3 | 0.049 | 0.119 | 不纠缠：0.119 |
| B，4 个 node | 4 | 0.049 | 0.116 | 不纠缠 0.116，两个大小 2 的本地 GHZ 0.115 |
| B，4 个 node | $n\to\infty$ | 0.049 | $\to0$ | 每个 node 3 个大小 $n/3$ 的本地 GHZ：0.119 |
| B′，3 个 node，$1{:}2{:}1$ | 1 | 0.25 | 0.063 | 中间 node 一个大小 2 的本地 GHZ：0.25 |
| B′，3 个 node，$1{:}2{:}1$ | 2 | 0.25 | 0.139 | 每个 node 2 个单元，中间 node 的单元大小加倍：0.30 |

$n$ 是边上 node 的 qubit 数；B′ 中间 node 有 $2n$ 个。网络 GHZ 是 A（2 个 node）$4n^2$，A（4 个 node）$7.11n^2$，B $3.16n^2$，B′ $4n^2$。

- **情形 A：information 最高的是每个 node 一个本地 GHZ，与 $n$ 无关。** 混合大小的分法（例如 $n=8$ 时 $4,2,1,1$）都更差。所以 information 之比保持在 4。
- **情形 B：每个 node 分成 2 到 4 个单元最好，比一个本地 GHZ 好 2.4 倍。** 单元越多，越容易读出 node 的 phase；单元越大，phase 放大越多。两者在 2 到 4 个单元时平衡。混合大小的分法（cascade，例如 $2,1,1$）在 $n\le4$ 时都更差。
- **B′ 比 B 少一个 node，网络 GHZ 反而更强。** 同样 $4n$ 个 qubits，B′ 的网络 GHZ 是 $4n^2$，B 是 $3.16n^2$，因为 B′ 把 qubits 集中在 aperture 的两端和中心（曲率的最优设计）。只用本地纠缠的一方也更强（0.30 对 0.119），所以比值更小。

## 3　跟踪误差

精确模拟，$\rho\to\infty$，MSE 以 $q_{\text{目标}}^{2/3}$ 为单位。分法固定时 MSE 按 $n^{-2/3}$ 缩放（第 1 节），所以只模拟单元大小为 1 的情形，再换算到"每个 node $m$ 个单元、每个单元 $n/m$ 个 qubits"。网络 GHZ 用 toy 4 的值换算：B 是 $1.31\,n^{-2/3}$，A（2 个 node）是 $1.21\,n^{-2/3}$，B′ 是 $1.93\,(2n)^{-2/3}$。

**情形 B，4 个 node。**

| 每个 node 的单元数 $m$ | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|
| MSE（单元大小 1，即每个 node $m$ 个不纠缠 qubits） | 18.2 | 4.16 | 2.39 | 1.67 | 1.15 | 0.96 |
| 只用本地纠缠 / 网络 GHZ（与单元大小无关） | 14 | 5.0 | 3.8 | 3.2 | 2.9 | 2.9 |

$n$ 个 qubit 的 node 可以选任何整除 $n$ 的 $m$，所以 $n=2$ 时比值是 5.0，$n=3$ 时 3.8，$n=4$ 时 3.2，$n=6,8$ 时约 2.9。$m=1$ 一列是 toy 4 的值。

**情形 A，2 个 node。**

| 每个 node 的单元数 $m$ | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| MSE（单元大小 1） | 2.96 | 1.63 | 1.24 | 0.96 |
| 只用本地纠缠 / 网络 GHZ | 2.4 | 2.1 | 2.1 | 2.0 |

**情形 B′，3 个 node（$1{:}2{:}1$）。** $n=1$（中间 node 一个大小 2 的本地 GHZ，3 个 bit 相乘）9.3，网络 GHZ 1.22，比值 7.7。$n=2$（每个 node 2 个单元）2.63，网络 GHZ 0.77，比值 3.4。

**网络一方用多个 GHZ 是否更好。** 把网络的 qubits 分成一大一小两个 GHZ（cascade），小的帮助消除 fringe 歧义，以便取更长的 $T$。结果都不如一个 GHZ：

| 情形 | 一个 GHZ | 两个 GHZ |
|---|---|---|
| B，$n=4$ | 0.527 | $3+1$：0.552 |
| B，$n=8$ | 0.328 | $7+1$：0.376；$6+2$：0.349 |
| A，2 个 node，$n=4$ | 0.480 | $3+1$：0.512 |

- **MSE 的差距比 information 的差距小得多。** 情形 B 在 $n=6,8$ 时 information 之比是 27 到 42，MSE 之比只有 2.9。网络 GHZ 每个周期一个 bit，fringe 窄，预测误差必须远小于 fringe 宽度，$T$ 受 lock constraint 限制；toy 4 里单个 GHZ 的 MSE 是线性模型无约束下界的 1.8 倍（1.93 对 1.09）。每个 node 有多个 bit 时似然没有歧义，这部分损失小得多。
- **情形 B 在 $n\ge4$ 时，MSE 最好的做法是 node 内不纠缠。** 这与 information 的排序（每个 node 3 个本地 GHZ 最好）不同，原因同上。
- **情形 A 也略有下降**，从 2.4 到 2.0，同样来自多 bit 读出放宽了 lock。

## 4　Dephasing 限制 GHZ 的大小

每个 qubit 独立 dephasing，速率 $\gamma$，大小 $G$ 的 GHZ 的 visibility 是 $e^{-G\gamma T}$。固定 $T$ 时，单个 GHZ 的 information $G^2e^{-2G\gamma T}$ 在 $G^*=1/(2\gamma T)$ 处最大。这里用一个简化：GHZ 最多 $G^*$ 个 qubit，不超过时没有衰减。

均匀磁场噪声这类空间相关的 dephasing 就是干扰 mode 本身，已经在模型里；$G^*$ 只由不相关的部分决定。

**只用本地纠缠。** 每个 node 分成 $r=n/G^*$ 个大小 $G^*$ 的本地 GHZ（或更小的单元），information 是 $G^{*2}$ 乘第 2.1 节 $m=r$ 时的值。

**网络纠缠。** 把 qubits 分成多个大小 $G^*$ 的网络 GHZ，每个横跨全部 node，权重按 $|f_{\text{目标}}(z_j)|$ 分配（A 的 4 个 node 时，外侧两个 node 一组、内侧两个 node 一组）。这样分的总 information 正好等于"把干扰也跟住"时的上限 $rG^{*2}\sum_j f_j^2$。

两者之比就是第 2.1 节表中比例的倒数；情形 B 在 $r=1$ 时本地一方改用更小的单元，比值从 16 降到 6.6。结果见结论第 5 条的表。

**含义。** 网络纠缠省掉的只是"读不出干扰 phase"的损失。Node 小于 $G^*$ 时，网络 GHZ 可以比任何本地 GHZ 都大，这是额外的增益；node 大于 $G^*$ 时，两边的 GHZ 一样大，剩下的只有读出损失，而它随 node 的 qubit 数减小。

这一节只比较了 information。由第 3 节，跟踪 MSE 之比还会更小。

## 5　网络纠缠的建立方式

不同的建立方式，在这个模型里影响的是能得到哪一类态、成本是多少：

| 方式 | 得到的态 | 成本随 $n$ | 已有的实现 |
|---|---|---|---|
| 网络 Bell pair 加 node 内 CNOT（fusion） | 任意整数权重的全网 GHZ | 每个 GHZ $k-1$ 个 pairs，与 $n$ 无关 | Kómár 2014 协议；Zhang 2026 用 25 cm cable 做 state transfer；ion 和 neutral atom 节点用 photonic link 生成 Bell pair（Nichol 2022；Seubert 2026） |
| 只在部分 link 上有 pair | 几个较小的 GHZ，组之间做经典乘积 | 每条 link 一个 pair | Toy 4 第 2、5 节。每个 node 先做本地 GHZ 后，toy 4 的 information 规律不变（B：每合并两组乘 4）；但 node 有多个 bit 时，未合并的组之间也能读出 phase，这个规律会变弱，没有算 |
| 多个并行的网络 GHZ | 每个 GHZ 用每个 node 的一部分 qubits | 每个 GHZ $k-1$ 个 pairs | 第 4 节：dephasing 限制 GHZ 大小时用这种 |
| Gaussian 纠缠（squeezing 跨 node 分布） | 跨 node 的 squeezed state | 适合大 ensemble | 一团 squeezed 原子分成几份（[Malia 2022](https://arxiv.org/abs/2205.06382)；[Li 2026](https://arxiv.org/abs/2504.08677)）；光通过多个 ensemble 的 QND 测量（[Wasilewski 2010](https://arxiv.org/abs/0907.2453)）。静态时相对本地 squeezing 最多低 $M$ 倍（Gessner 2020） |

前三种是同一族态（GHZ 型），区别只是资源。Gaussian 一族在强干扰、跟踪的情形下没有算。

## 6　类似工作与对方向的判断

| 工作 | 设定 | 结论 | 与本文的关系 |
|---|---|---|---|
| [Kómár et al., Nat. Phys. 2014](https://arxiv.org/abs/1310.6045) | $K$ 个 clock node，每个 $n$ 个原子；中心与每个 node 共享一个 EPR pair，teleport 一个 qubit 后各 node 用 CNOT 扩展；不同大小 GHZ 的 cascade | 全网 $nK$ 个原子的 GHZ 跟踪共同的 local oscillator | 多 qubit node、本地纠缠加网络 link 的架构，目标是均匀 mode |
| [Kómár et al., PRL 2016](https://arxiv.org/abs/1603.06258) | 上面的 neutral atom 实现：node 内 Rydberg 纠缠，node 间 photonic link | | 同上 |
| [Proctor–Knott–Dunningham, PRL 2018](https://arxiv.org/abs/1707.06252) | $d$ 个 sensor，每个多个粒子 | sensor 之间不纠缠时的最优态是每个 sensor 一个本地 GHZ；估计线性泛函时网络纠缠的 variance 最多低 $d$ 倍；两个 site 各 $N/2$ 个粒子测梯度时低 2 倍 | 静态、干扰已知时的上限。情形 A（2 个 node）在干扰很强时是 4 倍，多出的 2 倍来自单 bit 读不出干扰 phase |
| [Sekatski–Wölk–Dür, PRR 2020](https://arxiv.org/abs/1905.06765) | 每个 node $n_j$ 个 qubit，空间相关噪声 | 免疫噪声的网络纠缠态对乘积态有最多 $2^{-(J-1)}$ 的优势；这个界在单 qubit sensor 的例子里推出 | 对应 toy 4 的单 qubit 结果。第 2.1 节显示 node 有多个 qubit 时这个优势大部分消失 |
| [Gessner–Smerzi–Pezzè, Nat. Commun. 2020](https://doi.org/10.1038/s41467-020-17471-3) | 每个 mode 一团原子；本地 squeezing 对跨 mode 的 squeezing | 本地 squeezing 已能让所有参数低于 shot noise；跨 mode 纠缠对某个线性组合最多再低 $M$ 倍 | Gaussian 版本的静态上限 |
| [Ehrenberg et al., arXiv 2110.07613](https://arxiv.org/abs/2110.07613) | 每个 sensor 一个 qubit | 最优估计 $\alpha\cdot\theta$ 需要的纠缠大小约为 $\lVert\alpha\rVert_1/\lVert\alpha\rVert_\infty$ | 网络 GHZ 要横跨多少 node |
| [Zhang et al., Nat. Commun. 2026](https://arxiv.org/abs/2412.18398) | 超导 modules，每个 4 个 transmon；Bell pair 在中心 module 生成后经 cable 分到两个 sensor module，再用本地 CNOT 扩展成 4-qubit GHZ | 梯度的总 variance 比"每个 module 一个本地 Bell pair、分别估计再相减"低 3.44 dB；参数静态，场由 gate 模拟 | 最接近的实验，benchmark 与本文相同 |
| [Robinson et al., Nat. Phys. 2024](https://jila.colorado.edu/sites/default/files/2024-02/SpinSqueezed%20Clock%20comparison%20NatPhys2024_0.pdf) | 同一个 lattice 里两团 Sr 原子各自 squeezed，差分比较 | 只用本地纠缠的差分测量 | "只用本地纠缠"这个 benchmark 的实验形态 |
| [Cao et al., Nature 2024](https://doi.org/10.1038/s41586-024-07913-z) | Tweezer clock 中最多 9 个原子的 GHZ；不同大小的 GHZ 同时使用 | 单个 GHZ 的 dynamic range 不够，在最优 dark time 不比不纠缠好；cascade 解决 phase 的歧义 | 与第 3 节"多 bit 放宽 lock、单个大 GHZ 受 lock 限制"是同一个现象 |

Bate 2025（3 个 ion 在同一个 trap 里测二次项）和 Megidish 2019（4 个 ion 的 pattern）在本文的语言里介于两者之间：ion 之间相距 µm 到 mm，看到不同的场，相当于"网络"；纠缠靠同一个 trap 里的 gate 生成，成本像"本地"。

**评分**（把"多 qubit node"作为方向 A 的扩展）：

| 版本 | 创新性 | 重要性 | 可行性 |
|---|---|---|---|
| 多 qubit node，网络纠缠对只用本地纠缠的增益 | 2 | 3 | 4 |

- 创新性 2：架构是 Kómár 2014，静态上限是 Proctor 2018 和 Gessner 2020。新的是强干扰下"单 bit 损失随 node 变大而消失"和 dephasing 下的临界条件，两者都是对已有结论的限定。
- 重要性 3：它不提供新的优势，但决定了方向 A 的 claim 在哪些平台成立。
- 可行性 4：模型和计算都简单。

**对 whitepaper 的建议。** 方向 A 的 claim 补一句适用条件："the advantage over locally entangled nodes requires nodes with few qubits, so that a network-wide GHZ state fits within the coherence budget; for large-ensemble nodes, each node resolves its own phase and classical cancellation of common-mode disturbance becomes nearly free." 情形 B 的 14 倍应注明是单 qubit node 的值；每个 node 2 个 qubit 时是 5 倍，4 个以上时约 3 倍。

## 核对深度

- **Fisher information。** 单 qubit node 的值与 toy 4 一致（A 2 个 node 1.0，A 4 个 node 1.337，B 0.0494）。总 bit 数不超过 12 时精确遍历；更多时 Monte Carlo，40000 到 60000 个样本，统计误差约 0.5% 到 1%。Reference phases 只优化了每个 node 的 offset 和每类单元的相对 offset，没有对每个 qubit 单独优化；A 2 个 node、$m=4$ 时完全优化比均匀分布高 2%（5.65 对 5.54）。所以只用本地纠缠的值可能略低估，偏差对网络一方有利，不超过几个百分点。
- **分法的搜索。** A（2 个 node）搜索了 $n\le8$ 的全部分法（每个 node 相同）；B 搜索了 $n\le4$ 的全部分法，$n\to\infty$ 的结论来自等大小单元（$m\le8$）。没有搜索各 node 不同的分法，也没有考虑本地 squeezing 等非 GHZ 型的本地纠缠。所以只用本地纠缠的最优值是下界，网络纠缠的增益是上界。
- **跟踪误差。** 每个配置 2 到 3 个 seeds，每个 seed 64 条轨迹、2000 个周期，lock 参数扫 4 到 5 个值，表中取最好的 $c$ 下各 seed 的平均。多 bit 的配置 seeds 之间一般相差 5% 以内。单 qubit node 的 B 不纠缠容易 phase slip：$c=0.5$ 时本文三个 seeds 是 56.9、21.7、20.5，toy 4 的两个 seeds 是 20.3、17.9，表中沿用 toy 4 的 18.2。Reference phases 按 $d=0$ 处的 Fisher information 选，没有针对跟踪优化，这也对网络一方有利。
- **网络一方。** 一个 GHZ 的值由 toy 4 按缩放关系换算，本文用模拟核对了 B、$n=4$（0.527，换算值 0.521）。两个 GHZ 的 cascade 只试了表中 4 种；更深的 cascade（大小 $n,n/2,n/4,\dots$）在 $n$ 大时可能有用，没有算。
- **情形 A 的 4 个 node** 在 $n\ge2$ 时没有做跟踪模拟。
- **Dephasing。** 第 4 节把 dephasing 简化为 GHZ 大小的上限 $G^*$，只比较了 information，没有做跟踪模拟。
- **干扰强度有限时没有算。** $\rho\to\infty$ 是网络纠缠增益最大的情形；有限 $\rho$ 时只用本地纠缠的一方还可以跟踪干扰，增益只会更小。
- **文献。** Kómár 2014 核对了正文中生成全网 GHZ 的步骤；Proctor 2018、Gessner 2020、Sekatski–Wölk–Dür 2020、Zhang 2026、Ehrenberg 核对了正文的相关部分；Cao 2024 和 Robinson 2024 只核对了摘要。Sekatski–Wölk–Dür 的 $2^{-(J-1)}$ 界是否对多 qubit node 也有推导，只读了相关段落，没有读附录。

## 复现

代码在 [code/](code/)：

- `toy5_nodes.py`：多 qubit node 的精确似然（Fourier 级数、免疫项），Fisher information（遍历或 Monte Carlo）。
- `toy5_sim.py`：精确跟踪模拟（particle filter），沿用 toy 4 的约定。
- `run_t5_KU.py`：第 2.1 节的表。`run_t5_part.py`：第 2.2 节的分法搜索。`run_t5_b3.py`：B′ 的分法。`run_t5_sim.py`：第 3 节只用本地纠缠的模拟。`run_t5_net.py`：第 3 节网络一方的 cascade。`t5_summary.py`：汇总和第 4 节的比值，写入 `res_t5_summary.json`。
