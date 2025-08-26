import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_CSV = Path("data/processed/products.csv")
FIG_DIR = Path("eda/figures")

def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_CSV.exists():
        print("[ERR] No data found. Run the collector first.")
        return

    df = pd.read_csv(DATA_CSV)
    # basic cleaning
    df["price_min"] = pd.to_numeric(df.get("price_min"), errors="coerce")
    df["price_max"] = pd.to_numeric(df.get("price_max"), errors="coerce")
    df["marketplace"] = df.get("marketplace").fillna("unknown")

    print("[SUMMARY]")
    print(df.describe(include="all").transpose().head(15))

    # plot top categories
    ct = df["category"].value_counts().head(20)
    plt.figure(figsize=(8,5))
    ct.plot(kind="bar")
    plt.title("Top categories (count)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "top_categories.png")

    # price min histogram
    plt.figure(figsize=(8,5))
    df["price_min"].dropna().plot(kind="hist", bins=40)
    plt.title("Price min distribution")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "price_min_hist.png")

    # top suppliers
    s = df["supplier_name"].fillna("Unknown").value_counts().head(15)
    plt.figure(figsize=(8,5))
    s.plot(kind="bar")
    plt.title("Top suppliers")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "top_suppliers.png")

    print(f"[OK] Figures saved to {FIG_DIR.resolve()}")

if __name__ == "__main__":
    main()
