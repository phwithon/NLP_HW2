"""Compute every number, table, figure and example reported in the paper.

Usage:
  python src/analyze.py                                   # results/ -> outputs/
  python src/analyze.py --results results_pilot --data data/pilot.jsonl --out outputs_pilot

Outputs (all deterministic given config.yaml's seed):
  summary.csv            per model x prompt x condition: rates with 95% CIs
  deltas.csv             paired differences vs. each presence baseline (IRR, IRR_usd) and
                         near-minus-far, with CIs and decisions; plus IRR_usd - IRR
  hypotheses.md          decision for each hypothesis, model and prompt
  table_main.tex         Table: substitution / abstention rate per condition (main prompt)
  table_delta.tex        Table: Delta vs. IRR per axis and level (main prompt)
  table_irr.tex          Table: the two presence baselines and Delta vs. each (main prompt)
  table_baselines.tex    Table: reference strategies vs. models (main prompt)
  table_ablation.tex     Table: prompt ablation
  table_position.tex     Table: substitution by probe-fact position and by v's option letter
  fig_delta.pdf/.png     Figure: Delta per axis and level with CIs
  examples.md / .tex     random examples: n/2 drawn from errors, n/2 from correct predictions
"""

import argparse
import json
import os
import re

import numpy as np
import pandas as pd
import yaml

AXES = ["period", "metric", "entity", "scope"]
NEAR_FAR = ["near", "far"]
COND_ORDER = ["ANS", "IRR", "IRR_usd"] + [f"{a}_{l}" for a in AXES for l in NEAR_FAR]
COND_LABEL = {
    "ANS": "ANS (answer present)", "IRR": "IRR (unrelated figure)",
    "IRR_usd": "IRR-USD (unrelated dollar figure)",
    "period_near": "Period: previous year", "period_far": "Period: five years earlier",
    "metric_near": "Metric: operating income", "metric_far": "Metric: revenue",
    "entity_near": "Entity: subsidiary", "entity_far": "Entity: unrelated company",
    "scope_near": "Scope: fourth quarter", "scope_far": "Scope: one segment",
}
# Colours: slots 1-2 of the dataviz reference categorical palette (validated pair).
NEAR_COLOR, FAR_COLOR, INK, MUTED = "#2a78d6", "#eb6834", "#222222", "#8a8a85"


# ---------------------------------------------------------------- statistics
def item_matrix(df, value):
    """items x conditions matrix of a 0/1 indicator (rows aligned by item_id)."""
    m = df.pivot_table(index="item_id", columns="condition", values=value, aggfunc="first")
    return m.reindex(columns=COND_ORDER)


def boot_idx(n_items, B, seed):
    return np.random.default_rng(seed).integers(0, n_items, size=(B, n_items))


def mean_ci(x, idx):
    x = np.asarray(x, dtype=float)
    stats = x[idx].mean(axis=1)
    return x.mean(), np.percentile(stats, 2.5), np.percentile(stats, 97.5)


def pct(x):
    return f"{100 * x:.1f}"


def fmt_ci(m, lo, hi, signed=False):
    s = "+" if signed and m > 0 else ""
    return f"{s}{100 * m:.1f} [{100 * lo:.1f}, {100 * hi:.1f}]"


def short(model):
    return model.split("/")[-1].replace("-Instruct", "")


# Presence baselines. IRR (shares outstanding, no "$") is the primary baseline fixed in the
# proposal; IRR_usd (inventories, "$v million") matches the surface form of the near-miss
# probes and of the option text, so Delta vs. IRR_usd removes any exact-string-match effect.
BASELINES = ["IRR", "IRR_usd"]
PRIMARY = "IRR"


def decide(lo, hi, interpretable):
    if not interpretable:
        return "uninterpretable (ANS accuracy below threshold)"
    if lo > 0:
        return "supported"
    if hi < 0:
        return "reversed"
    return "not supported"


