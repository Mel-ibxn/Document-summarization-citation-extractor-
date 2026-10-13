# SewEval Paper — Code Cross-Check Report

Cross-checked against the full codebase in `c:\Users\Shana\RESEARCH\SewEval\`.  
Files examined: all eight metric modules, `evaluate.py`, `aggregator.py`, `repair_pattern.py`, `batch_repair.py`, `simulator/connector.py`, `simulator/mock.py`, `FINAL_COMPARATIVE_REPORT.csv` (500 rows), `FINAL_DATASET_REPORT.csv` (500 rows).

---

## ✅ Confirmed Correct

The following claims in the paper are consistent with the code.

| Claim | Source |
|---|---|
| Eight metrics evaluated | `evaluate.py` registers exactly 7 geometric metrics + 1 strain metric = 8 total ✅ |
| Shapely used for self-intersection check | `self_intersection.py` line 26: `poly.is_valid and poly.is_simple` ✅ |
| Seam tolerance τ = 0.5 cm | `seam_alignment.py` default `threshold=0.5`; `repair_pattern.py` `match_seams(..., threshold=0.5)` ✅ |
| Minimum width threshold 1 cm | `min_width.py` `CRITICAL_CM = 1.0` (with `fabric_cfg` override, default fabric_cfg) ✅ |
| Aspect ratio pass threshold 10:1 | `aspect_ratio.py` line 47: `ratio > 10 or ratio < 0.1` ✅ |
| Fabric width 150 cm | `fabric_utilization.py` `FABRIC_WIDTH = 150.0` ✅ |
| Metric weights (all eight) | `aggregator.py` WEIGHTS dict matches Table 1 exactly ✅ |
| IPS-OG Phase 1: Auto-Grading with 10% tolerance, φ = C_target / C_current | `repair_pattern.py` `apply_auto_grading()` lines 268–275 ✅ |
| IPS-OG Phase 2: Smooth redundant vertices (angle within 2° of 180°) | `smooth_panel()` uses `threshold=2.0` degrees ✅ |
| IPS-OG Phase 2: Degenerate panel recovery via buffer/skeleton | `repair_panel_geometry()` uses `LineString.buffer()` for area < 1e-6 ✅ |
| IPS-OG Phase 2: `buffer(0)` cleanup for invalid polygons | `repair_panel_geometry()` lines 94–100 (uses `buffer(0.01).buffer(-0.01)` + fallback `buffer(0)`) ✅ |
| IPS-OG Phase 3: Seam rescaling about midpoint | `match_seams()` lines 241–243: midpoint-centred rescale ✅ |
| IPS-OG Phase 4: Re-validation pass | `repair_pattern_json()` Pass 3 (lines 307–309) ✅ |
| NVIDIA Warp referenced as physics engine | `connector.py` attempts `import warp as wp` ✅ |
| FATAL FAILURE = score 0.0 | `aggregator._get_grade()`: F/FATAL returned for score < 0.5; score 0.0 always F ✅ |
| Ribbon skirt (rand_97ABI9ORNR) baseline = 0.0 | CSV row: `rand_97ABI9ORNR, 0.0, 0.5, UNSEWABLE` ✅ |
| GOOD pattern (rand_ONTB2Y23YM) baseline ≥ 0.8 | CSV row: `rand_ONTB2Y23YM, 0.83, 0.83, GOOD` ✅ |
| 500-pattern benchmark | Both CSVs have exactly 500 data rows ✅ |
| No pattern remains at FATAL after repair (0 FATAL post-repair) | Post-repair CSV: 0 rows with `baseline_score=0.0` in optimized column ✅ |

---

## ❌ Discrepancies — Must Fix

### D1. Baseline Classification Table (Table 3) — Numbers Are Wrong

The paper states:

| Category | Count | % |
|---|---|---|
| GOOD | 2 | 0.4% |
| FAIR | 2 | 0.4% |
| UNSEWABLE | 0 | 0.0% |
| **FATAL FAILURE** | **496** | **99.2%** |

**What the CSV actually shows** (using `baseline_score`):

| Category | Count | % |
|---|---|---|
| GOOD (≥0.8) | 2 | 0.4% |
| FAIR (0.6–0.8) | 185 | 37.0% |
| UNSEWABLE (0.1–0.6) | 252 | 50.4% |
| **FATAL (= 0.0)** | **60** | **12.0%** |
| N/A (one broken row) | 1 | 0.2% |

> [!CAUTION]
> The paper claims 99.2% FATAL, but only **60/500 (12%)** patterns have `baseline_score = 0.0`. The remaining 437 non-zero patterns are UNSEWABLE or FAIR, not FATAL. **Table 3 is incorrect and must be rewritten.**

**Root cause:** The paper treats ALL patterns as FATAL because the `before_failures` column of `FINAL_COMPARATIVE_REPORT.csv` labels every single row `"FATAL CRASH (Self-Intersection/Degeneracy)"` — this is a label applied during report generation, not a sewability score category. The actual sewability scores for most patterns are in the 0.53–0.67 range (UNSEWABLE/POOR), not 0.0.

---

### D2. Post-Repair Classification Table (Table 4) — Numbers Are Wrong

The paper states:

| Category | Count | % |
|---|---|---|
| GOOD | 1 | 0.2% |
| **FAIR** | **68** | **13.6%** |
| UNSEWABLE | 431 | 86.2% |
| FATAL | 0 | 0.0% |

**What the CSV actually shows** (post-repair `final_status` from `FINAL_DATASET_REPORT.csv`):

| Category | Count | % |
|---|---|---|
| GOOD | 1 | 0.2% |
| FAIR | 2 | 0.4% |
| POOR *(not in paper's schema)* | 144 | 28.8% |
| UNSEWABLE | 352 | 70.4% |
| N/A | 1 | 0.2% |
| FATAL | 0 | 0.0% |

> [!CAUTION]
> The paper claims 68 patterns reach FAIR after repair (13.6%), but the CSV shows only **2 FAIR** post-repair. The 144 "POOR" patterns in the data do not appear in the paper's schema at all.

**Root cause (two issues):**
1. The aggregator uses **five** grade bands (`GOOD / FAIR / POOR / UNSEWABLE / FATAL`), but the paper only describes **four** (`GOOD / FAIR / UNSEWABLE / FATAL`). POOR (0.60–0.70) is silently omitted from the paper's Table 2.
2. The paper likely counted POOR + FAIR together as "FAIR" when drafting the narrative (144 + 2 = 146 ≠ 68), or used an earlier version of the scores.

---

### D3. Score Categorization Table (Table 2) — POOR Band Is Missing

**Code (`aggregator.py`):**
```python
if score >= 0.80: return "A", "GOOD"
if score >= 0.70: return "B", "FAIR"
if score >= 0.60: return "C", "POOR"   # ← This exists in code, not in paper
if score >= 0.50: return "D", "UNSEWABLE"
return "F", "FATAL"
```

**Paper Table 2:**
| Category | Score Range |
|---|---|
| GOOD | ≥ 0.8 |
| FAIR | 0.6 ≤ Score < 0.8 |
| UNSEWABLE | 0.1 ≤ Score < 0.6 |
| FATAL FAILURE | 0.0 |

> [!WARNING]
> The paper collapses POOR (0.60–0.70) and FAIR (0.70–0.80) into a single "FAIR" band, but the code has them as separate grades. The paper's FAIR threshold (≥ 0.6) does not match the code's FAIR threshold (≥ 0.70). Either the table or the code must be corrected.

---

### D4. S_topo Scoring Formula vs. Code Behaviour

**Paper says:**
> "If any panel in a pattern fails this check, the entire pattern receives a score of 0."

**Code (`self_intersection.py` line 44):**
```python
score = valid_count / total_panels
```

> [!WARNING]
> The code returns a **fraction** (e.g., 0.75 if 3 of 4 panels are valid). It does **not** return 0 for the whole pattern when any single panel fails. The paper's binary "entire pattern = 0" rule is not implemented. Fix either the code (add an `if any invalid: return 0.0`) or correct the formula description in the paper.

---

### D5. S_stitch (Seam Alignment) — Formula Mismatch

**Paper formula:**
$$S_{stitch} = \begin{cases} 1 & \text{if } |L_1 - L_2| \leq 0.5\text{ cm} \\ 0 & \text{otherwise} \end{cases}$$
> "Each stitching pair is evaluated independently. The overall seam alignment score is the **fraction** of stitching pairs that satisfy the length-matching criterion."

**Code (`seam_alignment.py` line 78–80):**
```python
final_score = np.mean(errors) if errors else 1.0
final_score = max(0.0, 1.0 - final_score / threshold) if errors else 1.0
```

> [!WARNING]
> The code does **not** use a binary pass/fail per pair. It computes a **continuous** score based on average error across all pairs, converted via `1 - avg_error / threshold`. Additionally, the metric measures **sampled-point deviation** between edge curves, not a simple edge-length difference `|L1 - L2|`. The paper's formula and the code's implementation are fundamentally different.

---

### D6. W_min — Formula and Implementation Mismatch

**Paper formula:**
> "The minimum width is computed by eroding the panel geometry using a disk of radius 0.5 cm."
> `W_min = diameter(P ⊖ Disk(0.5 cm))`

**Code (`min_width.py`):**
```python
def rotating_calipers(points):  # Minimum width of convex hull
```

> [!WARNING]
> The code uses **rotating calipers on the convex hull** (minimum bounding width), not a morphological erosion. These produce different results for non-convex panels. The paper's formula describing erosion with a disk is not implemented.

Also: the paper says "Panels with minimum width below 1 cm receive a **proportional score**", but the code actually returns `0.0` for any panel below `CRITICAL_CM = 1.0`. The proportional behaviour only applies in the 1.0–2.0 cm range (`MIN_ACCEPTABLE_CM = 2.0`), not at the 1 cm threshold the paper describes.

---

### D7. S_strain — Warp Simulation Not Actually Used

**Paper says:**
> "Simulation is performed using the NVIDIA Warp physics engine, which provides per-element strain values for the draped garment mesh."
> Formula: `S_strain = 1.0 − (Σ ε_j · A_j / Σ A_j)`

**Code (`simulator/connector.py` line 38, `mock.py`):**
```python
# connector.py — always falls back to mock:
return run_mock_simulation(pattern, fabric_type)

