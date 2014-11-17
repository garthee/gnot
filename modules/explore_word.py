#!/usr/bin/python

import os
import json
import csv
from collections import defaultdict

from jinja2 import Markup

from pstemmer import PorterStemmer


STOPWORDS = set(
    ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
     'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
     'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
     'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
     'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
     'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
     'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
     'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
     'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', \
     'the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 'for', 'on', 'are', 'with', 'as', 'I',
     'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by', 'hot', 'but', 'some', 'what', 'there',
     'we', 'can', 'out', 'other', 'were', 'all', 'your', 'when', 'up', 'use', 'word', 'how', 'said', 'an', 'each',
     'she', 'which', 'do', 'their', 'time', 'if', 'will', 'way', 'about', 'many', 'then', 'them', 'would', 'write',
     'like', 'so', 'these', 'her', 'long', 'make', 'thing', 'see', 'him', 'two', 'has', 'look', 'more', 'day', 'could',
     'go', 'come', 'did', 'my', 'sound', 'no', 'most', 'number', 'who', 'over', 'know', 'water', 'than', 'call',
     'first', 'people', 'may', 'down', 'side', 'been', 'now', 'find', 'any', 'new', 'work', 'part', 'take', 'get',
     'place', 'made', 'live', 'where', 'after', 'back', 'little', 'only', 'round', 'man', 'year', 'came', 'show',
     'every', 'good', 'me', 'give', 'our', 'under', '-', '_', '\'', '\'s', 'one', 'two', 'three', 'four', 'five', 'six',
     'seven', 'eight', 'nine', 'ten'])

# STOPWORDS = ["able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again", "against", "aint", "allow", "allows", "almost", "alone", "along", "already", "also", "also,although,always,am,among", "although", "always", "among", "amongst", "amoungst", "amount", "another", "any,anyhow,anyone,anything,anyway", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "arent", "around", "aside", "asking", "associated", "available", "away", "awfully", "back,be,became", "became", "because", "because,become,becomes", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bill", "both", "bottom,but", "brief", "call", "came", "cannot", "cant", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "cmon", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldnt", "couldnt", "course", "currently", "definitely", "describe", "described", "despite", "detail", "didnt", "different", "does", "doesnt", "doing", "done", "dont", "down", "downwards", "during", "each", "eight", "either", "eleven,else", "else", "elsewhere", "empty", "enough", "entirely", "especially", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "exactly", "example", "except", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "followed", "following", "follows", "former", "formerly", "forth", "forty", "found", "four", "from", "front", "full", "further", "furthermore", "gets", "getting", "give", "given", "gives", "goes", "going", "gone", "gotten", "greetings", "hadnt", "happens", "hardly", "hasnt", "hasnt", "have", "havent", "having", "hello", "help", "hence", "here", "hereafter", "hereby", "herein", "heres", "hereupon", "hers", "herself", "hes", "himself", "hither", "hopefully", "howbeit", "however", "hundred", "ignored", "ill", "immediate", "inasmuch", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", "interest", "into", "inward", "isnt", "itd", "itll", "its", "itself", "ive", "just", "keep", "keeps", "kept", "know", "known", "knows", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "lets", "like", "liked", "likely", "little", "look", "looking", "looks", "made", "mainly", "many", "maybe", "mean", "meanwhile", "merely", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "myself", "name", "namely", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", "next", "nine", "nobody", "none", "noone", "normally", "nothing", "novel", "nowhere", "obviously", "often", "okay", "once", "ones", "only", "onto", "other", "others", "otherwise", "ought", "ours", "ourselves", "outside", "over", "overall", "own,part", "particular", "particularly", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", "quite", "rather", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively", "right", "said", "same", "saying", "says", "second", "secondly", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "should", "shouldnt", "show", "side", "since", "sincere", "sixty", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "such", "sure", "system", "take", "taken", "tell", "tends", "than", "thank", "thanks", "thanx", "that", "thats", "thats", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "theres", "theres", "thereupon", "these", "they", "theyd", "theyll", "theyre", "theyve", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "together", "took", "toward", "towards", "tried", "tries", "truly", "trying", "twelve", "twenty", "twice", "under", "unfortunately", "unless", "unlikely", "until", "unto", "upon", "used", "useful", "uses", "using", "usually", "value", "various", "very", "want", "wants", "wasnt", "wed", "welcome", "well", "well", "went", "were", "were", "werent", "weve", "what", "whatever", "whats", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether", "which", "while", "whither", "whoever", "whole", "whom", "whos", "whose", "will", "willing", "wish", "with", "within", "without", "wonder", "wont", "would", "wouldnt", "youd", "youll", "your", "youre", "yours", "yourself", "yourselves", "youve", "zero"]

from db import export_sql


def render(vis, request, info):
    info["message"] = []

    reload = int(request.args.get("reload", '0'))
    table = request.args.get("table", '')
    where = request.args.get("where", '1=1')
    field = request.args.get("field", '')
    view = request.args.get("view", '')
    minlen = request.args.get("MinCharLength", '3')
    rStopWords = int(request.args.get("RemoveStopWords", '0'))
    StemWords = int(request.args.get("StemWords", '0'))
    start = request.args.get("start", '0')  # start at 0

    limit = request.args.get("limit", '200')

    if len(table) == 0 or len(field) == 0:
        info["message"].append("table or field missing.")
        info["message_class"] = "failure"
    else:
        sql = "select word, count(*) as n from (select regexp_split_to_table(regexp_replace(lower(coalesce(%s,'')),'[^a-z0-9@]+',' ','g'),' ') as word, * from %s where %s) as a  where char_length(word) > %s group by 1 order by 2 desc limit %s offset %s" % (
        field, table, where, minlen, limit, start)

        (datfile, reload, result) = export_sql(sql, vis.config, reload, None, view)
        if len(result) > 0:
            info["message"].append(result)
            info["message_class"] = "failure"
        else:
            info["message_class"] = "success"
            if reload > 0:
                info["message"].append("Loaded fresh.")
            else:
                info["message"].append("Loading from cache. Use reload=1 to reload.")

        datfileNew = datfile + 'edited.csv'

        if reload:
            with open(datfile) as f:
                terms = csv.reader(f)
                #terms = map(lambda term: term(0).replace("'s",'').replace("'", '').replace(".", " ").replace(",", " "), terms)
                if rStopWords:
                    terms = filter(lambda term: term[0] not in STOPWORDS, terms)
                if StemWords:
                    p = PorterStemmer()
                    d = defaultdict(int)
                    for term in terms:
                        d[p.stem(term[0], 0, len(term[0]) - 1)] += int(term[1])
                    terms = d.items()

                header = ["text", "size"]
                with open(datfileNew, 'w') as f2:
                    cs = csv.writer(f2)
                    cs.writerow(header)
                    for term in terms:
                        cs.writerow(term)

        info["datfile"] = datfileNew

    pfield = request.args.get("pfield", [])
    info["title"] = "FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>" % (','.join(pfield), table)
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))