# ---------------------------------------------------------------- analysis
def analyze_run(df, B, seed, ans_min):
    """All statistics for one model x prompt run."""
    df = df.copy()
    df["sub"] = (df["pred_kind"] == "v").astype(int)
    df["abst"] = (df["pred_kind"] == "unk").astype(int)
    df["dist"] = (df["pred_kind"] == "distractor").astype(int)
    S, A, D, C = (item_matrix(df, k) for k in ("sub", "abst", "dist", "correct"))
    n = len(S)
    idx = boot_idx(n, B, seed)  # the same resamples for every statistic of this run

    summary = []
    for c in COND_ORDER:
        row = {"condition": c, "n_items": n}
        for name, M in (("substitution", S), ("abstention", A), ("distractor", D), ("accuracy", C)):
            m, lo, hi = mean_ci(M[c].values, idx)
            row.update({name: m, f"{name}_lo": lo, f"{name}_hi": hi})
        summary.append(row)
    summary = pd.DataFrame(summary)

    ans_acc = summary.set_index("condition").loc["ANS", "accuracy"]
    interpretable = ans_acc >= ans_min

    deltas = []
    for base in BASELINES:
        b = S[base].values
        for a in AXES:
            d_near = S[f"{a}_near"].values - b
            d_far = S[f"{a}_far"].values - b
            for level, d in (("near", d_near), ("far", d_far), ("near-far", d_near - d_far)):
                m, lo, hi = mean_ci(d, idx)
                deltas.append({"baseline": base, "axis": a, "contrast": level, "delta": m, "lo": lo, "hi": hi,
                               "decision": decide(lo, hi, interpretable)})
        # pooled over the four axes (near level): one number for the ablation table
        pooled = np.mean([S[f"{a}_near"].values for a in AXES], axis=0) - b
        m, lo, hi = mean_ci(pooled, idx)
        deltas.append({"baseline": base, "axis": "pooled", "contrast": "near", "delta": m, "lo": lo, "hi": hi,
                       "decision": decide(lo, hi, interpretable)})
    # surface-form effect: same value, both unrelated, only "$v million" vs. "v million" differs
    m, lo, hi = mean_ci(S["IRR_usd"].values - S["IRR"].values, idx)
    deltas.append({"baseline": "IRR", "axis": "format", "contrast": "IRR_usd-IRR", "delta": m, "lo": lo, "hi": hi,
                   "decision": "CI excludes zero" if lo > 0 or hi < 0 else "CI includes zero"})
    return summary, pd.DataFrame(deltas), ans_acc, interpretable, df


# ---------------------------------------------------------------- tables
def latex_table(path, caption, label, header, rows, colspec, note=None, wide=False):
    """wide=True spans both columns (table*); otherwise the tabular is scaled to the column width."""
    env = "table*" if wide else "table"
    lines = [f"\\begin{{{env}}}[t]", "\\centering", "\\small"]
    if not wide:
        lines.append("\\resizebox{\\columnwidth}{!}{%")
    lines += [f"\\begin{{tabular}}{{{colspec}}}", "\\toprule", header + " \\\\", "\\midrule"]
    for r in rows:
        lines.append("\\midrule" if r == "MIDRULE" else r + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}" + ("" if wide else "}")]
    if note:
        lines.append(f"\\par\\vspace{{2pt}}\\footnotesize {note}")
    lines += [f"\\caption{{{caption}}}", f"\\label{{{label}}}", f"\\end{{{env}}}", ""]
    open(path, "w").write("\n".join(lines))


