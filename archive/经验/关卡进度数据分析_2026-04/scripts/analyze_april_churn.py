from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


INPUT = Path("/Users/mt/Downloads/1.13-1.15关卡进度.xlsx")
OUT_DIR = Path("/Users/mt/Documents/Codex/tmp/level_progress_analysis/data/april_focus")
OUT_DIR.mkdir(parents=True, exist_ok=True)

APRIL_SHEET = "4.4-4.8"
JAN_SHEETS = ["1.13-1.15", "1.09-1.11"]
PAY_ORDER = ["1~7", "7~50", "50~100", "100~300", "300~+∞"]
BASELINE_LEVEL_MAX_ORDER = 4
SIGNIFICANT_DELTA = 0.03
MIN_SIGNAL_CHURN = 5


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
    return float((chapter - 1) * 15 + level)


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
    if "付费分层" in df.columns:
        return df.assign(_sort=df["付费分层"].map(order).fillna(99)).sort_values("_sort").drop(columns="_sort")
    return df


def parse_blocks(df: pd.DataFrame) -> dict:
    cols = list(df.columns)
    progress_id_idx = cols.index("游戏ID.1")
    delta_id_idx = cols.index("游戏ID.2")
    churn_idx = cols.index("流失关卡")
    return {
        "id_col": cols[0],
        "pay_col": cols[1],
        "id1_col": "游戏ID.1",
        "id2_col": "游戏ID.2",
        "raw_stage_cols": cols[2 : progress_id_idx - 2],
        "churn_col": cols[churn_idx],
        "delta_cols": cols[delta_id_idx + 1 :],
    }


