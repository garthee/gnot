import os
import json, csv

STOPWORDS = ["able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again", "against", "aint", "allow", "allows", "almost", "alone", "along", "already", "also", "also,although,always,am,among", "although", "always", "among", "amongst", "amoungst", "amount", "another", "any,anyhow,anyone,anything,anyway", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "arent", "around", "aside", "asking", "associated", "available", "away", "awfully", "back,be,became", "became", "because", "because,become,becomes", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bill", "both", "bottom,but", "brief", "call", "came", "cannot", "cant", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "cmon", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldnt", "couldnt", "course", "currently", "definitely", "describe", "described", "despite", "detail", "didnt", "different", "does", "doesnt", "doing", "done", "dont", "down", "downwards", "during", "each", "eight", "either", "eleven,else", "else", "elsewhere", "empty", "enough", "entirely", "especially", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "exactly", "example", "except", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "followed", "following", "follows", "former", "formerly", "forth", "forty", "found", "four", "from", "front", "full", "further", "furthermore", "gets", "getting", "give", "given", "gives", "goes", "going", "gone", "gotten", "greetings", "hadnt", "happens", "hardly", "hasnt", "hasnt", "have", "havent", "having", "hello", "help", "hence", "here", "hereafter", "hereby", "herein", "heres", "hereupon", "hers", "herself", "hes", "himself", "hither", "hopefully", "howbeit", "however", "hundred", "ignored", "ill", "immediate", "inasmuch", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", "interest", "into", "inward", "isnt", "itd", "itll", "its", "itself", "ive", "just", "keep", "keeps", "kept", "know", "known", "knows", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "lets", "like", "liked", "likely", "little", "look", "looking", "looks", "made", "mainly", "many", "maybe", "mean", "meanwhile", "merely", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "myself", "name", "namely", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", "next", "nine", "nobody", "none", "noone", "normally", "nothing", "novel", "nowhere", "obviously", "often", "okay", "once", "ones", "only", "onto", "other", "others", "otherwise", "ought", "ours", "ourselves", "outside", "over", "overall", "own,part", "particular", "particularly", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", "quite", "rather", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively", "right", "said", "same", "saying", "says", "second", "secondly", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "should", "shouldnt", "show", "side", "since", "sincere", "sixty", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "such", "sure", "system", "take", "taken", "tell", "tends", "than", "thank", "thanks", "thanx", "that", "thats", "thats", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "theres", "theres", "thereupon", "these", "they", "theyd", "theyll", "theyre", "theyve", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "together", "took", "toward", "towards", "tried", "tries", "truly", "trying", "twelve", "twenty", "twice", "under", "unfortunately", "unless", "unlikely", "until", "unto", "upon", "used", "useful", "uses", "using", "usually", "value", "various", "very", "want", "wants", "wasnt", "wed", "welcome", "well", "well", "went", "were", "were", "werent", "weve", "what", "whatever", "whats", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether", "which", "while", "whither", "whoever", "whole", "whom", "whos", "whose", "will", "willing", "wish", "with", "within", "without", "wonder", "wont", "would", "wouldnt", "youd", "youll", "your", "youre", "yours", "yourself", "yourselves", "youve", "zero"]

from db import export_sql
def render(vis, request, info):
	info["message"] = []
	
	reload = request.args.get("reload", 0)
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	field = request.args.get("field", '')
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	
	limit = request.args.get("limit", '200')
	
	if len(table) == 0 or len(field) == 0:
		info["message"].append("table or field missing.")
		info["message_class"] = "failure"
	else:
		sql = "select word, count(*) as n from (select regexp_split_to_table(regexp_replace(lower(coalesce(%s,'')),'[^a-z0-9@]+',' ','g'),' ') as word, * from %s where %s) as a  where char_length(word) > 3 group by 1 order by 2 desc limit %s offset %s"%(field, table, where,limit, start)
		header = "text,size"
		(datfile, reload, result) = export_sql(sql, vis.config, reload, header, view)
		if len(result) > 0:
			info["message"].append(result)
			info["message_class"] = "failure"
		else:
			info["message_class"] = "success"
			if reload > 0:
				info["message"].append("Loaded fresh.")
			else:
				info["message"].append("Loading from cache. Use reload=1 to reload.")
			
		info["datfile"]=	datfile

	info["title"] = "%s from %s"%(field, table)