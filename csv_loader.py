import json
from pathlib import Path
import pandas as pd

def save_data_structured(items, out_dir="data/processed", basename="products"):
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)
    jsonl_path = outp / f"{basename}.jsonl"
    csv_path = outp / f"{basename}.csv"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for it in items:
            # it is a pydantic model or dict
            if hasattr(it, "model_dump"):
                f.write(it.model_dump_json() + "\n")
            else:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")

    # create a DataFrame
    rows = []
    for it in items:
        if hasattr(it, "model_dump"):
            rows.append(it.model_dump())
        else:
            rows.append(it)
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"[SAVED] {len(rows)} rows -> {jsonl_path}, {csv_path}")
