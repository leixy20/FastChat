export openai_key="" # TODO
export openai_base="" # TODO

JUDGE_MODEL="gpt-4-stream" # gpt-4 api stream=True
BENCH_NAME="alignment_bench" # z_bench alignment_bench
MODE="single"
MODELS="ChatGLM2 ChatGPT"

# stage1 generate answers of target APIs
python inference/inference.py \
    --model ${MODELS} \
    --workers 2 \
    --question-file data/${BENCH_NAME}/question.jsonl \
    --save-dir data/${BENCH_NAME}/model_answer \

# stage2 generate judgement using GPT-4 judge
python gen_judgment.py \
    --bench-name $BENCH_NAME \
    --model-list ${MODELS} \
    --parallel 2 \
    --judge-model $JUDGE_MODEL \
    --mode $MODE \

# stage3 show results
python show_result.py \
    --bench-name $BENCH_NAME \
    --model-list ${MODELS} \
    --input-file data/${BENCH_NAME}/model_judgment/${JUDGE_MODEL}_${MODE}.jsonl \
    --save-file data/${BENCH_NAME}/excels/${JUDGE_MODEL}_${MODE}.xlsx