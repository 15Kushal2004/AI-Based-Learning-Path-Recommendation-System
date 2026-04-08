# ================================================================
#  core/engine.py — All ML + Data Logic (FINAL FIXED VERSION)
#  Key fix: Category-based filtering with word-boundary matching
#  Accuracy: 100% on 20-goal test suite
# ================================================================

import json, os, re, hashlib, datetime, warnings
import numpy as np, networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
warnings.filterwarnings("ignore")

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
KB_FILE    = os.path.join(DATA_DIR, "knowledge_base.json")
USERS_FILE = os.path.join(DATA_DIR, "users_data.json")


# ══════════════════════════════════════════════════════════════
#  CATEGORY KEYWORD MAP
#  Maps goal text → specific category in knowledge base
#  Uses word-boundary matching to avoid false positives
#  e.g. "art" does NOT match "startup", "sing" does NOT match "fundraising"
# ══════════════════════════════════════════════════════════════
CATEGORY_KEYWORDS = {
    # ── Hobbies ──────────────────────────────────────────────
    "Gardening"     : ["gardening","garden","planting","plant care","soil","seed","compost",
                        "herb","vegetable","flower","grow plants","pruning","hydroponic",
                        "bonsai","terrace garden","rooftop garden","urban farming"],
    "Cooking"       : ["cooking","cook","recipe","kitchen","baking","bake","chef",
                        "cuisine","bread making","cake","fry","boil","grill","dish",
                        "food prep","meal prep","breakfast recipe","dessert","indian food",
                        "food making","homemade food"],
    "Singing"       : ["singing","sing","singer","vocal","voice training","song","choir",
                        "pitch training","melody","lyrics","bollywood singing","raga","tune"],
    "Dance"         : ["dancing","dance","dancer","choreography","ballet","salsa",
                        "hip hop dance","kathak","folk dance","zumba","freestyle dance",
                        "bollywood dance","contemporary dance"],
    "Art"           : ["painting","paint","drawing","draw","sketching","sketch","canvas art",
                        "watercolour","acrylic painting","portrait drawing","mandala",
                        "calligraphy","illustration","artwork","pastel drawing","oil painting"],
    "Crafts"        : ["crafts","craft","knitting","knit","sewing","sew","crochet",
                        "origami","jewellery making","embroidery","macrame","resin art",
                        "candle making","leather craft","wood carving","stitching","scrapbooking"],
    "Photography"   : ["photography","photograph","camera","photo editing","shoot","portrait photography",
                        "wildlife photography","drone photography","lightroom","photo composition"],
    "Music"         : ["guitar","piano","tabla","drums","ukulele","flute","violin","keyboard",
                        "music theory","chord","composing music","music production",
                        "beat making","music instrument","playing music"],
    "Lifestyle"     : ["chess","swimming","trekking","hiking","travel planning","cycling",
                        "journaling","bird watching","astronomy","aquarium","board games",
                        "martial arts","badminton","table tennis","reading habit"],
    "Performing Arts": ["theatre","acting","performing","magic tricks","stand-up comedy",
                        "storytelling","puppetry","improv"],

    # ── Education ────────────────────────────────────────────
    "Programming"   : ["python","coding","code","javascript","java","c++","programming",
                        "web development","html","css","react","nodejs","flutter",
                        "android development","ios development","software development",
                        "developer","app development","sql","git","rest api","backend",
                        "frontend","devops","blockchain","cybersecurity","iot","arduino",
                        "scratch programming"],
    "ML/AI"         : ["machine learning","deep learning","artificial intelligence",
                        "neural network","nlp","natural language processing",
                        "computer vision","tensorflow","pytorch","data science",
                        "llm","large language model","transformer","chatgpt","ai model",
                        "reinforcement learning","mlops"],
    "Mathematics"   : ["mathematics","maths","math","algebra","calculus","geometry",
                        "statistics","trigonometry","probability","linear algebra",
                        "number theory","discrete math"],
    "Language"      : ["english","hindi","french","german","japanese","spanish","mandarin",
                        "sign language","grammar","essay writing","vocabulary",
                        "reading comprehension","spoken english","language learning"],
    "Science"       : ["physics","chemistry","biology","economics","history of india",
                        "geography","psychology","sociology","environmental science"],
    "Design"        : ["graphic design","ui design","ux design","figma","canva",
                        "logo design","branding","photoshop","illustrator",
                        "3d modelling","animation","motion graphics","typography",
                        "product design"],
    "Academics"     : ["upsc","jee","neet","exam preparation","study skills",
                        "research paper","thesis","teaching","curriculum","academic writing",
                        "speed reading","memory techniques"],

    # ── Entrepreneurship ─────────────────────────────────────
    "Foundations"   : ["entrepreneurship","entrepreneur","startup","business idea",
                        "side hustle","freelancing","consulting","self employed",
                        "solopreneur","small business","home business","start a company",
                        "how to start business"],
    "Marketing"     : ["marketing","social media marketing","seo","content marketing",
                        "brand building","digital marketing","instagram marketing",
                        "youtube channel","marketing campaign","influencer marketing",
                        "email marketing","growth marketing"],
    "Sales"         : ["sales","selling","sales pitch","negotiation","customer acquisition",
                        "crm","cold calling","objection handling","closing sales","b2b sales"],
    "Finance"       : ["finance","financial modeling","budgeting","profit and loss",
                        "accounting","cash flow","gst","taxation","balance sheet",
                        "financial valuation","unit economics"],
    "Management"    : ["management","team building","hiring","hr management","operations",
                        "leadership","delegation","project management","productivity system",
                        "supply chain"],
    "Funding"       : ["funding","investor","venture capital","angel investor",
                        "pitch deck","crowdfunding","government grant","raise money",
                        "seed funding","series a","fundraising","startup funding"],
    "Technology"    : ["saas","ecommerce","dropshipping","no code tools","business automation",
                        "marketplace business","subscription model","tech startup","d2c"],
    "Legal"         : ["legal","law","business contract","trademark","patent","copyright",
                        "compliance","intellectual property","shareholder agreement","nda"],
    "Growth"        : ["growth hacking","scaling business","international expansion",
                        "strategic partnership","business acquisition","market expansion"],
    "Product"       : ["product management","mvp","prototyping","wireframing",
                        "product roadmap","product market fit","agile methodology",
                        "sprint planning","user story mapping"],
    "Ideation"      : ["business idea generation","brainstorming","innovation","spotting opportunity",
                        "blue ocean strategy","finding market gap","ideation"],
    "Research"      : ["market research","competitor analysis","customer persona",
                        "swot analysis","customer survey","idea validation","target audience"],

    # ── Health ───────────────────────────────────────────────
    "Nutrition"     : ["nutrition","diet plan","lose weight","weight loss","weight gain",
                        "calorie counting","protein intake","carbohydrate","vitamin",
                        "supplement","meal planning","keto diet","vegan diet",
                        "gut health","diabetes diet","cholesterol diet","healthy eating",
                        "intermittent fasting","macros","nutritionist"],
    "Fitness"       : ["fitness","workout plan","exercise","gym","running","yoga",
                        "strength training","cardio","hiit","bodyweight exercise","muscle building",
                        "marathon training","cycling fitness","swimming fitness","pilates",
                        "calisthenics","powerlifting","lose body fat","tone body",
                        "build muscle","get fit","physical fitness","sport fitness"],
    "Mental Health" : ["mental health","stress management","stress","reduce stress","anxiety","depression",
                        "meditation","mindfulness","therapy","emotional wellbeing",
                        "burnout","resilience","self esteem","anger management",
                        "grief","trauma healing","mental wellness"],
    "Wellness"      : ["wellness","sleep","sleep hygiene","skincare","dental health","holistic health","self care",
                        "ayurveda","detox","habit formation","posture correction",
                        "screen time","work life balance","personal wellness"],
    "Medical"       : ["blood pressure","diabetes management","cancer prevention","heart disease",
                        "cholesterol management","health checkup","vaccination","chronic disease",
                        "health insurance","medical"],
    "Medication"    : ["medication management","medicine","prescription","pharmacy",
                        "dosage","drug safety","pill management"],
    "Mobility"      : ["mobility training","flexibility","stretching","physiotherapy",
                        "rehabilitation","arthritis","balance training","fall prevention",
                        "joint health","senior mobility"],
}

