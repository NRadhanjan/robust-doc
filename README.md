# ROBUST DOC: Evaluating Feature Robustness in Malicious PDF Detection Against Structural Perturbations

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security Research](https://img.shields.io/badge/Domain-Cybersecurity%20%2F%20ML-red.svg)]()
[![Status: Complete](https://img.shields.io/badge/Project%20Status-100%25%20Completed-success.svg)]()

> **Investigators / Authors:**  
> • **Jasmeet Ranjan Srivastava** (23BCI0019)  
> • **Radhanjan Neelamraju** (23BCI0126)  

---

## 📌 Executive Summary & The Core Research Question

Current machine learning detectors for malicious PDFs report benchmark accuracies exceeding **98%** on static, unmodified files. However, this headline number conceals a critical operational vulnerability: **classifiers are tested on static files with identical packaging**, revealing nothing about how detection features behave under routine document transformations.

* **The Analogy:** We are not engineering a "faster car" (a novel classifier). We are stress-testing how standard cars perform on gravel, in torrential rain, and uphill. The detector is the car; the controlled structural mutations are the test conditions.
* **The Core Research Question:**
  > *"How robust are malicious-document detection methods when the same documents undergo structure-preserving mutations — and which specific features remain reliable versus which are fragile?"*

---

## 🔬 Key Scientific Novelty vs. Existing Literature

| Prior Literature Category | Typical Methodology | The Critical Gap | Our ROBUST DOC Approach |
| :--- | :--- | :--- | :--- |
| **Detection Papers** *(Smutz & Stavrou 2012)* | Train classifier $\to$ report single aggregate accuracy ($98\%+$) | Tells nothing about feature behavior when structure shifts naturally. | Profiles **per-feature stability** across individual static dimensions. |
| **Adversarial Evasion Papers** *(Šrndić & Laskov 2014, EvadeML 2016)* | Deliberately optimized, mathematically targeted gradient/genetic attacks. | Studies specialized hacker attacks, not routine everyday document processing. | Evaluates **non-adversarial structural transformations** (office re-saving, stream compression). |
| **Retraining Defense Papers** *(Tong et al. 2019, Chen et al. 2020)* | Adversarially retrain models on hand-picked features. | Causes high false-positive rates on complex corporate PDFs. | Serves as the **diagnostic prerequisite**: discovers which features to drop and which to conserve. |

---

## 🏗️ System Architecture (Two-Layer Model)

```
                       [ Curated 100-PDF Benchmark Dataset ]
                           (50 Benign + 50 Malicious)
                                       │
                                       ▼
                   ┌───────────────────────────────────────┐
                   │    LAYER A: BASELINE DETECTOR SUITE   │
                   │ (Random Forest, Decision Tree, SVM,   │
                   │  Gradient Boosting Classifier)        │
                   └───────────────────┬───────────────────┘
                                       │ Baseline Prediction + Confidence
                                       ▼
                   ┌───────────────────────────────────────┐
                   │   LAYER B: STRUCTURAL MUTATION ENGINE │
                   │  1. Metadata Perturbation             │
                   │  2. Stream Recompression (Flate)      │
                   │  3. Object Reordering & Linearization │
                   └───────────────────┬───────────────────┘
                                       │ Parameterized Intensity (10% - 100%)
                                       ▼
                   ┌───────────────────────────────────────┐
                   │     SAFETY & VALIDITY GATEKEEPER      │
                   │  V1: Clean Parser Syntax              │
                   │  V2: Catalog & Page Tree Resolution   │
                   │  V3: /OpenAction -> JS Reachability   │
                   │  V4: Byte-for-Byte Payload Preserved  │
                   └───────────────────┬───────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
              [ Mutants Passing V1-V4 ]      [ Corrupted Mutants ]
                        │                             │
                        ▼                             ▼
             Re-evaluate Classifiers          DISCARD & LOG
                        │
                        ▼
    ┌─────────────────────────────────────────────────────────┐
    │                 DIAGNOSTIC OUTPUTS & METRICS            │
    │  • 1,500-Trial Multi-Model Robustness Matrix            │
    │  • Continuous Degradation Curves (Novel Add-On #2)      │
    │  • Per-Feature Stability Bar Chart & Matrix             │
    │  • The Official One-Page Detector Fragility Report      │
    │  • Defensive Blueprint (Hardened Detector Prototype)   │
    └─────────────────────────────────────────────────────────┘
```

---

## 🛡️ The Research Confound & Validity Control

> **Critical Methodological Guardrail:**  
> If a structural mutation accidentally corrupts a file or severs the execution trigger (`/Root -> /OpenAction`), a subsequent drop in detector confidence merely indicates broken malware, **NOT** feature fragility.  
> 
> To control for this confound, our **Structural Validity Gatekeeper** enforces:
> 1. **V1 & V2 (Syntactic Health):** The file must parse cleanly via conformant C++ QPDF engines without syntax or cross-reference exceptions.
> 2. **V3 & V4 (Structural Reachability):** The `/OpenAction`, `/AA`, or `/Names/JavaScript` dictionary must structurally resolve to an intact, callable payload stream. Only valid, verified mutants enter evaluation.

---

## 📊 Empirical Results & Experimental Findings

### 1. Multi-Model Robustness Benchmark (150 Trials per Model at $\lambda = 0.8$)
We evaluated whether feature fragility is an algorithm-specific artifact or an architectural vulnerability of static feature sets:

| Classifier Architecture | Trials Tested | Retained Malicious | Retention Rate (%) | Empirical Robustness Verdict |
| :--- | :---: | :---: | :---: | :--- |
| **Random Forest (Baseline)** | 150 | 146 | **97.3%** | **High Robustness** (Ensemble averaging buffers individual feature noise) |
| **Hardened Random Forest (Our Blueprint)** | 150 | 142 | **94.7%** | **High Robustness** (Trained exclusively on 12 conserved structural invariants) |
| **Decision Tree (Single Estimator)** | 150 | 24 | **16.0%** | **Extremely Vulnerable** (Single threshold splits flip easily) |
| **Gradient Boosting (GBDT)** | 150 | 24 | **16.0%** | **Extremely Vulnerable** (Sequential residual trees overfit to packaging) |
| **Support Vector Machine (RBF Kernel)** | 150 | 3 | **2.0%** | **Near-Total Collapse** (Metric distances warped by file size/stream shifts) |

> **Key Discovery:** Distance-based models (SVM) and un-bagged tree splits collapse almost entirely (**2% to 16% retention**) under routine transformations, demonstrating that feature fragility is an inherent flaw of static PDF packaging features.

---

### 2. Feature Stability Matrix (1,500-Trial Battery)

```text
==================================================================
           EMPIRICAL FEATURE STABILITY MATRIX (1,500 TRIALS)
==================================================================
[+] Conserved / Invariant Features (100% Stability):
    * count_javascript / count_js    : 100.0%  (Directly tied to payload)
    * count_openaction / count_aa     : 100.0%  (Semantic execution entry-points)
    * count_annot / count_uri         : 100.0%  (Interaction nodes remain connected)
    * num_pages                       : 100.0%  (Document topology unaffected)

[~] Moderately Stable Features:
    * byte_entropy                    :  84.2%  (Minor drift under compression)
    * num_objects / indirect_objects  :  54.9%  (Altered during linearization)

[-] Extremely Fragile Features (Surface Packaging Artifacts):
    * num_trailer_entries             :  47.6%  (Converted to xref streams)
    * file_size                       :  35.6%  (Fluctuates widely under resaving)
    * num_compressed_streams          :  13.8%  (Easily altered by office tools)
    * ratio_compressed_streams        :   7.6%  (Inverted during routine optimization)
==================================================================
```

---

### 3. The Detector Fragility Report Deliverable

```text
==================================================================
                   DETECTOR FRAGILITY REPORT                      
==================================================================
Model: Baseline Random Forest (100-Sample Benchmark)
Overall Robustness Score: 90.0/100 -> LOW RISK (Ensemble)
------------------------------------------------------------------
Detection Retention per Mutation Type:
  * metadata_mutation       : #######     74.7%  (Critical Drop)
  * recompression           : #########   98.7%
  * object_reordering       : #########   96.7%
------------------------------------------------------------------
Headline Feature Stability (Top Reliable vs Fragile):
  [+] High Stability Features (Conserved Anchors):
      count_javascript          ########## 100.0%
      count_openaction          ########## 100.0%
      count_aa                  ########## 100.0%
      count_annot               ########## 100.0%
  [-] Fragile / Volatile Features (Surface Packaging):
      num_trailer_entries       ####        47.6%
      file_size                 ###         35.6%
      num_compressed_streams    #           13.8%
      ratio_compressed_streams               7.6%
------------------------------------------------------------------
Verdict: The detector's confidence is heavily influenced by packaging
artifacts. Routine resaving or non-adversarial processing can degrade
detection confidence by up to 48% on genuine malware payloads.
==================================================================
```

---

## 🛠️ Project Structure

```
pdf-robustness-study/
│
├── src/
│   ├── config.py                 # Feature definitions (~28 features), paths, parameters
│   ├── features/
│   │   └── extractor.py          # Structural, keyword, stream, and metadata feature extractor
│   ├── models/
│   │   ├── detector.py           # Multi-model baseline detectors (RF, DT, SVM, GBDT)
│   │   └── hardened_detector.py  # Hardened detector blueprint (conserved features only)
│   ├── mutations/                # Structural Mutation Engines
│   │   ├── base.py               # Abstract base class with intensity parametrization
│   │   ├── metadata_mutation.py  # Mutation 1: Author, Producer, ModDate alteration/wiping
│   │   ├── stream_recompression.py# Mutation 2: FlateDecode recompression / filter inversion
│   │   └── object_reordering.py  # Mutation 3: Fast Web View linearization & xref restructuring
│   ├── safety/
│   │   └── validator.py          # SAFETY GATEKEEPER: Parser health & payload reachability
│   └── evaluation/
│       ├── reporter.py           # Stability matrix & Detector Fragility Report generator
│       └── visualizer.py         # High-resolution degradation curves & bar chart engine
│
├── data/
│   ├── samples/                  # 100 Curated Benchmark PDFs (50 Benign + 50 Malicious)
│   ├── make_samples.py           # Synthetic seed generator with ground-truth triggers
│   └── download_real_pdfs.py     # Downloader for real CVEs and Mozilla PDF.js samples
│
├── train_all_models.py           # Master script: Trains all 5 classifiers
├── run_final_evaluation.py       # Master script: 1,500-trial evaluation & plot generator
├── test_demo.py                  # Live 15-second Review / Viva demonstration script
├── create_final_report_doc.py    # Generates final comprehensive DOCX thesis report
├── create_review3_ppt.py         # Generates Review 3 PowerPoint with embedded figures
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## 🚀 Quickstart & Reproduction Guide

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/NRadhanjan/robust-doc.git
cd robust-doc
pip install -r requirements.txt
```

### 2. Run the Live 15-Second Viva Demonstration
```bash
python test_demo.py
```
*Loads a real-world CVE exploit (CVE-2024-4367), applies all three mutations, validates payload reachability, displays feature drift, and renders the Detector Fragility Report.*

### 3. Train All Classifiers
```bash
python train_all_models.py
```
*Trains Random Forest, Decision Tree, SVM, Gradient Boosting, and the Hardened Detector on the 100-sample dataset.*

### 4. Execute the Full 1,500-Trial Master Evaluation
```bash
python run_final_evaluation.py
```
*Runs the 10-intensity structural battery across all 50 malicious files, evaluates all 5 models, exports `final_evaluation_metrics.json`, and generates publication figures.*

---

## 🛡️ Viva Voce Defense: Anticipated Questions & Expert Answers

> **Q1: "Your detector can be fooled — why not just build a robust one from the start?"**  
> **Answer:** Robustness cannot be engineered without first measuring what breaks. You cannot fix what has not been diagnosed. This project is the **diagnostic step** — our per-feature stability results form the empirical blueprint for which features a hardened detector should rely upon (e.g. JavaScript presence, structural object relationships) and which volatile features it should deprioritize (e.g. file size, stream ratios). In cybersecurity research, measurement/attack papers and defense papers are separate, sequential milestones.

> **Q2: "How do you know your mutation didn't just destroy the malicious functionality instead of testing robustness?"**  
> **Answer:** Every mutated file must pass our automated two-stage **Structural Validity Gatekeeper** (`validator.py`) before entering results. We verify: (1) that the file parses cleanly without corruption, and (2) that the execution trigger (such as `/Root -> /OpenAction` pointing to a valid `/JavaScript` stream) is still structurally intact and callable. Any file where the payload was neutralized was strictly rejected so we never mistook broken malware for feature fragility.

> **Q3: "Isn't 'detectors can be evaded' already known in the literature?"**  
> **Answer:** Yes, but existing evasion research (e.g., EvadeML, genetic algorithms, gradient-based attacks) studies *deliberately optimized, mathematically adversarial attacks* designed against a specific model. We study a different, more pervasive threat: whether classifiers withstand *routine, non-adversarial structural noise* generated by standard document processing tools. Furthermore, we report findings as **per-feature stability**, not a single aggregate accuracy number.

> **Q4: "Why did SVM collapse (2.0% retention) compared to Random Forest (97.3%)?"**  
> **Answer:** SVM relies on continuous geometric distances (RBF kernel) across the feature space. Because features like `file_size`, `metadata_length`, and compression counts have large absolute numerical magnitudes, slight structural edits cause massive coordinate shifts in the metric space, pushing mutated malware across the hyperplane into the benign region. Random Forest, by contrast, uses axis-aligned decision trees with ensemble averaging, isolating fragile packaging features from robust execution features.
