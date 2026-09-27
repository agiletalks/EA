import json
import re
import os
import math
import urllib.request

print("Starting Emotional Agility Practitioner Guide Master Curation & Text Repair...")

# 1. Download or load English 10,000 wordlist for DP token unsmashing
word_cost = {}
wordlist_cache = "tools/guide_tools/english_10k.txt"

if not os.path.exists(wordlist_cache):
    url = 'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears.txt'
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            words = response.read().decode('utf-8').splitlines()
            with open(wordlist_cache, "w", encoding="utf-8") as f:
                f.write("\n".join(words))
    except Exception as e:
        print(f"Warning: Could not download wordlist: {e}")
        words = []
else:
    with open(wordlist_cache, "r", encoding="utf-8") as f:
        words = f.read().splitlines()

total_words = len(words) if words else 10000
for i, w in enumerate(words):
    word_cost[w.lower()] = math.log((i + 1) * math.log(total_words + 1))

# Domain-specific terms for Emotional Agility
domain_terms = [
    'agility', 'emotional', 'sawubona', 'practitioner', 'workbook', 'unhooked', 'unhooking',
    'susan', 'david', 'room', 'map', 'holding', 'stretching', 'flipchart', 'flipcharts',
    'stepped', 'stepping', 'showing', 'walking', 'moving', 'brooding', 'bottling', 'monkey',
    'compassion', 'curiosity', 'courage', 'mindset', 'debrief', 'harvesting', 'harvest',
    'resourced', 'spacing', 'spaciousness', 'stanceless', 'fidelity', 'wellbeing', 'well-being',
    'badge', 'cohort', 'offsite', 'breakout', 'playlist', 'reclaiming', 'authorship',
    'theatricals', 'metacircle', 'touchstone', 'grounding', 'groundwork', 'guardrails',
    'intimacy', 'confidentiality', 'disclosure', 'waterfall', 'piggybacking', 'intention'
]
for t in domain_terms:
    word_cost[t.lower()] = math.log(3 * math.log(total_words + 1))

def dp_split_smashed_token(s):
    s_clean = re.sub(r'[^a-zA-Z]', '', s)
    if len(s_clean) < 7:
        return s
    s_lower = s_clean.lower()
    if s_lower in word_cost and len(s_clean) < 14:
        return s
        
    n = len(s_lower)
    cost = [0] + [float('inf')] * n
    prev = [0] * (n + 1)
    
    for i in range(1, n + 1):
        for j in range(max(0, i - 18), i):
            sub = s_lower[j:i]
            if sub in word_cost:
                c = cost[j] + word_cost[sub]
                if c < cost[i]:
                    cost[i] = c
                    prev[i] = j
                    
    if cost[n] == float('inf'):
        return s
        
    tokens = []
    idx = n
    while idx > 0:
        p = prev[idx]
        tokens.append(s_clean[p:idx])
        idx = p
    tokens.reverse()
    
    single_letters = [t for t in tokens if len(t) == 1 and t.lower() not in ['a', 'i']]
    if len(single_letters) > 1:
        return s
        
    return " ".join(tokens)

# Precision regex replacements
PRECISION_REPLACEMENTS = [
    (r'\beeeeb\b', ''),
    (r'\btheunique\b', 'the unique'),
    (r'\bandnothingelse\b', 'and nothing else'),
    (r'\bdonotneed\b', 'do not need'),
    (r'\btoremember\b', 'to remember'),
    (r'\bthiswork\b', 'this work'),
    (r'\bfrstengagement\b', 'first engagement'),
    (r'\bfrst\b', 'first'),
    (r'\btheparticipants\b', 'the participants'),
    (r'\barepagesinyour\b', 'are pages in your'),
    (r'\bdelitymactand\b', 'fidelity, impact, and'),
    (r'\bdelitymact\b', 'fidelity, impact'),
    (r'\bRightnow\b', 'Right now'),
    (r'\beveryroom\b', 'every room'),
    (r'\bthatwhenyouask\b', 'that when you ask'),
    (r'\blandwhere\b', 'land where'),
    (r'\byouintend\b', 'you intend'),
    (r'\bTwoBooks,OnePage\b', 'Two Books, One Page'),
    (r'\bTwoBooks\b', 'Two Books'),
    (r'\bOnePage\b', 'One Page'),
    (r'\bParticipantWorkbook\b', 'Participant Workbook'),
    (r'\bPractitionerGuide\b', 'Practitioner Guide'),
    (r'\bEmotionalAgility\b', 'Emotional Agility'),
    (r'\bEmotionalgility\b', 'Emotional Agility'),
    (r'\bShowingUp\b', 'Showing Up'),
    (r'\bhowingUp\b', 'Showing Up'),
    (r'\bhowingU\b', 'Showing Up'),
    (r'\bhowing\b', 'Showing Up'),
    (r'\bSteppingOut\b', 'Stepping Out'),
    (r'\bStppingu\b', 'Stepping Out'),
    (r'\bSteppingu\b', 'Stepping Out'),
    (r'\bWalkingYourWhy\b', 'Walking Your Why'),
    (r'\bWalkingourWhy\b', 'Walking Your Why'),
    (r'\bMovingOn\b', 'Moving On'),
    (r'\bMovingn\b', 'Moving On'),
    (r'\bLivingIntotheQuestion\b', 'Living Into the Question'),
    (r'\bLivingInto theQuestion\b', 'Living Into the Question'),
    (r'\bivingInto theQustion\b', 'Living Into the Question'),
    (r'\bOpeningtheQuestion\b', 'Opening the Question'),
    (r'\bTheRoomMap\b', 'The Room Map'),
    (r'\bMood-taskmatching\b', 'Mood-task matching'),
    (r'\bGoingmeta\b', 'Going meta'),
    (r'\bInYourBackPocket\b', 'In Your Back Pocket'),
    (r'\bHoldtheReveal\b', 'Hold the Reveal'),
    (r'\bWhatThisModuleTeaches\b', 'What This Module Teaches'),
    (r'\bTheJourney\b', 'The Journey'),
    (r'\bTheClock\b', 'The Clock'),
    (r'\bTheShape\b', 'The Shape'),
    (r'\bStartHere\b', 'Start Here'),
    (r'\bSusanDavid\b', 'Susan David'),
    (r'\bHarvardBusinessReview\b', 'Harvard Business Review'),
    (r'\bThinkers5o\b', 'Thinkers50'),
    (r'\btheBreakthrough\b', 'the Breakthrough'),
    (r'\bBreakthroughIdea\b', 'Breakthrough Idea'),
    (r'\bWallStreetJournal\b', 'Wall Street Journal'),
    (r'\bafterarainstorm-shadow\b', 'after a rainstorm — shadow'),
    (r'\bafterarainstorm\b', 'after a rainstorm'),
    (r'\bsustainablealthy,resilintl\b', 'sustainable, healthy, resilient'),
    (r'\binevitableuncertainty,risks,and\b', 'inevitable uncertainty, risks, and'),
    (r'\binevitableuncertainty\b', 'inevitable uncertainty'),
    (r'\bculture,ngagement,wellbeing\b', 'culture, engagement, wellbeing'),
    (r'\bfeelings?”createsroom\b', 'feelings?” creates room'),
    (r'\bcreatesroom\b', 'creates room'),
    (r'\baroundexperience\b', 'around experience'),
    (r'\bcollapsesevent\b', 'collapses event'),
    (r'\bandresponse\b', 'and response'),
    (r'\bWhereamoment\b', 'Where a moment'),
    (r'\bcanderail\b', 'can derail'),
    (r'\bWatch&Adjust\b', 'Watch & Adjust'),
    (r'\btowatchfor\b', 'to watch for'),
    (r'\bintobeing\b', 'into being'),
    (r'\bwhole heart ed\b', 'wholehearted'),
    (r'\bAt itscore\b', 'At its core'),
    (r'\bWhen the storywrites us\b', 'When the story writes us'),
    (r'\bMe, We, s,Beyod\b', 'Me, We, Us, Beyond'),
    (r'\bShortnrparationtmStartwithPreparethenreadoldsedirectndridgeseephoomMappenwhileyoufacilitatandmrk\b', 'Short on preparation time? Start with Prepare, then read Hold, redirect, and Bridge. Keep The Room Map open while you facilitate, and mark In Your Back Pocket for quick recovery.'),
    (r'\bAharvest isthgatheringafteranxpriencewhateoloticedroducedoroncludedcollected fromthmandmadevisible\b', 'A harvest is the gathering after an experience — what people noticed, produced, or concluded, collected from them and made visible to the'),
    (r'\bwhole roomaword each in around,thecompletion of aoneword sentenceanswersona flipchatso thegroupcanmakemeaning\b', 'whole room (a word each in a round, the completion of a one-word sentence, answers on a flipchart) so the group can make meaning'),
    (r'\bofittogether\b', 'of it together'),
    (r'\bIftheatraldiapearedvnuteoulstillwmyetivandwhaitimtringtrea\?\b', 'If the theatricals disappeared in five minutes, would you still know what the objective is and what it is trying to create? Then protect it.'),
    (r'\bEarth·Moon·Jupiter\b', 'Earth · Moon · Jupiter'),
    (r'\bEarthPMoonPJupiter\b', 'Earth · Moon · Jupiter'),
    (r'\bSawubona\"XIsee you\b', '“Sawubona” — I see you'),
    (r'\b“Sawubona\"—Isee you\b', '“Sawubona” — I see you'),
    (r'\b“Sawubona\"-I see you\b', '“Sawubona” — I see you'),
    (r'\bisheretoheloumeettheroommeetourselfandfacilitateEmotionalAgilitywithdelitymactand\b', 'is here to help you meet the room, meet yourself, and facilitate Emotional Agility with fidelity, impact, and'),
    (r'\bThwltfnaablntad clinical assesment,orlinical teatmenthat holds even whenyou are clinically trainedorthe settingisaclinic orhealthcontxt\.\b', 'This work is educational and transformative; it is not therapy, clinical assessment, or clinical treatment. That holds even when you are clinically trained or the setting is a clinical or health context.'),
    (r'\bThefollowingexerciseisaveryusefulandpowerfulexplorationthatwillinformthediscussionsthatfollow\.Youwillgetthemost outf the exerciseif yourespondhonestlyand openly\.Althoughwewillesharing someoftheinsightsthat arisefromityoucanchoosewhich insightsyouharewiththegroupandwhichyouprfetremainprivateleaeonlhareinsightsthatyouarecomfortableharing\b', '“The following exercise is a very useful and powerful exploration that will inform the discussions that follow. You will get the most out of the exercise if you respond honestly and openly. Although we will be sharing some of the insights that arise from it, you can choose which insights you share with the group and which you prefer to remain private. Please only share insights that you are comfortable sharing.”'),
    (r'\bPleasechoose somethingthat isrealand deepand trueforyouand that youareresourced tobewithfortherestoftheday\.\b', '“Please choose something that is real and deep and true for you, and that you are resourced to be with for the rest of the day.”'),
]

