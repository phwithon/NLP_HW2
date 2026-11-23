"""Generate the near-miss financial abstention benchmark.

Each base item asks for the net income of a fictitious company c in fiscal year y.
The accompanying note contains four numeric facts. Exactly one of them, the
*probe fact*, carries the value v in every condition; only its label changes:

  ANS              the probe fact is the target itself (net income of c in y)
  IRR              same company and year, same number, unrelated quantity
                   (shares outstanding, in millions, printed without "$") -> presence baseline
  IRR_usd          same company and year, same number, unrelated dollar amount
                   (inventories, "$v million") -> presence baseline whose surface
                   form matches the near-miss conditions and the option text exactly
  period/near|far  net income of c in y-1 | y-5
  metric/near|far  operating income | revenue of c in y
  entity/near|far  net income of a named subsidiary of c | of an unrelated company in y
  scope/near|far   fourth-quarter net income of c in y | net income of one segment of c in y

The four answer options are identical across the eleven conditions of an item:
v, two plausible values absent from the note, and an abstention option.

Usage:
  python src/generate.py --split main  --out data/items.jsonl
  python src/generate.py --split pilot --out data/pilot.jsonl
"""

import argparse
import json
import os
import random
import re

import yaml

CONDITIONS = [
    ("ANS", None, None),
    ("IRR", None, None),
    ("IRR_usd", None, None),
    ("period_near", "period", "near"),
    ("period_far", "period", "far"),
    ("metric_near", "metric", "near"),
    ("metric_far", "metric", "far"),
    ("entity_near", "entity", "near"),
    ("entity_far", "entity", "far"),
    ("scope_near", "scope", "near"),
    ("scope_far", "scope", "far"),
]

UNK_TEXT = "The value cannot be determined from the note"
LETTERS = ["A", "B", "C", "D"]

# Syllables for fictitious names. Generated names are checked against a small
# list of real company names; extend REAL_NAMES if you notice a collision.
PREFIXES = ["Nor", "Kel", "Ver", "Tal", "Bra", "Quil", "Mor", "Sel", "Dar", "Fen",
            "Gal", "Hal", "Ist", "Jor", "Lum", "Oss", "Pel", "Ros", "Tor", "Wyn"]
SUFFIXES = ["vane", "dris", "mont", "wick", "oria", "eth", "ana", "holt", "ford", "isk",
            "ora", "ven", "dale", "mere", "tine", "ack", "ery", "ion", "una", "eld"]
FORMS = ["Holdings", "Group", "Industries", "Corporation", "Systems", "Partners"]
SUB_FORMS = ["Logistics", "Energy", "Materials", "Software", "Retail", "Foods"]
SEGMENTS = ["Consumer Products", "Industrial Solutions", "Digital Services",
            "Healthcare", "Infrastructure", "Specialty Chemicals"]
REAL_NAMES = {"oracle", "verizon", "honda", "halliburton"}

QUESTION_TEMPLATES = [
    "What was {c}'s net income in fiscal year {y}?",
    "How much net income did {c} report for fiscal year {y}?",
    "According to the note, what was the net income of {c} in fiscal year {y}?",
]


def fictitious_name(rng, used):
    while True:
        stem = rng.choice(PREFIXES) + rng.choice(SUFFIXES)
        if stem.lower() not in REAL_NAMES and stem not in used:
            used.add(stem)
            return stem


def money(x):
    return f"${x:,} million"


def possessive(name):
    return name + ("'" if name.endswith("s") else "'s")


def probe_fact_text(row):
    """The probe fact of a row, without list bullet or final period."""
    facts = [l for l in row["note"].split(":\n", 1)[1].replace(". ", ".\n").split("\n") if l.strip()]
    return facts[row["probe_position"]].lstrip("- ").rstrip(".")


# Earlier wording of three probe subjects, kept only to reproduce the overlap robustness check
# (paper, Appendix): it embeds the target fact verbatim in scope_far (both styles) and in
# entity_near (list style). Select with --templates overlap; the main benchmark never uses it.
OVERLAP_SUBJECTS = {
    "entity_near": "{sub}, a wholly owned subsidiary of {c},",
    "entity_far": "{other}, an unrelated company,",
    "scope_far": "the {seg} segment of {c}",
}
TEMPLATES = "clean"  # set by main()


