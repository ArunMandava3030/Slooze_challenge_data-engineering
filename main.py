#src\main.py
import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List

from src.collectors.indiamart import IndiaMartCollector
from src.collectors.alibaba import AlibabaCollector
from src.parsers.models import Product, to_jsonl, to_csv
from src.utils.storage import ensure_dirs, dedupe_products

def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run(categories_file: Path, config_file: Path):
    cfg = load_yaml(config_file)
    cats = load_yaml(categories_file)

    out_dir = Path(cfg.get("output_dir", "data/processed"))
    raw_dir = Path(cfg.get("raw_dir", "data/raw"))
    ensure_dirs([out_dir, raw_dir])

    limit = int(cfg.get("limit_per_category", 100))
    delay_min = float(cfg.get("delay_min", 1.0))
    delay_max = float(cfg.get("delay_max", 2.0))
    timeout = float(cfg.get("timeout_seconds", 15))
    max_retries = int(cfg.get("max_retries", 3))
    save_raw = bool(cfg.get("save_raw_html", False))
    basename = cfg.get("output_basename", "products")

    all_products: List[Product] = []

    # IndiaMart
    im_cats = cats.get("indiamart", {})
    im = IndiaMartCollector(config=cfg)
    for cat_name, url in im_cats.items():
        print(f"[RUN] IndiaMart | {cat_name}")
        raw = im.collect(category=cat_name, category_url=url, limit=limit, save_raw=save_raw)
        for r in raw:
            try:
                p = Product(**r)
                all_products.append(p)
            except Exception as e:
                print(f"[VALIDATION] IndiaMart item skipped: {e}")

    # Alibaba
    ab_cats = cats.get("alibaba", {})
    ab = AlibabaCollector(config=cfg)
    for cat_name, url in ab_cats.items():
        print(f"[RUN] Alibaba  | {cat_name}")
        raw = ab.collect(category=cat_name, category_url=url, limit=limit, save_raw=save_raw)
        for r in raw:
            try:
                p = Product(**r)
                all_products.append(p)
            except Exception as e:
                print(f"[VALIDATION] Alibaba item skipped: {e}")

    # Dedupe
    all_products = dedupe_products(all_products)

    # Save
    out_jsonl = out_dir / f"{basename}.jsonl"
    out_csv = out_dir / f"{basename}.csv"
    to_jsonl(all_products, out_jsonl)
    to_csv(all_products, out_csv)

    print(f"[DONE] Saved {len(all_products)} products to {out_jsonl} and {out_csv}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--categories", type=str, default="categories.yaml", help="Path to categories.yaml")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()
    run(Path(args.categories), Path(args.config))
