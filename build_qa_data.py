import json
import argparse

from tqdm import tqdm
from transformers import pipeline


MODEL_DICT = {
    'mbert': 'songhee/i-manual-mbert',
    'koelectra': 'sehandev/koelectra-long-qa',
}


def load_data():
    with open('./data/i-manual_train.json') as dataset_file:
        dataset_json = json.load(dataset_file)
        dataset = dataset_json['data']

    return dataset


def save_result(model_name: str, result: dict):
    # Prod
    with open(f'./data/{model_name}.json', 'w', encoding='UTF-8') as result_file:
        result_file.write(json.dumps(result, ensure_ascii=False))

    # Dev
    with open(f'./data/{model_name}-pretty.json', 'w', encoding='UTF-8') as result_file:
        result_file.write(json.dumps(result, ensure_ascii=False, indent=4))


def answer_data(nlp, data):
    result_list = []
    for article in tqdm(data):
        result = {
            'title': article['title'],
            'contents': [],
        }

        for paragraph in article['paragraphs']:
            context = paragraph['context']

            content = {
                'context': context,
                'qas': [],
            }

            for qa in paragraph['qas']:
                question = qa['question']
                answer = nlp(context=context, question=question)['answer']

                content['qas'].append({
                    'id': qa['id'],
                    'question': question,
                    'answer': answer,
                })

            result['contents'].append(content)

        result_list.append(result)

    return result_list


def main(model_name):
    nlp = pipeline('question-answering', model=MODEL_DICT[model_name], tokenizer=MODEL_DICT[model_name], device=0)
    data = load_data()

    result = answer_data(nlp, data)
    save_result(model_name, result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='train data의 결과를 미리 저장')
    parser.add_argument('--model', type=str, help='mbert, koelectra', required=True)

    args = parser.parse_args()
    main(args.model)