def probe_label(cond, item):
    """Label of the probe fact under a condition, as (subject, quantity, period)."""
    c, y = item["company"], item["year"]
    sub, other, seg = item["subsidiary"], item["other_company"], item["segment"]
    if TEMPLATES == "overlap" and cond in OVERLAP_SUBJECTS:
        return (OVERLAP_SUBJECTS[cond].format(sub=sub, other=other, seg=seg, c=c), "net income", f"fiscal year {y}")
    return {
        "ANS":         (c, "net income", f"fiscal year {y}"),
        "IRR":         (c, "shares outstanding", f"fiscal year {y}"),
        "IRR_usd":     (c, "inventories", f"fiscal year {y}"),
        "period_near": (c, "net income", f"fiscal year {y - 1}"),
        "period_far":  (c, "net income", f"fiscal year {y - 5}"),
        "metric_near": (c, "operating income", f"fiscal year {y}"),
        "metric_far":  (c, "revenue", f"fiscal year {y}"),
        # Subjects are worded so that the target fact ("<c>: net income, ..." / "<c> reported net
        # income ...") never occurs verbatim inside a near-miss fact; check_rows enforces this.
        "entity_near": (f"{sub} (a wholly owned subsidiary of {c})", "net income", f"fiscal year {y}"),
        "entity_far":  (f"{other} (an unrelated company)", "net income", f"fiscal year {y}"),
        "scope_near":  (c, "fourth-quarter net income", f"fiscal year {y}"),
        "scope_far":   (f"{possessive(c)} {seg} segment", "net income", f"fiscal year {y}"),
    }[cond]


def render_fact(subject, quantity, period, value_str, style):
    subject = subject[0].upper() + subject[1:]
    if style == "list":
        return f"- {subject.rstrip(',')}: {quantity}, {period}: {value_str}"
    if quantity == "number of employees":
        return f"{subject} had {value_str} employees in {period}."
    if quantity == "shares outstanding":
        return f"{subject} had {value_str} shares outstanding in {period}."
    return f"{subject} reported {quantity} of {value_str} in {period}."


def make_base_item(idx, rng, used_names):
    company = f"{fictitious_name(rng, used_names)} {rng.choice(FORMS)}"
    subsidiary = f"{fictitious_name(rng, used_names)} {rng.choice(SUB_FORMS)}"
    other_company = f"{fictitious_name(rng, used_names)} {rng.choice(FORMS)}"
    year = rng.randint(2020, 2025)
    v = rng.randint(120, 980)

    # Two distractor options absent from the note: one below and one above v.
    lo = round(v * (1 - rng.uniform(0.06, 0.15)))
    hi = round(v * (1 + rng.uniform(0.06, 0.15)))

    # Three filler facts unrelated to the question, with values far from the options.
    taken = {v, lo, hi}

    def far_value(a, b):
        while True:
            x = rng.randint(a, b)
            if all(abs(x - t) > 0.25 * t for t in taken):
                taken.add(x)
                return x

    filler_pool = [
        ("total assets", lambda: money(far_value(3000, 15000))),
        ("capital expenditure", lambda: money(far_value(40, 900))),
        ("cash and cash equivalents", lambda: money(far_value(200, 2500))),
        ("long-term debt", lambda: money(far_value(500, 6000))),
        ("number of employees", lambda: f"{far_value(1500, 40000):,}"),
    ]
    fillers = [(q, f()) for q, f in rng.sample(filler_pool, 3)]

    options = [money(v), money(lo), money(hi), UNK_TEXT]
    rng.shuffle(options)  # fixed across all conditions of this item

    return {
        "item_id": idx,
        "company": company,
        "subsidiary": subsidiary,
        "other_company": other_company,
        "segment": rng.choice(SEGMENTS),
        "year": year,
        "v": v,
        "fillers": fillers,
        "options": options,
        "probe_position": idx % 4,               # counterbalanced across items
        "style": "list" if idx % 2 == 0 else "prose",
        "question": rng.choice(QUESTION_TEMPLATES).format(c=company, y=year),
    }


