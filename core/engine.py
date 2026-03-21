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