# mock.py — deterministic, complexity-based stub:
complexity = (num_panels * 0.01) + (avg_verts * 0.001)
max_strain = min(0.2, complexity * fabric_mod)
```

> [!CAUTION]
> The actual Warp physics engine is **never called** — `connector.py` always falls back to `run_mock_simulation()` even when Warp is installed (line 38 is unconditional). The mock returns a simple complexity function, not Green-Lagrange strain per mesh element. All reported strain scores in the benchmark are mock values. The paper must either acknowledge this limitation or the Warp integration must be implemented.

Also: the evaluate pipeline uses `max_strain` from the mock but the paper's formula uses area-weighted **mean** strain. The code and paper formula are inconsistent.

---

### D8. Manufacturing Info (S_info) — Formula and Scope Mismatch

**Paper formula:**
> `N = 3P + E` (grain line + piece label + seam allowance per panel, plus one allowance per edge)
> `S_info = (1/N) Σ 1(m_i ∈ Spec)`

**Code (`manufacturing_info.py`):**
```python
has_notches = any(...)
has_grain = any(...)
has_allowance = any(...)
score = (0.33 if has_notches else 0) + (0.33 if has_grain else 0) + (0.34 if has_allowance else 0)
```

> [!WARNING]
> The code checks only 3 binary pattern-level flags (`any` across all panels), giving a coarse 0/0.33/0.66/1.0 output. The paper describes a fine-grained per-field count across `N = 3P + E` total fields. The paper also says piece labels are required, but the code does not check for them. The formula in the paper is aspirational — it is not implemented.

---

### D9. Ribbon Skirt Recovery Score

**Paper says:**
> "The optimized pattern achieved a score of **0.63** with FAIR status."

**CSV (`FINAL_COMPARATIVE_REPORT.csv`, row `rand_97ABI9ORNR`):**
> `baseline_score=0.0, optimized_score=0.5, final_status=UNSEWABLE`

> [!WARNING]
> The paper claims 0.63/FAIR for the ribbon skirt; the CSV records 0.50/UNSEWABLE. This is a direct numerical contradiction in the case study narrative. If the 0.63 value came from a separate evaluation run, that run's output needs to be identified and the CSV updated; otherwise the paper claim must be corrected.

---

### D10. Seam Angles — Threshold Mismatch

**Paper says:** "A vertex receives a score of 1 if its interior angle falls between **20° and 178°**."

**Code (`seam_angles.py` line 54):**
```python
if 30 <= angle <= 150:
    valid_angles += 1
