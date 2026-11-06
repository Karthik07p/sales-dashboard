"""Generate a fully synthetic CRM history (same schema the dashboard engine reads) for the public portfolio dashboard.

Everything here is invented: salespeople, organisations, contacts, deals, notes, meetings and call counts. No real company or person is used.
Run:  python generate_history.py   ->  history.json
"""
import datetime as dt, json, math, random

random.seed(20261106)
D = dt.date
TODAY = D(2026, 11, 6)
START = D(2026, 8, 3)                       # first working day of the data
PULLS = ['2026-10-06', '2026-10-15', '2026-10-25', '2026-11-06']
IST = '+05:30'

# ------------------------------------------------------------------ salespeople (all fictional) and regions
BDES = {  # region label -> owners
    'North Zone': ['Aarav Khanna'],
    'South Zone': ['Kavya Reddy', 'Arvind Subramanian'],
    'West Zone': ['Rohan Deshmukh'],
    'East Zone': ['Ishita Banerjee'],
    'USA': ['Vikram Nair', 'Sneha Kulkarni'],
    'Canada': ['Ananya Iyer'],
    'Australia': ['Siddharth Rao'],
    'Europe': ['Meera Kapoor'],
    'RoW': ['Aditya Verma'],
}
ALL_BDES = [b for v in BDES.values() for b in v]
FX = {'INR': 1, 'USD': 84, 'CAD': 62, 'AUD': 55, 'EUR': 92, 'GBP': 108, 'AED': 23, 'SGD': 63, 'CHF': 98, 'SEK': 8}

# region -> (open deals, [(state/country, currency, [cities])...], account-suffixes)
REGIONS = {
    'North Zone': dict(n=52, loc=[('Delhi NCR', 'INR', ['New Delhi', 'Gurugram', 'Noida']), ('Uttar Pradesh', 'INR', ['Lucknow', 'Kanpur', 'Varanasi']), ('Haryana', 'INR', ['Faridabad', 'Panipat']),
                                  ('Punjab', 'INR', ['Ludhiana', 'Amritsar']), ('Rajasthan', 'INR', ['Jaipur', 'Jodhpur']), ('Uttarakhand', 'INR', ['Dehradun'])],
                       suf=['Industries Ltd', 'Infra Projects Pvt Ltd', 'Logistics Pvt Ltd', 'Energy Ltd', 'Realty Ltd', 'Technologies Pvt Ltd'], indian=1.0, w=[4, 3, 2, 2, 2, 1]),
    'South Zone': dict(n=60, loc=[('Karnataka', 'INR', ['Bengaluru', 'Mysuru', 'Hubballi']), ('Tamil Nadu', 'INR', ['Chennai', 'Coimbatore', 'Madurai']), ('Telangana', 'INR', ['Hyderabad', 'Warangal']),
                                  ('Andhra Pradesh', 'INR', ['Visakhapatnam', 'Vijayawada']), ('Kerala', 'INR', ['Kochi', 'Thiruvananthapuram'])],
                       suf=['Industries Ltd', 'Infra Projects Pvt Ltd', 'Healthcare Pvt Ltd', 'Energy Ltd', 'Technologies Pvt Ltd', 'Logistics Pvt Ltd'], indian=1.0, w=[5, 4, 4, 2, 2]),
    'West Zone': dict(n=56, loc=[('Maharashtra', 'INR', ['Mumbai', 'Pune', 'Nagpur', 'Nashik']), ('Gujarat', 'INR', ['Ahmedabad', 'Surat', 'Vadodara']), ('Madhya Pradesh', 'INR', ['Indore', 'Bhopal']),
                                 ('Goa', 'INR', ['Panaji'])],
                       suf=['Industries Ltd', 'Realty Ltd', 'Logistics Pvt Ltd', 'Energy Ltd', 'Infra Projects Pvt Ltd', 'Pharma Pvt Ltd'], indian=1.0, w=[6, 4, 2, 1]),
    'East Zone': dict(n=28, loc=[('West Bengal', 'INR', ['Kolkata', 'Siliguri']), ('Odisha', 'INR', ['Bhubaneswar', 'Rourkela']), ('Bihar', 'INR', ['Patna']), ('Jharkhand', 'INR', ['Ranchi', 'Jamshedpur']),
                                 ('Assam', 'INR', ['Guwahati'])],
                       suf=['Industries Ltd', 'Mining & Metals Ltd', 'Infra Projects Pvt Ltd', 'Power Ltd', 'Technologies Pvt Ltd'], indian=1.0, w=[4, 3, 1, 2, 1]),
    'USA': dict(n=70, loc=[('California', 'USD', ['San Francisco', 'San Jose', 'Los Angeles']), ('Texas', 'USD', ['Austin', 'Dallas', 'Houston']), ('New York', 'USD', ['New York']),
                           ('Illinois', 'USD', ['Chicago']), ('Massachusetts', 'USD', ['Boston']), ('Washington', 'USD', ['Seattle']), ('Florida', 'USD', ['Miami', 'Tampa']), ('Georgia', 'USD', ['Atlanta'])],
                suf=['Systems Inc.', 'Group Inc.', 'Holdings LLC', 'Corp.', 'Technologies Inc.', 'Partners LLC'], indian=.3, w=[5, 4, 4, 3, 2, 2, 2, 2]),
    'Canada': dict(n=30, loc=[('Ontario', 'CAD', ['Toronto', 'Ottawa', 'Mississauga']), ('British Columbia', 'CAD', ['Vancouver', 'Victoria']), ('Alberta', 'CAD', ['Calgary', 'Edmonton']),
                              ('Quebec', 'CAD', ['Montreal'])],
                   suf=['Corp.', 'Inc.', 'Group Ltd.', 'Holdings Inc.', 'Technologies Ltd.'], indian=.3, w=[6, 3, 3, 2]),
    'Australia': dict(n=34, loc=[('New South Wales', 'AUD', ['Sydney', 'Newcastle']), ('Victoria', 'AUD', ['Melbourne']), ('Queensland', 'AUD', ['Brisbane', 'Gold Coast']), ('Western Australia', 'AUD', ['Perth']),
                                 ('South Australia', 'AUD', ['Adelaide'])],
                      suf=['Pty Ltd', 'Group Pty Ltd', 'Holdings Pty Ltd', 'Australia Pty Ltd'], indian=.25, w=[6, 5, 4, 3, 1]),
    'Europe': dict(n=46, loc=[('United Kingdom', 'GBP', ['London', 'Manchester', 'Birmingham']), ('Germany', 'EUR', ['Berlin', 'Munich', 'Frankfurt']), ('France', 'EUR', ['Paris', 'Lyon']),
                              ('Netherlands', 'EUR', ['Amsterdam', 'Rotterdam']), ('Spain', 'EUR', ['Madrid', 'Barcelona']), ('Sweden', 'SEK', ['Stockholm']), ('Ireland', 'EUR', ['Dublin']),
                              ('Italy', 'EUR', ['Milan']), ('Switzerland', 'CHF', ['Zurich'])],
                   suf=['Ltd', 'GmbH', 'Group', 'Holding', 'Technologies'], indian=.12, w=[6, 6, 3, 3, 2, 2, 2, 2, 1]),
    'RoW': dict(n=30, loc=[('United Arab Emirates', 'AED', ['Dubai', 'Abu Dhabi']), ('Singapore', 'SGD', ['Singapore']), ('Saudi Arabia', 'USD', ['Riyadh', 'Jeddah']), ('South Africa', 'USD', ['Johannesburg', 'Cape Town']),
                             ('Brazil', 'USD', ['Sao Paulo']), ('Japan', 'USD', ['Tokyo', 'Osaka']), ('Kenya', 'USD', ['Nairobi']), ('Malaysia', 'USD', ['Kuala Lumpur'])],
                suf=None, indian=.2, w=[6, 5, 3, 3, 2, 2, 1, 1]),
}
REGIONS['RoW']['suf'] = ['LLC', 'Pte Ltd', 'Group', 'Holdings', 'FZE']
INDUSTRIES = ['Infrastructure & EPC', 'Manufacturing', 'Logistics & Ports', 'Energy & Utilities', 'Real Estate', 'Healthcare', 'Financial Services', 'Telecom', 'Retail & FMCG', 'Education']
PRODUCTS = ['Enterprise Platform Licence', 'Analytics Suite Rollout', 'Workflow Automation', 'Compliance Cloud', 'Data Hub Integration', 'Pilot and Scale-up', 'Multi-site Deployment', 'Managed Services Renewal']

