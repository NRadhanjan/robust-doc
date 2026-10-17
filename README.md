# Evaluating Feature Robustness in Malicious PDF Detection Against Structural Perturbations

## 📌 Project Overview
* **The One-Line Pitch:** We are not building "yet another malicious PDF detector." We are stress-testing an existing detector to find out which of its detection features are trustworthy and which break easily when a document undergoes simple, non-adversarial structural perturbations (re-saving, recompressing, editing metadata).
* **Research Question:** *"How robust are malicious-document detection methods when the same documents undergo structure-preserving mutations — and which specific features remain reliable versus which are fragile?"*

---

## 🎯 Review 2 Milestone Scope (50–60% Implementation)

This repository fulfills the **Review 2 requirements (50–60% complete)**:

| Component | Status | Description |
| :--- | :---: | :--- |
| **Layer A: Baseline Detector** | ✅ Complete | Feature-based classifier (PDFRate/Mimicus features + Scikit-Learn Random Forest) with confidence scoring. |
| **Layer B: Mutation Engine** | ✅ Complete | All 3 non-adversarial structural mutations implemented with continuous intensity control: (1) Metadata modification, (2) Stream recompression, (3) Object reordering. |
| **Safety & Validity Gatekeeper** | ✅ Complete | Validates that mutated files open cleanly AND verifies that malicious triggers (`/OpenAction`, `/JavaScript`, streams) remain structurally reachable. Discards invalid files. |
| **Evaluation & Reporting Pipeline** | ✅ Complete | Feature drift tracker, detection retention % calculator, and **Detector Fragility Report** generator. |
| **Sample Dataset Generator** | ✅ Complete | Generates reproducible seed samples for calibration and testing. |
| *Full 100+ PDF Batch Run* | ⏳ Review 3 | Expanding to large external corpus and generating multi-intensity degradation curves. |
| *SHAP / TreeExplainer Integration* | ⏳ Review 3 | Stretch goal for per-prediction feature shift attribution. |

---

## 🏗️ Architecture & Modules

```
pdf-robustness-study/
│
├── src/
│   ├── config.py                 # Feature definitions, paths, intensity settings
│   ├── features/
│   │   └── extractor.py          # PDFRate/Mimicus structural & statistical extractor (~28 features)
│   ├── models/
│   │   └── detector.py           # Layer A: Baseline Random Forest classifier + confidence
│   ├── mutations/                # Layer B: Controlled Structural Mutation Engine
│   │   ├── base.py               # Abstract base class with intensity parametrization
│   │   ├── metadata_mutation.py  # Mutation 1: Author, Producer, ModDate alteration/wiping
│   │   ├── stream_recompression.py# Mutation 2: FlateDecode recompression / filter inversion
│   │   └── object_reordering.py  # Mutation 3: Fast Web View linearization & xref restructuring
│   ├── safety/
│   │   └── validator.py          # CRITICAL GATEKEEPER: Open check & payload reachability verifier
│   └── evaluation/
│       └── reporter.py           # Feature stability matrix & Detector Fragility Report generator
│
├── data/
│   ├── samples/                  # PDF samples (50 total: 20 real downloaded + 30 seed)
│   ├── generated_mutations/      # Mutated PDFs produced during trials
│   ├── make_samples.py           # Seed sample generator
│   └── download_real_pdfs.py     # Script to fetch real Benign (Mozilla) & Exploit PoC (CVE) PDFs
│
├── train_baseline.py             # Script to train/calibrate baseline detector
├── run_experiment.py             # Batch experiment runner
├── test_demo.py                  # Live Review 2 viva demonstration script
└── requirements.txt              # Project dependencies
```

---

## 🚀 Quickstart & Demo Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Live Review 2 Demo
Run the self-contained demonstration script:
```bash
python test_demo.py
```
This script will:
1. Initialize the baseline detector (Layer A).
2. Take a malicious PDF and display its baseline prediction and key features.
3. Apply each of the 3 structural mutations at controlled intensities.
4. Pass each mutated file through the **Safety & Reachability Gatekeeper**.
5. Re-run the detector and show the exact feature drift and confidence drop.
6. Print the **Detector Fragility Report**.

### 3. Run Experiments Across Multiple Samples
```bash
python run_experiment.py --samples 5
```

---

## 🛡️ Critical Viva Questions & Prepared Answers

> **Q1: "Your detector can be fooled — why not just build a robust one instead?"**  
> **Answer:** Robustness cannot be engineered without first measuring what breaks. You can't fix what hasn't been systematically diagnosed. This project is the *diagnostic step* — our per-feature stability results form the empirical blueprint for which features a hardened detector should rely upon (e.g. JavaScript presence, structural object relationships) and which volatile features it should deprioritize (e.g. file size, metadata fields). In security literature, measurement/attack papers and defense papers are separate, sequential milestones.

> **Q2: "How do you know your mutation didn't just destroy the malicious functionality instead of testing robustness?"**  
> **Answer:** Every mutated file must pass our automated two-stage **Structural Validity Gatekeeper** before entering results. We verify: (1) that the file parses cleanly without corruption, and (2) that the execution trigger (such as `/Root -> /OpenAction` pointing to a valid `/JavaScript` stream) is still structurally intact and reachable. Any file where the payload is neutralized is rejected from the evaluation so we don't mistake broken malware for feature fragility.

> **Q3: "Isn't 'detectors can be evaded' already known in the literature?"**  
> **Answer:** Yes, but existing evasion literature (e.g., EvadeML, genetic algorithms, gradient-based attacks) studies *deliberately optimized, mathematically adversarial attacks* designed against a specific model. We study a different, more pervasive threat: whether classifiers withstand *routine, non-adversarial structural noise* generated by standard document processing tools. Furthermore, we report findings as **per-feature stability**, not a single aggregate accuracy number.
