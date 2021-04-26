import json


def open_and_convert(filepath):
    with open(filepath, encoding="utf-8") as jfile:
        array = json.load(jfile)
        return array


def search_for_args(array, par_dict):
    res = []
    for d in array:
        for key, value in par_dict.items():
            if d[key] != value:
                break
        else:
            res.append(d)
    if res:
        return res
    return False


def add_d(lang, pars):
    lang, name, userid, words, answers = pars
    print(words, answers)
    # if lang == 'eng':
    filepath = "english.json"
    popularity = 0
    through = {}
    reversed = {}
    for i in range(len(words)):
        through[words[i]] = answers[i]
    for i in range(len(words)):
        reversed[answers[i]] = words[i]

    d = {"name": name, "userid": userid, "len": len(words), "popularity": 0, "words_through": through, "reversed": reversed}
    print(d)
    array = open_and_convert(filepath)
    array.append(d)
    with open(filepath, "w", encoding="utf-8") as jfile:
        json.dump(array, jfile)