def write_tables(out, runs, models, main_prompt, prompts):
    # Main table: substitution and abstention per condition, one column pair per model.
    header = "Condition & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{short(m)}}}" for m in models)
    sub = " & " + " & ".join("Sub. & Abst." for _ in models)
    rows = [sub, "MIDRULE"]
    for c in COND_ORDER:
        cells = []
        for m in models:
            s = runs[(m, main_prompt)]["summary"].set_index("condition").loc[c]
            if c == "ANS":
                cells += [f"\\textit{{acc.}} {pct(s['accuracy'])}", pct(s["abstention"])]
            else:
                cells += [pct(s["substitution"]), pct(s["abstention"])]
        rows.append(f"{COND_LABEL[c]} & " + " & ".join(cells))
        if c == BASELINES[-1]:
            rows.append("MIDRULE")
    latex_table(os.path.join(out, "table_main.tex"),
                f"Substitution rate (Sub., \\% of items whose prediction is the probe value $v$) and abstention rate "
                f"(Abst., \\%) per condition, prompt \\textsc{{{main_prompt}}}. For \\textsc{{Ans}}, the first column is "
                f"accuracy and the second is the false-abstention rate. Chance is 25.0 for every cell.",
                "tab:main", header, rows, "l" + "rr" * len(models))

    # Delta table.
    header = "Axis & Contrast & " + " & ".join(short(m) for m in models)
    rows = []
    for a in AXES + ["pooled"]:
        for ctr in (["near", "far", "near-far"] if a != "pooled" else ["near"]):
            cells = []
            for m in models:
                d = runs[(m, main_prompt)]["deltas"]
                r = d[(d.baseline == PRIMARY) & (d.axis == a) & (d.contrast == ctr)].iloc[0]
                star = "$^{*}$" if r["lo"] > 0 or r["hi"] < 0 else ""
                cells.append(fmt_ci(r["delta"], r["lo"], r["hi"], signed=True) + star)
            name = {"near": "$\\Delta_{\\text{near}}$", "far": "$\\Delta_{\\text{far}}$",
                    "near-far": "$\\Delta_{\\text{near}}-\\Delta_{\\text{far}}$"}[ctr]
            rows.append(f"{a.capitalize() if ctr == 'near' else ''} & {name} & " + " & ".join(cells))
        if a == "scope":
            rows.append("MIDRULE")
    latex_table(os.path.join(out, "table_delta.tex"),
                f"Paired differences in substitution rate relative to \\textsc{{Irr}} (percentage points, 95\\% bootstrap "
                f"CI over base items), prompt \\textsc{{{main_prompt}}}. $^{{*}}$: CI excludes zero. "
                f"\\emph{{Pooled}} averages the four near-miss conditions.",
                "tab:delta", header, rows, "ll" + "r" * len(models))

    # Baselines: reference strategies (computed analytically) vs. models.
    header = "Strategy & ANS acc. & Sub.\\ (IRR) & Sub.\\ (near-miss) & Abst.\\ (no answer)"
    rows = ["Uniform random choice & 25.0 & 25.0 & 25.0 & 25.0",
            "Always pick the context figure & 100.0 & 100.0 & 100.0 & 0.0",
            "Always abstain & 0.0 & 0.0 & 0.0 & 100.0", "MIDRULE"]
    for m in models:
        s = runs[(m, main_prompt)]["summary"].set_index("condition")
        near = [f"{a}_near" for a in AXES]
        no_ans = [c for c in COND_ORDER if c != "ANS"]
        rows.append(f"{short(m)} & {pct(s.loc['ANS', 'accuracy'])} & {pct(s.loc['IRR', 'substitution'])} & "
                    f"{pct(s.loc[near, 'substitution'].mean())} & {pct(s.loc[no_ans, 'abstention'].mean())}")
    latex_table(os.path.join(out, "table_baselines.tex"),
                f"Reference strategies and models (prompt \\textsc{{{main_prompt}}}, \\%). Sub.\\ (near-miss) averages "
                f"the four near conditions; Abst.\\ averages all ten conditions without an answer.",
                "tab:baselines", header, rows, "lrrrr", wide=True)

    # Prompt ablation.
    header = "Model & Prompt & ANS acc. & False abst. & Sub.\\ (IRR) & Pooled $\\Delta_{\\text{near}}$"
    rows = []
    for m in models:
        for p in prompts:
            r = runs[(m, p)]
            s = r["summary"].set_index("condition")
            d = r["deltas"]
            pooled = d[(d.baseline == PRIMARY) & (d.axis == "pooled")].iloc[0]
            rows.append(f"{short(m) if p == prompts[0] else ''} & \\textsc{{{p}}} & {pct(s.loc['ANS', 'accuracy'])} & "
                        f"{pct(s.loc['ANS', 'abstention'])} & {pct(s.loc['IRR', 'substitution'])} & "
                        f"{fmt_ci(pooled['delta'], pooled['lo'], pooled['hi'], signed=True)}")
    latex_table(os.path.join(out, "table_ablation.tex"),
                "Effect of the explicit abstention instruction (\\%; $\\Delta$ in percentage points with 95\\% CI).",
                "tab:ablation", header, rows, "llrrrr", wide=True)

    # Presence baselines: does matching the option string matter, and does H1 survive the stricter baseline?
    header = ("Model & Sub.\\ (IRR) & Sub.\\ (IRR-USD) & IRR-USD $-$ IRR & "
              "Pooled $\\Delta_{\\text{near}}$ vs.\\ IRR & Pooled $\\Delta_{\\text{near}}$ vs.\\ IRR-USD")
    rows = []
    for m in models:
        r = runs[(m, main_prompt)]
        s, d = r["summary"].set_index("condition"), r["deltas"]
        fm = d[d.axis == "format"].iloc[0]
        cells = [pct(s.loc["IRR", "substitution"]), pct(s.loc["IRR_usd", "substitution"]),
                 fmt_ci(fm["delta"], fm["lo"], fm["hi"], signed=True)]
        for base in BASELINES:
            pr = d[(d.baseline == base) & (d.axis == "pooled")].iloc[0]
            cells.append(fmt_ci(pr["delta"], pr["lo"], pr["hi"], signed=True))
        rows.append(f"{short(m)} & " + " & ".join(cells))
    latex_table(os.path.join(out, "table_irr.tex"),
                f"The two presence baselines (prompt \\textsc{{{main_prompt}}}, \\%; differences in percentage points "
                f"with 95\\% CI). IRR prints $v$ as an unrelated count (``$v$ million'' shares), IRR-USD as an unrelated "
                f"dollar amount (``\\$$v$ million'' inventories) that matches the option text exactly.",
                "tab:irr", header, rows, "lrrrrr", wide=True)

    # Position analysis (main prompt, near-miss conditions only).
    header = "Model & Factor & " + " & ".join(["1", "2", "3", "4"])
    rows = []
    for m in models:
        df = runs[(m, main_prompt)]["df"]
        near = df[df.condition.isin([f"{a}_near" for a in AXES])]
        by_pos = near.groupby("probe_position")["sub"].mean().reindex(range(4))
        by_let = near.groupby("v_letter")["sub"].mean().reindex(list("ABCD"))
        rows.append(f"{short(m)} & Probe-fact position & " + " & ".join(pct(x) for x in by_pos))
        rows.append(f" & Option letter of $v$ (A--D) & " + " & ".join(pct(x) for x in by_let))
    latex_table(os.path.join(out, "table_position.tex"),
                f"Substitution rate (\\%) in the four near-miss conditions by the position of the probe fact in the note "
                f"and by the option letter of $v$ (prompt \\textsc{{{main_prompt}}}). Probe position is counterbalanced "
                f"(30 items each) but coincides with note style (positions 1, 3: list; 2, 4: prose); the option letter "
                f"of $v$ is randomized per item, not balanced.",
                "tab:position", header, rows, "llrrrr")


