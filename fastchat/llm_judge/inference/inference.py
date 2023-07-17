import argparse
import jsonlines
import json
import random
import os
from models import get_model_api

if __name__ == '__main__':
    """
    singleround inference 
    input question doc format:
        question_doc = {
            "question_id": int,
            "category": str,
            "turns": List[str],
        }
    output answer file format
         {
            "question_id": int,
            "category": str,
            "answer_id": str,
            "model_id": str,
            "choices": [{
                "index": 0,
                "turns": [
                    str
                ],
            }]
        }
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=None,
        help="A list of models to be inferenced",
    )
    parser.add_argument("--workers", type=int)
    parser.add_argument("--question-file", type=str)
    parser.add_argument("--save-dir", type=str)
    parser.add_argument(
        "--first-n", type=int, help="A debug option. Only run the first `n` questions."
    )
    args = parser.parse_args()

    for model_name in args.models:
        model = get_model_api(model_name, args.workers)
        if model is None:
            print("invalid model: ", model_name)
            exit(1)
        print("inference model: ", model_name)
        
        docs = []
        with jsonlines.open(args.question_file, "r") as f:
            for doc in f:
                docs.append(doc)
            f.close()

        if args.first_n:
            docs = docs[: args.first_n]
        print(f"load {len(docs)} docs")

        prompts = [data["turns"][0] for data in docs]
        outputs = model.generate_text(prompts)

        os.makedirs(args.save_dir, exist_ok=True)
        save_path = os.path.join(args.save_dir, f"{model_name}.jsonl")
        with jsonlines.open(save_path, 'w') as f:
            for doc, output in zip(docs, outputs):
                doc["model_id"] = model_name
                doc["answer_id"] = str(doc["question_id"]) + "_" + model_name
                if output is not None:
                    doc["choices"] = [{"index":0, "turns": [output.strip()]}]
                else:
                    doc["choices"] = [{"index":0, "turns": [None]}]
                f.write(doc)
            f.close()