# ------------------------------------------------------------------ name pools (invented combinations)
IN_F = ['Aditi', 'Ananya', 'Bhavna', 'Chitra', 'Deepika', 'Divya', 'Esha', 'Gayatri', 'Harini', 'Isha', 'Jaya', 'Kalpana', 'Lakshmi', 'Madhuri', 'Neha', 'Nisha', 'Pooja', 'Priya', 'Radhika', 'Rashmi', 'Sangeeta', 'Shreya', 'Sunita', 'Tanvi', 'Uma', 'Vandana']
IN_M = ['Abhishek', 'Ajay', 'Amit', 'Anand', 'Arjun', 'Ashok', 'Deepak', 'Gaurav', 'Harish', 'Kiran', 'Manoj', 'Mohit', 'Naveen', 'Nikhil', 'Pranav', 'Rahul', 'Rajesh', 'Rohit', 'Sandeep', 'Sanjay', 'Suresh', 'Tarun', 'Varun', 'Vivek', 'Yogesh']
IN_L = ['Agarwal', 'Bhatt', 'Chandra', 'Desai', 'Gupta', 'Iyer', 'Jain', 'Joshi', 'Kapoor', 'Krishnan', 'Kulkarni', 'Mehta', 'Menon', 'Mishra', 'Nair', 'Patel', 'Pillai', 'Rao', 'Reddy', 'Saxena', 'Shah', 'Sharma', 'Singh', 'Srinivasan', 'Tiwari', 'Verma']
WEST_F = ['Emma', 'Olivia', 'Sophie', 'Hannah', 'Grace', 'Chloe', 'Megan', 'Claire', 'Laura', 'Rachel', 'Amelia', 'Natalie']
WEST_M = ['James', 'Daniel', 'Matthew', 'Ryan', 'Andrew', 'Thomas', 'Nathan', 'Oliver', 'Samuel', 'Ethan', 'Luke', 'Jack']
WEST_L = ['Anderson', 'Bennett', 'Carter', 'Dawson', 'Ellis', 'Fraser', 'Gallagher', 'Hughes', 'Irving', 'Jenkins', 'Keller', 'Lawson', 'Mitchell', 'Nolan', 'Palmer', 'Quinn', 'Reynolds', 'Sutton', 'Turner', 'Walsh']
EU_NAMES = {'Germany': (['Lukas', 'Jonas', 'Felix', 'Anna', 'Lena', 'Katharina'], ['Meyer', 'Schneider', 'Keller', 'Vogel', 'Brandt']), 'France': (['Louis', 'Hugo', 'Camille', 'Chloe', 'Julien'], ['Laurent', 'Moreau', 'Fontaine', 'Girard']),
            'Netherlands': (['Daan', 'Sem', 'Eva', 'Sanne', 'Bram'], ['de Vries', 'van Dijk', 'Bakker', 'Visser']), 'Spain': (['Pablo', 'Diego', 'Lucia', 'Marta', 'Javier'], ['Navarro', 'Ortega', 'Castillo', 'Romero']),
            'Sweden': (['Erik', 'Linnea', 'Oskar', 'Astrid'], ['Lindqvist', 'Berg', 'Holm', 'Nyberg']), 'Italy': (['Marco', 'Giulia', 'Luca', 'Chiara'], ['Rossi', 'Conti', 'Ferrari', 'Galli']),
            'Switzerland': (['Noah', 'Lea', 'Elias', 'Nina'], ['Baumann', 'Keller', 'Frei', 'Zimmermann']), 'Ireland': (['Cian', 'Aoife', 'Ciara', 'Eoin'], ['Murphy', 'Kelly', 'Doyle', 'Byrne'])}
