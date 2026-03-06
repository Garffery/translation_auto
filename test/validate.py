import asyncio
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import sacrebleu
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agent.translation_agent import workflow


def _normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _pick_columns(columns: Sequence[str]) -> Tuple[str, str]:
    normalized = [(c, _normalize_text(c).lower()) for c in columns]
    zh_candidates = []
    en_candidates = []
    for original, low in normalized:
        if any(k in low for k in ["中文", "zh", "cn", "chinese", "source", "原文", "src"]):
            zh_candidates.append(original)
        if any(k in low for k in ["英文", "en", "english", "target", "译文", "tgt", "reference", "ref"]):
            en_candidates.append(original)

    zh_col = zh_candidates[0] if zh_candidates else (columns[0] if columns else "")
    en_col = ""
    if en_candidates:
        en_col = en_candidates[0]
    elif len(columns) >= 2:
        en_col = columns[1]
    else:
        en_col = zh_col

    return zh_col, en_col


def _read_pairs_with_pandas(xlsx_path: Path) -> List[Tuple[str, str]]:
    import pandas as pd

    df_or_sheets = pd.read_excel(xlsx_path)
    if isinstance(df_or_sheets, dict):
        df = next(iter(df_or_sheets.values()))
    else:
        df = df_or_sheets

    columns = [str(c) for c in df.columns.tolist()]
    zh_col, en_col = _pick_columns(columns)

    if zh_col not in df.columns:
        zh_col = df.columns[0]
    if en_col not in df.columns:
        en_col = df.columns[1] if len(df.columns) >= 2 else df.columns[0]

    pairs: List[Tuple[str, str]] = []
    for _, row in df.iterrows():
        zh = _normalize_text(row.get(zh_col))
        en = _normalize_text(row.get(en_col))
        if not zh and not en:
            continue
        pairs.append((zh, en))
    return pairs


def load_excel_pairs(xlsx_path: Path) -> List[Tuple[str, str]]:
    return _read_pairs_with_pandas(xlsx_path)


async def translate_one(app, zh_text: str, thread_id: str) -> str:
    thread_config = {"configurable": {"thread_id": thread_id}}
    request = f"帮我把这句话翻译为英文  {zh_text}"
    payload = {"origin_query": request}
    res: Optional[str] = None
    async for event in app.astream(payload, config=thread_config, stream_mode="values"):
        if "final_result" in event and event["final_result"] is not None:
            res = event["final_result"].content
    return _normalize_text(res)


async def translate_all(app, zh_list: Sequence[str], max_concurrency: int = 3) -> List[str]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _run(i: int, zh: str) -> str:
        async with semaphore:
            return await translate_one(app, zh, thread_id=str(i + 1))

    tasks = [asyncio.create_task(_run(i, zh)) for i, zh in enumerate(zh_list)]
    return await asyncio.gather(*tasks)


if __name__ == '__main__':
    load_dotenv()
    app = workflow.compile()

    async def main():
        xlsx_path = Path(__file__).resolve().parents[1] / "data" / "en-zh-100.xlsx"
        pairs = load_excel_pairs(xlsx_path)
        pairs = pairs[0:2]
        if not pairs:
            raise RuntimeError(f"Excel 里没有读到任何数据: {xlsx_path}")

        zh_list = [zh for zh, _ in pairs]
        ref_list = [en for _, en in pairs]

        hyp_list = await translate_all(app, zh_list)

        sentence_scores = [
            sacrebleu.sentence_bleu(hyp, [ref]).score
            for hyp, ref in zip(hyp_list, ref_list)
        ]
        avg_sentence_bleu = sum(sentence_scores) / max(len(sentence_scores), 1)
        corpus_bleu = sacrebleu.corpus_bleu(hyp_list, [ref_list]).score

        print(f"样本数: {len(pairs)}")
        print(f"平均 sentence BLEU: {avg_sentence_bleu:.4f}")
        print(f"corpus BLEU: {corpus_bleu:.4f}")
        # print("前 5 条样例:")
        # for i, (zh, ref, hyp, s) in enumerate(zip(zh_list, ref_list, hyp_list, sentence_scores)):
        #     if i >= 5:
        #         break
        #     print(f"{i+1}. zh={zh}")
        #     print(f"   ref={ref}")
        #     print(f"   hyp={hyp}")
        #     print(f"   sentence_bleu={s:.4f}")


    asyncio.run(main())
