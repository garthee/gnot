from collections import defaultdict
import csv
from collections import defaultdict

from jinja2 import Markup

from db import export_sql
from pstemmer import PorterStemmer


STOPWORDS = ["able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again",
             "against", "aint", "allow", "allows", "almost", "alone", "along", "already", "also",
             "also,although,always,am,among", "although", "always", "among", "amongst", "amoungst", "amount", "another",
             "any,anyhow,anyone,anything,anyway", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways",
             "anywhere", "apart", "appear", "appreciate", "appropriate", "arent", "around", "aside", "asking",
             "associated", "available", "away", "awfully", "back,be,became", "became", "because",
             "because,become,becomes", "become", "becomes", "becoming", "been", "before", "beforehand", "behind",
             "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bill", "both",
             "bottom,but", "brief", "call", "came", "cannot", "cant", "cant", "cause", "causes", "certain", "certainly",
             "changes", "clearly", "cmon", "come", "comes", "concerning", "consequently", "consider", "considering",
             "contain", "containing", "contains", "corresponding", "could", "couldnt", "couldnt", "course", "currently",
             "definitely", "describe", "described", "despite", "detail", "didnt", "different", "does", "doesnt",
             "doing", "done", "dont", "down", "downwards", "during", "each", "eight", "either", "eleven,else", "else",
             "elsewhere", "empty", "enough", "entirely", "especially", "even", "ever", "every", "everybody", "everyone",
             "everything", "everywhere", "exactly", "example", "except", "fifteen", "fifth", "fify", "fill", "find",
             "fire", "first", "five", "followed", "following", "follows", "former", "formerly", "forth", "forty",
             "found", "four", "from", "front", "full", "further", "furthermore", "gets", "getting", "give", "given",
             "gives", "goes", "going", "gone", "gotten", "greetings", "hadnt", "happens", "hardly", "hasnt", "hasnt",
             "have", "havent", "having", "hello", "help", "hence", "here", "hereafter", "hereby", "herein", "heres",
             "hereupon", "hers", "herself", "hes", "himself", "hither", "hopefully", "howbeit", "however", "hundred",
             "ignored", "ill", "immediate", "inasmuch", "indeed", "indicate", "indicated", "indicates", "inner",
             "insofar", "instead", "interest", "into", "inward", "isnt", "itd", "itll", "its", "itself", "ive", "just",
             "keep", "keeps", "kept", "know", "known", "knows", "last", "lately", "later", "latter", "latterly",
             "least", "less", "lest", "lets", "like", "liked", "likely", "little", "look", "looking", "looks", "made",
             "mainly", "many", "maybe", "mean", "meanwhile", "merely", "might", "mill", "mine", "more", "moreover",
             "most", "mostly", "move", "much", "must", "myself", "name", "namely", "near", "nearly", "necessary",
             "need", "needs", "neither", "never", "nevertheless", "next", "nine", "nobody", "none", "noone", "normally",
             "nothing", "novel", "nowhere", "obviously", "often", "okay", "once", "ones", "only", "onto", "other",
             "others", "otherwise", "ought", "ours", "ourselves", "outside", "over", "overall", "own,part",
             "particular", "particularly", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably",
             "provides", "quite", "rather", "really", "reasonably", "regarding", "regardless", "regards", "relatively",
             "respectively", "right", "said", "same", "saying", "says", "second", "secondly", "seeing", "seem",
             "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously",
             "seven", "several", "shall", "should", "shouldnt", "show", "side", "since", "sincere", "sixty", "some",
             "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon",
             "sorry", "specified", "specify", "specifying", "still", "such", "sure", "system", "take", "taken", "tell",
             "tends", "than", "thank", "thanks", "thanx", "that", "thats", "thats", "their", "theirs", "them",
             "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "theres",
             "theres", "thereupon", "these", "they", "theyd", "theyll", "theyre", "theyve", "thickv", "thin", "think",
             "third", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru",
             "thus", "together", "took", "toward", "towards", "tried", "tries", "truly", "trying", "twelve", "twenty",
             "twice", "under", "unfortunately", "unless", "unlikely", "until", "unto", "upon", "used", "useful", "uses",
             "using", "usually", "value", "various", "very", "want", "wants", "wasnt", "wed", "welcome", "well", "well",
             "went", "were", "were", "werent", "weve", "what", "whatever", "whats", "when", "whence", "whenever",
             "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether",
             "which", "while", "whither", "whoever", "whole", "whom", "whos", "whose", "will", "willing", "wish",
             "with", "within", "without", "wonder", "wont", "would", "wouldnt", "youd", "youll", "your", "youre",
             "yours", "yourself", "yourselves", "youve", "zero"]


def _array2mat(fl, flo, rStopWords, StemWords):
    terms = csv.reader(open(fl, 'r'))
    if rStopWords:
        terms = filter(lambda term: term[1] not in STOPWORDS, terms)
    if StemWords:
        p = PorterStemmer()
        d = defaultdict(int)
        for term in terms:
            d[(term[0], p.stem(term[1], 0, len(term[1]) - 1))] += int(term[2])
        terms = map(lambda d: (d[0][0], d[0][1], d[1]), d.items())

    table = defaultdict(dict)
    words = set()
    for (year, word, item) in terms:
        table[num_if_is_number(year)][word] = item
        words.add(word)

    fo = csv.writer(open(flo, 'w'))
    years = sorted(table.keys())
    fo.writerow(['Words'] + [str(year) for year in years])
    for word in words:
        row = [table[year].get(word, '0') for year in years]
        fo.writerow([word] + row)

    return years[0], years[-1]


def num_if_is_number(s):
    try:
        return float(s)
    except ValueError:
        return s


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
    xField = request.args.get("xField", '')
    limit = request.args.get("limit", '20')

    if len(table) == 0 or len(field) == 0:
        info["message"].append("table or field missing.")
        info["message_class"] = "failure"
    else:
        sql = "select t, word, n from ( select *,row_number() over (partition by t order by n desc) as rank from ( select word, t,n from ( select word, t, count(*) as n from (select regexp_split_to_table(regexp_replace(lower(coalesce(%s,'')),'[^a-z0-9@]+',' ','g'),' ') as word, %s as t from %s where %s) as a where char_length(word) > %s group by 1,2 ) as a where n > 5 ) as a ) as a where rank >= %s and rank <= %s + %s" % (
        field, xField, table, where, minlen, start, start, limit)

        header = None
        (datfile, reload, result) = export_sql(sql, vis.config, reload, header, view)
        datfilen = datfile + '_2mat.csv'
        if len(result) > 0:
            info["message"].append(result)
            info["message_class"] = "failure"
        else:
            info["message_class"] = "success"
            if reload > 0:
                info["message"].append("Loaded fresh.")
            else:
                info["message"].append("Loading from cache. Use reload=1 to reload.")

            (startYear, endYear) = _array2mat(datfile, datfilen, rStopWords, StemWords)
            info["datfile"] = datfilen
            info["title"] = "%s from %s to %s" % (field, startYear, endYear)

    pfield = request.args.get("pfield", [])
    info["title"] = "FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>" % (','.join(pfield), table)
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))

    return vis.render_template('explore_mashed_series.html', **info)