from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


INPUT = Path("/Users/mt/Downloads/1.13-1.15关卡进度.xlsx")
OUT_DIR = Path("/Users/mt/Documents/Codex/tmp/level_progress_analysis/data/period_comparison")
OUT_DIR.mkdir(parents=True, exist_ok=True)


PAY_ORDER = ["1~7", "7~50", "50~100", "100~300", "300~+∞"]


def pct(n: float, d: float) -> float:
    return float(n / d) if d else 0.0


def stage_label(value) -> str:
    if value is None or pd.isna(value):
        return ""
    v = int(value)
    if v < 100:
        return str(v)
    return f"{v // 100}-{v % 100:02d}"


def stage_order(value) -> float:
    if value is None or pd.isna(value):
        return np.nan
    v = int(value)
    if v < 100:
        return np.nan
    chapter = v // 100
    level = v % 100
    if chapter <= 0 or level <= 0:
        return np.nan
    return (chapter - 1) * 15 + level


def first_non_null(values: pd.Series):
    s = values.dropna()
    return np.nan if s.empty else s.iloc[0]


def last_non_null(values: pd.Series):
    s = values.dropna()
    return np.nan if s.empty else s.iloc[-1]


def longest_run(values: list[float]) -> tuple[int, float | None]:
    best_len = 0
    best_value = None
    cur_len = 0
    cur_value = None
    for raw in values:
        if pd.isna(raw):
            cur_len = 0
            cur_value = None
            continue
        value = int(raw)
        if value == cur_value:
            cur_len += 1
        else:
            cur_value = value
            cur_len = 1
        if cur_len > best_len:
            best_len = cur_len
            best_value = value
    return best_len, best_value


def sort_pay(df: pd.DataFrame) -> pd.DataFrame:
    order = {k: i for i, k in enumerate(PAY_ORDER)}
    return df.assign(_sort=df["付费分层"].map(order).fillna(99)).sort_values("_sort").drop(columns="_sort")


def parse_blocks(df: pd.DataFrame) -> dict:
    cols = list(df.columns)
    progress_id_idx = cols.index("游戏ID.1")
    delta_id_idx = cols.index("游戏ID.2")
    churn_idx = cols.index("流失关卡")
    return {
        "id_col": cols[0],
        "pay_col": cols[1],
        "raw_stage_cols": cols[2 : progress_id_idx - 2],
        "progress_cols": cols[progress_id_idx + 1 : churn_idx],
        "churn_col": cols[churn_idx],
        "delta_cols": cols[delta_id_idx + 1 :],
    }