def build_rows(item):
    rows = []
    v_str = money(item["v"])
    letter_of = {opt: LETTERS[i] for i, opt in enumerate(item["options"])}
    c, y = item["company"], item["year"]
    for cond, axis, level in CONDITIONS:
        subject, quantity, period = probe_label(cond, item)
        value_str = f"{item['v']:,} million" if cond == "IRR" else v_str
        probe = render_fact(subject, quantity, period, value_str, item["style"])
        facts = [render_fact(c, q, f"fiscal year {y}", val, item["style"]) for q, val in item["fillers"]]
        facts.insert(item["probe_position"], probe)
        sep = "\n" if item["style"] == "list" else " "
        note = f"Financial note on {c}:\n" + sep.join(facts)

        gold_text = v_str if cond == "ANS" else UNK_TEXT
        rows.append({
            "item_id": item["item_id"],
            "condition": cond,
            "axis": axis,
            "level": level,
            "note": note,
            "question": item["question"],
            "options": item["options"],
            "gold": letter_of[gold_text],
            "v_letter": letter_of[v_str],
            "unk_letter": letter_of[UNK_TEXT],
            "probe_position": item["probe_position"],
            "style": item["style"],
        })
    return rows


def count_amount(text, num):
    """Occurrences of '<num> million' not preceded by another digit or comma."""
    return len(re.findall(r"(?<![\d,])" + re.escape(num) + r" million", text))


def check_rows(rows):
    """Fail loudly if any design invariant is violated."""
    by_item = {}
    for r in rows:
        by_item.setdefault(r["item_id"], []).append(r)
        # v appears exactly once in the note (IRR prints it without "$", IRR_usd with "$").
        v_num = r["options"][LETTERS.index(r["v_letter"])].replace("$", "").replace(" million", "")
        assert count_amount(r["note"], v_num) == 1, (r["item_id"], r["condition"], "v count")
        # distractor options never appear in the note.
        for i, opt in enumerate(r["options"]):
            if LETTERS[i] not in (r["v_letter"], r["unk_letter"]):
                num = opt.replace("$", "").replace(" million", "")
                assert count_amount(r["note"], num) == 0, (r["item_id"], r["condition"], "distractor in note")
        # IRR_usd and the near-miss conditions print v exactly as the option text does.
        if r["condition"] != "IRR":
            assert r["options"][LETTERS.index(r["v_letter"])] in r["note"], (r["item_id"], r["condition"], "v surface form")
        # the target label (net income of c in y) appears only under ANS.
        assert r["gold"] == (r["v_letter"] if r["condition"] == "ANS" else r["unk_letter"])
    for iid, rs in by_item.items():
        assert len(rs) == len(CONDITIONS), (iid, "missing conditions")
        # the target fact (the ANS probe) never occurs verbatim inside another condition's note,
        # so no near-miss condition contains an exact copy of the answer sentence.
        target = probe_fact_text(next(r for r in rs if r["condition"] == "ANS"))
        for r in rs:
            if r["condition"] != "ANS" and TEMPLATES == "clean":
                assert target not in r["note"], (iid, r["condition"], "target fact embedded verbatim")
        assert len({tuple(r["options"]) for r in rs}) == 1, (iid, "options differ across conditions")
        assert len({r["probe_position"] for r in rs}) == 1, (iid, "probe position differs")
        # conditions of an item differ only in the probe fact: notes have equal fact counts.
        assert len({r["note"].count("\n") + r["note"].count(". ") for r in rs}) == 1, (iid, "fact count")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--split", choices=["main", "pilot"], default="main")
    ap.add_argument("--out", default=None)
    ap.add_argument("--templates", choices=["clean", "overlap"], default="clean",
                    help="'overlap' reproduces the earlier wording used only for the robustness check")
    args = ap.parse_args()
    global TEMPLATES
    TEMPLATES = args.templates
    cfg = yaml.safe_load(open(args.config))

    seed = cfg["seed"] if args.split == "main" else cfg["pilot_seed"]
    n = cfg["n_items"] if args.split == "main" else cfg["n_pilot_items"]
    out = args.out or ("data/items.jsonl" if args.split == "main" else "data/pilot.jsonl")

    rng = random.Random(seed)
    used = set()
    rows = []
    for i in range(n):
        rows.extend(build_rows(make_base_item(i, rng, used)))
    check_rows(rows)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows ({n} items x {len(CONDITIONS)} conditions) to {out} "
          f"[seed={seed}, templates={args.templates}]")


if __name__ == "__main__":
    main()
