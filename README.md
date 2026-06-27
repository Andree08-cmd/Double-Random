# 📊 Balanced FEN Dataset for Double Random Chess (960²)

This repository contains an open-source Python script and a verified dataset of **445 perfectly balanced FENs** for the **Double Random Chess (960²)** variant. 

The main goal of this project is to mitigate and eliminate the severe first-turn imbalances, as well as the critical asymmetries between white and black pieces, using a rigorous three-stage **algorithmic filtering approach powered by Stockfish**.

---

## 🛠️ Filtering Methodology (Funnel Algorithm)

### 🛑 1. Stage I: Initial Screening (Structural Blunder Filter)
* **Engine Configuration:** `Depth = 12` | `MultiPV = 1`
* **Strict Cutoff Criteria:** The mathematical evaluation must fall strictly within the interval between **−1.0** and **+1.0**.

> **Technical Rationale:** A depth of 12 *plies* (half-moves) is equivalent to a predictive analysis of approximately 6 full moves ahead for each side. If Stockfish detects an advantage greater than 1.0 pawn of equivalent material in such a short horizon, the starting position features a severe and unrecoverable structural imbalance. Positions that fail at this stage are discarded immediately, optimizing computational processing time and costs.

---

### 🎯 2. Stage II: Dynamic Options Refinement (The "Sweet Spot")
* **Engine Configuration:** `Depth = 23` | `MultiPV = 5`
* **Strict Cutoff Criteria:**
  * The **top 2 best candidate lines/moves** must score strictly between **−0.23** and **+0.23**.
  * The **next 3 subsequent moves** (MultiPV slots 3, 4, and 5) must orbit strictly between **−0.8** and **+0.8**.

> **Technical Rationale:** To ensure human playability, it is not enough for a position to be strictly balanced in a single, perfect computer line (which would lead to forced and rigid play). Using `MultiPV = 5` ensures that both players have multiple viable, rich, and healthy strategic paths. Limiting the top two choices close to **0.0** shields pure mathematical balance, while allowing a tolerance of up to **±0.8** on the other lines guarantees tactical dynamism, allowing intuitive choices without instantly punishing a human chess player for not finding the exact machine move.

---

### 🏆 3. Stage III: Advanced Validation (