ROW_NAMES = {'United Arab Emirates': (['Omar', 'Yousef', 'Layla', 'Fatima', 'Khalid'], ['Al Mansoori', 'Al Suwaidi', 'Haddad', 'Nasser']), 'Saudi Arabia': (['Faisal', 'Abdullah', 'Noura', 'Sultan'], ['Al Qahtani', 'Al Harbi', 'Zahrani']),
             'Singapore': (['Wei Jie', 'Mei Ling', 'Jun Hao', 'Priscilla', 'Daniel'], ['Tan', 'Lim', 'Ng', 'Chong']), 'South Africa': (['Thabo', 'Pieter', 'Naledi', 'Johan'], ['Naidoo', 'van der Merwe', 'Dlamini', 'Botha']),
             'Brazil': (['Rafael', 'Camila', 'Thiago', 'Beatriz'], ['Silva', 'Oliveira', 'Costa', 'Almeida']), 'Japan': (['Haruto', 'Yui', 'Kenji', 'Aiko'], ['Tanaka', 'Sato', 'Nakamura', 'Kobayashi']),
             'Kenya': (['Brian', 'Wanjiru', 'Kevin', 'Achieng'], ['Mwangi', 'Otieno', 'Kamau', 'Njoroge']), 'Malaysia': (['Hafiz', 'Siti', 'Aiman', 'Nurul'], ['Abdullah', 'Rahman', 'Lee', 'Chong'])}
DESIGNATIONS = ['CTO', 'VP Engineering', 'Head of Procurement', 'Director - IT', 'Programme Manager', 'COO', 'Head of Digital Transformation', 'General Manager - Operations', 'Chief Information Officer',
                'Senior Manager - Strategic Sourcing', 'Head of Projects', 'VP Operations', 'Director of Technology', 'Chief Digital Officer', 'Head of Planning']
SYL1 = ['Zen', 'Alt', 'Kav', 'Noor', 'Triv', 'Orbi', 'Harl', 'Brind', 'Cald', 'Fen', 'Marl', 'Quil', 'Tess', 'Vant', 'Lum', 'Solen', 'Drav', 'Kest', 'Arv', 'Nexa', 'Pria', 'Veda', 'Stra', 'Cor', 'Mer', 'Sab']
SYL2 = ['vara', 'rix', 'ach', 'vi', 'esh', 'tra', 'ow', 'le', 'er', 'wick', 'low', 'lon', 'sera', 'or', 'ora', 'ne', 'ia', 'rel', 'an', 'lis', 'ven', 'dis', 'mark', 'ton', 'ra', 'quil']

_id = [402000000000]
def nid():
    _id[0] += random.randint(3, 997)
    return _id[0]

def iso(d, h=None, m=None):
    h = random.randint(9, 18) if h is None else h
    m = random.randint(0, 59) if m is None else m
    return f'{d.isoformat()}T{h:02d}:{m:02d}:{random.randint(0, 59):02d}{IST}'

def wdays(a, b):
    out, d = [], a
    while d <= b:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(1)
    return out

def next_wd(d):
    while d.weekday() >= 5:
        d += dt.timedelta(1)
    return d

def first_pull_on_or_after(d):
    s = d.isoformat() if isinstance(d, dt.date) else str(d)[:10]
    for p in PULLS:
        if p >= s:
            return p
    return PULLS[-1]

