# LLM-Judge on Z-bench and Alignment-bench

## Install

```bash
git clone https://github.com/leixy20/FastChat.git
cd FastChat
pip install -e .
pip install jsonlines, openpyxl, openai, anthropic
```

## Dataset Details

### z-bench 

+ Consists of 310 Chinese single-round questions
+ Categories: "基础能力", "进阶能力", "垂直领域"
+ Data is placed in `fastchat/llm_judge/data/z_bench/question.jsonl`
+ Human-annotated reference answers is placed in `fastchat/llm_judge/data/z_bench/reference_answer/gpt-4-API.jsonl`

### Alignment-bench

+ Consists of 776 Chinese single-round questions
+ Categories: "评价看法", "基本任务", "写作类", "询求建议", "数学类", "逻辑推理", "学科知识问答", "中文理解进阶", "字词级别理解", "现实世界理解", "角色扮演"
+ Data is placed in `fastchat/llm_judge/data/alignment_bench/question.jsonl`
+ Human-annotated reference answers is placed in `fastchat/llm_judge/data/alignment_bench/reference_answer/gpt-4-API.jsonl`

## Use Guide

NOTE: before the evaluation process, first navigate to the target dir `fastchat/llm_judge`

### API Inference

This module `fastchat/llm_judge/inference` is intended for get model's answers via APIs.
Before inference, follow the TODO signs in `inference/models.py` to fill the url and the key.

Example usage:

```bash
BENCH_NAME="alignment_bench" # z_bench mt_bench alignment_bench
MODELS="ChatGLM2 ChatGPT"
python inference/inference.py \
    --model ${MODELS} \
    --workers 2 \
    --question-file data/${BENCH_NAME}/question.jsonl \
    --save-dir data/${BENCH_NAME}/model_answer \
    # --first-n 2 # using first-n as a debug option
```

The prompts come from `data/${BENCH_NAME}/question.jsonl` and the results will be saved in `data/${BENCH_NAME}/model_answer/{model_name}.jsonl`

Currently support models: GPT-3.5 and GLM series. If you want to add more models to this module, add them in `inference/models.py`

### GPT-4 Judgment

This module is used to get GPT-4's judgment of the generated answers.

Example usage:

```bash
JUDGE_MODEL="gpt-4-stream" # gpt-4 api stream=True
BENCH_NAME="z_bench" # z_bench mt_bench alignment_bench
MODE="single"
MODELS="ChatGLM2 ChatGPT"

python gen_judgment.py \
    --bench-name $BENCH_NAME \
    --model-list ${MODELS} \
    --parallel 2 \
    --judge-model $JUDGE_MODEL \
    --mode $MODE \
    # --first-n 2 # using first-n as a debug option
```

We use get-4 model to grade every single answer on a 1 to 10 scale. The judgment file will be saved in `data/alignment_bench/model_judgment/gpt-4-stream_single.jsonl`

### Show results

This module is used to show the results generated in `GPT-4 Judgment` section.

Example usage:

```bash
JUDGE_MODEL="gpt-4-stream" # gpt-4 api stream=True
BENCH_NAME="z_bench" # z_bench mt_bench alignment_bench
MODE="single"
MODELS="ChatGLM2 ChatGPT"

python show_result.py \
    --bench-name $BENCH_NAME \
    --model-list ${MODELS} \
    --input-file data/${BENCH_NAME}/model_judgment/${JUDGE_MODEL}_${MODE}.jsonl \
    --save-file data/${BENCH_NAME}/excels/${JUDGE_MODEL}_${MODE}.xlsx
```

The result file will be saved as `data/${BENCH_NAME}/excels/${JUDGE_MODEL}_${MODE}.xlsx`

### One-stop

fill your openai_key and openai_base_url in `scripts/eval.sh`
Use `bash scripts/eval.sh` to complete the whole process mentioned above.