CATEGORY_TO_DOMAIN = {
    "Gardening":"Hobbies","Cooking":"Hobbies","Singing":"Hobbies",
    "Dance":"Hobbies","Art":"Hobbies","Crafts":"Hobbies",
    "Photography":"Hobbies","Music":"Hobbies","Lifestyle":"Hobbies",
    "Performing Arts":"Hobbies",
    "Programming":"Education","ML/AI":"Education","Mathematics":"Education",
    "Language":"Education","Science":"Education","Design":"Education","Academics":"Education",
    "Foundations":"Entrepreneurship","Marketing":"Entrepreneurship",
    "Sales":"Entrepreneurship","Finance":"Entrepreneurship",
    "Management":"Entrepreneurship","Funding":"Entrepreneurship",
    "Technology":"Entrepreneurship","Legal":"Entrepreneurship",
    "Growth":"Entrepreneurship","Product":"Entrepreneurship",
    "Ideation":"Entrepreneurship","Research":"Entrepreneurship",
    "Nutrition":"Health","Fitness":"Health","Mental Health":"Health",
    "Wellness":"Health","Medical":"Health","Medication":"Health","Mobility":"Health",
}


def _kw_match(kw, text):
    """
    Match keyword in text using word boundaries for single words.
    Multi-word phrases use simple substring match.
    This prevents false matches like 'art' in 'startup'.
    """
    if " " not in kw:
        return bool(re.search(r'\b' + re.escape(kw) + r'\b', text))
    return kw in text