```

> [!WARNING]
> The code uses **[30°, 150°]**, not [20°, 178°] as stated in the paper. The docstring (line 26) even contradicts itself: "Score = fraction of angles in [30°, 150°] range. Fail if any angle < 20° or > 160°." Three different thresholds appear: the paper (20°, 178°), the code's valid range (30°, 150°), and the code's failure trigger (< 20° or > 160°). Only one set should exist.

---

### D11. IPS-OG Phase Naming vs. Code Structure

**Paper describes 5 phases:**  
Phase 1 (Grading) → Phase 2 (Sanitization) → Phase 3 (Seam Coordination) → Phase 4 (Re-Validation) → Phase 5 (Nesting)

**Code (`repair_pattern_json()`):**  
Pass 0 (Grading) → Pass 1 (Geometry) → Pass 2 (Seam Matching) → Pass 3 (Final Geo Repair)

> [!NOTE]
> Phase 5 (non-overlapping nesting) is described in the paper and referenced in `fabric_utilization.py` comments but has no dedicated implementation in `repair_pattern.py`. The nesting in `fabric_utilization.py` is used only for scoring, not as a separate repair step that produces an SVG layout. The paper's claim that Phase 5 produces a "print-ready layout suitable for SVG export" is not backed by code.

---

## ⚠️ Minor Issues

| # | Location | Issue |
|---|---|---|
| M1 | Abstract | "13.2% of patterns improved to sewable state" — CSV shows 2 FAIR + 1 GOOD = 3 patterns at FAIR or above post-repair (0.6%), not 13.2% |
| M2 | S_topo formula | The paper binary formula uses `{1 if valid, 0 otherwise}` but the code returns a fraction; no mention that the score is a fraction of valid panels |
| M3 | Fabric utilization | Paper says GOOD ≥ 70%, FAIR < 40%. Code threshold for a warning is < 70%, but normalization target is 80% (`TARGET = 0.80`). These are inconsistent |
| M4 | `seam_alignment.py` | `final_score` variable is computed twice (lines 78 and 80); line 78 is immediately overwritten and never used |
| M5 | `repair_pattern.py` Phase 2 | Paper says degenerate panels use "medial axis skeleton". Code uses `LineString.buffer()` on the raw vertex list, not a true medial axis |
| M6 | Pattern count | The paper says `rand_97ABI9ORNR` had "105 flagged vertices" for seam angles. The CSV shows `seam_angles (62)` — a different count |
| M7 | One broken row | `rand_6GDQKVAYKU` has `optimized_score=0.0` and `final_status=N/A` in both CSVs — this pattern was not repaired successfully but is still counted in the 500 |

---

## Summary Table

| Finding | Severity | Action |
|---|---|---|
| Table 3 baseline counts wrong (99.2% FATAL vs actual 12%) | 🔴 Critical | Rewrite Table 3 with actual score distributions |
| Table 4 post-repair counts wrong (68 FAIR vs actual 2) | 🔴 Critical | Rewrite Table 4; add POOR category |
| Table 2 missing POOR band | 🔴 Critical | Add POOR (0.6–0.7) to Table 2 or merge with code |
| S_topo: binary-zero rule not implemented | 🟠 Major | Fix code or fix paper formula |
| S_stitch: paper formula ≠ code implementation | 🟠 Major | Align formula with continuous implementation |
| W_min: erosion formula ≠ rotating calipers code | 🟠 Major | Align formula with actual implementation |
| Strain: Warp not actually used (always mock) | 🟠 Major | Add disclosure or implement Warp bridge |
| S_info: per-field formula not implemented | 🟠 Major | Align formula with 3-flag implementation |
| Ribbon skirt score: 0.63 in paper vs 0.50 in CSV | 🟠 Major | Reconcile case study score |
| Seam angles threshold: 20–178° (paper) vs 30–150° (code) | 🟠 Major | Unify to a single threshold |
| Phase 5 nesting: described but not implemented as repair step | 🟡 Minor | Clarify scope or implement |
| Utilization target discrepancy (70% vs 80%) | 🟡 Minor | Align constants |
| `final_score` double-assignment in seam_alignment.py | 🟡 Minor | Remove dead line 78 |
| M7 broken row (rand_6GDQKVAYKU) | 🟡 Minor | Note or exclude from count |
