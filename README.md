# When the Number Is Missing: Near-Miss Figures and LLM Abstention in Financial QA

Code and data for a controlled diagnostic benchmark that tests whether LLMs report a
similar-looking figure from the context instead of abstaining when the requested
financial figure is absent.

Each base item asks for the **net income of a fictitious company in a given fiscal year**.
The note always contains four numeric facts; one of them, the *probe fact*, carries the
same value *v* in every condition, and only its label changes:

| Condition | Probe fact | Correct answer |
|---|---|---|
| `ANS` | net income of the company in the asked year | *v* |
| `IRR` | shares outstanding (same number, unrelated quantity, printed as "v million") | cannot be determined |
| `IRR_usd` | inventories (same number, unrelated dollar amount, printed as "$v million") | cannot be determined |
| `period_near` / `period_far` | net income one / five years earlier | cannot be determined |
| `metric_near` / `metric_far` | operating income / revenue | cannot be determined |
| `entity_near` / `entity_far` | net income of a subsidiary / of an unrelated company | cannot be determined |
| `scope_near` / `scope_far` | fourth-quarter net income / net income of one segment | cannot be determined |

The four options (v, two values absent from the note, and "The value cannot be determined
from the note") are identical across the eleven conditions of an item, so the paired difference
between a near-miss condition and `IRR` isolates the effect of resemblance from the mere
presence of a number.

`IRR` is the primary presence baseline fixed in the proposal. Because it prints v without "$",
it does not match the option text "$v million" exactly, whereas every near-miss probe does.
`IRR_usd` closes this gap: it is an unrelated dollar amount printed exactly like the option, so
the difference vs. `IRR_usd` cannot be explained by exact string matching, and `IRR_usd - IRR`
measures the surface-form effect on its own. Adding `IRR_usd` leaves the other 1,200 rows of
the benchmark byte-identical.

## Repository layout

```
config.yaml          every setting that affects reported numbers (seeds, sizes, models, prompts)
src/generate.py      builds the benchmark and checks its design invariants
src/run.py           next-token scoring of option letters A-D with a Hugging Face model
src/analyze.py       rates, paired bootstrap CIs, hypothesis decisions, LaTeX tables, figure, examples
src/extra.py         supplementary analyses: note style, overlap robustness check, error composition
colab_run.ipynb      runs the whole pipeline on Google Colab
data/                generated benchmark (items.jsonl: main, pilot.jsonl: pilot, items_overlap.jsonl: robustness check)
results/             model predictions (+ .meta.json with library versions, GPU and runtime)
results_pilot/       pilot predictions; results_overlap/: predictions for the overlap check
outputs/             tables, figure and examples used in the paper
```

## Environment

- Google Colab, NVIDIA T4 GPU (16 GB), Python 3.10 or later
- `pip install -r requirements.txt` (PyTorch is preinstalled on Colab)
- Models: `Qwen/Qwen2.5-1.5B-Instruct`, `Qwen/Qwen2.5-3B-Instruct`, loaded in float16
- The exact `torch` / `transformers` versions and the GPU used for each run are written to
  `results/<model>__<prompt>.meta.json`.

The fastest way to reproduce everything is to open `colab_run.ipynb` in Colab with a T4
runtime and run all cells; the first cell asks you to upload this repository as a zip file.

## Reproducing the results

```bash
# 1. benchmark (120 items x 11 conditions = 1,320 rows; deterministic)
python src/generate.py --split main            # -> data/items.jsonl

# 2. predictions for 2 models x 2 prompts (GPU)
python src/run.py --data data/items.jsonl --all    # -> results/

# 3. every table, the figure and the examples
python src/analyze.py                              # -> outputs/

# 4. supplementary analyses (note style, overlap robustness check, error composition)
python src/extra.py                                # -> outputs/
```

All predictions used in the paper are included in `results/`, `results_pilot/` and
`results_overlap/`, so steps 3-4 reproduce every table and figure without a GPU.

| Paper element | File produced by step 3 |
|---|---|
| Main results (substitution / abstention per condition) | `outputs/table_main.tex` |
| Paired differences vs. IRR, hypothesis tests | `outputs/table_delta.tex`, `outputs/hypotheses.md` |
| Presence baselines IRR vs. IRR-USD (surface-form control) | `outputs/table_irr.tex` |
| Reference strategies (baselines) | `outputs/table_baselines.tex` |
| Prompt ablation (with / without abstention instruction) | `outputs/table_ablation.tex` |
| Position analysis | `outputs/table_position.tex` |
| Figure: Δ per axis and level | `outputs/fig_delta.pdf` |
| Randomly sampled examples (half drawn at random from errors, half from correct predictions) | `outputs/examples.tex`, `outputs/examples.md` |
| All numbers in machine-readable form | `outputs/summary.csv`, `outputs/deltas.csv` |
| Main table under the other prompt (appendix) | `outputs/table_main_neutral.tex` (step 4) |
| Substitution by note style (list / prose) | `outputs/table_style.tex` (step 4) |
| Overlap robustness check | `outputs/table_overlap.tex` (step 4) |
| Error composition | `outputs/errors.csv` (step 4) |

### Overlap robustness check

An earlier wording of three probe subjects embedded the target fact verbatim (for instance
"The Healthcare segment of **Ossora Group reported net income of $773 million in fiscal year
2024**"). The final benchmark rewords them, and `generate.py` now rejects any note that contains
the target fact verbatim. The earlier version is kept only for the robustness check in the paper:

```bash
python src/generate.py --split main --templates overlap --out data/items_overlap.jsonl
python src/run.py --data data/items_overlap.jsonl --all --results results_overlap   # GPU; predictions included
python src/extra.py                                                                 # -> outputs/table_overlap.tex
```

To run a single model and prompt: `python src/run.py --model Qwen/Qwen2.5-3B-Instruct --prompt instructed`.
To inspect the exact prompt: `python src/run.py --show-prompt --prompt instructed`.

### Pilot

The abstention-instruction wording was checked on a separate pilot set generated with a
different seed, so the main benchmark was not used for tuning:

```bash
python src/generate.py --split pilot                         # -> data/pilot.jsonl
python src/run.py --data data/pilot.jsonl --all              # -> results_pilot/
python src/analyze.py --results results_pilot --data data/pilot.jsonl --out outputs_pilot
```

## Random seeds and determinism

| What | Seed (in `config.yaml`) |
|---|---|
| Main benchmark generation, option order | `seed: 2026` |
| Pilot benchmark generation | `pilot_seed: 7` |
| Bootstrap resampling (B = 2,000) and example sampling | `seed: 2026` |
| Model inference | none needed: scoring takes the arg-max of next-token probabilities, no sampling |

`generate.py`, `analyze.py` and `extra.py` are deterministic. Model scores can differ in the last
digits across GPU types, library versions or batch composition (float16); the versions used are
recorded in the `.meta.json` files (Colab T4, Python 3.13.16, torch 2.14.1+cu130,
transformers 5.22.1). Across two separate runs on the same setup, 3,839 of the 3,840 predictions
for conditions shared by `results/` and `results_overlap/` were identical; the one change was a
near-tie (p = 0.48 vs. 0.52 between two options).

## Design checks

`generate.py` refuses to write the benchmark if any invariant fails: *v* appears exactly once
in every note, the two distractor values never appear in a note, v is printed exactly as its option text in every condition except `IRR`, the target fact (the `ANS` probe) never occurs verbatim inside the note of any other condition (so no near-miss probe contains an exact copy of the answer sentence), the options and the probe
position are identical across the eleven conditions of an item, and all conditions of an item
contain the same number of facts. Probe position (1-4) and note style (list / prose) are
balanced across items; the option order is random per item.