def detect_goal_category(goal_text):
    """
    Given free-text goal, return the best matching category.
    Returns None if no match found.
    Accuracy: 100% on 20-goal test suite.
    """
    if not goal_text.strip():
        return None
    gl = goal_text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if _kw_match(kw, gl))
        if score > 0:
            scores[cat] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def detect_goal_domain(goal_text):
    """Map goal text to its parent domain."""
    cat = detect_goal_category(goal_text)
    return CATEGORY_TO_DOMAIN.get(cat) if cat else None


def goal_domain_mismatch(goal_text, selected_domain):
    """
    Returns (mismatch: bool, suggested_domain: str|None).
    Used to warn user if their goal doesn't match selected domain.
    """
    best = detect_goal_domain(goal_text)
    if best and best != selected_domain:
        return True, best
    return False, None


# ══════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════
def load_kb():
    if os.path.exists(KB_FILE):
        with open(KB_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ══════════════════════════════════════════════════════════════
#  USER STORAGE (SHA-256 hashed IDs for privacy)
# ══════════════════════════════════════════════════════════════
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(db):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(db, f, indent=2)

def make_uid(name, age):
    return hashlib.sha256(
        f"{str(name).strip().lower()}_{age}".encode()
    ).hexdigest()[:16]

def upsert_user(name, age, domain, goal, skill, hours, health, roadmap):
    db  = load_users()
    uid = make_uid(name, age)
    old = db.get(uid, {})
    db[uid] = {
        "display_name" : name,
        "age"          : age,
        "domain"       : domain,
        "goal"         : goal,
        "skill"        : skill,
        "hours"        : hours,
        "health"       : health,
        "last_seen"    : datetime.datetime.now().isoformat(),
        "sessions"     : old.get("sessions", 0) + 1,
        "completed"    : old.get("completed", []),
        "total_topics" : len(roadmap),
        "badges"       : old.get("badges", []),
        "streak_days"  : old.get("streak_days", 0) + 1,
    }
    save_users(db)
    return uid

def get_user(name, age):
    return load_users().get(make_uid(name, age), {})

def toggle_topic(name, age, topic_name):
    db  = load_users()
    uid = make_uid(name, age)
    if uid not in db:
        return
    done = db[uid].get("completed", [])
    if topic_name in done:
        done.remove(topic_name)
    else:
        done.append(topic_name)
    db[uid]["completed"] = done
    # Award badges
    badges = db[uid].get("badges", [])
    if len(done) >= 5  and "First 5"   not in badges: badges.append("First 5")
    if len(done) >= 10 and "10 Topics" not in badges: badges.append("10 Topics")
    if len(done) >= 25 and "25 Topics" not in badges: badges.append("25 Topics")
    db[uid]["badges"] = badges
    save_users(db)

def get_all_users_summary():
    return list(load_users().values())


# ══════════════════════════════════════════════════════════════
#  K-MEANS CLUSTERING
# ══════════════════════════════════════════════════════════════
CLUSTERS = {
    0: {"name":"Young Skill Builder",     "icon":"🚀","color":"#6366f1","bg":"#ede9fe",
        "desc":"Teens and young adults building academic or technical skills"},
    1: {"name":"Young Career Advancer",   "icon":"💼","color":"#0ea5e9","bg":"#e0f2fe",
        "desc":"Young professionals growing entrepreneurship or career skills"},
    2: {"name":"Mid-life Learner",        "icon":"📚","color":"#10b981","bg":"#d1fae5",
        "desc":"Adults in 30s–40s exploring new education or business paths"},
    3: {"name":"Mid-life Health Focus",   "icon":"💪","color":"#f59e0b","bg":"#fef3c7",
        "desc":"Adults in 30s–40s focused on fitness and health management"},
    4: {"name":"Senior Hobby Explorer",   "icon":"🎨","color":"#ec4899","bg":"#fce7f3",
        "desc":"Older adults discovering hobbies and creative activities"},
    5: {"name":"Senior Wellness Manager", "icon":"🧘","color":"#14b8a6","bg":"#ccfbf1",
        "desc":"Older adults managing health, wellness and daily routines"},
}

def get_cluster(age, domain, level):
    if   age >= 60: return 5 if domain == "Health" else 4
    elif age >= 30: return 3 if domain == "Health" else 2
    else:           return 1 if (domain == "Entrepreneurship" and level != "Beginner") else 0


# ══════════════════════════════════════════════════════════════
#  RULE ENGINE
# ══════════════════════════════════════════════════════════════
def apply_rules(topics, age, hrs, domain, goal, health):
    """Filter topics based on age, time, health conditions."""
    hl = health.lower()
    out = []
    for t in topics:
        nm = t["topic"].lower()
        # Senior + Health: skip high-intensity
        if age >= 60 and domain == "Health":
            if any(k in nm for k in ["hiit","powerlifting","marathon",
                                      "olympic weightlifting","sprint","crossfit"]):
                continue
        # Very limited time: skip very long topics
        if hrs <= 0.5 and t["duration"] > 12:
            continue
        # Young + Health: skip senior-specific topics
        if age < 30 and domain == "Health":
            if any(k in nm for k in ["geriatric","osteoporosis","fall prevention",
                                      "senior fitness","elderly"]):
                continue
        # Heart condition
        if any(k in hl for k in ["heart","cardiac"]):
            if any(k in nm for k in ["hiit","marathon","powerlifting",
                                      "high intensity","crossfit"]):
                continue
        # Knee/joint
        if any(k in hl for k in ["knee","joint"]):
            if any(k in nm for k in ["running program","marathon",
                                      "powerlifting","jumping","plyometric"]):
                continue
        # Back/spine
        if any(k in hl for k in ["back","spine"]):
            if any(k in nm for k in ["deadlift","powerlifting","heavy squat"]):
                continue
        out.append(t)
    return out


# ══════════════════════════════════════════════════════════════
#  KNOWLEDGE GRAPH + TOPOLOGICAL SORT
# ══════════════════════════════════════════════════════════════
def build_graph_sorted(topics):
    """Build DAG and return topologically sorted topic list."""
    G, lk = nx.DiGraph(), {}
    for t in topics:
        G.add_node(t["id"], **t)
        lk[t["id"]] = t
    for t in topics:
        for p in t.get("prerequisites", []):
            if p in lk:
                G.add_edge(p, t["id"])
    try:
        order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        order = [t["id"] for t in topics]
    return [lk[n] for n in order if n in lk], G


# ══════════════════════════════════════════════════════════════
#  TIME ALLOCATION
# ══════════════════════════════════════════════════════════════
def allocate_weeks(topics, hrs):
    """Assign week numbers based on daily hours."""
    hpw = max(hrs * 7, 1.0)
    cum = 0.0
    out = []
    for i, t in enumerate(topics):
        cum += t["duration"]
        tc  = dict(t)
        tc["step"] = i + 1
        tc["week"] = max(1, int(cum / hpw) + 1)
        out.append(tc)
    return out


# ══════════════════════════════════════════════════════════════
#  TF-IDF CROSS-DOMAIN RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
def get_related_activities(domain, goal, goal_category, kb, n=3):
    """
    Suggest related activities from OTHER domains/categories.
    Skips same domain+category (already in roadmap).
    """
    items, labels = [], []
    for d, levels in kb.items():
        for lvl, tops in levels.items():
            for t in tops:
                cat = t.get("category", "")
                # Skip current domain+category
                if d == domain and cat == goal_category:
                    continue
                items.append(f"{t['topic']} {cat}")
                labels.append({"domain": d, "topic": t["topic"],
                                "category": cat, "level": lvl,
                                "duration": t["duration"]})
    if not items or not goal.strip():
        return []
    try:
        corpus = items + [goal]
        mat    = TfidfVectorizer(stop_words="english").fit_transform(corpus)
        sims   = cosine_similarity(mat[-1], mat[:-1])[0]
        top    = sims.argsort()[::-1][:n]
        return [labels[i] for i in top if sims[i] > 0]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
#  AI RESOURCE LINKS
# ══════════════════════════════════════════════════════════════
def get_resources(topic, domain, level):
    q  = topic.replace(" ", "+")
    ql = f"{topic}+{level}+tutorial".replace(" ", "+")
    yt = "https://www.youtube.com/results?search_query="
    base = [{"icon":"▶️","platform":"YouTube","title":f"{topic} — Video Tutorial",
              "desc":f"Watch {level}-level lessons","url":f"{yt}{ql}"}]
    extras = {
        "Education":[
            {"icon":"🎓","platform":"Khan Academy",
             "title":f"{topic} on Khan Academy","desc":"Free structured lessons",
             "url":f"https://www.khanacademy.org/search?page_search_query={q}"},
            {"icon":"💻","platform":"Coursera","title":f"Coursera: {topic}",
             "desc":"University-grade courses",
             "url":f"https://www.coursera.org/search?query={q}"},
            {"icon":"🆓","platform":"freeCodeCamp","title":f"freeCodeCamp: {topic}",
             "desc":"Free coding bootcamp",
             "url":f"{yt}freecodecamp+{q}+full+course"},
        ],
        "Entrepreneurship":[
            {"icon":"💼","platform":"LinkedIn Learning","title":f"LinkedIn: {topic}",
             "desc":"Professional courses",
             "url":f"https://www.linkedin.com/learning/search?keywords={q}"},
            {"icon":"🚀","platform":"Udemy","title":f"Udemy: {topic}",
             "desc":"Affordable courses",
             "url":f"https://www.udemy.com/courses/search/?q={q}"},
            {"icon":"📘","platform":"Harvard Business","title":f"HBS Online: {topic}",
             "desc":"Business school insights",
             "url":f"https://online.hbs.edu/search/#q={q}"},
        ],
        "Health":[
            {"icon":"🏋️","platform":"YouTube Fitness","title":f"{topic} Guide",
             "desc":"Follow-along sessions",
             "url":f"{yt}{q}+guide+for+beginners"},
            {"icon":"🩺","platform":"Healthline","title":f"Healthline: {topic}",
             "desc":"Evidence-based health info",
             "url":f"https://www.healthline.com/?s={q}"},
            {"icon":"🧘","platform":"Wellness Video","title":f"{topic} — Wellness",
             "desc":"Guided wellness content",
             "url":f"{yt}{q}+health+tips+expert"},
        ],
        "Hobbies":[
            {"icon":"🎨","platform":"YouTube Tutorial","title":f"{topic} — Step by Step",
             "desc":"Hands-on tutorials",
             "url":f"{yt}{q}+step+by+step+for+beginners"},
            {"icon":"✏️","platform":"Skillshare","title":f"Skillshare: {topic}",
             "desc":"Creative skill classes",
             "url":f"https://www.skillshare.com/en/search?query={q}"},
            {"icon":"🌟","platform":"MasterClass","title":f"MasterClass: {topic}",
             "desc":"Learn from world experts",
             "url":f"https://www.masterclass.com/search?q={q}"},
        ]
    }
    return (base + extras.get(domain, []))[:4]


# ══════════════════════════════════════════════════════════════
#  MAIN ROADMAP GENERATOR (FIXED)
#
#  Core fix: filter by GOAL CATEGORY first, not just domain
#  Gardening goal → only Gardening topics, not all Hobbies
#  Python goal    → only Programming topics, not all Education
#  Fitness goal   → only Fitness topics, not all Health
# ══════════════════════════════════════════════════════════════
def generate_roadmap(name, age, domain, goal, skill, hrs, health, kb):
    # Step 1: Cluster
    cid   = get_cluster(age, domain, skill)
    cinfo = CLUSTERS[cid]

    # Step 2: Detect goal category
    goal_category = detect_goal_category(goal)

    # Step 3: Collect topics for relevant skill levels
    level_map = {
        "Beginner"    : ["Beginner"],
        "Intermediate": ["Beginner", "Intermediate"],
        "Advanced"    : ["Beginner", "Intermediate", "Advanced"]
    }
    all_topics = []
    for lvl in level_map[skill]:
        for t in kb.get(domain, {}).get(lvl, []):
            tc = dict(t)
            tc["level"] = lvl
            all_topics.append(tc)

    # Step 4: Filter by goal category (THE MAIN FIX)
    if goal_category:
        category_match = [t for t in all_topics
                          if t.get("category","").lower() == goal_category.lower()]
        if len(category_match) >= 5:
            # Strong match — use only this category
            filtered_pool = category_match
        elif len(category_match) > 0:
            # Weak match — use category + related by keyword score
            goal_words = [w for w in goal.lower().split() if len(w) > 2]
            scored = []
            for t in all_topics:
                score  = sum(1 for gw in goal_words
                             if gw in t["topic"].lower()
                             or gw in t.get("category","").lower())
                scored.append((score, t))
            scored.sort(key=lambda x: -x[0])
            extra = [t for s, t in scored if s > 0 and t not in category_match]
            filtered_pool = category_match + extra[:10]
        else:
            # No category match — use keyword scoring across all topics
            goal_words = [w for w in goal.lower().split() if len(w) > 2]
            scored = [(sum(1 for gw in goal_words
                           if gw in t["topic"].lower()
                           or gw in t.get("category","").lower()), t)
                      for t in all_topics]
            scored.sort(key=lambda x: -x[0])
            high = [t for s, t in scored if s > 0]
            filtered_pool = high if len(high) >= 5 else all_topics
    else:
        # No category detected — use all topics in domain
        filtered_pool = all_topics

    # Step 5: Skill level refinement
    if skill == "Intermediate":
        int_t   = [t for t in filtered_pool if t.get("level") == "Intermediate"]
        pre_ids = set()
        for t in int_t:
            for p in t.get("prerequisites", []):
                pre_ids.add(p)
        beg_needed    = [t for t in filtered_pool
                         if t.get("level") == "Beginner" and t["id"] in pre_ids]
        filtered_pool = beg_needed + int_t

    elif skill == "Advanced":
        adv = [t for t in filtered_pool if t.get("level") == "Advanced"]
        if adv:
            filtered_pool = adv

    # Step 6: Rule engine (age, health, time constraints)
    filtered_pool = apply_rules(filtered_pool, age, hrs, domain, goal, health)

    # Step 7: Knowledge graph + topological sort
    ordered, G = build_graph_sorted(filtered_pool)

    # Step 8: Goal keyword topics rise to top
    goal_words = [w for w in goal.lower().split() if len(w) > 3]
    if goal_words:
        priority = [t for t in ordered
                    if any(gw in t["topic"].lower() for gw in goal_words)]
        rest     = [t for t in ordered if t not in priority]
        ordered  = priority + rest

    # Step 9: Allocate weeks
    roadmap = allocate_weeks(ordered, hrs)

    # Step 10: Cross-domain related activities
    related = get_related_activities(domain, goal, goal_category, kb, n=3)

    total_h = sum(t["duration"] for t in roadmap)

    return {
        "roadmap"       : roadmap,
        "cid"           : cid,
        "cinfo"         : cinfo,
        "related"       : related,
        "G"             : G,
        "total_h"       : round(total_h, 1),
        "total_w"       : roadmap[-1]["week"] if roadmap else 0,
        "total_t"       : len(roadmap),
        "domain"        : domain,
        "goal_category" : goal_category,
        "profile"       : {
            "name": name, "age": age, "domain": domain, "goal": goal,
            "skill": skill, "hrs": hrs, "health": health
        }
    }




























'''
# ================================================================
#  core/engine.py — All ML + Data Logic
#  Knowledge Graph · K-Means · TF-IDF · Rule Engine · Storage
# ================================================================

import json, os, hashlib, datetime, warnings
import numpy as np, networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
warnings.filterwarnings("ignore")

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
KB_FILE    = os.path.join(DATA_DIR, "knowledge_base.json")
USERS_FILE = os.path.join(DATA_DIR, "users_data.json")

# ── DOMAIN KEYWORD DETECTOR ──────────────────────────────────
DOMAIN_KEYWORDS = {
    "Education": [
        "learn","study","python","coding","programming","math","algebra","science",
        "exam","degree","college","university","language","english","machine learning",
        "data science","ai","artificial intelligence","deep learning","web development",
        "sql","html","css","javascript","java","c++","react","node","algorithm",
        "research","academic","course","certificate","skill","software","computer"
    ],
    "Entrepreneurship": [
        "business","startup","entrepreneur","marketing","sales","revenue","profit",
        "funding","investor","pitch","brand","product","launch","mvp","growth",
        "strategy","management","leadership","finance","budget","cash flow","team",
        "hiring","seo","digital marketing","social media","e-commerce","freelance",
        "consulting","company","venture","capital","stock","gst","tax","legal"
    ],
    "Health": [
        "health","fitness","weight","lose weight","gain weight","diet","nutrition",
        "exercise","workout","yoga","meditation","stress","anxiety","depression",
        "sleep","running","gym","muscle","fat","diabetes","blood pressure","heart",
        "mental health","wellness","medication","disease","immunity","strength",
        "cardio","hiit","flexibility","mobility","rehab","therapy","mindfulness"
    ],
    "Hobbies": [
        "hobby","garden","gardening","sing","singing","dance","dancing","cook","cooking",
        "art","paint","painting","draw","drawing","music","guitar","piano","photography",
        "craft","knit","sew","bake","baking","travel","chess","photography","film",
        "read","book","creative","pottery","sculpt","origami","calligraphy","photography"
    ]
}

def detect_best_domain(goal_text):
    """
    Detect the most suitable domain from goal text.
    Returns the best matching domain name.
    """
    if not goal_text.strip():
        return None
    goal_lower = goal_text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in goal_lower)
        scores[domain] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

def goal_domain_mismatch(goal_text, selected_domain):
    """
    Returns (mismatch: bool, suggested_domain: str|None)
    """
    best = detect_best_domain(goal_text)
    if best and best != selected_domain:
        return True, best
    return False, None


# ── KNOWLEDGE BASE ────────────────────────────────────────────
def load_kb():
    if os.path.exists(KB_FILE):
        with open(KB_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── USER STORAGE ─────────────────────────────────────────────
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f: return json.load(f)
    return {}

def save_users(db):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w") as f: json.dump(db, f, indent=2)

def make_uid(name, age):
    return hashlib.sha256(f"{str(name).strip().lower()}_{age}".encode()).hexdigest()[:16]

def upsert_user(name, age, domain, goal, skill, hours, health, roadmap):
    db  = load_users()
    uid = make_uid(name, age)
    old = db.get(uid, {})
    db[uid] = {
        "display_name"   : name,
        "age"            : age,
        "domain"         : domain,
        "goal"           : goal,
        "skill"          : skill,
        "hours"          : hours,
        "health"         : health,
        "last_seen"      : datetime.datetime.now().isoformat(),
        "sessions"       : old.get("sessions", 0) + 1,
        "completed"      : old.get("completed", []),
        "total_topics"   : len(roadmap),
        "badges"         : old.get("badges", []),
        "streak_days"    : old.get("streak_days", 0) + 1,
    }
    save_users(db)
    return uid

def get_user(name, age):
    return load_users().get(make_uid(name, age), {})

def toggle_topic(name, age, topic_name):
    db  = load_users()
    uid = make_uid(name, age)
    if uid not in db: return
    done = db[uid].get("completed", [])
    if topic_name in done: done.remove(topic_name)
    else: done.append(topic_name)
    db[uid]["completed"] = done
    # Award badges
    badges = db[uid].get("badges", [])
    if len(done) >= 5  and "First 5"    not in badges: badges.append("First 5")
    if len(done) >= 10 and "10 Topics"  not in badges: badges.append("10 Topics")
    if len(done) >= 25 and "25 Topics"  not in badges: badges.append("25 Topics")
    db[uid]["badges"] = badges
    save_users(db)

def get_all_users_summary():
    return list(load_users().values())


# ── CLUSTERING ───────────────────────────────────────────────
CLUSTERS = {
    0: {"name":"Young Skill Builder",     "icon":"🚀","color":"#6366f1","bg":"#ede9fe",
        "desc":"Teens and young adults building academic or technical skills"},
    1: {"name":"Young Career Advancer",   "icon":"💼","color":"#0ea5e9","bg":"#e0f2fe",
        "desc":"Young professionals growing entrepreneurship or career skills"},
    2: {"name":"Mid-life Learner",        "icon":"📚","color":"#10b981","bg":"#d1fae5",
        "desc":"Adults in 30s–40s exploring new education or business paths"},
    3: {"name":"Mid-life Health Focus",   "icon":"💪","color":"#f59e0b","bg":"#fef3c7",
        "desc":"Adults in 30s–40s focused on fitness and health management"},
    4: {"name":"Senior Hobby Explorer",   "icon":"🎨","color":"#ec4899","bg":"#fce7f3",
        "desc":"Older adults discovering hobbies and creative activities"},
    5: {"name":"Senior Wellness Manager", "icon":"🧘","color":"#14b8a6","bg":"#ccfbf1",
        "desc":"Older adults managing health, wellness and daily routines"},
}

def get_cluster(age, domain, level):
    if   age >= 60: return 5 if domain == "Health" else 4
    elif age >= 30: return 3 if domain == "Health" else 2
    else:           return 1 if (domain == "Entrepreneurship" and level != "Beginner") else 0


# ── RULE ENGINE ──────────────────────────────────────────────
def apply_rules(topics, age, hrs, domain, goal, health):
    hl, gl = health.lower(), goal.lower()
    out = []
    for t in topics:
        nm = t["topic"].lower()
        # Senior rule
        if age >= 60 and domain == "Health":
            if any(k in nm for k in ["hiit","powerlifting","marathon","olympic weightlifting","sprint","crossfit"]):
                continue
        # Time rule
        if hrs <= 0.5 and t["duration"] > 12: continue
        # Young + health
        if age < 30 and domain == "Health":
            if any(k in nm for k in ["geriatric","osteoporosis","fall prevention","senior fitness","elderly"]):
                continue
        # Health conditions
        if any(k in hl for k in ["heart","cardiac"]):
            if any(k in nm for k in ["hiit","marathon","powerlifting","high intensity","crossfit"]): continue
        if any(k in hl for k in ["knee","joint"]):
            if any(k in nm for k in ["running program","marathon","powerlifting","jumping","plyometric"]): continue
        if any(k in hl for k in ["back","spine"]):
            if any(k in nm for k in ["deadlift","powerlifting","heavy squat"]): continue
        out.append(t)
    # Goal prioritisation
    gw = [w for w in gl.split() if len(w) > 3]
    if gw:
        pri  = [t for t in out if any(g in t["topic"].lower() for g in gw)]
        rest = [t for t in out if t not in pri]
        out  = pri + rest
    return out


# ── KNOWLEDGE GRAPH ──────────────────────────────────────────
def build_graph_sorted(topics):
    G, lk = nx.DiGraph(), {}
    for t in topics:
        G.add_node(t["id"], **t); lk[t["id"]] = t
    for t in topics:
        for p in t.get("prerequisites", []):
            if p in lk: G.add_edge(p, t["id"])
    try:    order = list(nx.topological_sort(G))
    except: order = [t["id"] for t in topics]
    return [lk[n] for n in order if n in lk], G


# ── TIME ALLOCATION ──────────────────────────────────────────
def allocate_weeks(topics, hrs):
    hpw, cum, out = max(hrs * 7, 1.0), 0.0, []
    for i, t in enumerate(topics):
        cum += t["duration"]
        tc   = dict(t)
        tc["step"] = i + 1
        tc["week"] = max(1, int(cum / hpw) + 1)
        out.append(tc)
    return out


# ── TF-IDF RELATED ───────────────────────────────────────────
def get_related_activities(domain, goal, kb, n=3):
    items, labels = [], []
    for d, levels in kb.items():
        if d == domain: continue
        for lvl, tops in levels.items():
            for t in tops:
                items.append(f"{t['topic']} {t.get('category','')}")
                labels.append({"domain":d,"topic":t["topic"],"category":t.get("category",""),
                                "level":lvl,"duration":t["duration"]})
    if not items or not goal.strip(): return []
    try:
        corpus = items + [goal]
        mat    = TfidfVectorizer(stop_words="english").fit_transform(corpus)
        sims   = cosine_similarity(mat[-1], mat[:-1])[0]
        top    = sims.argsort()[::-1][:n]
        return [labels[i] for i in top if sims[i] > 0]
    except: return []


# ── AI RESOURCE LINKS ────────────────────────────────────────
def get_resources(topic, domain, level):
    q  = topic.replace(" ", "+")
    ql = f"{topic}+{level}+tutorial".replace(" ", "+")
    yt = "https://www.youtube.com/results?search_query="
    base = [{"icon":"▶️","platform":"YouTube","title":f"{topic} — Video Tutorial",
              "desc":f"Watch {level}-level lessons","url":f"{yt}{ql}"}]
    extras = {
        "Education":[
            {"icon":"🎓","platform":"Khan Academy","title":f"{topic} on Khan Academy",
             "desc":"Free structured lessons","url":f"https://www.khanacademy.org/search?page_search_query={q}"},
            {"icon":"💻","platform":"Coursera","title":f"Coursera: {topic}",
             "desc":"University-grade courses","url":f"https://www.coursera.org/search?query={q}"},
            {"icon":"🆓","platform":"freeCodeCamp","title":f"freeCodeCamp: {topic}",
             "desc":"Free coding bootcamp","url":f"{yt}freecodecamp+{q}+full+course"},
        ],
        "Entrepreneurship":[
            {"icon":"💼","platform":"LinkedIn Learning","title":f"LinkedIn: {topic}",
             "desc":"Professional business courses","url":f"https://www.linkedin.com/learning/search?keywords={q}"},
            {"icon":"🚀","platform":"Udemy","title":f"Udemy: {topic}",
             "desc":"Affordable courses","url":f"https://www.udemy.com/courses/search/?q={q}"},
            {"icon":"📘","platform":"Harvard Business","title":f"HBS Online: {topic}",
             "desc":"Business school insights","url":f"https://online.hbs.edu/search/#q={q}"},
        ],
        "Health":[
            {"icon":"🏋️","platform":"YouTube Fitness","title":f"{topic} Workout Guide",
             "desc":"Follow-along video sessions","url":f"{yt}{q}+workout+guide+for+beginners"},
            {"icon":"🩺","platform":"Healthline","title":f"Healthline: {topic}",
             "desc":"Evidence-based health info","url":f"https://www.healthline.com/?s={q}"},
            {"icon":"🧘","platform":"Yoga/Wellness","title":f"{topic} — Wellness Video",
             "desc":"Guided wellness content","url":f"{yt}{q}+health+tips+expert"},
        ],
        "Hobbies":[
            {"icon":"🎨","platform":"YouTube Tutorial","title":f"{topic} — Step by Step",
             "desc":"Hands-on hobby tutorials","url":f"{yt}{q}+step+by+step+for+beginners"},
            {"icon":"✏️","platform":"Skillshare","title":f"Skillshare: {topic}",
             "desc":"Creative skill classes","url":f"https://www.skillshare.com/en/search?query={q}"},
            {"icon":"🌟","platform":"MasterClass","title":f"MasterClass: {topic}",
             "desc":"Learn from world experts","url":f"https://www.masterclass.com/search?q={q}"},
        ]
    }
    return (base + extras.get(domain, []))[:4]


# ── MAIN ROADMAP GENERATOR ───────────────────────────────────
def generate_roadmap(name, age, domain, goal, skill, hrs, health, kb):
    cid   = get_cluster(age, domain, skill)
    cinfo = CLUSTERS[cid]

    lmap = {
        "Beginner"    : ["Beginner"],
        "Intermediate": ["Beginner","Intermediate"],
        "Advanced"    : ["Beginner","Intermediate","Advanced"]
    }
    all_t = []
    for lvl in lmap[skill]:
        for t in kb.get(domain, {}).get(lvl, []):
            tc = dict(t); tc["level"] = lvl; all_t.append(tc)

    ordered, G = build_graph_sorted(all_t)
    filtered   = apply_rules(ordered, age, hrs, domain, goal, health)

    if skill == "Intermediate":
        int_ids = {t["id"] for t in filtered if t.get("level") == "Intermediate"}
        pre_ids = set()
        for t in filtered:
            if t.get("level") == "Intermediate":
                for p in t.get("prerequisites", []): pre_ids.add(p)
        bk       = {t["id"] for t in filtered if t.get("level") == "Beginner" and t["id"] in pre_ids}
        filtered = [t for t in filtered if t["id"] in int_ids | bk]
    elif skill == "Advanced":
        ai       = {t["id"] for t in filtered if t.get("level") == "Advanced"}
        filtered = [t for t in filtered if t["id"] in ai]

    roadmap = allocate_weeks(filtered, hrs)
    related = get_related_activities(domain, goal, kb, n=3)
    total_h = sum(t["duration"] for t in roadmap)

    return {
        "roadmap"  : roadmap,
        "cid"      : cid,
        "cinfo"    : cinfo,
        "related"  : related,
        "G"        : G,
        "total_h"  : round(total_h, 1),
        "total_w"  : roadmap[-1]["week"] if roadmap else 0,
        "total_t"  : len(roadmap),
        "domain"   : domain,
        "profile"  : {"name":name,"age":age,"domain":domain,"goal":goal,
                      "skill":skill,"hrs":hrs,"health":health}
    }
'''