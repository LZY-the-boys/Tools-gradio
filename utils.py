import json
def to_jsonl(data, path):
    with open(path, 'w') as f:
        for line in data:
            f.write(json.dumps(line,ensure_ascii=False)+'\n')

def from_jsonl(path):
    return [json.loads(line) for line in open(path, 'r') ]

def from_json(path):
    return json.load(open(path))

def to_json(data, path):
    return json.dump(data, open(path,'w'), ensure_ascii=False)