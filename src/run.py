"""Score every benchmark row with an instruction-tuned LLM.

The prediction is the option letter (A-D) with the highest next-token
probability after the chat prompt, so no free-form output is parsed.

Usage:
  python src/run.py --data data/items.jsonl --model Qwen/Qwen2.5-3B-Instruct --prompt neutral
  python src/run.py --data data/items.jsonl --all       # every model x prompt in config.yaml
"""

import argparse
import json
import os
import platform
import time

import yaml

LETTERS = ["A", "B", "C", "D"]

SYSTEM = "You are a careful financial analyst."

INSTRUCTION = {
    "neutral": "Read the financial note and answer the multiple-choice question.",
    "instructed": ("Read the financial note and answer the multiple-choice question. "
                   "Use only the information in the note. If the note does not state the requested value, "
                   "choose the option saying that the value cannot be determined."),
}


def build_messages(row, prompt):
    opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(row["options"]))
    user = (f"{INSTRUCTION[prompt]}\n\n{row['note']}\n\n"
            f"Question: {row['question']}\n{opts}\n\n"
            "Answer with the letter of the correct option only.")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def letter_token_ids(tok):
    ids = []
    for c in LETTERS:
        enc = tok.encode(c, add_special_tokens=False)
        assert len(enc) == 1, f"letter {c} is not a single token: {enc}"
        ids.append(enc[0])
    return ids


def run(rows, model_name, prompt, batch_size, dtype_name, out_path):
    import torch
    import transformers
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(0)
    dtype = getattr(torch, dtype_name)
    tok = AutoTokenizer.from_pretrained(model_name)
    tok.padding_side = "left"  # so that position -1 is the last real token of every prompt
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype, device_map="cuda").eval()
    ids = letter_token_ids(tok)

    texts = [tok.apply_chat_template(build_messages(r, prompt), tokenize=False, add_generation_prompt=True)
             for r in rows]

    out = []
    t0 = time.time()
    with torch.no_grad():
        for s in tqdm(range(0, len(rows), batch_size), desc=f"{model_name.split('/')[-1]} / {prompt}"):
            enc = tok(texts[s:s + batch_size], return_tensors="pt", padding=True).to(model.device)
            logits = model(**enc).logits[:, -1, ids].float()
            probs = torch.softmax(logits, dim=-1).cpu().tolist()
            for r, p in zip(rows[s:s + batch_size], probs):
                pred = LETTERS[max(range(4), key=lambda i: p[i])]
                kind = "v" if pred == r["v_letter"] else "unk" if pred == r["unk_letter"] else "distractor"
                out.append({
                    "item_id": r["item_id"], "condition": r["condition"], "axis": r["axis"],
                    "level": r["level"], "probe_position": r["probe_position"], "style": r["style"],
                    "gold": r["gold"], "v_letter": r["v_letter"], "unk_letter": r["unk_letter"],
                    "pred": pred, "pred_kind": kind, "correct": int(pred == r["gold"]),
                    "probs": dict(zip(LETTERS, p)),
                    "model": model_name, "prompt": prompt,
                })

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    meta = {
        "model": model_name, "prompt": prompt, "n_rows": len(out), "seconds": round(time.time() - t0, 1),
        "torch": torch.__version__, "transformers": transformers.__version__, "python": platform.python_version(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, "dtype": dtype_name,
    }
    with open(out_path.replace(".jsonl", ".meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(f"wrote {len(out)} predictions to {out_path} ({meta['seconds']} s)")


def out_name(results_dir, model_name, prompt):
    return os.path.join(results_dir, f"{model_name.split('/')[-1]}__{prompt}.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--data", default="data/items.jsonl")
    ap.add_argument("--results", default=None, help="output folder (default: results/ or results_pilot/)")
    ap.add_argument("--model", default=None)
    ap.add_argument("--prompt", choices=list(INSTRUCTION), default=None)
    ap.add_argument("--all", action="store_true", help="run every model x prompt listed in the config")
    ap.add_argument("--show-prompt", action="store_true", help="print the first prompt and exit")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))

    rows = [json.loads(l) for l in open(args.data)]
    results_dir = args.results or ("results_pilot" if "pilot" in args.data else "results")

    if args.show_prompt:
        for m in build_messages(rows[0], args.prompt or "neutral"):
            print(f"[{m['role']}]\n{m['content']}\n")
        return

    jobs = ([(m, p) for m in cfg["models"] for p in cfg["prompts"]] if args.all
            else [(args.model or cfg["models"][0], args.prompt or cfg["prompts"][0])])
    for model_name, prompt in jobs:
        run(rows, model_name, prompt, cfg["batch_size"], cfg["dtype"], out_name(results_dir, model_name, prompt))
        import gc, torch
        gc.collect(); torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