def analyze_sheet(name: str, df: pd.DataFrame) -> dict:
    blocks = parse_blocks(df)
    id_col = blocks["id_col"]
    pay_col = blocks["pay_col"]
    raw = df[blocks["raw_stage_cols"]].apply(pd.to_numeric, errors="coerce")
    raw = raw.mask(raw < 100)
    progress = raw.map(stage_order)
    delta = progress.diff(axis=1)
    delta.iloc[:, 0] = progress.iloc[:, 0]
    churn = pd.to_numeric(df[blocks["churn_col"]], errors="coerce")

    row = pd.DataFrame(
        {
            "游戏ID": df[id_col],
            "付费分层": df[pay_col],
            "首日进度": progress.iloc[:, 0],
            "最高进度": progress.max(axis=1, skipna=True),
            "最终进度": progress.apply(last_non_null, axis=1),
            "记录天数": progress.count(axis=1),
            "有效新增关卡": delta.sum(axis=1, skipna=True),
            "平均每日新增": delta.mean(axis=1, skipna=True),
            "原表流失关卡": churn,
            "起始原始关卡": raw.apply(first_non_null, axis=1),
            "最高原始关卡": raw.max(axis=1, skipna=True),
            "最终原始关卡": raw.apply(last_non_null, axis=1),
        }
    )
    runs = raw.apply(lambda x: longest_run(x.tolist()), axis=1)
    row["最长连续停留天数"] = [r[0] for r in runs]
    row["最长停留原始关卡"] = [r[1] for r in runs]
    row["最终原始关卡标签"] = row["最终原始关卡"].map(stage_label)
    row["最高原始关卡标签"] = row["最高原始关卡"].map(stage_label)
    row["最长停留原始关卡标签"] = row["最长停留原始关卡"].map(stage_label)
    row["是否流失"] = row["原表流失关卡"].notna()
    row["首日到最终进度差"] = row["最终进度"] - row["首日进度"]

    n = len(row)
    pay_counts = (
        row["付费分层"].fillna("未标注").value_counts().rename_axis("付费分层").reset_index(name="人数")
    )
    pay_counts["占比"] = pay_counts["人数"] / n

    day_summary = []
    for i, col in enumerate(progress.columns):
        values = progress[col]
        day_name = "首日" if i == 0 else f"{i + 1}日"
        day_summary.append(
            {
                "天数": day_name,
                "天序": i + 1,
                "有记录人数": int(values.notna().sum()),
                "有记录率": pct(values.notna().sum(), n),
                "平均累计进度": float(values.mean()) if values.notna().any() else None,
                "中位累计进度": float(values.median()) if values.notna().any() else None,
                "P75累计进度": float(values.quantile(0.75)) if values.notna().any() else None,
            }
        )
    day_summary = pd.DataFrame(day_summary)

    delta_summary = []
    for i, col in enumerate(delta.columns):
        values = delta[col]
        day_name = "首日" if i == 0 else f"{i + 1}日"
        delta_summary.append(
            {
                "天数": day_name,
                "天序": i + 1,
                "有新增记录人数": int(values.notna().sum()),
                "平均新增关卡": float(values.mean()) if values.notna().any() else None,
                "中位新增关卡": float(values.median()) if values.notna().any() else None,
                "新增为0人数": int((values == 0).sum()),
                "新增为0占有记录比": pct((values == 0).sum(), values.notna().sum()),
            }
        )
    delta_summary = pd.DataFrame(delta_summary)

    by_pay = (
        row.groupby("付费分层", dropna=False)
        .agg(
            人数=("游戏ID", "count"),
            流失人数=("是否流失", "sum"),
            首日进度均值=("首日进度", "mean"),
            最高进度均值=("最高进度", "mean"),
            最终进度均值=("最终进度", "mean"),
            最终进度中位数=("最终进度", "median"),
            记录天数均值=("记录天数", "mean"),
            最长停留天数均值=("最长连续停留天数", "mean"),
        )
        .reset_index()
    )
    by_pay["流失率"] = by_pay["流失人数"] / by_pay["人数"]
    by_pay = sort_pay(by_pay)

    churn_levels = (
        row[row["是否流失"]]
        .groupby(["最终原始关卡", "最终原始关卡标签"])
        .agg(流失人数=("游戏ID", "count"), 付费分层数=("付费分层", "nunique"))
        .reset_index()
        .sort_values(["流失人数", "最终原始关卡"], ascending=[False, True])
    )

    stay_levels = (
        row.dropna(subset=["最长停留原始关卡"])
        .assign(最长停留原始关卡=lambda x: x["最长停留原始关卡"].astype(int))
        .groupby("最长停留原始关卡")
        .agg(
            出现为最长停留人数=("游戏ID", "count"),
            平均连续停留天数=("最长连续停留天数", "mean"),
            最大连续停留天数=("最长连续停留天数", "max"),
        )
        .reset_index()
    )
    stay_levels["关卡标签"] = stay_levels["最长停留原始关卡"].map(stage_label)
    stay_levels = stay_levels.sort_values(
        ["出现为最长停留人数", "平均连续停留天数"], ascending=[False, False]
    )

    final_stage_dist = (
        row.groupby(["最终原始关卡", "最终原始关卡标签"], dropna=False)
        .agg(人数=("游戏ID", "count"))
        .reset_index()
        .sort_values("人数", ascending=False)
    )

    row.to_csv(OUT_DIR / f"row_metrics_{name}.csv", index=False)
    day_summary.to_csv(OUT_DIR / f"day_summary_{name}.csv", index=False)
    delta_summary.to_csv(OUT_DIR / f"delta_summary_{name}.csv", index=False)
    by_pay.to_csv(OUT_DIR / f"by_pay_{name}.csv", index=False)
    churn_levels.to_csv(OUT_DIR / f"churn_levels_{name}.csv", index=False)
    stay_levels.to_csv(OUT_DIR / f"stay_levels_{name}.csv", index=False)
    final_stage_dist.to_csv(OUT_DIR / f"final_stage_dist_{name}.csv", index=False)

    return {
        "sheet": name,
        "players": n,
        "raw_stage_days": len(blocks["raw_stage_cols"]),
        "progress_days": len(progress.columns),
        "delta_days": len(delta.columns),
        "pay_counts": pay_counts.to_dict(orient="records"),
        "first_day_mean": float(row["首日进度"].mean()),
        "first_day_median": float(row["首日进度"].median()),
        "final_progress_mean": float(row["最终进度"].mean()),
        "final_progress_median": float(row["最终进度"].median()),
        "highest_progress_mean": float(row["最高进度"].mean()),
        "highest_progress_median": float(row["最高进度"].median()),
        "record_days_mean": float(row["记录天数"].mean()),
        "record_days_median": float(row["记录天数"].median()),
        "churn_players": int(row["是否流失"].sum()),
        "churn_rate": pct(row["是否流失"].sum(), n),
        "day_summary_head": day_summary.head(8).to_dict(orient="records"),
        "day_summary_tail": day_summary.tail(8).to_dict(orient="records"),
        "delta_summary_head": delta_summary.head(8).to_dict(orient="records"),
        "delta_summary_tail": delta_summary.tail(8).to_dict(orient="records"),
        "by_pay": by_pay.to_dict(orient="records"),
        "top_churn_levels": churn_levels.head(15).to_dict(orient="records"),
        "top_stay_levels": stay_levels.head(15).to_dict(orient="records"),
        "top_final_stage": final_stage_dist.head(15).to_dict(orient="records"),
    }


def main():
    sheets = pd.read_excel(INPUT, sheet_name=None)
    summaries = [analyze_sheet(name, df) for name, df in sheets.items()]
    with open(OUT_DIR / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