def inr_fmt(n):
    s = str(int(n)); head, tail = s[:-3], s[-3:]
    if not head:
        return tail
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:]); head = head[:-2]
    if head:
        parts.insert(0, head)
    return ','.join(parts + [tail])

# ------------------------------------------------------------------ organisations, contacts
used_names = set()
def org_name(region):
    cfg = REGIONS[region]
    for _ in range(200):
        n = random.choice(SYL1) + random.choice(SYL2)
        if n not in used_names:
            used_names.add(n); break
    return n.capitalize() + ' ' + random.choice(cfg['suf'])

def person(region, country):
    cfg = REGIONS[region]
    if region.endswith('Zone') or random.random() < cfg['indian']:
        f = random.choice(IN_F + IN_M); l = random.choice(IN_L)
    elif region == 'Europe' and country in EU_NAMES:
        fs, ls = EU_NAMES[country]; f, l = random.choice(fs), random.choice(ls)
    elif region == 'RoW' and country in ROW_NAMES:
        fs, ls = ROW_NAMES[country]; f, l = random.choice(fs), random.choice(ls)
    else:
        f = random.choice(WEST_F + WEST_M); l = random.choice(WEST_L)
    return f'{f} {l}'

ACCOUNTS, CONTACTS, DEALS = [], [], []
cid_by_acc = {}

def new_account(region, owner=None):
    cfg = REGIONS[region]
    li = random.choices(range(len(cfg['loc'])), weights=cfg['w'])[0]
    state, cur, cities = cfg['loc'][li]
    a = dict(name=org_name(region), region=region, state=state, cur=cur, city=random.choice(cities), industry=random.choice(INDUSTRIES),
             owner=owner or random.choice(BDES[region]), contacts=[])
    ACCOUNTS.append(a)
    for _ in range(random.choice([2, 2, 3, 3, 4])):
        c = dict(id=nid(), ac=a['name'], nm=person(region, state), ds=random.choice(DESIGNATIONS), o=a['owner'], sg=region, state=state, city=a['city'], ind=a['industry'],
                 cr=START + dt.timedelta(random.randint(-200, 80)), calls=[], acct=a)
        if c['cr'] > TODAY - dt.timedelta(2):
            c['cr'] = TODAY - dt.timedelta(random.randint(3, 30))
        a['contacts'].append(c); CONTACTS.append(c)
    return a

TAG_W = [('Hot', .14), ('Warm', .19), ('Mild', .27), ('Cold/Dormant', .40)]
STAGES_BY_TAG = {'Hot': [('Negotiation', .45), ('Soft Closure', .25), ('Evaluation', .30)], 'Warm': [('Evaluation', .45), ('Positive', .40), ('Negotiation', .15)],
                 'Mild': [('Positive', .50), ('Prospect', .35), ('Evaluation', .15)], 'Cold/Dormant': [('Prospect', .45), ('Dormant', .40), ('Positive', .15)]}

def pick(pairs):
    return random.choices([p[0] for p in pairs], weights=[p[1] for p in pairs])[0]

