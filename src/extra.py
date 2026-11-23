"""Supplementary analyses reported in the paper's analysis section and appendix.

Usage (after src/analyze.py):
  python src/extra.py            # results/, results_overlap/ -> outputs/

Outputs:
  table_main_<p>.tex   the main table for every prompt other than the main one (appendix)
  table_style.tex      substitution by note style (list / prose), main prompt
  table_overlap.tex    clean templates vs. the earlier wording that embedded the target fact
  errors.csv           composition of errors per model x prompt x condition
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import (AXES, COND_LABEL, analyze_run, boot_idx, fmt_ci, latex_table, mean_ci, pct, short,
                     write_tables)

NEAR_MISS = [f"{a}_{l}" for a in AXES for l in ("near", "far")]


def load(results_dir):
    rows = []
    for p in sorted(glob.glob(os.path.join(results_dir, "*.jsonl"))):
        rows += [json.loads(l) for l in open(p)]
    df = pd.DataFrame(rows)
    df["sub"] = (df.pred_kind == "v").astype(int)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--results", default="results")
    ap.add_argument("--overlap", default="results_overlap")
    ap.add_argument("--out", default="outputs")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    models, mp, B, seed = cfg["models"], cfg["main_prompt"], cfg["bootstrap_resamples"], cfg["seed"]
    df = load(args.results)

    # --- main table for the non-main prompt(s), same layout as table_main.tex
    import tempfile, shutil
    runs = {}
    for (m, p), d in df.groupby(["model", "prompt"]):
        summary, deltas, _, _, dd = analyze_run(d.drop(columns="sub"), B, seed, cfg["ans_acc_min"])
        runs[(m, p)] = {"summary": summary, "deltas": deltas, "df": dd}
    for p in cfg["prompts"]:
        if p == mp:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            write_tables(tmp, runs, models, p, cfg["prompts"])
            tex = open(os.path.join(tmp, "table_main.tex")).read().replace("\\label{tab:main}", f"\\label{{tab:main-{p}}}")
            open(os.path.join(args.out, f"table_main_{p}.tex"), "w").write(tex)

    # --- note style: list vs. prose (items are split 60/60 by style, so CIs resample within style)
    header = "Condition & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{short(m)}}}" for m in models)
    rows = [" & " + " & ".join("List & Prose" for _ in models), "MIDRULE"]
    for c in NEAR_MISS:
        cells = []
        for m in models:
            d = df[(df.model == m) & (df.prompt == mp) & (df.condition == c)]
            for st in ("list", "prose"):
                x = d[d["style"] == st].sort_values("item_id")["sub"].values
                cells.append(pct(x.mean()))
        rows.append(f"{COND_LABEL[c]} & " + " & ".join(cells))
    latex_table(os.path.join(args.out, "table_style.tex"),
                f"Substitution rate (\\%) by note style, prompt \\textsc{{{mp}}} (60 items per style).",
                "tab:style", header, rows, "l" + "rr" * len(models))

    # --- overlap robustness: same items and predictions protocol, earlier wording of three subjects
    if os.path.isdir(args.overlap):
        ov = load(args.overlap)
        changed = ["entity_near", "entity_far", "scope_far"]
        header = "Model & Prompt & Condition & Overlap & Clean & Clean $-$ Overlap"
        rows = []
        for m in models:
            for p in cfg["prompts"]:
                for c in changed:
                    a = ov[(ov.model == m) & (ov.prompt == p) & (ov.condition == c)].sort_values("item_id")["sub"].values
                    b = df[(df.model == m) & (df.prompt == p) & (df.condition == c)].sort_values("item_id")["sub"].values
                    mm, lo, hi = mean_ci(b - a, boot_idx(len(a), B, seed))
                    ptag = ("\\textsc{" + p + "}") if c == changed[0] else ""
                    rows.append(f"{short(m) if (p, c) == (cfg['prompts'][0], changed[0]) else ''} & "
                                f"{ptag} & {COND_LABEL[c]} & "
                                f"{pct(a.mean())} & {pct(b.mean())} & {fmt_ci(mm, lo, hi, signed=True)}")
            if m != models[-1]:
                rows.append("MIDRULE")
        latex_table(os.path.join(args.out, "table_overlap.tex"),
                    "Substitution rate (\\%) under the earlier wording of three probe subjects (\\emph{Overlap}) and under "
                    "the final wording (\\emph{Clean}); paired difference in percentage points with 95\\% CI. In the earlier "
                    "wording the target fact occurred verbatim inside the probe for \\emph{Scope: one segment} (all notes) "
                    "and \\emph{Entity: subsidiary} (list-style notes only); for \\emph{Entity: unrelated company} only the "
                    "punctuation of the subject changed. All other conditions are identical in both versions.",
                    "tab:overlap", header, rows, "lllrrr", wide=True)

    # --- error composition
    err = df[df.correct == 0].groupby(["model", "prompt", "condition", "pred_kind"]).size().rename("n").reset_index()
    err.to_csv(os.path.join(args.out, "errors.csv"), index=False)
    for m in models:
        e = err[(err.model == m) & (err.prompt == mp)]
        tot = e.n.sum()
        scope = e[e.condition.str.startswith("scope")].n.sum()
        print(f"{short(m)} / {mp}: {tot} errors, {scope} in scope conditions "
              f"({100 * scope / max(tot, 1):.1f}%), kinds {e.groupby('pred_kind').n.sum().to_dict()}")
    print(f"wrote table_style.tex, table_overlap.tex, errors.csv to {args.out}/")


if __name__ == "__main__":
    main()