# ---------------------------------------------------------------- figure
def write_figure(out, runs, models, main_prompt):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "serif", "font.size": 7.5, "axes.edgecolor": MUTED,
                         "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
    fig, axs = plt.subplots(1, len(models), figsize=(3.4, 2.5), sharey=True, squeeze=False)
    x = np.arange(len(AXES))
    w = 0.36
    for ax, m in zip(axs[0], models):
        d = runs[(m, main_prompt)]["deltas"]
        d = d[d.baseline == PRIMARY]
        for k, (lvl, col, hatch) in enumerate((("near", NEAR_COLOR, None), ("far", FAR_COLOR, "////"))):
            r = d[d.contrast == lvl].set_index("axis").reindex(AXES)
            y = 100 * r["delta"].values
            err = 100 * np.vstack([r["delta"] - r["lo"], r["hi"] - r["delta"]])
            ax.bar(x + (k - 0.5) * w, y, w * 0.92, color=col, hatch=hatch, edgecolor="white", linewidth=0.6,
                   label=lvl, zorder=2)
            ax.errorbar(x + (k - 0.5) * w, y, yerr=err, fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.5, zorder=3)
        ax.axhline(0, color=MUTED, linewidth=0.8, zorder=1)
        ax.set_xticks(x, [a.capitalize() for a in AXES], fontsize=6.5, rotation=30, ha="right", rotation_mode="anchor")
        ax.set_title(short(m), color=INK)
        ax.grid(axis="y", color="#e6e6e3", linewidth=0.6, zorder=0)
        ax.spines[["top", "right"]].set_visible(False)
    axs[0][0].set_ylabel("$\\Delta$ substitution vs. IRR (pp)")
    handles, labels = axs[0][0].get_legend_handles_labels()
    fig.legend(handles, [f"{l} variant" for l in labels], loc="lower center", ncol=2, frameon=False,
               fontsize=7, handlelength=1.2, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(out, f"fig_delta.{ext}"), dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- examples
def write_examples(out, runs, models, main_prompt, data, n, seed):
    """Random rows (not cherry-picked) from the largest model, main prompt.

    Errors are rare for the stronger model, so a uniform sample may contain none. We therefore
    draw n/2 rows uniformly from the errors and the rest uniformly from the correct rows."""
    m = models[-1]
    df = runs[(m, main_prompt)]["df"]
    wrong, right = df[df.correct == 0], df[df.correct == 1]
    n_wrong = min(n // 2, len(wrong))
    sample = pd.concat([wrong.sample(n=n_wrong, random_state=seed),
                        right.sample(n=min(n - n_wrong, len(right)), random_state=seed)])
    sample = sample.sort_values(["item_id", "condition"])
    key = {(r["item_id"], r["condition"]): r for r in data}
    md = [f"# Randomly sampled examples\n\nModel `{m}`, prompt `{main_prompt}`, seed {seed}. "
          f"{n_wrong} rows drawn uniformly at random from the {len(wrong)} errors and {len(sample) - n_wrong} "
          f"from the {len(right)} correct predictions (no manual selection).\n"]
    tex = ["% Randomly sampled examples (uniform, seed fixed); edit layout as needed.",
           "\\begin{table*}[t]", "\\centering", "\\small",
           "\\begin{tabular}{p{0.11\\linewidth}cp{0.42\\linewidth}cccc}", "\\toprule",
           "Condition & Asked & Probe fact in the note & Gold & Pred. & $p(v)$ & $p(\\textsc{unk})$ \\\\", "\\midrule"]
    for _, r in sample.iterrows():
        row = key[(r["item_id"], r["condition"])]
        probe = [l for l in row["note"].replace(". ", ".\n").split("\n") if l.strip()][1 + row["probe_position"]]
        ok = "correct" if r["correct"] else "WRONG"
        md.append(f"## item {r['item_id']} / {r['condition']} -> {ok}\n\n```\n{row['note']}\n\nQ: {row['question']}\n" +
                  "\n".join(f"{l}. {o}" for l, o in zip("ABCD", row["options"])) +
                  f"\n```\n\ngold {r['gold']}, predicted {r['pred']} ({r['pred_kind']}); "
                  f"p = {json.dumps({k: round(v, 3) for k, v in r['probs'].items()})}\n")
        esc = probe.lstrip("- ").replace("$", "\\$").replace("%", "\\%")
        asked = "FY" + re.search(r"fiscal year (\d{4})", row["question"]).group(1)
        mark = "" if r["correct"] else "$^{\\times}$"
        tex.append(f"{COND_LABEL[r['condition']].split(' (')[0]} & {asked} & {esc} & {r['gold']} & {r['pred']}"
                   f"{mark} & {r['probs'][r['v_letter']]:.2f} & "
                   f"{r['probs'][r['unk_letter']]:.2f} \\\\")
    tex += ["\\bottomrule", "\\end{tabular}",
            f"\\caption{{Randomly sampled predictions of {short(m)} (prompt \\textsc{{{main_prompt}}}): "
            f"{n_wrong} drawn at random from its {len(wrong)} errors and {len(sample) - n_wrong} from its correct "
            "predictions; $^{\\times}$ marks errors.}", "\\label{tab:examples}", "\\end{table*}", ""]
    open(os.path.join(out, "examples.md"), "w").write("\n".join(md))
    open(os.path.join(out, "examples.tex"), "w").write("\n".join(tex))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--results", default="results")
    ap.add_argument("--data", default="data/items.jsonl")
    ap.add_argument("--out", default="outputs")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    os.makedirs(args.out, exist_ok=True)

    data = [json.loads(l) for l in open(args.data)]
    runs, all_summary, all_deltas, hyp = {}, [], [], ["# Hypothesis decisions\n"]
    models = [m for m in cfg["models"]]
    prompts = cfg["prompts"]
    for m in models:
        for p in prompts:
            path = os.path.join(args.results, f"{m.split('/')[-1]}__{p}.jsonl")
            if not os.path.exists(path):
                raise SystemExit(f"missing {path}: run src/run.py first")
            df = pd.DataFrame([json.loads(l) for l in open(path)])
            summary, deltas, ans_acc, ok, df = analyze_run(df, cfg["bootstrap_resamples"], cfg["seed"], cfg["ans_acc_min"])
            runs[(m, p)] = {"summary": summary, "deltas": deltas, "df": df}
            all_summary.append(summary.assign(model=m, prompt=p))
            all_deltas.append(deltas.assign(model=m, prompt=p))

            hyp.append(f"## {short(m)} / {p}\n\nANS accuracy {pct(ans_acc)}% "
                       f"({'interpretable' if ok else 'BELOW threshold ' + pct(cfg['ans_acc_min']) + '%: not interpretable'})\n")
            for base in BASELINES:
                hyp.append(f"Baseline {base}{' (primary)' if base == PRIMARY else ' (robustness)'}:")
                db = deltas[deltas.baseline == base]
                for a in AXES:
                    n_ = db[(db.axis == a) & (db.contrast == "near")].iloc[0]
                    g_ = db[(db.axis == a) & (db.contrast == "near-far")].iloc[0]
                    hyp.append(f"- {a}: H1 Delta_near = {fmt_ci(n_['delta'], n_['lo'], n_['hi'], True)} pp -> {n_['decision']}; "
                               f"H2 near-far = {fmt_ci(g_['delta'], g_['lo'], g_['hi'], True)} pp -> {g_['decision']}")
                hyp.append("")
            s_ = summary.set_index("condition")
            floor = [b for b in BASELINES if s_.loc[b, "substitution"] == 0]
            hyp.append(f"Presence baselines: substitution IRR {pct(s_.loc['IRR', 'substitution'])}%, "
                       f"IRR_usd {pct(s_.loc['IRR_usd', 'substitution'])}%"
                       + (f" -> {', '.join(floor)} at floor: Delta equals the raw near-miss substitution rate, "
                          "and the surface-form contrast cannot be estimated" if floor else ""))
            fm = deltas[deltas.axis == "format"].iloc[0]
            hyp.append(f"Surface form (IRR_usd - IRR) = {fmt_ci(fm['delta'], fm['lo'], fm['hi'], True)} pp -> {fm['decision']}")
            hyp.append("")

    pd.concat(all_summary).to_csv(os.path.join(args.out, "summary.csv"), index=False, float_format="%.4f")
    pd.concat(all_deltas).to_csv(os.path.join(args.out, "deltas.csv"), index=False, float_format="%.4f")
    open(os.path.join(args.out, "hypotheses.md"), "w").write("\n".join(hyp))
    main_prompt = cfg["main_prompt"]
    write_tables(args.out, runs, models, main_prompt, prompts)
    write_figure(args.out, runs, models, main_prompt)
    write_examples(args.out, runs, models, main_prompt, data, cfg["n_examples"], cfg["seed"])
    print("\n".join(hyp))
    print(f"wrote tables, figure and examples to {args.out}/")


if __name__ == "__main__":
    main()