def clean_sheet(name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
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
            "批次": name,
            "游戏ID": df[id_col],
            "付费分层": df[pay_col],
            "首日进度": progress.iloc[:, 0],
            "最高进度": progress.max(axis=1, skipna=True),
            "最终进度": progress.apply(last_non_null, axis=1),
            "记录天数": progress.count(axis=1),
            "有效新增关卡": delta.clip(lower=0).sum(axis=1, skipna=True),
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
    for source in ["起始原始关卡", "最高原始关卡", "最终原始关卡", "最长停留原始关卡"]:
        row[f"{source}标签"] = row[source].map(stage_label)
        row[f"{source}序号"] = row[source].map(stage_order)
    row["是否流失"] = row["原表流失关卡"].notna()
    row["首日到最终进度差"] = row["最终进度"] - row["首日进度"]

    diagnostics = {
        "批次": name,
        "样本人数": int(len(row)),
        "原始关卡天数": int(len(blocks["raw_stage_cols"])),
        "id1不一致数": int((df[id_col] != df[blocks["id1_col"]]).sum()),
        "id2不一致数": int((df[id_col] != df[blocks["id2_col"]]).sum()),
        "第10章及以后记录数": int((raw >= 1000).sum().sum()),
        "原始0记录数": int((df[blocks["raw_stage_cols"]].apply(pd.to_numeric, errors="coerce") == 0).sum().sum()),
    }
    return row, diagnostics


def batch_summary(rows: pd.DataFrame, label: str) -> dict:
    n = len(rows)
    return {
        "批次": label,
        "人数": int(n),
        "首日平均进度": float(rows["首日进度"].mean()),
        "首日中位进度": float(rows["首日进度"].median()),
        "最终平均进度": float(rows["最终进度"].mean()),
        "最终中位进度": float(rows["最终进度"].median()),
        "平均记录天数": float(rows["记录天数"].mean()),
        "记录天数中位数": float(rows["记录天数"].median()),
        "流失人数": int(rows["是否流失"].sum()),
        "流失率": pct(rows["是否流失"].sum(), n),
        "1~7占比": pct((rows["付费分层"] == "1~7").sum(), n),
        "前四关最终停留占比": pct((rows["最终进度"] <= BASELINE_LEVEL_MAX_ORDER).sum(), n),
    }


def level_metrics(rows: pd.DataFrame, label: str) -> pd.DataFrame:
    levels = pd.concat(
        [
            rows["最终原始关卡"].dropna(),
            rows["最长停留原始关卡"].dropna(),
        ],
        ignore_index=True,
    ).dropna()
    if levels.empty:
        return pd.DataFrame()
    levels = sorted(set(int(x) for x in levels if int(x) >= 100), key=stage_order)
    records = []
    churn_rows = rows[rows["是否流失"]]
    for level in levels:
        order = stage_order(level)
        reached = int((rows["最高进度"] >= order).sum())
        churn_count = int((churn_rows["最终原始关卡"] == level).sum())
        final_count = int((rows["最终原始关卡"] == level).sum())
        stay_subset = rows[rows["最长停留原始关卡"] == level]
        stay_count = int(len(stay_subset))
        avg_stay = float(stay_subset["最长连续停留天数"].mean()) if stay_count else 0.0
        records.append(
            {
                "口径": label,
                "关卡": int(level),
                "关卡标签": stage_label(level),
                "关卡序号": order,
                "是否前四关基准段": bool(order <= BASELINE_LEVEL_MAX_ORDER),
                "到达该关人数": reached,
                "流失人数": churn_count,
                "最终停留人数": final_count,
                "最长停留人数": stay_count,
                "平均连续停留天数": avg_stay,
                "归一化流失率": pct(churn_count, reached),
            }
        )
    return pd.DataFrame(records)


def pay_summary(rows: pd.DataFrame, label: str) -> pd.DataFrame:
    summary = (
        rows.groupby("付费分层", dropna=False)
        .agg(
            人数=("游戏ID", "count"),
            流失人数=("是否流失", "sum"),
            首日进度均值=("首日进度", "mean"),
            最终进度均值=("最终进度", "mean"),
            最终进度中位数=("最终进度", "median"),
            记录天数均值=("记录天数", "mean"),
            最长停留天数均值=("最长连续停留天数", "mean"),
        )
        .reset_index()
    )
    summary["批次"] = label
    summary["流失率"] = summary["流失人数"] / summary["人数"]
    return sort_pay(summary[["批次", "付费分层", "人数", "流失人数", "流失率", "首日进度均值", "最终进度均值", "最终进度中位数", "记录天数均值", "最长停留天数均值"]])


def classify(row: pd.Series, median_rate: float) -> str:
    if bool(row["是否前四关基准段"]):
        return "前四关基准段"
    if row["4月流失人数"] >= MIN_SIGNAL_CHURN and row["4月变化"] >= SIGNIFICANT_DELTA:
        return "4月新增/加重问题"
    if row["4月流失人数"] >= MIN_SIGNAL_CHURN and row["1月基线流失人数"] >= MIN_SIGNAL_CHURN:
        return "长期卡点"
    if row["4月流失人数"] >= MIN_SIGNAL_CHURN and row["4月归一化流失率"] <= median_rate:
        return "自然人数堆积"
    if row["4月流失人数"] > 0:
        return "低样本观察"
    return "无明显流失"


def build_comparison(level_by_label: dict[str, pd.DataFrame]) -> pd.DataFrame:
    apr = level_by_label[APRIL_SHEET].copy()
    jan = level_by_label["1月基线"].copy()
    jan113 = level_by_label["1.13-1.15"].copy()
    jan109 = level_by_label["1.09-1.11"].copy()

    base_cols = ["关卡", "关卡标签", "关卡序号", "是否前四关基准段"]
    comp = apr[base_cols].copy()
    rename_map = {
        "到达该关人数": "4月到达人数",
        "流失人数": "4月流失人数",
        "最终停留人数": "4月最终停留人数",
        "最长停留人数": "4月最长停留人数",
        "平均连续停留天数": "4月平均连续停留天数",
        "归一化流失率": "4月归一化流失率",
    }
    comp = comp.merge(apr[["关卡", *rename_map.keys()]].rename(columns=rename_map), on="关卡", how="left")

    for source, prefix in [
        (jan, "1月基线"),
        (jan113, "1.13"),
        (jan109, "1.09"),
    ]:
        cols = ["关卡", "到达该关人数", "流失人数", "最终停留人数", "最长停留人数", "平均连续停留天数", "归一化流失率"]
        comp = comp.merge(
            source[cols].rename(
                columns={
                    "到达该关人数": f"{prefix}到达人数",
                    "流失人数": f"{prefix}流失人数",
                    "最终停留人数": f"{prefix}最终停留人数",
                    "最长停留人数": f"{prefix}最长停留人数",
                    "平均连续停留天数": f"{prefix}平均连续停留天数",
                    "归一化流失率": f"{prefix}归一化流失率",
                }
            ),
            on="关卡",
            how="left",
        )

    count_cols = [c for c in comp.columns if c.endswith("人数")]
    rate_cols = [c for c in comp.columns if c.endswith("率")]
    comp[count_cols] = comp[count_cols].fillna(0).astype(int)
    comp[rate_cols] = comp[rate_cols].fillna(0.0)
    comp["4月变化"] = comp["4月归一化流失率"] - comp["1月基线归一化流失率"]

    active = comp[(comp["4月流失人数"] > 0) & (~comp["是否前四关基准段"])]
    median_rate = float(active["4月归一化流失率"].median()) if not active.empty else 0.0
    max_churn = max(float(comp["4月流失人数"].max()), 1.0)
    comp["优先级分"] = (
        comp["4月归一化流失率"] * 45
        + (comp["4月流失人数"] / max_churn) * 35
        + comp["4月变化"].clip(lower=0) * 20
    )
    comp["问题类型"] = comp.apply(lambda r: classify(r, median_rate), axis=1)
    comp.loc[comp["是否前四关基准段"], "优先级分"] = 0
    comp = comp.sort_values(["优先级分", "4月流失人数", "关卡序号"], ascending=[False, False, True])
    return comp


def main():
    sheets = pd.read_excel(INPUT, sheet_name=None)
    all_rows = []
    diagnostics = []
    for name, df in sheets.items():
        rows, diag = clean_sheet(name, df)
        all_rows.append(rows)
        diagnostics.append(diag)

    rows_all = pd.concat(all_rows, ignore_index=True)
    april_rows = rows_all[rows_all["批次"] == APRIL_SHEET].copy()
    jan_rows = rows_all[rows_all["批次"].isin(JAN_SHEETS)].copy()

    summaries = [batch_summary(rows_all[rows_all["批次"] == name].copy(), name) for name in sheets.keys()]
    summaries.append(batch_summary(jan_rows, "1月基线"))
    summary_df = pd.DataFrame(summaries)

    level_by_label = {
        name: level_metrics(rows_all[rows_all["批次"] == name].copy(), name) for name in sheets.keys()
    }
    level_by_label["1月基线"] = level_metrics(jan_rows, "1月基线")
    comparison = build_comparison(level_by_label)

    april_main = comparison.sort_values(["4月流失人数", "4月归一化流失率"], ascending=[False, False]).copy()
    priority = comparison[~comparison["是否前四关基准段"]].copy()
    priority = priority[priority["4月流失人数"] > 0].sort_values(["优先级分", "4月流失人数"], ascending=[False, False])

    pay_rows = []
    for name in sheets.keys():
        pay_rows.append(pay_summary(rows_all[rows_all["批次"] == name].copy(), name))
    pay_rows.append(pay_summary(jan_rows, "1月基线"))
    pay_df = pd.concat(pay_rows, ignore_index=True)

    for name, df in level_by_label.items():
        df.to_csv(OUT_DIR / f"level_metrics_{name}.csv", index=False)
    rows_all.to_csv(OUT_DIR / "player_detail_all.csv", index=False)
    april_rows.to_csv(OUT_DIR / "player_detail_4月.csv", index=False)
    summary_df.to_csv(OUT_DIR / "period_summary.csv", index=False)
    comparison.to_csv(OUT_DIR / "three_period_level_comparison.csv", index=False)
    april_main.to_csv(OUT_DIR / "april_main_analysis.csv", index=False)
    priority.to_csv(OUT_DIR / "priority_levels.csv", index=False)
    pay_df.to_csv(OUT_DIR / "pay_comparison.csv", index=False)
    pd.DataFrame(diagnostics).to_csv(OUT_DIR / "diagnostics.csv", index=False)

    top_priority = priority.head(8)[["关卡标签", "问题类型", "4月流失人数", "4月归一化流失率", "1月基线归一化流失率", "4月变化", "优先级分"]]
    payload = {
        "input": str(INPUT),
        "output_dir": str(OUT_DIR),
        "summary": summary_df.to_dict(orient="records"),
        "diagnostics": diagnostics,
        "top_priority": top_priority.to_dict(orient="records"),
        "april_top_churn": april_main.head(12)[["关卡标签", "4月到达人数", "4月流失人数", "4月归一化流失率", "问题类型"]].to_dict(orient="records"),
        "rules": {
            "front_four": "1-01 到 1-04 仅作为基准段，不做关卡体验归因",
            "stage_order": "累计进度 = (章节 - 1) * 15 + 小关",
            "significant_delta": SIGNIFICANT_DELTA,
            "min_signal_churn": MIN_SIGNAL_CHURN,
        },
    }
    with open(OUT_DIR / "april_focus_summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