def clean_and_repair_text(text):
    text = re.sub(r'eeeeb', '', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    for pat, rep in PRECISION_REPLACEMENTS:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
        
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    text = re.sub(r'([a-zA-Z0-9]),([a-zA-Z])', r'\1, \2', text)
    text = re.sub(r'([a-zA-Z0-9])\.([A-Z])', r'\1. \2', text)
    text = re.sub(r'([a-zA-Z0-9]);([a-zA-Z])', r'\1; \2', text)
    text = re.sub(r'([a-zA-Z0-9]):([a-zA-Z])', r'\1: \2', text)
    text = re.sub(r'([a-zA-Z0-9])\?([A-Z])', r'\1? \2', text)
    text = re.sub(r'([a-zA-Z0-9])\!([A-Z])', r'\1! \2', text)
    
    words_list = text.split()
    repaired_words = []
    for w in words_list:
        clean_w = re.sub(r'[^a-zA-Z]', '', w)
        if len(clean_w) >= 12 and not any(k in clean_w.lower() for k in ['http', 'www', 'harvard', 'practitioner', 'facilitat']):
            split_w = dp_split_smashed_token(clean_w)
            if split_w != clean_w:
                w = w.replace(clean_w, split_w)
        repaired_words.append(w)
        
    text = " ".join(repaired_words)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

# Full curated article bodies for key pages where OCR layout scrambled columns
CURATED_ARTICLES = {
    "PG_Page_001_Intro_IMG_5556.JPG": """
<h3 class="article-heading">Hello, World.</h3>
<p class="article-paragraph">Just as the sky is home to all kinds of weather, we have the unique human capacity to experience a full range of emotions, thoughts, stories, and situations.</p>
<p class="article-paragraph">The way we navigate these impacts every aspect of ourselves and our organizations: culture, engagement, wellbeing, leadership, and so much more.</p>
<p class="article-paragraph">Just as the healing balm of a sunny day unfolds after a rainstorm — shadow coexisting with light — the most sustainable, healthy, resilient organizations are those that grow alongside inevitable uncertainty, risks, and challenge.</p>
<p class="article-paragraph">There is no innovation without potential failure; no collaboration without conflict. There is no capacity to thrive without the skills to navigate what is.</p>
<p class="article-paragraph">It's a world where the only certainty is uncertainty.</p>
<h3 class="article-heading">Meet EMOTIONAL AGILITY</h3>
<p class="article-paragraph"><strong>Introduction to the Practitioner Journey</strong></p>
""",

    "PG_Page_006_Sawubona_IMG_5560.JPG": """
<h3 class="article-heading">Sawubona.</h3>
<p class="article-paragraph">In South Africa, where I come from, <strong>“Sawubona”</strong> is the Zulu word for “hello.”</p>
<p class="article-paragraph">There's a beautiful and powerful intention behind the word because “sawubona” literally translated, means:</p>
<blockquote class="article-quote">“I see you, and by seeing you, I bring you into being.”</blockquote>
<p class="article-paragraph">At its core, <strong>Emotional Agility</strong> is about the capacity to see ourselves and others in a wholehearted and healthy way. It's a set of essential psychological skills for our complex world; a world that often chooses not to see.</p>
<p class="article-paragraph">I am so grateful to have the opportunity to share it with you.</p>
<p class="article-paragraph" style="margin-top: 24px;">Warmly,<br><strong>Susan David, Ph.D.</strong></p>
""",

    "PG_Page_007_About_IMG_5561.JPG": """
<h3 class="article-heading">About Dr. Susan David</h3>
<p class="article-paragraph">Dr. Susan David is a Harvard Medical School psychologist, TED speaker, and the #1 Wall Street Journal bestselling author of <em>Emotional Agility</em>.</p>
<p class="article-paragraph">She created the Emotional Agility framework, recognized by <strong>Harvard Business Review</strong> as its <em>Management Idea of the Year</em> and by <strong>Thinkers50</strong> with the <em>Breakthrough Idea Award</em>. Her TED Talk has more than 12 million views. Named by Thinkers50 as one of the world's most influential management thinkers, her work is reshaping workplaces and homes worldwide.</p>
<ul style="margin: 20px 0 20px 24px; line-height: 2;">
  <li><strong>#1 Wall Street Journal Bestselling Author</strong></li>
  <li><strong>Winner of the Thinkers50 Breakthrough Idea Award</strong></li>
  <li><strong>Recipient of the Harvard Business Review Management Idea of the Year</strong></li>
  <li><strong>Cofounder of the Institute of Coaching</strong> (a Harvard Medical School / McLean Affiliate)</li>
  <li><strong>Expert Contributor</strong> to the U.S. Surgeon General's Mental Health and Well-being at Work Roundtable</li>
</ul>
<p class="article-paragraph" style="color: var(--text-muted); font-size: 0.95em;">Follow: @SUSANDAVID_PHD · susandavid.com</p>
""",

    "PG_P_StartHere_01_IMG_5562.JPG": """
<h3 class="article-heading">Start Here</h3>
<blockquote class="article-quote">“Sawubona” — I see you.</blockquote>
<p class="article-paragraph">This Practitioner Guide is here to help you meet the room, meet yourself, and facilitate Emotional Agility with fidelity, impact, and beauty. It's got you. You've got you.</p>
<p class="article-paragraph">In every room that this work opens, a guest arrives. Right now, that guest is you. Welcome.</p>

<h3 class="article-heading">How to Use This Guide</h3>
<p class="article-paragraph">The Guide assumes certification, and nothing else. You do not need to remember every move, or to have run this work already. Before your first engagement, read this front section, then each module's practitioner pages, in the order you plan to facilitate.</p>

<h3 class="article-heading">Two Books, One Page Number</h3>
<p class="article-paragraph">The Emotional Agility Practitioner Guide and the Emotional Agility Participant Workbook page numbers mirror one another. For example: your <strong>Hooked, Page 12</strong> will be the same as the participants' <strong>Hooked, Page 12</strong>. That way you can be confident that when you ask participants to turn to a given page, they’ll land where you intend.</p>
<p class="article-paragraph">In addition, there are pages in your Practitioner Guide that do not appear in the Participant Workbook. These help you introduce a prompt, debrief a conversation, adapt an exercise, and similar. These pages are included at the beginning of each module and will have the identifier <em>“Practitioner”</em> and the practitioner-specific page number (for example: <em>Hooked · Practitioner 1</em>; <em>Hooked · Practitioner 2</em>) in the footer. Practitioner numbering restarts with each module.</p>

<h3 class="article-heading">The Markers (課堂四大引導標記)</h3>
<p class="article-paragraph">Every module's practitioner pages use the same small set of labels. In <strong>The Room Map</strong>, every activity has four columns:</p>

<div class="article-callout callout-dosay">
  <div class="callout-header"><span class="callout-icon">🗣️</span> <span class="callout-title">DO / SAY (導師引導指令與開口金句)</span></div>
  <div class="callout-content">What you do, and the lines you say aloud. Spoken lines are placed in quotation marks.</div>
</div>

<div class="article-callout callout-hold">
  <div class="callout-header"><span class="callout-icon">🛑</span> <span class="callout-title">HOLD (刻意留白 / 暫不介入)</span></div>
  <div class="callout-content">What you deliberately don't facilitate, say, or unpack just yet. Protect the space for discovery.</div>
</div>

<div class="article-callout callout-listen">
  <div class="callout-header"><span class="callout-icon">👂</span> <span class="callout-title">LISTEN FOR (傾聽學員訊號)</span></div>
  <div class="callout-content">What to be attuned to in the room's energy, language, resistance, or breakthroughs.</div>
</div>

<div class="article-callout callout-bridge">
  <div class="callout-header"><span class="callout-icon">🌉</span> <span class="callout-title">BRIDGE (轉場橋樑句)</span></div>
  <div class="callout-content">The sentence you say aloud to transition the room cleanly into the next activity.</div>
</div>

<div class="article-callout callout-adjust">
  <div class="callout-header"><span class="callout-icon">⚡</span> <span class="callout-title">WATCH & ADJUST (現場應變處置)</span></div>
  <div class="callout-content">Where a moment can derail: what to watch for, paired with the small move to make if it happens.</div>
</div>

<div class="article-callout callout-carry">
  <div class="callout-header"><span class="callout-icon">🔥</span> <span class="callout-title">CARRY (貫穿全場核心概念)</span></div>
  <div class="callout-content">An idea or phrase you keep alive through the module so later moments can lean on it.</div>
</div>

<div class="article-callout callout-save">
  <div class="callout-header"><span class="callout-icon">📦</span> <span class="callout-title">SAVE FOR LATER (後置儲備)</span></div>
  <div class="callout-content">Specific words that are banked for a later module (for example: the shift from “I am sad” to “I am noticing sadness” is saved for Stepping Out).</div>
</div>

<blockquote class="article-quote"><strong>Short on preparation time?</strong> Start with <em>Prepare</em>, then read <em>Hold</em>, <em>redirect</em>, and <em>Bridge</em>. Keep <em>The Room Map</em> open while you facilitate, and mark <em>In Your Back Pocket</em> for quick recovery.</blockquote>

<h3 class="article-heading">The Workbook Is Not the Work</h3>
<p class="article-paragraph">The rhythm of transformative learning is:</p>
<div style="background: #f1f5f9; padding: 14px 18px; border-radius: 8px; font-weight: 600; text-align: center; margin: 16px 0; color: #0f172a;">
  Experience ➔ Notice ➔ Harvest ➔ Meaning ➔ Language ➔ Application
</div>
<p class="article-paragraph">A <strong>harvest</strong> is the gathering after an experience — what people noticed, produced, or concluded, collected from them and made visible to the whole room (a word each in a round, the completion of a one-word sentence, answers on a flipchart) so the group can make meaning of it together.</p>
<p class="article-paragraph">Know the objective beneath the activity. A <em>Values Walk</em> (Walking Your Why) is not merely value selection. <em>Earth · Moon · Jupiter</em> is not merely a fun warm-up. Before you run any significant experience, know what it is designed to create. Then protect it.</p>
<blockquote class="article-quote">“If the theatricals disappeared in five minutes, would you still know what the objective is and what it is trying to create? Then protect it.”</blockquote>
""",

    "PG_P_StartHere_02_IMG_5563.JPG": """
<h3 class="article-heading">Order, Time, and Content</h3>
<p class="article-paragraph">Discovery is key to effective learning. The workbook supports that:</p>
<ul style="margin: 14px 0 20px 24px; line-height: 1.9;">
  <li><strong>choice before room-wide reveal</strong>;</li>
  <li><strong>seeing before naming</strong>;</li>
  <li><strong>private thinking before group influence</strong>;</li>
  <li><strong>silence before debrief</strong>;</li>
  <li><strong>experience before explanation</strong>.</li>
</ul>

<h3 class="article-heading">The Order You Run</h3>
<p class="article-paragraph">The workbook's main modules are sequenced in its logical order: <strong>Hooked</strong> is first, because it names the condition everything else answers.</p>
<p class="article-paragraph"><strong>Run the modules in any order that serves your room.</strong> However, if you are facilitating all the modules, we recommend this order:</p>
<ol style="margin: 14px 0 20px 24px; line-height: 1.9;">
  <li><strong>Opening the Question</strong> (the introduction & container)</li>
  <li><strong>Showing Up</strong> (building compassion & safe ground)</li>
  <li><strong>Hooked</strong> (tuning to hooks once self-compassion is activated)</li>
  <li><strong>Stepping Out</strong> (curiosity & unhooking)</li>
  <li><strong>Walking Your Why</strong> (courage & values)</li>
  <li><strong>Moving On</strong> (values in action)</li>
  <li><strong>Living Into the Question</strong> (the conclusion)</li>
</ol>
<p class="article-paragraph">Diving straight into <em>Hooked</em> without prior safety can hook participants before they have a way to meet what comes up. Start with being seen first, and people then meet the same material feeling supported and resourced. That choice of deferring Hooked until later is an example of <strong>mood-task matching</strong>. The pages don't change; your path through them does.</p>
<p class="article-paragraph">Inside a module, the same freedom holds: choose the experiences the room needs, and treat the module's own order (<em>The Journey</em>) as a natural full route, not a rigid required sequence.</p>

<h3 class="article-heading">The Time Choices</h3>
<p class="article-paragraph">You can use the workbook for workshops of any length. Each module's practitioner pages give you three things to plan with:</p>
<ul style="margin: 14px 0 20px 24px; line-height: 1.9;">
  <li><strong>THE JOURNEY</strong>: the module's beats in order, with the room's emotional arc beneath them.</li>
  <li><strong>THE CLOCK</strong>: which beats move quickly and which need the most room. In words, never rigid minutes.</li>
  <li><strong>THE SHAPE</strong>: what to protect, what to cut first, and what never to compress.</li>
</ul>
<blockquote class="article-quote"><strong>“Do less. Do not do everything faster.”</strong><br>When you have more time, use it for participant sensemaking, spacious transitions, questions, and application — not automatically for more concepts.</blockquote>

<h3 class="article-heading">The Content Choices</h3>
<p class="article-paragraph">Emotional Agility is a foundational skillset. Its capacities are crucial to every aspect of how we love, how we live, how we work, how we lead, and how we parent. You can choose the content that meets your needs:</p>
<ul style="margin: 14px 0 20px 24px; line-height: 1.9;">
  <li><strong>Full Workshop</strong>: for those receiving the <em>Emotional Agility Trained</em> badge, coverage would be of all four moves (Showing Up, Stepping Out, Walking Your Why, Moving On), together with Hooked, Opening the Question, and Living Into the Question.</li>
  <li><strong>Culture transformation</strong>: for a given client you might select key beats that focus on hooks, an organizational case study (e.g. <em>Hooked in the Operating Room</em>), the full <em>Walking Your Why</em> module, and then select pieces of <em>Moving On</em> with a focus on bringing values into action in the organization.</li>
  <li><strong>Leadership development</strong>: for a leadership cohort you might pair <em>Showing Up</em> with the full <em>Walking Your Why</em>, then close with <em>Moving On</em> so real change happens: capture emotions met honestly, leadership led from values.</li>
  <li><strong>A team in change</strong>: for a team in the middle of restructuring or new direction, you might focus on hooks, run <em>Stepping Out</em> in full to create space, light <em>Walking Your Why</em>, then choose closing pieces of <em>Moving On</em>.</li>
</ul>
""",

    "PG_P_StartHere_03_IMG_5564.JPG": """
<h3 class="article-heading">Program Types Continued</h3>
<p class="article-paragraph"><strong>Well-being workshop:</strong> for a well-being focus, you might stay with <em>Showing Up</em> in full, giving the room time to be with what is here, then add gentle selections from <em>Stepping Out</em> and <em>Walking Your Why</em>.</p>
<p class="article-paragraph"><strong>A values engagement:</strong> for a values offsite, you might run the full <em>Walking Your Why</em>, then close with <em>Moving On</em> (values in action).</p>
<p class="article-paragraph"><strong>Beyond the workplace:</strong> in a classroom, a clinic, or a congregation, the same choices hold: you might open with <em>Showing Up</em>, then choose the move your setting most needs.</p>

<h3 class="article-heading">Choose the Lens as Well as the Content (ME · WE · US)</h3>
<ul style="margin: 14px 0 20px 24px; line-height: 2;">
  <li><strong>ME</strong> · with yourself — thoughts · emotions · values · attention · choices · patterns of response</li>
  <li><strong>WE</strong> · with one another — relationships · conversations · trust · conflict · collaboration · leadership</li>
  <li><strong>US</strong> · with the team, organization, or culture — norms · culture · structures · expectations · incentives · routines · environment</li>
</ul>
<p class="article-paragraph"><strong>Me · We · Us</strong> is a lens, not a headcount or setting. A one-to-one coaching engagement can work at all three (a client's own hooks, their relationships, the culture they lead in); a room of thirty can be doing <em>ME</em> work (each person on their own well-being or leadership). Choose the lens, or the movement among lenses, that serves the objective.</p>

<h3 class="article-heading">Every Module Distinguishes:</h3>
<ul style="margin: 14px 0 20px 24px; line-height: 1.9;">
  <li><strong>WHAT EVERY ROOM NEEDS</strong>: the psychological conditions, protections, sequence, or meaning that make the experience what it is.</li>
  <li><strong>WHAT YOU CHOOSE FOR THIS ROOM</strong>: staging, examples, grouping, medium, level of focus, or other forms that can change without losing the move. Choose depth to fit the room you actually have (<strong>right-sizing</strong>).</li>
</ul>
<blockquote class="article-quote">And always let the learning travel back into life. True and impactful learning closes the knowledge ➔ action gap. The test is not whether participants completed the activity. It is whether they can recognize and use the move beyond the room.</blockquote>

<h3 class="article-heading">One Build, Two Reveals</h3>
<p class="article-paragraph">One build is primary: <strong>Emotional Agility — the four moves</strong>: <em>Showing Up, Stepping Out, Walking Your Why, Moving On</em>. Participants hear its name at the opening. They live it one move at a time. They see it written on a flipchart. By the last module the room is looking at it, assembled from what they lived.</p>
<p class="article-paragraph">Two delightful reveals serve that build: <strong>From Being Written to Writing</strong>, and <strong>The Capacities</strong>. In the room they arrive slowly, on purpose.</p>
<p class="article-paragraph">The practitioner knows where the work is going. Participants do not need the map before they walk the ground. When people experience something before it is fully named, the language arrives as recognition — <em>“Ah. That is what I have been noticing”</em> — rather than <em>“I know this already; now we are doing an exercise about it.”</em></p>

<h3 class="article-heading">From Being Written to Writing (Authorship)</h3>
<p class="article-paragraph">The first reveal is called <strong>Authorship</strong>. The journey: <strong>reclaiming human agency</strong>.</p>
<p class="article-paragraph">At <em>Hooked</em>, participants live inside the loss of agency: a thought, an emotion, a role, a group, a situation, or a system is experienced as “the truth” and starts deciding the next move for us, and the rigidity that follows. The story is authoring us. <em>Showing Up</em> welcomes emotions as data. <em>Stepping Out</em> creates the gap to see the story as part, not the whole. <em>Walking Your Why</em> puts courage and values behind them. <em>Moving On</em> puts it into action: what a person, a team, or an organization does next.</p>
<p class="article-paragraph">And on the last page of <em>Moving On</em> (Page 113), the arc is explicit:</p>
<blockquote class="article-quote">“A story can author us. With Emotional Agility, we author it.”</blockquote>
<p class="article-paragraph">Do not teach authorship early. Let <em>Hooked</em> establish the experience of being written, the loss of agency, and let the moves build, so the close lands as recognition.</p>

<h3 class="article-heading">The Capacities (四大心理能力)</h3>
<p class="article-paragraph">The second reveal is the <strong>Capacities: Compassion · Curiosity · Courage · Values in Action</strong>:</p>
<ul style="margin: 14px 0 20px 24px; line-height: 2;">
  <li><strong>Showing Up</strong> activates <strong>Compassion (同理心)</strong></li>
  <li><strong>Stepping Out</strong> activates <strong>Curiosity (好奇心)</strong></li>
  <li><strong>Walking Your Why</strong> activates <strong>Courage (勇氣)</strong></li>
  <li><strong>Moving On</strong> activates <strong>Values in Action (行動價值)</strong></li>
</ul>
<p class="article-paragraph">In <em>Opening the Question</em>, surface compassion, curiosity, and courage unexplained on the Intention Wall (three flipcharts, each headed with one capacity word). That is exactly what lets each reveal land as recognition rather than surprise.</p>
""",

    "PG_P_StartHere_04_IMG_5565.JPG": """
<h3 class="article-heading">The Language You'll Carry</h3>
<p class="article-paragraph">Do they understand it? How have they encountered it? Can they use it?</p>
<p class="article-paragraph"><strong>Threading:</strong> <em>Opening the Question</em> is threading at work: the words in the room before the teaching arrives. Spiral risk: material repeating in ways that disengage. Threading supports the natural build and keeps surprise reveals for their right time.</p>

<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>Stance language:</strong> The way you ask a question is part of the teaching. Prefer language that models Emotional Agility. For example: <em>“What did you notice about your feelings?”</em> creates room around experience, whereas <em>“How did this make you feel?”</em> collapses event and response.</li>
  <li><strong>Going meta:</strong> After an experience has landed, you may briefly take participants behind the curtain of the learning design: <em>“Why do you think we wrote privately before talking?”</em> Then connect the design move to their own context, so they can use it in their own work and lives. (Its room form is the “meta” circle, under Rituals.)</li>
  <li><strong>Mood-task matching:</strong> Ask: what does this objective need from the room? Different tasks need different conditions: play, stillness, candor, expansive thinking, careful analysis, connection. Sometimes change the task; sometimes change the conditions, through movement, silence, a break, music, arrangement, or grouping.</li>
  <li><strong>Right-sizing (Plus Two Percent):</strong> Right-size the depth, challenge, and how much you ask people to share to the people and context you actually have. Then ask: what would create just enough stretch for learning? Right-sizing is not making everything easy. Learning does not happen in complete comfort. <em>Plus two percent</em> is not forcing gratuitous vulnerability. It is the smallest real stretch.</li>
  <li><strong>Spaciousness:</strong> Enough room for experience to register and internalize, before the next demand arrives. It may be silence, writing before speaking, a breath before a debrief, walking back from an activity with no talking, or choosing not to answer immediately. Sometimes the most skilled move is to leave a little more space.</li>
</ul>

<h3 class="article-heading">Rituals (課堂深度對話儀式)</h3>
<p class="article-paragraph">A good ritual makes a room easier to enter. It creates continuity, permission, belonging, or a clear way of listening. Create rituals that feel normative, fun, and connecting — never performative or emotionally coercive. A ritual can be as small as:</p>

<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>Circle:</strong> Circle (especially in programs of more than a day) can create a reliable container for listening without immediate fixing. Keep the mechanics simple: one clear question (for example, an arrival stem everyone completes: <em>“I am arriving with...”</em>); a sharing routine (listening only; the next voice simply begins); a passed object if you like (a small object, a stick for example, handed around to transition from one speaker to the next); and a clear completion cue (<em>“I'm complete.”</em>). Then let the structure hold the work. And the rounds form travels: after an exercise, a quick harvest in rounds — one word or phrase each, no commenting — closes any module cleanly and hands to the next.</li>
  <li><strong>“I'm complete”:</strong> The deeper implication is not that everything is resolved. It is that difficult experience can be present without becoming the whole self; that even with the experience, we are our whole and full selves, and we are enough. Use the phrase only when it fits the room; the function matters more than the form.</li>
  <li><strong>The Vault (情感保險箱等級):</strong> A shared language for how deeply to open:
    <div style="margin: 12px 0; padding: 12px 18px; background: #ffffff; border: 1px solid var(--border-light); border-radius: 6px;">
      <strong>Vault 1:</strong> Safe, normative, professional, easy to discuss.<br>
      <strong>Vault 2:</strong> More personal and reflective.<br>
      <strong>Vault 3:</strong> The real, vulnerable, high-stakes conversations.
    </div>
    After that, you can simply invite a <em>“Vault 2 round”</em> and everyone in the room knows exactly what is being asked.</li>
</ul>
""",

    "PG_P_StartHere_05_IMG_5566.JPG": """
<h3 class="article-heading">Rituals Continued</h3>
<p class="article-paragraph"><strong>The “Meta” Circle:</strong> After an experience, stepping into it marks that you are going meta: stepping above what was experienced to describe the design and make it explicit. In our own rooms it is a rug on the floor: you step onto it, and the room can see the mode has changed. Do not explain the device before the experience; the useful move is the visible shift in perspective.</p>
<p class="article-paragraph"><strong>A Shared Playlist:</strong> Built by the room across the workshop: anyone adds a song; it plays in breaks and at transitions.</p>

<h3 class="article-heading">Remote and Hybrid Facilitation (遠距與混合教學實務)</h3>
<p class="article-paragraph">Ask: what does in-person design make possible, and how can we create that here? Remote rooms still need arrival, choice, private thinking, shared presence, movement, protected reveals, silence, and human connection:</p>

<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>Protect independent thinking:</strong> When an experience depends on seeing or choosing for yourself, use private writing before chat, keep the answer off the screen until everyone has chosen, and make the instruction visible before breakout work.</li>
  <li><strong>Let silence stay silent:</strong> Online silence can make a practitioner anxious. Do not automatically fill it. <em>“Take your time. I'll leave a little space here.”</em> Then actually leave it.</li>
  <li><strong>Use the body and the room beyond the screen:</strong> Invite participants to stand, step back, widen their gaze, write by hand, put their hand on their hearts, or move when the experience benefits from a physical shift. The screen is the medium; it does not have to become the whole room.</li>
  <li><strong>Three practices from our own Zoom rooms:</strong>
    <ol style="margin: 10px 0 10px 20px;">
      <li><strong>The Waterfall:</strong> Everyone types an answer to the prompt (e.g. <em>“I am arriving with ___”</em>), and NO ONE presses enter until you say "3, 2, 1, Enter!" It is fun, it brings vibrant energy to the chat, and early answers don't influence the rest.</li>
      <li><strong>Self-sustaining circles:</strong> Breakout rooms run their own circle, with the question and any agreements posted where everyone can see them.</li>
      <li><strong>Broadcast reminders:</strong> The broadcast line carries cues and protections, so groups are never interrupted mid-share (<em>“Two minutes remain. Find a natural place to pause.”</em>).</li>
    </ol>
  </li>
  <li><strong>Hybrid rooms:</strong> Guard against a first-class and a second-class room. Remote participants need equitable access to instructions and materials; response time and discussion; private reflection; hearing and being heard; and usable movement or pairing options. If the hybrid setup cannot support an experience with dignity, choose another way to create the psychological move.</li>
</ul>

<h3 class="article-heading">Materials, Music, and Ambience</h3>
<p class="article-paragraph"><strong>The container is part of the content:</strong> Before a significant experience, ask: what is the objective here, and what kind of room will help people enter it? Room design should support the task, not advertise production value. Think about transitions too: music or movement between segments shapes the group's energy in ways an announcement cannot. Match them to the group and to the task ahead (<strong>mood-task matching</strong>).</p>
<p class="article-paragraph"><strong>Music has a job:</strong> Use music when it helps create or change tone, energy, movement, or attention. Use NO music when a page-turn is protecting a reveal, words need to be heard, participants are speaking, silence is doing the work, or music would sentimentalize the moment. Choose music for the task, not because it worked last time.</p>
<p class="article-paragraph"><strong>Change the room to change attention:</strong> A perceptible physical shift can carry meaning, large or simple: move from tables to open floor; lower screens; take a short silent walk; move outside to watch the sunset; turn toward a window; stand; change chairs. Do not reproduce memorable production details merely because they were memorable. Ask what change in attention the moment needs.</p>
<p class="article-paragraph"><strong>Let materials do psychological work:</strong> A material earns its place when it helps participants see something, carry an idea, or change attention.</p>
""",

    "PG_P_StartHere_06_IMG_5567.JPG": """
<h3 class="article-heading">Guardrails (專業防線與守則)</h3>
<p class="article-paragraph">Work within your professional scope and your client remit.</p>

<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>Your Scope:</strong> Know your qualifications, experience, relationship, remit, and the context.</li>
  <li><strong>Not Therapy:</strong> This work is educational and transformative; it is not therapy, clinical assessment, or clinical treatment. That holds even when you are clinically trained or the setting is a clinic or health context. People enter rooms carrying histories you cannot see. You do not need to know a participant's history in order to protect their agency.</li>
  <li><strong>Teaching Mode:</strong> When you are delivering Emotional Agility in Teaching Mode, every participant receives their own official <em>Participant Workbook</em>, whichever exercises or modules you choose to use. That is true at any program length.</li>
  <li><strong>The Trained Badge:</strong> Any length program is legitimate to run. One designation has a fixed threshold: participants qualify for the <em>Emotional Agility Trained</em> badge only through the <strong>Full Workshop: 24 hours of substantive curriculum, at least 18 of them substantive live engagement led personally by you</strong>, with full coverage of the curriculum: all four moves, together with Hooked, Opening the Question, and Living Into the Question. The threshold is hours and coverage, not a fixed running order.
    <ul style="margin: 8px 0 8px 20px;">
      <li>If a participant asks: <em>“As an Emotional Agility Trained individual, you are not certified to deliver the Emotional Agility workshop.”</em></li>
      <li>If a client asks: <em>“The Trained designation follows the Full Workshop; any shorter engagement delivers the work without it.”</em></li>
    </ul>
    A two-day workshop, a focused leadership session, or a single module can be excellent Emotional Agility work. The badge threshold does not determine whether the work is legitimate; it determines whether the Trained designation applies.</li>
</ul>

<h3 class="article-heading">Consent and Protections (知情同意與自主保護)</h3>
<p class="article-paragraph">Choice is not something added after a powerful exercise. It is part of the design: <strong>treat participants as capable</strong>. Protect agency, appropriate stretch, and the conditions for learning without assuming fragility or requiring disclosure.</p>

<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>Confidentiality:</strong> If the group itself is being asked to hold information confidentially, make that agreement explicit rather than assuming confidentiality exists because the room feels intimate.</li>
  <li><strong>Stories:</strong> When you read a story that touches difficult ground, give one brief sentence of notice just before you read it: <em>“This next story touches on loss.”</em> Give people enough to make an informed choice about how they engage.</li>
  <li><strong>The Invitation:</strong> For more personal exercises, help participants choose material that is real enough to matter and right-sized enough to carry. Where public sharing may follow, say so before participants choose their material.</li>
</ul>

<blockquote class="article-quote"><strong>Three Reusable Invitation Stems:</strong><br><br>
1. <em>“The following exercise is a very useful and powerful exploration that will inform the discussions that follow. You will get the most out of the exercise if you respond honestly and openly. Although we will be sharing some of the insights that arise from it, you can choose which insights you share with the group and which you prefer to remain private. Please only share insights that you are comfortable sharing.”</em><br><br>
2. <em>“Please choose something that is real and deep and true for you, and that you are resourced to be with for the rest of the day.”</em>
</blockquote>
""",

    "PG_P_StartHere_07_IMG_5568.JPG": """
<h3 class="article-heading">Consent and Protections Continued</h3>
<blockquote class="article-quote">“The pass is always welcome.”</blockquote>
<p class="article-paragraph">Most of that protection is built into how you ask. Structure for distance and people can answer honestly: a team you worked in years ago rather than the one sitting around you; a previous organization rather than this one; something already resolved rather than something still live. Participants can always write privately rather than speak, observe, choose a different example, take a less exposed version, or engage how they choose without explaining why. <strong>Ask well, and a pass is rarely needed.</strong></p>

<h3 class="article-heading">Wise Vulnerability (明智的脆弱)</h3>
<p class="article-paragraph"><strong>We are not entitled to people's vulnerability.</strong> Vulnerability can deepen connection, trust, honesty, and learning, but vulnerability is not automatically useful because it is vulnerable.</p>
<p class="article-paragraph">The question to carry is: <strong>What is wise to share, with whom, in this context, in this form, at this moment?</strong></p>

<p class="article-paragraph">Two things move independently:</p>
<ol style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>How raw the material is for the person:</strong> a wound is still live; a scar has healed enough to hold. You might share a wound with a friend of twenty years, and a scar with a group meeting for the first time.</li>
  <li><strong>Contextual trust:</strong> what this room, today, can actually hold. Contextual trust is often lower in a team mid-restructure, or in a room where people sit with their own leaders; it is often higher in a long-term relationship.</li>
</ol>
<p class="article-paragraph">These two move separately. Material that is right-sized in one room may not be right-sized in another. And more room for rawness still asks what the sharing requires of other people, and whether the person can hold what follows. The aim is neither the least vulnerability nor the most. <strong>The aim is wise vulnerability.</strong></p>

<h3 class="article-heading">Before a More Personal Exercise, Ask:</h3>
<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li>What are people being invited to reveal?</li>
  <li>How public is the sharing, and how permanent?</li>
  <li>Who is in the room with them — and what power is present?</li>
  <li>What might it cost them tomorrow?</li>
  <li>What is my professional remit here — and what is beyond it, calling for support or referral?</li>
  <li>What is the simplest route that can do the job?</li>
  <li>And what is the lower-exposure route that still creates the learning?</li>
</ul>
<p class="article-paragraph">There are many wise vulnerability adaptations that can be made: peer pairing rather than pairing across a reporting line; anonymous harvesting; or a higher-distance version of an activity.</p>
<blockquote class="article-quote">The room is not there to do the practitioner's psychological work.</blockquote>

<h3 class="article-heading">Meeting the Moment (現場棘手時刻的應變)</h3>
<p class="article-paragraph">As in any learning experience where people take in new ideas and look at their own lives and work, tough moments can come. Most are ordinary: a silence that runs long, a share that lands heavily. When one comes, <strong>slow down, stay warm</strong>. Follow the design; meet the room; use the lightest move that protects learning and dignity:</p>

<ul style="margin: 16px 0 24px 24px; line-height: 1.9;">
  <li><strong>Read before acting:</strong> Is the room working or stuck? Is the discomfort useful or overwhelming? Is the silence reflective or confused? Is this one participant's issue or the room's? Is the difficulty emotional, conceptual, relational, logistical, or technological? Read the pattern.</li>
  <li><strong>Your own hooks:</strong> You can get hooked while facilitating: urgency, defensiveness, a wish to be liked, fear that the room is bored, anxiety about time, or attachment to the exercise landing a particular way. That is being human, not failing. Notice it, name it to yourself, and ask:
    <div style="margin: 10px 0; padding: 10px 16px; background: #ffffff; border-left: 3px solid var(--accent-blue);">
      1. What am I noticing?<br>
      2. What is this room actually asking for?<br>
      3. What matters here?
    </div>
    Then take the smallest useful next step.</li>
  <li><strong>Hierarchy in the room:</strong> Pair across power with care; for the deeper shares, pair peers with peers. Choose exercises and invitations that support psychological safety, and generally, <strong>let leaders speak last</strong>.</li>
  <li><strong>A share that is hard to hear:</strong> Stay with the person rather than rushing to fix. Receive it:
    <blockquote class="article-quote" style="margin: 8px 0;">“Thank you for trusting us with that.”</blockquote>
    Give the room a quiet moment before anything else happens. Check in privately afterward.</li>
</ul>
""",

    "PG_P_StartHere_08_IMG_5569.JPG": """
<h3 class="article-heading">And Now, The Work.</h3>
<p class="article-paragraph">You have what you need. The room has what it needs. Trust the design, stay spacious, and meet what arises with compassion and curiosity.</p>
<blockquote class="article-quote" style="font-size: 1.25em; text-align: center; padding: 28px 20px;">
  “And now, the work.<br><strong>Dance if you can.</strong>”
</blockquote>
<p class="article-paragraph" style="text-align: center; color: var(--text-muted);">
  EMOTIONAL AGILITY PRACTITIONER GUIDE · START HERE · PRACTITIONER 8
</p>
"""
}

# Structured facilitation teaching synthesis cards for key modules and practitioner pages
SYNTHESIS_NOTES = {
    # Front Matter
    "PG_Page_001_Intro_IMG_5556.JPG": {
        "title": "單元導讀：情緒敏捷的核心意圖 (The Essence of Emotional Agility)",
        "objective": "打破傳統職場「只能維持正向思考」的迷思，為整體課程建立接納與真實的基調。",
        "mindset": "情緒如同多變的天氣；陰影與陽光本就並存。可持續、健康的組織不是消除衝突或不確定性，而是具備穿透與駕馭它們的心理彈性。",
        "prompt": "“Just as the sky is home to all kinds of weather, we have the unique human capacity to experience a full range of emotions.”",
        "watch": "留意是否有學員一開始就試圖為負面情緒辯解或急於壓抑，導師需先穩定場域：『所有情緒都是合法的數據』。",
        "link": "對照學員手冊 Page 1；投影片 Slide 01-03。"
    },
    "PG_Page_006_Sawubona_IMG_5560.JPG": {
        "title": "導師心法：Sawubona 看見的力量 (The Power of Being Seen)",
        "objective": "透過非洲祖魯族傳統問候「Sawubona（我看見你）」，建立全場最深層的心理安全感。",
        "mindset": "「看見」不是打量、不是評估、更不是急著修復對方。看見是全然地承認彼此帶著完整的歷史、脆弱與渴望來到這個房間。",
        "prompt": "“‘Sawubona’ means: I see you, and by seeing you, I bring you into being. Sikhona means: I am here.”",
        "watch": "不要把這個詞當成廉價的破冰口號，應給予數秒鐘的安靜停頓，讓學員真正感受『不帶評判地被看見』的重量。",
        "link": "對照學員手冊 Page 6；破冰與意圖牆建立基石。"
    },
    "PG_Page_007_About_IMG_5561.JPG": {
        "title": "創始人背景：Susan David 博士與學術根基",
        "objective": "向企業主管與專業學員展示情緒敏捷的嚴謹學術基礎與全球權威認可。",
        "mindset": "哈佛醫學院心理學家、TED 超過 1200 萬次觀看、Thinkers50 突破思想獎。這不是心靈雞湯，而是經過實證檢驗的管理心理學架構。",
        "prompt": "“Emotional Agility is recognized by Harvard Business Review as its Management Idea of the Year.”",
        "watch": "強調框架的實用性與科學性，破除學員對『情緒培訓缺乏商業價值』的潛在質疑。",
        "link": "對照學員手冊 Page 7；講師開場背景背書。"
    },
    
    # Start Here Practitioner 1-8
    "PG_P_StartHere_01_IMG_5562.JPG": {
        "title": "導師導引 01：手冊雙冊同頁對齊與四大標記 (How to Use This Guide)",
        "objective": "熟悉導師手冊與學員手冊的 1:1 鏡像對應機制，以及課堂心智地圖（The Room Map）的四大引導標記。",
        "mindset": "『手冊不是工作本身（The Workbook Is Not the Work）』。教學的有機韻律為：體驗 (Experience) → 覺察 (Notice) → 採集 (Harvest) → 意義 (Meaning) → 語言 (Language) → 應用 (Application)。",
        "prompt": "熟悉 DO / SAY（開口引導句）、HOLD（刻意留白）、LISTEN FOR（傾聽訊號）、BRIDGE（轉場橋樑）。",
        "watch": "時間緊迫時，不要加快說話節奏！先讀 Hold 與 Bridge，並常備『In Your Back Pocket』錦囊隨機應變。",
        "link": "導師必讀章節；串聯全冊所有單元的架構基礎。"
    },
    "PG_P_StartHere_02_IMG_5563.JPG": {
        "title": "導師導引 02：單元順序、時間掌控與內容剪裁 (Order, Time, and Content)",
        "objective": "學會依據不同企業情境（領導梯隊、團隊轉型、身心健康），自定義課程模組順序與深淺度。",
        "mindset": "『少做一點，不要急著做快（Do less. Do not do everything faster）』。心態與任務配對（Mood-Task Matching）：若現場能量防衛或低落，可先帶 Showing Up 建立同理與安全感，再回頭切入 Hooked。",
        "prompt": "“If we run all modules, we recommend: Opening → Showing Up → Hooked → Stepping Out → Walking Your Why → Moving On → Living Into the Question.”",
        "watch": "切忌把多出來的時間用來塞更多理論！多出來的時間應留給學員做意義建構（Sensemaking）與生活應用連結。",
        "link": "授證標準：Full Workshop 需滿 24 小時（至少 18 小時現場親授）方具 Emotional Agility Trained 證書資格。"
    },
    "PG_P_StartHere_03_IMG_5564.JPG": {
        "title": "導師導引 03：三維鏡頭 (ME·WE·US) 與雙重驚喜揭示 (Two Reveals)",
        "objective": "掌握課堂三大鏡頭（個人 ME、人際 WE、組織 US），以及「作者身分（Authorship）」與「四大核心能力」的慢速揭示節奏。",
        "mindset": "永遠讓體驗走在理論之前（Experience before naming）。學員必須先在 Hooked 體會『被故事編寫的無力感』，最後在 Moving On 迎來『自己成為故事作者』的深刻頓悟。",
        "prompt": "Showing Up 激活同理心（Compassion）· Stepping Out 激活好奇心（Curiosity）· Walking Your Why 激活勇氣（Courage）· Moving On 激活行動價值（Values in Action）。",
        "watch": "不要在第一天早上就急著把四大能力劇透給學員！將字卡無聲地貼在意圖牆上，讓最後一天的命名成為驚喜頓悟（Recognition）。",
        "link": "連動學員手冊 Page 113 核心金句：『故事可以編寫我們；但有了情緒敏捷，我們編寫故事』。"
    },
    "PG_P_StartHere_04_IMG_5565.JPG": {
        "title": "導師導引 04：引導姿態語言 (Stance) 與對話儀式 (Rituals)",
        "objective": "建立敏捷後設引導語言（Going Meta）與安全圈（Circle）對話機制。",
        "mindset": "注意問句的微小差距：問『你注意到自己對這件事有什麼感受？（What did you notice about your feelings?）』是在情緒與自我間拉開空間；問『這件事讓你感覺如何？』則會讓事件與情緒坍塌在一起。",
        "prompt": "安全圓圈必備三元素：明確的抵達開頭（『我今天帶著……而來』）、只傾聽不急著給建議、說完時宣告『我說完了（I'm complete）』。",
        "watch": "妥善運用情感保險箱等級（The Vault）：等級 1 為日常安全話題，等級 2 涉及個人隱私，等級 3 是深度脆弱對話。導師明確宣告『這輪我們只開到 Vault 2』能大幅降低焦慮。",
        "link": "教室現場管理核心指引；適用各單元的破冰與收尾采風。"
    },
    "PG_P_StartHere_05_IMG_5566.JPG": {
        "title": "導師導引 05：後設地毯、遠距混合會議與音樂氛圍 (Ambiance & Remote)",
        "objective": "掌握「後設圓圈（Meta Circle）」的空間轉移技巧、音樂的心理功能以及遠距線上 Zoom 互動守則。",
        "mindset": "音樂是一項工具：在轉場、身體移動時用音樂帶動能量；在深度書寫、反思揭示時『絕對保持安靜』，切勿濫情。遠距時請護衛獨立思考，善用瀑布流（Waterfall）。",
        "prompt": "“The waterfall: everyone types an answer in chat, but DO NOT press enter until I count down 3, 2, 1, GO!”",
        "watch": "在混合會議（Hybrid）中，嚴格防範遠距學員淪為『二等公民』，確保線上與線下有平等的反思時間與發言權。",
        "link": "遠距 Zoom / Teams 教學必備操作守則。"
    },
    "PG_P_StartHere_06_IMG_5567.JPG": {
        "title": "導師導引 06：安全防線 (Guardrails) 與非心理治療聲明 (Not Therapy)",
        "objective": "明確界定專業引導界限，恪守教育培訓與心理治療之分際，保護學員心理自主權。",
        "mindset": "情緒敏捷是激發人類潛能的教育訓練，絕非臨床診斷或心理治療。學員帶著我們看不見的過往創傷前來，導師的職責是護衛他們的自主權，而非挖掘其隱私。",
        "prompt": "“Please choose something that is real and deep and true for you, and that you are resourced to be with for the rest of the day.”（請選擇真實深刻、但你今天有充足心理能量能陪伴的事件）",
        "watch": "不強迫過度揭露脆弱（No gratuitous vulnerability）。只需推動 +2% 的挑戰延伸，並賦予學員選擇『保留在私密筆記本、不公開分享』的權利。",
        "link": "培訓合規性、學員心理保護與導師倫理守則。"
    },
    "PG_P_StartHere_07_IMG_5568.JPG": {
        "title": "導師導引 07：明智的脆弱 (Wise Vulnerability) 與棘手時刻應對 (Meeting the Moment)",
        "objective": "保護全場心理安全，界定『明智的脆弱』；當現場出現沈重、沉默或導師自身焦慮時的救援處置。",
        "mindset": "我們無權要求學員展現脆弱。區分傷口（Wound，尚未癒合）與傷疤（Scar，已能承受）；在階層與權力存在的場域中，由同儕配對、領導者最後發言。",
        "prompt": "“The pass is always welcome.”（學員永遠有權 Pass）· “Thank you for trusting us with that.”（感謝你信任全場並說出這份真實）。",
        "watch": "導師自己也會被鉤住（時間焦慮、想被喜愛、防衛心），此時問自己三個問題：我注意到什麼？全場真正需要什麼？此時什麼最重要？",
        "link": "導師自我校準、處理全場深層阻抗與棘手時刻的指南。"
    },
    "PG_P_StartHere_08_IMG_5569.JPG": {
        "title": "導師導引 08：啟程準備與與場域共舞 (Dance If You Can)",
        "objective": "在正式開課前調整身心狀態，完全信任學習設計與現場學員的智慧。",
        "mindset": "“And now, the work. Dance if you can.” 導師不是完美的專家，而是場域的守護者與陪伴者。保持靈動，享受教學。",
        "prompt": "“Trust the design, stay spacious, and meet what arises with compassion and curiosity.”",
        "watch": "開課前做 3 次深呼吸，放下對完美結果的執著，將焦點全然放在學員身上。",
        "link": "導師登台前 5 分鐘自我校準心法。"
    },

    # Module 0: Opening
    "PG_P_OpeningTheQuestion_01_IMG_5571.JPG": {
        "title": "單元 00 導師地圖：啟程與開啟提問 (Opening the Question)",
        "objective": "破冰、建立學習契約、啟動意圖牆（Intention Wall），讓學員帶著好奇心入座。",
        "mindset": "不要一開始就講大道理。讓學員彼此看見、在安靜中寫下抵達狀態，體驗被接納的節奏。",
        "prompt": "DO/SAY: “Welcome. You are in the right room. Whatever is present for you today is welcome here.”",
        "watch": "學員剛進教室時可能帶著未接來電或緊急信件的焦慮，給予足夠的轉換留白（Spaciousness）。",
        "link": "對照學員手冊 Page 10-11。"
    },

    # Module 1: Hooked
    "PG_P_Hooked_01_IMG_5580.JPG": {
        "title": "單元 01 導師地圖：被情緒鉤住 (Hooked - The Room Map)",
        "objective": "引導學員識別四大常見的情緒鉤子（猴子心智、壓抑封瓶、反芻深陷、執著正確），看見被鉤住時喪失自主權的代價。",
        "mindset": "不要急著幫學員脫鉤（Hold the fix）！學員必須先親身體驗『被鉤住是多麼普遍的人性現象』，降低自我苛責。",
        "prompt": "DO/SAY: “What is a hook? A hook is when a thought, emotion, or story captures your attention and starts driving your behavior.”",
        "watch": "學員容易陷入分析『是誰害我被鉤住』，導師需溫和拉回：『我們現在關注的是，當鉤子咬住時，你內在發生了什麼？』",
        "link": "對照學員手冊 Page 12-27；四大鉤子核心概念。"
    },

    # Module 2: Showing Up
    "PG_P_ShowingUp_01_IMG_5607.JPG": {
        "title": "單元 02 導師地圖：勇敢現身 (Showing Up - The Room Map)",
        "objective": "以自我同理心（Self-Compassion）直面所有情緒，學習將情緒視為『數據而非指令（Data not Directives）』。",
        "mindset": "現身不是舉白旗投降，而是有勇氣停留在當下。情緒是內在重要價值觀發出的訊號燈，不是必須立即執行的強制命令。",
        "prompt": "DO/SAY: “Emotions are data, not directives. They tell us what we care about, but they don't get to drive the car.”",
        "watch": "學員可能會產生『如果我承認難過，我就會崩潰』的恐懼，導師示範溫和接納的身體姿態，營造穩定的接納容器。",
        "link": "對照學員手冊 Page 28-49；同理心落地實踐。"
    },

    # Module 3: Stepping Out
    "PG_P_SteppingOut_01_retake1_IMG_5640.JPG": {
        "title": "單元 03 導師地圖：抽離跨出 (Stepping Out - The Room Map)",
        "objective": "創造刺激與回應之間的空間（The Gap），透過好奇心（Curiosity）與後設認知拉開觀照距離。",
        "mindset": "練習語言微調：從『我很生氣（I am angry）』轉變為『我注意到我內在有一股生氣的感受（I notice that I am feeling angry）』。看見棋局，而非淪為棋子。",
        "prompt": "DO/SAY: “Between stimulus and response there is a space. In that space is our power to choose our response.”",
        "watch": "抽離不是冷血逃避或解離，而是帶著溫暖的理解退後一步。注意學員是否過度理性化而切斷感受。",
        "link": "對照學員手冊 Page 50-69；解離技術與棋盤隱喻。"
    },

    # Module 4: Walking Your Why
    "PG_P_WalkingYourWhy_01_IMG_5671.JPG": {
        "title": "單元 04 導師地圖：踐行價值 (Walking Your Why - The Room Map)",
        "objective": "釐清個人的北極星核心價值觀（Core Values），在生命風暴中做出符合自我的勇氣抉擇。",
        "mindset": "Values Walk 不只是桌上分類挑選卡片，而是讓學員在身體移動中感受『為了在乎的事物而願意承受必要的不適』。",
        "prompt": "DO/SAY: “Courage is not the absence of fear; courage is fear walking. What is worth moving toward, even if it feels uncomfortable?”",
        "watch": "學員容易挑選『社會期待的漂亮詞彙』（如勤奮、成功），導師需挑戰：『如果沒人看見，這依然是你深層渴望活出的樣貌嗎？』",
        "link": "對照學員手冊 Page 70-93；價值觀實踐步道。"
    },

    # Module 5: Moving On
    "PG_P_MovingOn_01_IMG_5708.JPG": {
        "title": "單元 05 導師地圖：昂首前行 (Moving On - The Room Map)",
        "objective": "啟動『行動中的價值（Values in Action）』，利用 5% 的微調（The 5% Tweak）與習慣疊加（Piggybacking）落實轉變。",
        "mindset": "不要試圖一天之內推翻人生。最可持續的改變往往發生在微小、邊際的 5% 調校之中。在此單元迎來作者身分揭示（Authorship Reveal）。",
        "prompt": "DO/SAY: “A story can author us. With Emotional Agility, we author it. What is your 5% tweak today?”",
        "watch": "學員可能設定過於宏大難以達成的目標（例如每天跑10公里），導師需協助降階為『每天穿上跑鞋站在門口』的微習慣。",
        "link": "對照學員手冊 Page 94-115；微調行動計劃書。"
    },

    # Module 6: Living Into the Question
    "PG_Page_118_LivingIntoTheQuestion_IMG_5736.JPG": {
        "title": "單元 06 導讀：終生修煉 (Living Into the Question)",
        "objective": "收攏全冊學習成果，建立持續修煉的同儕夥伴與支持網絡，正式完成引導結業。",
        "mindset": "結業不是終點，而是帶著這些工具走入真實生活複雜性的開始。擁抱不確定性，在每個當下重新提問、重新調校。",
        "prompt": "DO/SAY: “Live into the questions now. Perhaps then, someday far in the future, you will gradually, without even noticing it, live your way into the answer.”",
        "watch": "創造莊嚴而溫暖的收尾儀式，讓每位學員帶著被看見的滿足感與行動指南離開房間。",
        "link": "對照學員手冊 Page 118-119；證書頒發與承諾卡。"
    }
}

MODULES_META = [
    {
        "id": "00_Front_Matter",
        "name": "Front Matter (封面與引言)",
        "icon": "📑",
        "filter": lambda fn: any(k in fn for k in ["PG_Cover", "PG_Page_001_Intro", "PG_Page_003_Intro", "PG_Page_004_BelongsTo", "PG_Page_005_Contents", "PG_Page_006_Sawubona", "PG_Page_007_About"])
    },
    {
        "id": "01_Start_Here",
        "name": "Start Here (導師導引)",
        "icon": "🚀",
        "filter": lambda fn: "StartHere" in fn
    },
    {
        "id": "02_Opening_the_Question",
        "name": "Opening the Question (啟程與破冰)",
        "icon": "🌱",
        "filter": lambda fn: "OpeningTheQuestion" in fn or "Opening" in fn
    },
    {
        "id": "03_Hooked",
        "name": "Hooked (被情緒鉤住)",
        "icon": "🪝",
        "filter": lambda fn: "Hooked" in fn
    },
    {
        "id": "04_Showing_Up",
        "name": "Showing Up (勇敢現身)",
        "icon": "☀️",
        "filter": lambda fn: "ShowingUp" in fn
    },
    {
        "id": "05_Stepping_Out",
        "name": "Stepping Out (抽離跨出)",
        "icon": "🔭",
        "filter": lambda fn: "SteppingOut" in fn
    },
    {
        "id": "06_Walking_Your_Why",
        "name": "Walking Your Why (踐行價值)",
        "icon": "🧭",
        "filter": lambda fn: "WalkingYourWhy" in fn
    },
    {
        "id": "07_Moving_On",
        "name": "Moving On (昂首前行)",
        "icon": "⛰️",
        "filter": lambda fn: "MovingOn" in fn
    },
    {
        "id": "08_Living_Into_the_Question",
        "name": "Living Into the Question (反思與實踐)",
        "icon": "💫",
        "filter": lambda fn: "LivingIntoTheQuestion" in fn or "Living" in fn
    },
    {
        "id": "09_Appendix",
        "name": "Appendix (附錄整合工具)",
        "icon": "📊",
        "filter": lambda fn: "Appendix" in fn
    }
]

known_headings_lower = [
    'start here', 'how to use this guide', 'two books, one page number',
    'the markers', 'the workbook is not the work', 'the room map',
    'the clock', 'the journey', 'the shape', 'design notes', 'prepare',
    'hold the reveal', 'for the room you have', 'in your back pocket',
    'what this module teaches', 'the order you run', 'the time choices',
    'the content choices', 'guardrails', 'your scope', 'remote and hybrid',
    'the language you\'ll carry', 'order, time, and content', 'rituals',
    'participant resources', 'contents', 'appendix', 'integration map',
    'one build, two reveals', 'from being written to writing', 'the capacities',
    'showing up activates compassion', 'stepping out activates curiosity',
    'walking your why activates courage', 'moving on activates values in action',
    'materials, music, and ambience', 'not therapy', 'teaching mode', 'the trained badge',
    'consent and protections', 'the invitation', 'circle', 'the vault'
]

def format_page_into_curated_html(raw_lines, fn):
    html_output = []
    
    # 1. Inject dedicated Facilitator Teaching Synthesis Card if available
    if fn in SYNTHESIS_NOTES:
        note = SYNTHESIS_NOTES[fn]
        html_output.append(f'''<div class="facilitator-synthesis-card">
  <div class="synthesis-header">
    <span class="synthesis-badge">導師教學梳理</span>
    <h4 class="synthesis-title">{escape_html(note["title"])}</h4>
  </div>
  <div class="synthesis-grid">
    <div class="synthesis-item">
      <div class="synthesis-item-title">🎯 核心教學目標</div>
      <div>{escape_html(note["objective"])}</div>
    </div>
    <div class="synthesis-item">
      <div class="synthesis-item-title">💡 導師心法與節奏</div>
      <div>{escape_html(note["mindset"])}</div>
    </div>
    <div class="synthesis-item">
      <div class="synthesis-item-title">🗣️ 關鍵話術與金句</div>
      <div>{escape_html(note["prompt"])}</div>
    </div>
    <div class="synthesis-item">
      <div class="synthesis-item-title">⚠️ 現場應變要點</div>
      <div>{escape_html(note["watch"])}</div>
    </div>
  </div>
</div>''')

    # 2. Check if a master curated article is provided
    if fn in CURATED_ARTICLES:
        html_output.append(CURATED_ARTICLES[fn].strip())
        return "\n".join(html_output)

    # 3. Otherwise, parse and clean lines
    cleaned_lines = []
    for raw in raw_lines:
        line = clean_and_repair_text(raw)
        if not line:
            continue
        if re.search(r'EMOTIONAL\s*AGILITY.*PRACTITIONER.*GUIDE', line, re.IGNORECASE) or \
           re.search(r'@?\s*2026\s*SUSAN\s*DAVID', line, re.IGNORECASE) or \
           re.search(r'VERSION\s*2\.0', line, re.IGNORECASE):
            continue
        if re.search(r'^[A-Z\s]+[·\-\–•P\s]+PRACTITIONER\s*\d+$', line, re.IGNORECASE):
            continue
        cleaned_lines.append(line)

    if not cleaned_lines:
        html_output.append('<p class="empty-state">*[本頁為原書跨頁圖表或純圖面設計，請點擊右上方「📷 原書對照」查看原版高解析度全貌]*</p>')
        return "\n".join(html_output)

    blocks = []
    curr_paragraph = []

    def flush_paragraph():
        if curr_paragraph:
            full_text = " ".join(curr_paragraph).strip()
            if full_text:
                blocks.append(('p', full_text))
            curr_paragraph.clear()

    for line in cleaned_lines:
        clean_lower = re.sub(r'[^a-z0-9\s]', '', line.lower()).strip()
        
        # Heading
        if clean_lower in known_headings_lower or (len(line) < 40 and not line.endswith(('.', ',', ';', ':', '-')) and line[0].isupper() and len(curr_paragraph) > 0):
            flush_paragraph()
            blocks.append(('h3', line))
            continue
            
        # Facilitator Markers
        marker_match = re.match(r'^(Do\s*/\s*Say|Hold|Listen\s+for|Bridge|Watch\s*&\s*Adjust|Carry|Save\s+for\s+later|In\s+Your\s+Back\s+Pocket)\s*:\s*(.*)', line, re.IGNORECASE)
        if marker_match:
            flush_paragraph()
            m_type = marker_match.group(1).strip()
            m_body = marker_match.group(2).strip()
            blocks.append(('marker', m_type, m_body))
            continue
            
        # Quotes
        if (line.startswith('“') or line.startswith('"')) and (line.endswith('”') or line.endswith('"') or len(line) < 140):
            flush_paragraph()
            blocks.append(('quote', line))
            continue

        curr_paragraph.append(line)

    flush_paragraph()

    for b in blocks:
        b_type = b[0]
        if b_type == 'h3':
            html_output.append(f'<h3 class="article-heading">{escape_html(b[1])}</h3>')
        elif b_type == 'quote':
            html_output.append(f'<blockquote class="article-quote">{escape_html(b[1])}</blockquote>')
        elif b_type == 'marker':
            m_type = b[1].lower()
            tag_name = b[1]
            body_text = escape_html(b[2])
            
            card_class = "callout-generic"
            icon = "📌"
            if "say" in m_type:
                card_class = "callout-dosay"
                icon = "🗣️"
                tag_name = "DO / SAY (導師引導語)"
            elif "hold" in m_type:
                card_class = "callout-hold"
                icon = "🛑"
                tag_name = "HOLD (刻意留白 / 暫不介入)"
            elif "listen" in m_type:
                card_class = "callout-listen"
                icon = "👂"
                tag_name = "LISTEN FOR (傾聽學員訊號)"
            elif "bridge" in m_type:
                card_class = "callout-bridge"
                icon = "🌉"
                tag_name = "BRIDGE (轉場金句)"
            elif "adjust" in m_type or "watch" in m_type:
                card_class = "callout-adjust"
                icon = "⚡"
                tag_name = "WATCH & ADJUST (現場應變微調)"
            elif "carry" in m_type:
                card_class = "callout-carry"
                icon = "🔥"
                tag_name = "CARRY (貫穿全場核心概念)"
            elif "save" in m_type:
                card_class = "callout-save"
                icon = "📦"
                tag_name = "SAVE FOR LATER (後置儲備)"
            elif "back pocket" in m_type or "pocket" in m_type:
                card_class = "callout-adjust"
                icon = "🎒"
                tag_name = "IN YOUR BACK POCKET (應急救援錦囊)"
                
            html_output.append(f'''<div class="article-callout {card_class}">
  <div class="callout-header"><span class="callout-icon">{icon}</span> <span class="callout-title">{tag_name}</span></div>
  <div class="callout-content">{body_text}</div>
</div>''')
        else:
            p_text = escape_html(b[1])
            for kw in [
                "Stance language:", "Going meta:", "Mood-task matching:", "Right-sizing:",
                "Spaciousness:", "Circle:", "The Vault:", "The Room Map:", "The Clock:",
                "The Journey:", "The Shape:", "Two Books, One Page Number:", "Authorship:",
                "The Capacities:", "Not Therapy:", "Teaching Mode:", "The Trained Badge:"
            ]:
                if kw.lower() in p_text.lower():
                    pattern = re.compile(re.escape(kw), re.IGNORECASE)
                    p_text = pattern.sub(f'<strong class="concept-keyword">{kw}</strong>', p_text)
            html_output.append(f'<p class="article-paragraph">{p_text}</p>')

    return "\n".join(html_output)

# Load raw JSON
json_path = "practitioner_guide/practitioner_guide_data.json"
with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

items = sorted(items, key=lambda x: int(re.search(r'IMG_(\d+)', x['file']).group(1)))
print(f"Loaded {len(items)} pages from {json_path}")

enriched_pages = []

for idx, it in enumerate(items):
    fn = it["file"]
    
    curr_mod = MODULES_META[0]
    for m in MODULES_META:
        if m["filter"](fn):
            curr_mod = m
            break
            
    page_type = "學員手冊"
    page_label = fn.replace("PG_", "").replace(".JPG", "")
    
    if "Cover" in fn:
        page_type = "封面"
        page_label = "封面 Cover"
    elif "Divider" in fn:
        page_type = "單元首頁"
        page_label = "單元首頁 Divider"
    elif "_P_" in fn:
        page_type = "導師指引"
        m_p = re.search(r'_P_([A-Za-z]+)_(\d+)', fn)
        if m_p:
            page_label = f"Practitioner {int(m_p.group(2))}"
    elif "_Page_" in fn:
        page_type = "學員手冊"
        m_num = re.search(r'_Page_(\d+)', fn)
        if m_num:
            page_label = f"Page {int(m_num.group(1))}"
    elif "Intro" in fn:
        page_type = "引言"
        
    html_content = format_page_into_curated_html(it.get("raw_lines", []), fn)
    raw_cleaned = clean_and_repair_text(" ".join(it.get("raw_lines", [])))
    
    enriched_pages.append({
        "index": idx,
        "file": fn,
        "moduleId": curr_mod["id"],
        "moduleName": curr_mod["name"],
        "moduleIcon": curr_mod["icon"],
        "pageType": page_type,
        "pageLabel": page_label,
        "photoUrl": f"/practitioner_guide/photos/{fn}",
        "lineCount": it.get("line_count", 0),
        "rawText": raw_cleaned,
        "htmlContent": html_content
    })

out_js = "web_app/js/guide_data.js"
with open(out_js, "w", encoding="utf-8") as f:
    f.write("window.PRACTITIONER_GUIDE_MODULES = " + json.dumps(MODULES_META, default=str, ensure_ascii=False, indent=2) + ";\n\n")
    f.write("window.PRACTITIONER_GUIDE_PAGES = " + json.dumps(enriched_pages, ensure_ascii=False, indent=2) + ";\n")

print(f"Successfully generated master curated reading dataset in {out_js} with {len(enriched_pages)} pages!")