def make_deal(a, status):
    region = a['region']; cfg = REGIONS[region]
    india = region.endswith('Zone')
    base = random.lognormvariate(math.log(15e5 if india else 30e5), .8 if india else .75)
    value = int(min(max(base, 3e5 if india else 8e5), 2.5e7 if india else 4e7) // 50000 * 50000)
    cur = a['cur']
    partner = (not india) and random.random() < .14 or (india and random.random() < .06)
    cr = D(2026, 2, 1) + dt.timedelta(random.randint(0, (TODAY - D(2026, 2, 1)).days - 3))
    if random.random() < .14:
        cr = TODAY - dt.timedelta(random.randint(1, 27))
    if status != 'Open':
        cr = D(2026, 2, 1) + dt.timedelta(random.randint(0, (TODAY - D(2026, 2, 1)).days - 25))
    tag = pick(TAG_W)
    stage = pick(STAGES_BY_TAG[tag])
    close = outcome = None
    if status != 'Open':
        outcome = status
        close = cr + dt.timedelta(random.randint(10, max(11, min(120, (TODAY - cr).days - 1))))
        if close > TODAY:
            close = TODAY - dt.timedelta(random.randint(1, 3))
        stage = 'Negotiation' if status == 'Won' else random.choice(['Evaluation', 'Positive', 'Prospect'])
        tag = 'Hot' if status == 'Won' else random.choice(['Warm', 'Mild', 'Cold/Dormant'])
    d = dict(id=nid(), acct=a, cr=cr, close=close, outcome=outcome, tag=tag, stage_open=stage, value=value, cur=cur, partner=partner,
             product=random.choice(PRODUCTS), owner=a['owner'], notes=[], acts=[], meets=[])
    d['name'] = f"{a['name']} - {d['product']}"
    cs = random.sample(a['contacts'], k=min(len(a['contacts']), random.choice([1, 2, 2, 3])))
    d['cids'] = [c['id'] for c in cs]
    d['contacts'] = cs
    DEALS.append(d)
    return d

# build open deals per region, then closed ones
for region, cfg in REGIONS.items():
    n_open = cfg['n']
    made = 0
    accts = []
    while made < n_open:
        a = new_account(region)
        accts.append(a)
        k = 2 if random.random() < .3 else 1
        for _ in range(k):
            if made < n_open:
                make_deal(a, 'Open'); made += 1
    for _ in range(int(n_open * .27)):        # closed deals (won / lost) on existing accounts
        make_deal(random.choice(accts), random.choices(['Won', 'Lost'], weights=[.3, .7])[0])
    for _ in range(int(n_open * .22)):         # prospecting-only accounts (contacts approached, no deal yet)
        new_account(region)

# a couple of wins in the current week, so the 'Won' tile is not empty
open_hot = [d for d in DEALS if d['outcome'] is None and d['tag'] == 'Hot' and d['cr'] < D(2026, 10, 20)]
for d, day in zip(random.sample(open_hot, 2), [D(2026, 11, 3), D(2026, 11, 5)]):
    d['outcome'], d['close'], d['stage_open'] = 'Won', day, 'Negotiation'

# scale open pipeline to about 90 Cr
open_sum = sum(d['value'] for d in DEALS if d['outcome'] is None)
k = 90e7 / open_sum
for d in DEALS:
    d['value'] = int(max(d['value'] * k, 3e5) // 50000 * 50000)
    if d['cur'] == 'INR':
        d['amt'] = d['value']; d['vt'] = f"INR {inr_fmt(d['value'])}"
    else:
        amt = int(round(d['value'] / FX[d['cur']], -3)) or 1000
        d['amt'] = amt; d['vt'] = f"{d['cur']} {amt:,}"; d['value'] = amt * FX[d['cur']]

# ------------------------------------------------------------------ events
NOTE_T = {
 'Hot': ["Call with {c} ({ds}): commercials agreed in principle, legal is reviewing the MSA. Targeting sign-off by {d}.",
         "Shared revised proposal v{n} covering {seats} users on a 3-year term. {c} will take it to the steering committee.",
         "Procurement asked for the security questionnaire and compliance report; both sent today. Decision expected next week.",
         "Pricing negotiation: customer asked for {disc}% off on a multi-year commit. Escalated to the regional head for approval.",
         "Sent the order form to {c}; waiting for the signed copy and a start date.",
         "{c} confirmed budget is approved for this quarter. Waiting on the purchase order."],
 'Warm': ["Demo completed for {c}'s team; strong feedback on reporting. Awaiting budget confirmation for next quarter.",
          "{c} asked for a reference call with a similar customer. Arranged for Thursday.",
          "Stakeholder mapping done: {c} is the champion, finance sign-off needed from the CFO office.",
          "Technical deep-dive with their IT team; integration with the existing ERP looks feasible.",
          "Sent the pricing sheet and a 90-day pilot outline. {c} to revert after the internal review."],
 'Mild': ["Intro call with {c}. Interested but no immediate requirement; revisit after their annual planning cycle.",
          "Sent product deck and a case study. {c} will circulate it internally.",
          "Follow-up email sent; no response yet. Will try again on a different day.",
          "{c} wants a short demo once the current vendor contract nears renewal."],
 'Cold/Dormant': ["No response after three attempts; moving to a nurture sequence.",
                  "{c} said the project is on hold until next financial year.",
                  "Contact has changed roles; looking for the new owner of this initiative.",
                  "Left a voicemail and sent a mail. Parking until Q1."],
}
ACT_KINDS = [('Email sent', ['Proposal draft shared', 'Case study sent', 'Meeting invite sent', 'Pricing sheet shared', 'Follow-up on last call']),
             ('Email replied', ['Asked for revised commercials', 'Confirmed meeting slot', 'Requested security documents', 'Shared feedback from the team']),
             ('Outgoing Call', ['Connected, 12 min', 'Connected, 7 min', 'Left voicemail']),
             ('Task Completed', ['Send revised quote', 'Share implementation timeline', 'Update CRM with decision-maker details', 'Prepare demo environment']),
             ('Followup Created', ['Call back after budget review', 'Check status of procurement', 'Schedule executive briefing'])]
M_TITLES = ['Product demo', 'Discovery call', 'Pricing discussion', 'Executive briefing', 'Technical deep-dive', 'Contract review', 'Pilot kickoff', 'Follow-up meeting']
M_DESC = ['Walkthrough of the platform for the project team', 'Requirements and success criteria', 'Commercial terms and licence scope', 'Steering committee update', 'Integration and security questions', 'Redlines on the draft agreement', 'Agree pilot scope and dates', 'Next steps after the demo']

rate = {'Hot': .075, 'Warm': .045, 'Mild': .019, 'Cold/Dormant': .005}
meet_rate = {'Hot': .5, 'Warm': .3, 'Mild': .13, 'Cold/Dormant': .03}
owner_cur_week_meet = 0

def poisson(l):
    L, k, p = math.exp(-l), 0, 1.0
    while True:
        p *= random.random()
        if p <= L:
            return k
        k += 1

NOTES, ACTS, MEETS = [], [], []
for d in DEALS:
    end = d['close'] or TODAY
    days = wdays(max(d['cr'], START), end)
    if not days:
        continue
    p = rate[d['tag']]
    for day in days:
        if random.random() > p:
            continue
        c = random.choice(d['contacts'])
        r = random.random()
        if r < .45:
            t = random.choice(NOTE_T[d['tag'] if d['tag'] in NOTE_T else 'Mild']).format(c=c['nm'], ds=c['ds'], d=(day + dt.timedelta(random.randint(5, 20))).strftime('%d %b'), n=random.randint(2, 4),
                                                                                       seats=random.choice([50, 120, 250, 400, 800]), disc=random.choice([5, 8, 10, 12]))
            NOTES.append(dict(date=iso(day), deal_id=d['id'], id=nid(), owner=d['owner'], seen=first_pull_on_or_after(day), text=t)); d['notes'].append(day)
        else:
            kind, texts = random.choice(ACT_KINDS)
            ACTS.append(dict(date=iso(day), deal_id=d['id'], id=f"k{nid():x}_ACT", kind=kind, owner=d['owner'], seen=first_pull_on_or_after(day), text=random.choice(texts))); d['acts'].append(day)
    # stage change event(s)
    if days and random.random() < .5:
        sd = random.choice(days)
        ACTS.append(dict(date=iso(sd), deal_id=d['id'], id=f"k{nid():x}_STAGE_CHANGE", kind='Stage change', owner='', seen=first_pull_on_or_after(sd), text='to ' + d['stage_open'])); d['sc'] = sd
    if d['outcome']:
        ACTS.append(dict(date=iso(d['close']), deal_id=d['id'], id=f"k{nid():x}_STAGE_CHANGE", kind='Stage change', owner='', seen=first_pull_on_or_after(d['close']),
                         text='to ' + ('Signed' if d['outcome'] == 'Won' and d['partner'] else 'Closed (Won)' if d['outcome'] == 'Won' else 'Lost'))); d['sc'] = d['close']
    # meetings
    for _ in range(poisson(meet_rate[d['tag']] * (1.4 if d['outcome'] == 'Won' else 1))):
        b = random.choice(days)
        w = next_wd(b + dt.timedelta(random.randint(1, 9)))
        if w > D(2026, 11, 13) or (d['close'] and w > d['close']):
            continue
        india = d['acct']['region'].endswith('Zone')
        virtual = random.random() > (.45 if india else .85)
        title = random.choice(M_TITLES); i = M_TITLES.index(title)
        loc = 'Virtual' if virtual else f"In person - {d['acct']['city']}"
        MEETS.append(dict(booked=iso(b), deal_id=d['id'], desc=M_DESC[i], id=nid(), location=loc, owner=d['owner'], seen=first_pull_on_or_after(b),
                          text=f"{title} on {w.strftime('%d %b')}, {loc}", title=title, when=iso(w, random.choice([10, 11, 14, 15, 16]), random.choice([0, 30]))))
        d['meets'].append((w, title))
    # explicit meeting-minutes notes now and then (counted as 'held from notes')
    if random.random() < .03 and days:
        md = random.choice(days)
        NOTES.append(dict(date=iso(md), deal_id=d['id'], id=nid(), owner=d['owner'], seen=first_pull_on_or_after(md),
                          text=f"Minutes of meeting with {random.choice(d['contacts'])['nm']}: agreed scope for the next phase and a follow-up demo for the wider team.")); d['notes'].append(md)

# ------------------------------------------------------------------ contact call history -> snapshots (last interaction per pull)
CS_OUT = [('Answered', .26), ('Meeting Set', .06), ('Interested but no immediate requirement', .07), ('Not Interested', .07), ('Existing Solution', .04), ('Not the right person', .04),
          ('No Answer', .24), ('Voice Mail', .08), ('Wrong Number', .02), ('Call Back Later', .12)]
BK = {'Answered': 'Contacted (no clear outcome)', 'Meeting Set': 'Positive', 'Interested but no immediate requirement': 'Positive', 'Not Interested': 'Negative', 'Existing Solution': 'Negative',
      'Not the right person': 'Contacted (no clear outcome)', 'No Answer': 'Not able to contact', 'Voice Mail': 'Not able to contact', 'Wrong Number': 'Not able to contact', 'Call Back Later': 'Contacted (no clear outcome)'}
RN = {'Meeting Set': ['Meeting booked for next week; sending invite.', 'Agreed to a demo with the wider team.'],
      'Interested but no immediate requirement': ['Interested; asked to reconnect next quarter.', 'Positive but no live project right now.'],
      'Not Interested': ['Not interested at the moment.', 'Already committed to another vendor.'], 'Existing Solution': ['Uses an in-house tool; not looking to change.'],
      'Answered': ['Short call; asked to email details.', 'Spoke briefly, will review the deck.'], 'Not the right person': ['Redirected to the IT head.'],
      'No Answer': ['Not reachable; tried twice.'], 'Voice Mail': ['Left a voicemail.'], 'Wrong Number': ['Number no longer valid.'], 'Call Back Later': ['Asked to call back after the board meeting.']}
deal_tag = {}
for d in DEALS:
    for c in d['contacts']:
        if d['outcome'] is None:
            deal_tag[c['id']] = max(deal_tag.get(c['id'], 'Cold/Dormant'), d['tag'], key=lambda t: ['Cold/Dormant', 'Mild', 'Warm', 'Hot'].index(t))

call_rate = {'Hot': .09, 'Warm': .06, 'Mild': .035, 'Cold/Dormant': .02, None: .03}
for c in CONTACTS:
    p = call_rate[deal_tag.get(c['id'])]
    for day in wdays(max(START, c['cr']), TODAY):
        if random.random() < p * (1.25 if day > D(2026, 10, 25) else 1):
            cs = pick(CS_OUT)
            c['calls'].append((day, cs, random.choice(RN[cs])))
            if random.random() < .1:
                ACTS.append(dict(contact_id=c['id'], date=iso(day), id=f"c{c['id']}|Email sent|{day.isoformat()}", kind='Email sent', owner=c['o'], seen=first_pull_on_or_after(day), text='Follow-up and product overview'))
            if random.random() < .03:
                ACTS.append(dict(contact_id=c['id'], date=iso(day + dt.timedelta(1)), id=f"c{c['id']}|Email replied|{day.isoformat()}", kind='Email replied', owner=c['o'],
                                 seen=first_pull_on_or_after(day + dt.timedelta(1)), text='Thanks, please share pricing details'))

# ------------------------------------------------------------------ snapshots
def pipelines():
    return [{'name': 'Enterprise Sales', 'stages': [{'ft': 'Open', 'name': 'Prospect', 'pos': 1}, {'ft': 'Open', 'name': 'Positive', 'pos': 2}, {'ft': 'Open', 'name': 'Evaluation', 'pos': 3},
                                                    {'ft': 'Open', 'name': 'Negotiation', 'pos': 4}, {'ft': 'Open', 'name': 'Soft Closure', 'pos': 5}, {'ft': 'Open', 'name': 'Dormant', 'pos': 6},
                                                    {'ft': 'Closed Won', 'name': 'Closed (Won)', 'pos': 7}, {'ft': 'Closed Lost', 'name': 'Lost', 'pos': 8}]},
            {'name': 'Partner Channel', 'stages': [{'ft': 'Open', 'name': 'Prospect', 'pos': 1}, {'ft': 'Open', 'name': 'Positive', 'pos': 2}, {'ft': 'Open', 'name': 'Evaluation', 'pos': 3},
                                                  {'ft': 'Open', 'name': 'Negotiation', 'pos': 4}, {'ft': 'Open', 'name': 'Soft Closure', 'pos': 5}, {'ft': 'Open', 'name': 'Dormant', 'pos': 6},
                                                  {'ft': 'Closed Won', 'name': 'Signed', 'pos': 7}, {'ft': 'Closed Lost', 'name': 'Lost', 'pos': 8}]}]

def dealrec(d, p):
    pd = D.fromisoformat(p)
    closed = d['close'] is not None and d['close'] <= pd
    status = (d['outcome'] if closed else 'Open')
    stage = d['stage_open']
    if closed:
        stage = ('Signed' if d['partner'] else 'Closed (Won)') if d['outcome'] == 'Won' else 'Lost'
    tag = 'Closed' if closed else d['tag']
    meets = sorted([m for m in d['meets'] if True], key=lambda m: m[0])
    upcoming = [(w, t) for w, t in meets if w > pd]
    notes_to = [n for n in NOTES if False]
    last_n = None
    dd = [x for x in d['notes'] + d['acts'] if x <= pd]
    lcd = max(dd).isoformat() if dd else d['cr'].isoformat()
    tk = []
    if not closed and random.random() < .55:
        tk = [[iso(pd + dt.timedelta(random.randint(-4, 14)), 12, 0), random.choice(['Send revised proposal', 'Follow up on budget approval', 'Schedule demo for stakeholders', 'Chase procurement for PO', 'Share reference customer contacts'])]]
    a = d['acct']
    return {'account': a['name'], 'amt': float(d['amt']), 'ap': [[iso(w, 11, 0), t] for w, t in meets if w <= D(2026, 11, 13)], 'aw': '', 'bd': '', 'cbk': [], 'cids': d['cids'], 'city': a['city'],
            'closed': d['close'].isoformat() if closed else '', 'cr': d['cr'].isoformat(), 'crby': d['owner'], 'currency': d['cur'], 'dcs': '; '.join(f"{c['nm']} ({c['ds']})" for c in d['contacts']),
            'det': 1, 'di': 'Indirect' if d['partner'] else 'Direct', 'division': a['region'], 'fo': False, 'ia': '', 'ic': False, 'id': d['id'], 'lcd': lcd, 'name': d['name'], 'owner': d['owner'],
            'pipeline': 'Partner Channel' if d['partner'] else 'Enterprise Sales', 'pt': 'NA', 'rn': '', 'stage': stage, 'status': status,
            'su': iso(d['close'], 15, 0) if closed else iso(d.get('sc', d['cr']), 11, 0), 'tag': tag, 'tk': tk, 'tv': 0.0, 'value': float(d['value']), 'vt': d['vt'], 'zone': [], 'stt': a['state'], 'ind': a['industry']}

latest_note = {}
for n in NOTES:
    latest_note.setdefault(n['deal_id'], []).append(n)

def contactrec(c, p):
    pd = D.fromisoformat(p)
    calls = [x for x in c['calls'] if x[0] <= pd]
    cs = li = rn = ''; bk = 'Status not reviewed'; ls = 'New'
    if calls:
        day, cs, rn = calls[-1]; li = day.isoformat(); bk = BK[cs]
        ls = {'Positive': 'Qualified', 'Negative': 'Unqualified'}.get(bk, 'Contacted')
    return {'ac': c['ac'], 'bk': bk, 'city': c['city'], 'cr': c['cr'].isoformat(), 'cs': cs, 'ds': c['ds'], 'id': c['id'], 'li': li, 'ls': ls, 'nm': c['nm'], 'o': c['o'], 'rn': rn, 'sg': c['sg'],
            'state': c['state'], 'ind': c['ind']}

deal_snaps, contact_snaps = [], []
for p in PULLS:
    pd = D.fromisoformat(p)
    ds = [dealrec(d, p) for d in DEALS if d['cr'] <= pd]
    for r in ds:                                              # remark = text of the latest note up to the pull
        ns = [n for n in latest_note.get(r['id'], []) if n['date'][:10] <= p]
        if ns:
            r['rn'] = sorted(ns, key=lambda n: n['date'])[-1]['text']
    deal_snaps.append({'as_of': p, 'deals': ds, 'pipelines': pipelines(), 'source': 'pull'})
    contact_snaps.append({'as_of': p, 'contacts': [contactrec(c, p) for c in CONTACTS if c['cr'] <= pd], 'inbound': [], 'static': {}})

# ------------------------------------------------------------------ daily stats
held_by_day = {}
for m in MEETS:
    held_by_day[(m['when'][:10], m['owner'])] = held_by_day.get((m['when'][:10], m['owner']), 0) + 1
daily, day_status = [], {}
for day in wdays(START, TODAY):
    day_status[day.isoformat()] = {'method': 'current', 's': 'stats'}
    dow_f = {0: 1.05, 1: 1.1, 2: 1.0, 3: .98, 4: .8}[day.weekday()]
    for b in ALL_BDES:
        base = 13.5 if b in ('Vikram Nair', 'Kavya Reddy', 'Aarav Khanna', 'Rohan Deshmukh') else 11.5
        calls = max(6, int(random.gauss(base * dow_f, 3.6)))
        conn = sum(1 for _ in range(calls) if random.random() < random.choice([.24, .27, .3]))
        daily.append({'calls': calls, 'connected': conn, 'date': day.isoformat(), 'meetings': held_by_day.get((day.isoformat(), b), 0), 'method': 'current', 'owner': b, 'src': 'stats'})

# ------------------------------------------------------------------ deal_changes (won / lost events)
changes = [{'date': d['close'].isoformat(), 'deal_id': d['id'], 'field': 'status', 'to': d['outcome']} for d in DEALS if d['outcome']]

users = {str(402000100000 + i * 37): n for i, n in enumerate(ALL_BDES)}
windows_def = [('2026-09-28', '2026-10-06', '28 Sep-6 Oct'), ('2026-10-05', '2026-10-15', '5-15 Oct'), ('2026-10-16', '2026-10-25', '16-25 Oct'), ('2026-10-26', '2026-11-06', '26 Oct-6 Nov')]
hist = {
    'schema': 3,
    'activities': sorted(ACTS, key=lambda a: a['date']),
    'bde_aliases': {n: [n.lower()] for n in ALL_BDES},
    'contact_snapshots': contact_snaps,
    'daily_pulls': {}, 'daily_stats': daily, 'day_seg': {}, 'day_status': day_status,
    'deal_changes': changes, 'deal_snapshots': deal_snaps, 'last_run': {},
    'meeting_overrides': {}, 'meetings': sorted(MEETS, key=lambda m: m['booked']),
    'north': {'ids': [], 'accounts': [], 'states': {}},
    'notes': sorted(NOTES, key=lambda n: n['date']),
    'owner_canon': {n: n for n in ALL_BDES},
    'pulls': {p: {'file': f'pull_{p}.json', 'window': [w[0], w[1]]} for p, w in zip(PULLS, windows_def)},
    'users_by_id': users, 'weekly_reports': [],
    'windows': [{'end': w[1], 'id': f'{w[0]}_{w[1]}', 'kind': 'review', 'label': w[2], 'notes': [], 'pull': p, 'start': w[0]} for p, w in zip(PULLS, windows_def)],
}
blob = json.dumps(hist, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
open('history.json', 'w', encoding='utf-8').write(blob)

last = deal_snaps[-1]['deals']
op = [d for d in last if d['status'] == 'Open']
print('deals', len(last), 'open', len(op), 'open value Cr', round(sum(d['value'] for d in op) / 1e7, 2),
      'hot', sum(d['tag'] == 'Hot' for d in op), 'warm', sum(d['tag'] == 'Warm' for d in op))
print('contacts', len(contact_snaps[-1]['contacts']), 'notes', len(NOTES), 'acts', len(ACTS), 'meetings', len(MEETS), 'size MB', round(len(blob) / 1048576, 2))
wk = [r for r in daily if '2026-11-02' <= r['date'] <= '2026-11-06']
print('week calls', sum(r['calls'] for r in wk), 'connected', sum(r['connected'] for r in wk))
for r in REGIONS:
    print(r, sum(1 for d in op if d['division'] == r), round(sum(d['value'] for d in op if d['division'] == r) / 1e7, 1), 'Cr')
