import requests
import time
import json
import os
import secrets
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import threading
import random
import re
import html
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = int(os.environ.get("OWNER_ID", "6286208795"))
BOT_USERNAME = "YOUR_BOT_USERNAME"
DB_FILE = os.environ.get("DB_FILE", "bot_data.json")

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Firebase Setup
# ==========================================
firebase_credentials_json = r"""
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "YOUR_CLIENT_EMAIL",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "YOUR_CLIENT_X509_CERT_URL",
  "universe_domain": "googleapis.com"
}
"""

try:
    firebase_credentials_json = os.environ.get("FIREBASE_CREDENTIALS", firebase_credentials_json)
    cred_dict = json.loads(firebase_credentials_json, strict=False)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase Connected! (Full Sync Enabled)")
except Exception as e:
    print(f"❌ Firebase Error: {e}")
    db = None

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/your_otp_group",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/FastOTP_Nishat",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "zenex_keys": [],
    "hadi_keys": [],
    "hadi_auto": False,
    "hadi_ranges": {},
    "hadi_manual_ranges": {},
    "hadi_api_on": True,
    "reseller_keys": {},
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "zenex_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "7": {"char": "🇰🇿", "iso": "KZ", "name": "Kazakhstan", "id": "5913724621433082323"},
        "20": {"char": "🇪🇬", "iso": "EG", "name": "Egypt", "id": "5913694831539916769"},
        "27": {"char": "🇿🇦", "iso": "ZA", "name": "South Africa", "id": "5911203119148044594"},
        "30": {"char": "🇬🇷", "iso": "GR", "name": "Greece", "id": "5911210399117611448"},
        "31": {"char": "🇳🇱", "iso": "NL", "name": "Netherlands", "id": "5913367645226275100"},
        "32": {"char": "🇧🇪", "iso": "BE", "name": "Belgium", "id": "5913529642802745141"},
        "33": {"char": "🇫🇷", "iso": "FR", "name": "France", "id": "5913605586414473124"},
        "34": {"char": "🇪🇸", "iso": "ES", "name": "Spain", "id": "5911193287967904547"},
        "36": {"char": "🇭🇺", "iso": "HU", "name": "Hungary", "id": "5913767635530551104"},
        "39": {"char": "🇮🇹", "iso": "IT", "name": "Italy", "id": "5913688444923547525"},
        "40": {"char": "🇷🇴", "iso": "RO", "name": "Romania", "id": "5913460373570195273"},
        "41": {"char": "🇨🇭", "iso": "CH", "name": "Switzerland", "id": "5913271227505448072"},
        "43": {"char": "🇦🇹", "iso": "AT", "name": "Austria", "id": "5911338831524664592"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"},
        "45": {"char": "🇩🇰", "iso": "DK", "name": "Denmark", "id": "5911206009661034712"},
        "46": {"char": "🇸🇪", "iso": "SE", "name": "Sweden", "id": "5911156510162949403"},
        "47": {"char": "🇳🇴", "iso": "NO", "name": "Norway", "id": "5913617397574537046"},
        "48": {"char": "🇵🇱", "iso": "PL", "name": "Poland", "id": "5913550391789752571"},
        "49": {"char": "🇩🇪", "iso": "DE", "name": "Germany", "id": "5911096835887337583"},
        "51": {"char": "🇵🇪", "iso": "PE", "name": "Peru", "id": "5911207993935925780"},
        "52": {"char": "🇲🇽", "iso": "MX", "name": "Mexico", "id": "5913687302462246518"},
        "53": {"char": "🇨🇺", "iso": "CU", "name": "Cuba", "id": "5431551436502611633"},
        "54": {"char": "🇦🇷", "iso": "AR", "name": "Argentina", "id": "5913573356979884082"},
        "55": {"char": "🇧🇷", "iso": "BR", "name": "Brazil", "id": "5911148568768418614"},
        "56": {"char": "🇨🇱", "iso": "CL", "name": "Chile", "id": "5911470957603592832"},
        "57": {"char": "🇨🇴", "iso": "CO", "name": "Colombia", "id": "5913773060074246009"},
        "58": {"char": "🇻🇪", "iso": "VE", "name": "Venezuela", "id": "5434009132753499322"},
        "60": {"char": "🇲🇾", "iso": "MY", "name": "Malaysia", "id": "5913654360063087453"},
        "61": {"char": "🇦🇺", "iso": "AU", "name": "Australia", "id": "5913632326880858455"},
        "62": {"char": "🇮🇩", "iso": "ID", "name": "Indonesia", "id": "5913479361620611038"},
        "63": {"char": "🇵🇭", "iso": "PH", "name": "Philippines", "id": "5911268638874145162"},
        "64": {"char": "🇳🇿", "iso": "NZ", "name": "New Zealand", "id": "5913640044937089340"},
        "65": {"char": "🇸🇬", "iso": "SG", "name": "Singapore", "id": "5911531460808051849"},
        "66": {"char": "🇹🇭", "iso": "TH", "name": "Thailand", "id": "5913617968805187987"},
        "79": {"char": "🇷🇺", "iso": "RU", "name": "Russia", "id": "5913274246867456342"},
        "81": {"char": "🇯🇵", "iso": "JP", "name": "Japan", "id": "5913293711659241040"},
        "82": {"char": "🇰🇷", "iso": "KR", "name": "South Korea", "id": "5913371673905598425"},
        "84": {"char": "🇻🇳", "iso": "VN", "name": "Vietnam", "id": "5913428887164949581"},
        "86": {"char": "🇨🇳", "iso": "CN", "name": "China", "id": "5913779335021466780"},
        "90": {"char": "🇹🇷", "iso": "TR", "name": "Turkey", "id": "5910995113881901195"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "93": {"char": "🇦🇫", "iso": "AF", "name": "Afghanistan", "id": "5913492040364068694"},
        "94": {"char": "🇱🇰", "iso": "LK", "name": "Sri Lanka", "id": "5911293163137406640"},
        "95": {"char": "🇲🇲", "iso": "MM", "name": "Myanmar", "id": "5433666360003540231"},
        "98": {"char": "🇮🇷", "iso": "IR", "name": "Iran", "id": "5911308891307643032"},
        "211": {"char": "🇸🇸", "iso": "SS", "name": "South Sudan", "id": "5911406262511211744"},
        "212": {"char": "🇲🇦", "iso": "MA", "name": "Morocco", "id": "5911482111633658301"},
        "213": {"char": "🇩🇿", "iso": "DZ", "name": "Algeria", "id": "5913782968563800236"},
        "216": {"char": "🇹🇳", "iso": "TN", "name": "Tunisia", "id": "5911332947419468671"},
        "218": {"char": "🇱🇾", "iso": "LY", "name": "Libya", "id": "5911236989260140996"},
        "220": {"char": "🇬🇲", "iso": "GM", "name": "Gambia", "id": "5913657267755945883"},
        "221": {"char": "🇸🇳", "iso": "SN", "name": "Senegal", "id": "5910995302860461643"},
        "222": {"char": "🇲🇷", "iso": "MR", "name": "Mauritania", "id": "5433859405898594234"},
        "223": {"char": "🇲🇱", "iso": "ML", "name": "Mali", "id": "5911305266355245916"},
        "224": {"char": "🇬🇳", "iso": "GN", "name": "Guinea", "id": "5913471858312744319"},
        "225": {"char": "🇨🇮", "iso": "CI", "name": "Côte d'Ivoire (Ivory Coast)", "id": "5222233374948602940"},
        "226": {"char": "🇧🇫", "iso": "BF", "name": "Burkina Faso", "id": "5913407764515786948"},
        "227": {"char": "🇳🇪", "iso": "NE", "name": "Niger", "id": "5911270086278124251"},
        "228": {"char": "🇹🇬", "iso": "TG", "name": "Togo", "id": "5913423260757790970"},
        "229": {"char": "🇧🇯", "iso": "BJ", "name": "Benin", "id": "5913735869952430547"},
        "230": {"char": "🇲🇺", "iso": "MU", "name": "Mauritius", "id": "5913291113204027321"},
        "231": {"char": "🇱🇷", "iso": "LR", "name": "Liberia", "id": "5913324167272337727"},
        "232": {"char": "🇸🇱", "iso": "SL", "name": "Sierra Leone", "id": "5911210450657218661"},
        "233": {"char": "🇬🇭", "iso": "GH", "name": "Ghana", "id": "5913391155877252952"},
        "234": {"char": "🇳🇬", "iso": "NG", "name": "Nigeria", "id": "5911143844304393105"},
        "235": {"char": "🇹🇩", "iso": "TD", "name": "Chad", "id": "5913299849167507310"},
        "236": {"char": "🇨🇫", "iso": "CF", "name": "Central African Republic", "id": "5913443245240619222"},
        "237": {"char": "🇨🇲", "iso": "CM", "name": "Cameroon", "id": "5911172109484167745"},
        "238": {"char": "🇨🇻", "iso": "CV", "name": "Cape Verde", "id": "5913571501554012193"},
        "239": {"char": "🇸🇹", "iso": "ST", "name": "Sao Tome and Principe", "id": "5913574331937462345"},
        "240": {"char": "🇬🇶", "iso": "GQ", "name": "Equatorial Guinea", "id": "5911306279967529251"},
        "241": {"char": "🇬🇦", "iso": "GA", "name": "Gabon", "id": "5911037896051137264"},
        "242": {"char": "🇨🇬", "iso": "CG", "name": "Congo", "id": "5911338788574990168"},
        "243": {"char": "🇨🇩", "iso": "CD", "name": "Congo, The Democratic Republic of the", "id": "5913770362834783827"},
        "244": {"char": "🇦🇴", "iso": "AO", "name": "Angola", "id": "5913753316109586411"},
        "245": {"char": "🇬🇼", "iso": "GW", "name": "Bissau", "id": "5911398694778836149"},
        "248": {"char": "🇸🇨", "iso": "SC", "name": "Seychelles", "id": "5911185183364616913"},
        "249": {"char": "🇸🇩", "iso": "SD", "name": "Sudan", "id": "5911387497799094470"},
        "250": {"char": "🇷🇼", "iso": "RW", "name": "Rwanda", "id": "5911455229433352234"},
        "251": {"char": "🇪🇹", "iso": "ET", "name": "Ethiopia", "id": "5911078333168227043"},
        "252": {"char": "🇸🇴", "iso": "SO", "name": "Somalia", "id": "5911397852965244436"},
        "253": {"char": "🇩🇯", "iso": "DJ", "name": "Djibouti", "id": "5911407709915190157"},
        "254": {"char": "🇰🇪", "iso": "KE", "name": "Kenya", "id": "5911154710571651231"},
        "255": {"char": "🇹🇿", "iso": "TZ", "name": "Tanzania", "id": "5911418949844603556"},
        "256": {"char": "🇺🇬", "iso": "UG", "name": "Uganda", "id": "5913488939397681980"},
        "257": {"char": "🇧🇮", "iso": "BI", "name": "Burundi", "id": "5913766441529642752"},
        "258": {"char": "🇲🇿", "iso": "MZ", "name": "Mozambique", "id": "5911333419865871464"},
        "260": {"char": "🇿🇲", "iso": "ZM", "name": "Zambia", "id": "5913564754160389778"},
        "261": {"char": "🇲🇬", "iso": "MG", "name": "Madagascar", "id": "5913766918271012920"},
        "262": {"char": "🇾🇹", "iso": "YT", "name": "Mayotte", "id": "5780471598922337683"},
        "263": {"char": "🇿🇼", "iso": "ZW", "name": "Zimbabwe", "id": "5911092502265336396"},
        "264": {"char": "🇳🇦", "iso": "NA", "name": "Namibia", "id": "5911108535378252443"},
        "265": {"char": "🇲🇼", "iso": "MW", "name": "Malawi", "id": "5433968339154122439"},
        "266": {"char": "🇱🇸", "iso": "LS", "name": "Lesotho", "id": "5911059881988723711"},
        "267": {"char": "🇧🇼", "iso": "BW", "name": "Botswana", "id": "5911513782722499475"},
        "268": {"char": "🇸🇿", "iso": "SZ", "name": "Eswatini (Swaziland)", "id": "5913374525763883286"},
        "269": {"char": "🇰🇲", "iso": "KM", "name": "Comoros", "id": "5911338582416560604"},
        "290": {"char": "🇸🇭", "iso": "SH", "name": "Saint Helena", "id": "5780471598922337683"},
        "291": {"char": "🇪🇷", "iso": "ER", "name": "Eritrea", "id": "5433723401464198287"},
        "297": {"char": "🇦🇼", "iso": "AW", "name": "Aruba", "id": "5780471598922337683"},
        "298": {"char": "🇫🇴", "iso": "FO", "name": "Faroe Islands", "id": "5296469342039327674"},
        "299": {"char": "🇬🇱", "iso": "GL", "name": "Greenland", "id": "5292014752283774878"},
        "350": {"char": "🇬🇮", "iso": "GI", "name": "Gibraltar", "id": "5780471598922337683"},
        "351": {"char": "🇵🇹", "iso": "PT", "name": "Portugal", "id": "5911023653939581472"},
        "352": {"char": "🇱🇺", "iso": "LU", "name": "Luxembourg", "id": "5913390842344640293"},
        "353": {"char": "🇮🇪", "iso": "IE", "name": "Ireland", "id": "5913440715504881532"},
        "354": {"char": "🇮🇸", "iso": "IS", "name": "Iceland", "id": "5911047899029967246"},
        "355": {"char": "🇦🇱", "iso": "AL", "name": "Albania", "id": "5911357458797826163"},
        "356": {"char": "🇲🇹", "iso": "MT", "name": "Malta", "id": "5911023714069123567"},
        "357": {"char": "🇨🇾", "iso": "CY", "name": "Cyprus", "id": "5911023550860366409"},
        "358": {"char": "🇫🇮", "iso": "FI", "name": "Finland", "id": "5911041344909873378"},
        "359": {"char": "🇧🇬", "iso": "BG", "name": "Bulgaria", "id": "5294329219965272288"},
        "370": {"char": "🇱🇹", "iso": "LT", "name": "Lithuania", "id": "5911172315642597775"},
        "371": {"char": "🇱🇻", "iso": "LV", "name": "Latvia", "id": "5913738489882480243"},
        "372": {"char": "🇪🇪", "iso": "EE", "name": "Estonia", "id": "5910986042910969906"},
        "373": {"char": "🇲🇩", "iso": "MD", "name": "Moldova, Republic of", "id": "5913456847402045950"},
        "374": {"char": "🇦🇲", "iso": "AM", "name": "Armenia", "id": "5913272455866093666"},
        "375": {"char": "🇧🇾", "iso": "BY", "name": "Belarus", "id": "5911011185649521599"},
        "376": {"char": "🇦🇩", "iso": "AD", "name": "Andorra", "id": "5911314702398396902"},
        "377": {"char": "🇲🇨", "iso": "MC", "name": "Monaco", "id": "5911245347266500057"},
        "378": {"char": "🇸🇲", "iso": "SM", "name": "San Marino", "id": "5913587968458625465"},
        "379": {"char": "🇻🇦", "iso": "VA", "name": "Holy See (Vatican City State)", "id": "5911211932420938860"},
        "380": {"char": "🇺🇦", "iso": "UA", "name": "Ukraine", "id": "5911406692007941050"},
        "381": {"char": "🇷🇸", "iso": "RS", "name": "Serbia", "id": "5913592598433369871"},
        "382": {"char": "🇲🇪", "iso": "ME", "name": "Montenegro", "id": "5913239436157522151"},
        "383": {"char": "🇽🇰", "iso": "XK", "name": "Kosovo", "id": "5911433681582429010"},
        "385": {"char": "🇭🇷", "iso": "HR", "name": "Croatia", "id": "5913692684056269311"},
        "386": {"char": "🇸🇮", "iso": "SI", "name": "Slovenia", "id": "5913431983836368644"},
        "387": {"char": "🇧🇦", "iso": "BA", "name": "Bosnia and Herzegovina", "id": "5913700002680541032"},
        "389": {"char": "🇲🇰", "iso": "MK", "name": "Republic of North Macedonia", "id": "5913394029210374721"},
        "420": {"char": "🇨🇿", "iso": "CZ", "name": "Czechia", "id": "5911198691036764307"},
        "421": {"char": "🇸🇰", "iso": "SK", "name": "Slovakia", "id": "5913751666842145020"},
        "423": {"char": "🇱🇮", "iso": "LI", "name": "Liechtenstein", "id": "5911166650580734660"},
        "500": {"char": "🇫🇰", "iso": "FK", "name": "Falkland Islands", "id": "5780471598922337683"},
        "501": {"char": "🇧🇿", "iso": "BZ", "name": "Belize", "id": "5913355005137522807"},
        "502": {"char": "🇬🇹", "iso": "GT", "name": "Guatemala", "id": "5913324858762072330"},
        "503": {"char": "🇸🇻", "iso": "SV", "name": "El Salvador", "id": "5913238624408703010"},
        "504": {"char": "🇭🇳", "iso": "HN", "name": "Honduras", "id": "5911406889576436289"},
        "505": {"char": "🇳🇮", "iso": "NI", "name": "Nicaragua", "id": "5334807849418003620"},
        "506": {"char": "🇨🇷", "iso": "CR", "name": "Costa Rica", "id": "5911261745451635030"},
        "507": {"char": "🇵🇦", "iso": "PA", "name": "Panama", "id": "5913428968769327174"},
        "508": {"char": "🇵🇲", "iso": "PM", "name": "Saint Pierre and Miquelon", "id": "5780471598922337683"},
        "509": {"char": "🇭🇹", "iso": "HT", "name": "Haiti", "id": "5913459789454643194"},
        "590": {"char": "🇬🇵", "iso": "GP", "name": "Guadeloupe", "id": "5780471598922337683"},
        "591": {"char": "🇧🇴", "iso": "BO", "name": "Bolivia", "id": "5913638795101606133"},
        "592": {"char": "🇬🇾", "iso": "GY", "name": "Guyana", "id": "5913579412883771480"},
        "593": {"char": "🇪🇨", "iso": "EC", "name": "Ecuador", "id": "5911273865849347408"},
        "594": {"char": "🇬🇫", "iso": "GF", "name": "French Guiana", "id": "5780471598922337683"},
        "595": {"char": "🇵🇾", "iso": "PY", "name": "Paraguay", "id": "5911014265141072316"},
        "596": {"char": "🇲🇶", "iso": "MQ", "name": "Martinique", "id": "5911378005921370347"},
        "597": {"char": "🇸🇷", "iso": "SR", "name": "Suriname", "id": "5913275539652611719"},
        "598": {"char": "🇺🇾", "iso": "UY", "name": "Uruguay", "id": "5913623088406204470"},
        "599": {"char": "🇨🇼", "iso": "CW", "name": "Curacao", "id": "5780471598922337683"},
        "670": {"char": "🇹🇱", "iso": "TL", "name": "Timor-Leste", "id": "5911141915864076479"},
        "672": {"char": "🇳🇫", "iso": "NF", "name": "Norfolk Island", "id": "5780471598922337683"},
        "673": {"char": "🇧🇳", "iso": "BN", "name": "Brunei", "id": "5911336409163109113"},
        "674": {"char": "🇳🇷", "iso": "NR", "name": "Nauru", "id": "5434131139889478358"},
        "675": {"char": "🇵🇬", "iso": "PG", "name": "Papua", "id": "5911107251183030903"},
        "676": {"char": "🇹🇴", "iso": "TO", "name": "Tonga", "id": "5433640100573491806"},
        "677": {"char": "🇸🇧", "iso": "SB", "name": "Solomon Islands", "id": "5911482712929080608"},
        "678": {"char": "🇻🇺", "iso": "VU", "name": "Vanuatu", "id": "5913511535220625585"},
        "679": {"char": "🇫🇯", "iso": "FJ", "name": "Fiji", "id": "5911393832875856716"},
        "680": {"char": "🇵🇼", "iso": "PW", "name": "Palau", "id": "5911283903187915549"},
        "681": {"char": "🇼🇫", "iso": "WF", "name": "Wallis and Futuna", "id": "5780471598922337683"},
        "682": {"char": "🇨🇰", "iso": "CK", "name": "Cook Islands", "id": "5780471598922337683"},
        "683": {"char": "🇳🇺", "iso": "NU", "name": "Niue", "id": "5780471598922337683"},
        "685": {"char": "🇼🇸", "iso": "WS", "name": "Samoa", "id": "5913325971158602854"},
        "686": {"char": "🇰🇮", "iso": "KI", "name": "Kiribati", "id": "5911294443037660118"},
        "687": {"char": "🇳🇨", "iso": "NC", "name": "New Caledonia", "id": "5780471598922337683"},
        "688": {"char": "🇹🇻", "iso": "TV", "name": "Tuvalu", "id": "5433684690923961019"},
        "689": {"char": "🇵🇫", "iso": "PF", "name": "French Polynesia", "id": "5780471598922337683"},
        "690": {"char": "🇹🇰", "iso": "TK", "name": "Tokelau", "id": "5780471598922337683"},
        "691": {"char": "🇫🇲", "iso": "FM", "name": "Micronesia, Federated States of", "id": "5911271104185373336"},
        "692": {"char": "🇲🇭", "iso": "MH", "name": "Marshall Islands", "id": "5913235935759175692"},
        "850": {"char": "🇰🇵", "iso": "KP", "name": "Korea", "id": "5434142701941437163"},
        "852": {"char": "🇭🇰", "iso": "HK", "name": "Hong Kong", "id": "5292166459118606932"},
        "853": {"char": "🇲🇴", "iso": "MO", "name": "Macau", "id": "6323557758096377611"},
        "855": {"char": "🇰🇭", "iso": "KH", "name": "Cambodia", "id": "5913699998385573485"},
        "856": {"char": "🇱🇦", "iso": "LA", "name": "Lao People's Democratic Republic", "id": "5913718526874489279"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "886": {"char": "🇹🇼", "iso": "TW", "name": "Taiwan", "id": "5366187256937726720"},
        "960": {"char": "🇲🇻", "iso": "MV", "name": "Maldives", "id": "5913501399097806832"},
        "961": {"char": "🇱🇧", "iso": "LB", "name": "Lebanon", "id": "5911504273664905447"},
        "962": {"char": "🇯🇴", "iso": "JO", "name": "Jordan", "id": "5913234136167878475"},
        "963": {"char": "🇸🇾", "iso": "SY", "name": "Syria", "id": "5433910876786670092"},
        "964": {"char": "🇮🇶", "iso": "IQ", "name": "Iraq", "id": "5911382442622587735"},
        "965": {"char": "🇰🇼", "iso": "KW", "name": "Kuwait", "id": "5913290705182134003"},
        "966": {"char": "🇸🇦", "iso": "SA", "name": "Saudi Arabia", "id": "4985897134424328239"},
        "967": {"char": "🇾🇪", "iso": "YE", "name": "Yemen", "id": "5913346492512341993"},
        "968": {"char": "🇴🇲", "iso": "OM", "name": "Oman", "id": "5913570801474343473"},
        "970": {"char": "🇵🇸", "iso": "PS", "name": "Palestine", "id": "5913684768431541668"},
        "971": {"char": "🇦🇪", "iso": "AE", "name": "United Arab Emirates", "id": "5913726554168365343"},
        "972": {"char": "🇮🇱", "iso": "IL", "name": "Israel", "id": "5911471936856134692"},
        "973": {"char": "🇧🇭", "iso": "BH", "name": "Bahrain", "id": "5913581663446634403"},
        "974": {"char": "🇶🇦", "iso": "QA", "name": "Qatar", "id": "5911260864983339619"},
        "975": {"char": "🇧🇹", "iso": "BT", "name": "Bhutan", "id": "5913236734623093021"},
        "976": {"char": "🇲🇳", "iso": "MN", "name": "Mongolia", "id": "5911041383564580038"},
        "977": {"char": "🇳🇵", "iso": "NP", "name": "Nepal", "id": "5913496520014958723"},
        "992": {"char": "🇹🇯", "iso": "TJ", "name": "Tajikistan", "id": "5911287639809463107"},
        "993": {"char": "🇹🇲", "iso": "TM", "name": "Turkmenistan", "id": "5913315521503170180"},
        "994": {"char": "🇦🇿", "iso": "AZ", "name": "Azerbaijan", "id": "5911197578640233518"},
        "995": {"char": "🇬🇪", "iso": "GE", "name": "Georgia", "id": "5913434771270144023"},
        "996": {"char": "🇰🇬", "iso": "KG", "name": "Kyrgyzstan", "id": "5911202161370337549"},
        "998": {"char": "🇺🇿", "iso": "UZ", "name": "Uzbekistan", "id": "5911051846104912282"},
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "w_methods", "w_group", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels", "voltx_auto", "stex_auto", "zenex_auto", "zenex_keys", "zenex_services", "zenex_search_countries", "hadi_keys", "hadi_auto", "hadi_manual_ranges", "hadi_api_on", "reseller_keys"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
zenex_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
ZENEX_BASE_URL = "https://api.zenexnetwork.com"
HADI_BASE_URL = "https://mknetworkbd.com/api/v3/public"
hadi_assigned_numbers = {}  # request_id(str) -> {"owner","number","key_idx","time"}
api_otp_inbox = {}  # request_id(str) -> {"otp","number","service","message","time"} — filled for owner == "api:<key>"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}

# 🌟 sAjaxSource (AJAX/DataTable) এবং Fallback HTML Parser Helper Function
def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    
    # সেশন শেষ হয়েছে বা লগইন পেজে রিডাইরেক্ট করেছে কি না তা চেক করা
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    # ৫.১ যদি sAjaxSource AJAX লিংক পাওয়া যায়
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            # 250 এর জায়গায় 10000 করে দেওয়া হলো যাতে সব মেসেজ ফেচ করতে পারে
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=10000&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])
        for row_val in rows:
            if not isinstance(row_val, list):
                continue
                
            if len(row_val) < max(n_idx, m_idx) + 1:
                continue
                
            num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
            msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
            
            clean_num = re.sub(r'\D', '', str(num_val))
            if clean_num and 5 <= len(clean_num) <= 18:
                otp = extract_otp_code(msg_val)
                if otp and len(msg_val) > 4:
                    results.append({"number": clean_num, "message": msg_val, "otp": otp})
                    
    else:
        # ৫.২ ডাইরেক্ট HTML টেবিল থেকে রিড করার ব্যাকআপ লজিক
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    return results, html_text

# Track active number sessions to expire them automatically
user_active_sessions = {}

assigned_number_rates = {}

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, hadi_assigned_numbers, processed_otps, assigned_number_rates
    
    loaded_from_local = False
    
    # ১. প্রথমে Local DB লোড করবে (এটি সবচেয়ে আপডেট থাকে, তাই Key হারাবে না)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                zenex_assigned_numbers = data.get("zenex_assigned_numbers", {})
                hadi_assigned_numbers = data.get("hadi_assigned_numbers", {})
                processed_otps = set(data.get("processed_otps", []))
                assigned_number_rates = data.get("assigned_number_rates", {})
                loaded_from_local = True
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

    # ২. এরপর Firestore থেকে শুধু মিসিং ডেটা লোড করবে (Local ডেটা ওভাররাইট করবে না)
    if db:
        try:
            doc = db.collection('settings').document('bot_config').get()
            if doc.exists:
                fs_data = doc.to_dict()
                for k in FS_KEYS:
                    # যদি Local-এ ডেটা না থাকে (ফাঁকা থাকে), তবেই শুধুমাত্র Firestore থেকে আনবে
                    if k in fs_data and (not loaded_from_local or bot_settings.get(k) in [None, [], ""]):
                        bot_settings[k] = fs_data[k]
                print("✅ Config Synced with Firestore!")
            else:
                fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
                db.collection('settings').document('bot_config').set(fs_data)
                print("✅ Firestore Config Initialized!")
        except Exception as e:
            print(f"❌ Error loading from Firestore: {e}")

def save_local_db():
    local_data = {
        "bot_settings": bot_settings,
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "zenex_assigned_numbers": zenex_assigned_numbers,
        "hadi_assigned_numbers": hadi_assigned_numbers,
        "processed_otps": list(processed_otps),
        "assigned_number_rates": assigned_number_rates
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
    except Exception as e:
        pass

def _sync_fs():
    if not db: return
    fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
    try:
        db.collection('settings').document('bot_config').set(fs_data)
    except: pass

def save_db():
    save_local_db()
    # 🌟 Firestore Save Threading: মেইন বটকে স্লো না করার জন্য ব্যাকগ্রাউন্ডে সেভ হবে
    # daemon=True সরিয়ে দেওয়া হলো যাতে সার্ভার রিস্টার্টের সময়ও ফায়ারবেস সেভ প্রসেস সম্পূর্ণ হয়
    threading.Thread(target=_sync_fs).start()

load_db()

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # 🌟 Keep-Alive Connection (Makes bot 10x faster)

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        # 🌟 Added timeout to prevent hanging!
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# 🌟 Local User List to completely remove Firebase Read Costs!
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and db:
            for doc in db.collection('users').select([]).stream():
                all_known_users.add(doc.id)
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        # 🌟 Non-blocking background save (Prevents lag)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    # 🌟 Dedicated Connection Pool for Broadcast (Fixes Port Exhaustion & Network Lag)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035) # Safe speed (28 msgs/sec) to prevent Telegram Ban
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_info_html(num_or_iso, return_full_name=False):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                name = data.get("name", num_or_iso)
                if return_full_name: return name
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        if return_full_name: return num_or_iso
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = num_or_iso.replace("+", "").replace(" ", "")
            if clean.startswith(code): return data.get("name", num_or_iso)
        return num_or_iso
        
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6: return f"{clean[:3]}DXA{clean[-3:]}"
    elif len(clean) > 2: return f"{clean[:1]}DXA{clean[-1:]}"
    return clean

# ==========================================
# OTP MESSAGE STYLE (Aura Edition)
# ==========================================
DEVELOPER_LINK = "https://t.me/FastOTP_Nishat"

def _otp_country_name(iso_code):
    name = get_flag_info_html(iso_code, return_full_name=True) if iso_code else None
    return name if name and name != iso_code else (iso_code or "Unknown")

def build_otp_text(display_num, iso, service_icon, service_name, lang_name, msg_text):
    safe_msg = html.escape(str(msg_text or "").strip()) or "N/A"
    country_name = html.escape(_otp_country_name(iso))
    ts = datetime.now().strftime("%H:%M:%S")
    body = (
        "『 ⚡ 𝙉𝙚𝙬 𝙊𝙏𝙋 𝘿𝙧𝙤𝙥𝙥𝙚𝙙 ⚡ 』\n\n"
        "┏━━━━━━━━━━━━━━━┓\n"
        f"┃ {get_flag_info_html(display_num)} <b>{country_name}</b>\n"
        f"┃ 📱 <code>{html.escape(str(display_num))}</code>\n"
        f"┃ {service_icon} <b>{html.escape(str(service_name))}</b>\n"
        f"┃ 💬 {html.escape(str(lang_name))} · 🕐 {ts}\n"
        "┗━━━━━━━━━━━━━━━┛\n\n"
        "✦ ── 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 ── ✦\n"
        f"「 {safe_msg} 」"
    )
    return render_body_text(body)

def otp_footer_row():
    row = [{"text": "Developer", "url": DEVELOPER_LINK, "style": "primary"}]
    if BOT_USERNAME and BOT_USERNAME != "YOUR_BOT_USERNAME":
        row.append({"text": "Bot", "url": f"https://t.me/{BOT_USERNAME}", "style": "primary"})
    return row

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat (Added Arabic Keywords)
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსאფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "threads": ["threads", "threads code", "threads verification"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],

    # 🔵 Tech & Mail
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    
    # 💰 Crypto & Trading
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],

    # 💳 Finance & Wallets
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],

    # 🛒 E-commerce & Delivery
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],

    # 🎮 Gaming & Entertainment
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],

    # 🎲 Betting & Casino
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],

    # ❤️ Dating
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

SERVICE_NAME_RE = re.compile(r"^[A-Za-z0-9 ]{2,20}$")

def validate_service_name(raw_text):
    # Cleans + validates an admin-typed service name. Returns (clean_name, error_message).
    cleaned = re.sub(r"\s+", " ", str(raw_text).strip()).upper()
    if not SERVICE_NAME_RE.match(cleaned):
        return None, "❌ <b>Invalid name!</b> Only letters, numbers & spaces (2-20 characters).\nExample: <code>TELEGRAM</code>\n\nSend the name again:"
    return cleaned, None

SERVICE_PANELS = {"stex_services": "StexSMS", "voltx_services": "VoltX", "zenex_services": "ZenexNetwork"}

def scan_invalid_services():
    found = []
    for key, label in SERVICE_PANELS.items():
        for srv in bot_settings.get(key, {}):
            if not SERVICE_NAME_RE.match(str(srv)):
                found.append((label, srv))
    return found

def cleanup_invalid_services():
    removed = scan_invalid_services()
    for key, label in SERVICE_PANELS.items():
        for lbl, srv in list(removed):
            if lbl == label and srv in bot_settings.get(key, {}):
                del bot_settings[key][srv]
    if removed:
        save_db()
    return removed

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s: break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    return detected_service.title(), "📱"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    # ১. Unicode Block দিয়ে নিখুঁত বর্ণমালা শনাক্তকরণ (100% Accurate for scripts)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean

    # ২. OTP Keyword দিয়ে ভাষা শনাক্তকরণ (Latin script languages)
    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    
    # ৩. উপরের কোনোটি না মিললে ডিফল্ট
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for ch in bot_settings["fj_channels"]:
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]: continue
        else: return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    banned = False
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get()
            banned = doc.exists and doc.to_dict().get("banned", False)
        except: pass
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        # হাইফেন (-) থাকলে সেটা রেখে দিবে, কিন্তু স্পেস থাকলে মুছে একসাথে করে দিবে
        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue
                
                # 🌟 Option 1 + Smart HTML Detection: কলামের নাম ও ব্যবহারকারীর দেওয়া সিরিয়াল দিয়ে সঠিক পজিশন বের করা
                final_n_idx = n_idx
                final_m_idx = m_idx
                
                # প্রথম রো (Header) চেক করে কলামের আসল সিরিয়াল মিলিয়ে নেওয়া
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text: final_n_idx = i
                    if m_col_name in c_text: final_m_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    
                    # হেডার রো (যেখানে সব th থাকে) সেগুলো থেকে ডাটা নিবে না
                    if all(c.name == 'th' for c in cols): continue
                    
                    if len(cols) > max(final_n_idx, final_m_idx):
                        # HTML টেবিল থেকে টেক্সট বের করা
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        
                        clean_num = re.sub(r'\D', '', num_text)
                        
                        # নাম্বারটা আসলেই ৫-১৮ ডিজিটের কিনা তা নিশ্চিত করা (যাতে উল্টাপাল্টা টেক্সট না আসে)
                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if otp and len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp})
        except Exception as e:
            pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []
            
            def process_item(item):
                pot_nums_list = []
                pot_msg = None
                values = []
                
                if isinstance(item, dict):
                    # ১. প্রথমে পরিচিত JSON Key (যেমন: num, phone, sms) দিয়ে খোঁজার চেষ্টা
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18:
                                if clean_val not in pot_nums_list: pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break
                    values = list(item.values())
                elif isinstance(item, list):
                    values = item

                # ২. যদি Key দিয়ে না পাওয়া যায়, তবে Smart Blind Scan (সব ভ্যালু চেক করবে)
                for v in values:
                    if isinstance(v, (dict, list)) or v is None: continue
                    v_str = str(v).strip()
                    
                    # Number Detection: 7 থেকে 18 ডিজিট
                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                        # Date/Time/IP এড়ানোর লজিক
                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    
                    # Message Detection: 5 অক্ষরের বেশি এবং শুধু সংখ্যা নয়
                    if len(v_str) > 4 and not v_str.isdigit():
                        if extract_otp_code(v_str):
                            if pot_msg is None or len(v_str) > len(pot_msg):
                                pot_msg = v_str
                                
                # 🌟 ৩. Multiple Numbers Logic (User Priority > Second Number > First Number)
                pot_num = None
                if pot_nums_list:
                    matched_user_num = None
                    for n in pot_nums_list:
                        # চেক করবে ইউজারের অ্যাসাইন করা নাম্বারের তালিকায় এই নাম্বারটি আছে কি না
                        if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                            matched_user_num = n
                            break
                    
                    if matched_user_num:
                        pot_num = matched_user_num
                    elif len(pot_nums_list) >= 2:
                        pot_num = pot_nums_list[1] # ইউজারের কাছে না থাকলে সরাসরি দ্বিতীয় নাম্বারটি নেবে
                    else:
                        pot_num = pot_nums_list[0]
                            
                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg)
                    if otp:
                        temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp})
                        
            def traverse_json(node):
                if isinstance(node, list):
                    if len(node) > 0 and not isinstance(node[0], (dict, list)):
                        # It's a flat list representing one record
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            
            # Remove duplicates
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except: pass
        
    return results

# 🌟 Advanced Automated Background Captcha Solver 🌟
def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        # 1. SOLVE CAPTCHA (Exact bot 3.py logic)
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        # 2. FIND FORM
        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        # 3. SUBMIT
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        # 4. VERIFY (Exact bot 3.py check logic)
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            # এখানে ফেইল হলে অংক কী পেয়েছিল তা দেখা যাবে
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db() # Save login status text to show in settings
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            # 🌟 auto sessions with sAjaxSource and Fallback HTML Parser
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("full_api_url"): 
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url: continue
                        
                        urls_to_try = []
                        if full_url:
                            urls_to_try.append(full_url)
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            
                        parsed_data = []
                        # 🌟 Browser Bypass (403 Forbidden Fix)
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        for try_url in urls_to_try:
                            try:
                                res = requests.get(try_url, headers=headers, timeout=10)
                                parsed_data = parse_panel_response(res.text, p)
                                if parsed_data:
                                    if not full_url and try_url != url and token:
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    break
                            except: continue
                        if not parsed_data: continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]
                        
                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        unique_id = f"{num}_{otp}"
                        
                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()
                                 
                            char, iso = get_flag_and_code(num)
                            app_full_name, prem_app_html = get_service_info_html(p.get("name", "Panel"), msg_text)
                            current_time = time.time()
                            
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })
                            # 🌟 শুধু লোকাল ফাইলে সেভ করবে, Firestore এ অহেতুক Write করবে না!
                            save_local_db()
                                 
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                            display_msg = build_otp_text(masked, iso, prem_app_html, app_full_name, lang_name, msg_text)
                            reward = float(bot_settings.get("otp_reward", 0.0))
                            
                            for fw in bot_settings.get("fw_groups", []):
                                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                                temp_row = []
                                styles = ["danger", "success", "primary"]
                                for i, btn in enumerate(fw.get("buttons", [])):
                                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                    temp_row.append(b_obj)
                                    if len(temp_row) == 2:
                                        kb.append(temp_row)
                                        temp_row = []
                                if temp_row: kb.append(temp_row)
                                if reward > 0: kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                kb.append(otp_footer_row())
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                            
                            owners = []
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            # 🌟 ALGORITHM FIX: সরাসরি Active Sessions থেকে মালিক খোঁজা 
                            # (কারণ Local Stock থেকে নাম্বার Assign হওয়ার সাথে সাথে ডিলিট হয়ে যায়)
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        break
                                        
                            # ব্যাকআপ হিসেবে StexSMS-তে চেক করা 
                            if not owners:
                                for stex_n, n_owner in stex_assigned_numbers.items():
                                    clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                        owners.append(n_owner)
                                        
                            owners = list(set(owners)) 
                            for owner_id in owners:
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                inbox_msg = build_otp_text(display_num, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                
                                # রিওয়ার্ড শুধু ব্যালান্সে যোগ হবে, বাটন/ডেভেলপার-বট শুধু OTP গ্রুপেই দেখাবে
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                if db:
                                    try: 
                                        db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)})
                                        if owner_id in user_cache:
                                            user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                    except: pass
        except Exception as e:
            pass
        time.sleep(5) 

# ==========================================
# Firebase User Management
# ==========================================
# 🌟 Local User Cache: বারবার Firestore থেকে Read করা বন্ধ করবে!
user_cache = {}

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    if not db: return {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0}
    
    doc_ref = db.collection('users').document(str(user_id))
    doc = doc_ref.get()
    if doc.exists: 
        data = doc.to_dict()
        if "total_otps" not in data: data["total_otps"] = 0
        if "banned" not in data: data["banned"] = False
        if "verified" not in data: data["verified"] = False
        user_cache[user_id] = data
        return data
    else:
        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False}
        doc_ref.set(new_user)
        user_cache[user_id] = new_user
        return new_user

def update_balance(user_id, amount):
    if user_id in user_cache:
        user_cache[user_id]["balance"] = user_cache[user_id].get("balance", 0.0) + float(amount)
    if not db: return
    try:
        doc_ref = db.collection('users').document(str(user_id))
        # 🌟 No more .get() before update! Saves 1 Read Cost instantly!
        doc_ref.set({"user_id": user_id, "balance": firestore.Increment(float(amount))}, merge=True)
    except: pass

def add_referral(inviter_id, new_user_id):
    if not db.collection('users').document(str(new_user_id)).get().exists:
        get_user(new_user_id) 
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        db.collection('users').document(str(inviter_id)).update({"total_refers": firestore.Increment(1)})
        if inviter_id in user_cache:
            user_cache[inviter_id]["total_refers"] = user_cache[inviter_id].get("total_refers", 0) + 1
        
        # আপনার দেওয়া নতুন ডিজাইন
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"🔥 <b>You Received {reward} TK</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"}, 
            {"text": "Search Number", "icon_custom_emoji_id": "5463352748751753567", "style": "primary"}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5352877703043258544", "style": "success"}, 
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"}
        ],
        [
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"}, 
            {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger"}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"}
        ]
    ]
    if is_admin(user_id): 
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "Zenex Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_control", "style": "success"},
         {"text": "Hadi Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "hadi_control", "style": "primary"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "Reseller API", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "reseller_control", "style": "success"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"}],
        [{"text": "DXA Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    auto_status = "ON" if bot_settings.get("stex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_stex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def zenex_control_keyboard():
    auto_status = "ON" if bot_settings.get("zenex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Zenex Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_zenex_keys", "style": "danger"}],
        [{"text": "Manage Zenex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_zenex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_zenex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def hadi_control_keyboard():
    auto_status = "ON" if bot_settings.get("hadi_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    api_on = bot_settings.get("hadi_api_on", True)
    api_status = "ON" if api_on else "OFF"
    api_emoji = "5352694861990501856" if api_on else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Hadi Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_hadi_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_hadi_keys", "style": "danger"}],
        [{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_hadi_range", "style": "success"},
         {"text": "View/Del Ranges", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_hadi_ranges", "style": "danger"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_hadi_auto", "style": "primary"},
         {"text": "Sync Now", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "hadi_sync_now", "style": "primary"}],
        [{"text": f"API Number: {api_status}", "icon_custom_emoji_id": api_emoji, "callback_data": "hadi_api_toggle", "style": "primary"},
         {"text": "Debug API", "icon_custom_emoji_id": "5305517382138112561", "callback_data": "hadi_debug", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def hadi_control_text():
    auto_total = sum(len(v) for v in (bot_settings.get("hadi_ranges") or {}).values())
    man_total = sum(len(v) for v in (bot_settings.get("hadi_manual_ranges") or {}).values())
    all_r = hadi_get_all_ranges()
    lines = [
        "💠 <b>Hadi Control Panel</b>\n",
        f"Total API Keys: {len(bot_settings.get('hadi_keys', []))}",
        f"Countries: {len(all_r)} | Auto Ranges: {auto_total} | Manual: {man_total}",
        f"API Number: {'ON' if bot_settings.get('hadi_api_on', True) else 'OFF'}",
    ]
    if hadi_last_sync["time"]:
        t = datetime.fromtimestamp(hadi_last_sync["time"]).strftime("%H:%M:%S")
        lines.append(f"Last Sync: {t} ({hadi_last_sync['count']} ranges)")
        if hadi_last_sync["error"]:
            lines.append(f"Sync Error: {html.escape(hadi_last_sync['error'])}")
    if hadi_last_error["msg"]:
        lines.append(f"Last API Error: {html.escape(hadi_last_error['msg'])}")
    lines.append("\nManage your Hadi (MK Network) API Keys and Ranges below:")
    return render_body_text("\n".join(lines))

def voltx_control_keyboard():
    auto_status = "ON" if bot_settings.get("voltx_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_voltx_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def dxa_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "dxa_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "dxa_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    # ১০ মিনিটের ট্রাফিক নেওয়ার জন্য 3600 (১ ঘণ্টা) এর জায়গায় 600 (১০ মিনিট) করে দেওয়া হলো
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 600]
    
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
        
    txt = "🔥 10 Minute LIVE Traffic\n\n"
    
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last 10 minutes...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            # Service Name and Total count
            txt += f"{prem_app_html} {app_full_name.upper()} {total}\n"
            
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
            c_list = c_list[:7] # আপনি চাইলে লিমিট সরাতে পারেন
            
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                
                # Logic for LOW, MEDIUM, HIGH
                if count < 20:
                    status_text = "LOW"
                    status_emoji = '<tg-emoji emoji-id="5408846744727334338">🔴</tg-emoji>'
                elif count < 30:
                    status_text = "MEDIUM"
                    status_emoji = '<tg-emoji emoji-id="5409220909393290791">🟡</tg-emoji>'
                else:
                    status_text = "HIGH"
                    status_emoji = '<tg-emoji emoji-id="5192812028632274956">🟢</tg-emoji>'
                        
                txt += f"{prem_flag_html} {c_name.upper()} :  {status_text} {status_emoji}\n"
                
            txt += "\n"
        
        now = datetime.now()
        current_time_str = now.strftime("%I:%M %p")
        updated_emoji = '<tg-emoji emoji-id="5336983442125001376">🕒</tg-emoji>'
        txt += f"{updated_emoji} Updated {current_time_str}\n"

        for srv, _, _ in srv_totals: 
            safe_srv = srv[:20] 
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
            
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    
    return txt, {"inline_keyboard": kb}

# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id) # 🌟 Save User locally for Free Broadcasts!

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                if db:
                    doc = db.collection('users').document(str(chat_id)).get()
                    if not doc.exists:
                        get_user(chat_id)
                        db.collection('users').document(str(chat_id)).update({"referred_by": inviter, "ref_paid": False})
                        
    if text.strip() == "/cleanup_services" and is_admin(chat_id):
        removed = cleanup_invalid_services()
        if removed:
            lines = "\n".join(f"• <code>{html.escape(n)}</code> (from {p})" for p, n in removed)
            send_message(chat_id, render_body_text(f"🧹 <b>Removed {len(removed)} invalid service(s):</b>\n{lines}"))
        else:
            send_message(chat_id, render_body_text("✅ No invalid service names found."))
        return

    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা (JSON) আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী? (যেমন: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত? (যেমন: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nবট এখন থেকে নিজেই ব্যাকগ্রাউন্ডে ক্যাপচা সলভ করে লগিন করে নিবে।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_bal = doc.to_dict().get('balance', 0.0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} ৳</b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc_ref = db.collection('users').document(str(target_uid))
                doc = doc_ref.get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_status = doc.to_dict().get("banned", False)
                new_status = not current_status
                doc_ref.update({"banned": new_status})
                
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                data = doc.to_dict()
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        # --- Menu Design Flow ---
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
            msg_text = render_body_text(f"{prem_flag_html} {iso} | {prem_app_html} {masked} | 💬 {lang_name}")
            
            for fw in bot_settings.get("fw_groups", []):
                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                temp_row = []
                styles = ["danger", "success", "primary"]
                for i, btn in enumerate(fw.get("buttons", [])):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row: kb.append(temp_row)
                kb.append(otp_footer_row())
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID পাওয়া গেছে: <code>{custom_emoji_id}</code>\n\n📌 এখন এটি সেভ করার জন্য টাইপ এবং নাম লিখুন।\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} কোনো Premium Emoji পাওয়া যায়নি! দয়া করে Custom Emoji সেন্ড করুন।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji সেভ হয়েছে!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji সেভ হয়েছে!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!\n\nসঠিক ফরম্যাট:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper()
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            country = text.upper()
            temp_data[chat_id]["country"] = country
            user_states[chat_id] = "wait_for_file_rate"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Country set.\n\n💰 Enter the OTP reward rate for this file (e.g. 5.0):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_file_rate" and text:
            try:
                rate = float(text.strip())
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid rate! Please enter a number (e.g. 5.0):"), reply_markup=get_cancel_kb())
                return
                
            country = temp_data[chat_id]["country"]
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)
            
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": temp_data[chat_id]["filename"], 
                "service": service, 
                "country": country, 
                "rate": rate,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
            total_uploaded_stats += len(clean_nums)
            save_db()
            
            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']} "
            
            broadcast_txt = f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n{prem_flag_html} {country} {prem_app_html} {service}\n➖➖➖➖➖➖➖➖\n📤 Total Added: <b>{len(clean_nums)}</b>\n💰 Reward: <b>{rate} TK</b>\n➖➖➖➖➖➖➖➖\nUse /start to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            
            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added to local stock with {rate} TK rate! Starting broadcast..."))
            
            def simple_broadcast(txt):
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                for u_id in list(all_known_users):
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except: pass
                    time.sleep(0.035)
            threading.Thread(target=simple_broadcast, args=(broadcast_txt,)).start()
            
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv, err = validate_service_name(text)
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            if err:
                if m_id: edit_message(chat_id, m_id, render_body_text(err), reply_markup=get_cancel_kb())
                return
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            existed = srv in bot_settings["stex_services"]
            if not existed: bot_settings["stex_services"][srv] = {}
            save_db()
            del user_states[chat_id]
            cb_data = f"nx_srv_{srv}" if existed else "manage_stex_srv"
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": m_id}, "data": cb_data, "id": "internal"})
            return

        elif state == "wait_nx_rename_srv" and text:
            new_name, err = validate_service_name(text)
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            old_srv = temp_data.get(chat_id, {}).get("srv")
            if err:
                if m_id: edit_message(chat_id, m_id, render_body_text(err), reply_markup=get_cancel_kb())
                return
            del user_states[chat_id]
            if old_srv in bot_settings.get("stex_services", {}) and new_name != old_srv:
                if new_name in bot_settings["stex_services"]:
                    send_message(chat_id, render_body_text(f"❌ <b>{new_name}</b> already exists! Rename cancelled."))
                else:
                    bot_settings["stex_services"][new_name] = bot_settings["stex_services"].pop(old_srv)
                    save_db()
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": m_id}, "data": f"nx_srv_{new_name}", "id": "internal"})
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv, err = validate_service_name(text)
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            if err:
                if m_id: edit_message(chat_id, m_id, render_body_text(err), reply_markup=get_cancel_kb())
                return
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            existed = srv in bot_settings["voltx_services"]
            if not existed: bot_settings["voltx_services"][srv] = {}
            save_db()
            del user_states[chat_id]
            cb_data = f"vx_srv_{srv}" if existed else "manage_voltx_srv"
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": m_id}, "data": cb_data, "id": "internal"})
            return

        elif state == "wait_vx_rename_srv" and text:
            new_name, err = validate_service_name(text)
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            old_srv = temp_data.get(chat_id, {}).get("srv")
            if err:
                if m_id: edit_message(chat_id, m_id, render_body_text(err), reply_markup=get_cancel_kb())
                return
            del user_states[chat_id]
            if old_srv in bot_settings.get("voltx_services", {}) and new_name != old_srv:
                if new_name in bot_settings["voltx_services"]:
                    send_message(chat_id, render_body_text(f"❌ <b>{new_name}</b> already exists! Rename cancelled."))
                else:
                    bot_settings["voltx_services"][new_name] = bot_settings["voltx_services"].pop(old_srv)
                    save_db()
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": m_id}, "data": f"vx_srv_{new_name}", "id": "internal"})
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_hadi_key" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            if "hadi_keys" not in bot_settings: bot_settings["hadi_keys"] = []
            bot_settings["hadi_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Hadi API Key Added! Total Keys: {len(bot_settings.get('hadi_keys', []))}"), reply_markup=hadi_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zenex_key" and text:
            bot_settings["zenex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Zenex API Key Added! Total Keys: {len(bot_settings.get('zenex_keys', []))}"), reply_markup=zenex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zsc" and text:
            code = text.strip().replace("+", "")
            if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
            bot_settings["zenex_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "zenex_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_zx_srv_name" and text:
            srv, err = validate_service_name(text)
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            if err:
                if m_id: edit_message(chat_id, m_id, render_body_text(err), reply_markup=get_cancel_kb())
                return
            if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
            existed = srv in bot_settings["zenex_services"]
            if not existed: bot_settings["zenex_services"][srv] = {}
            save_db()
            del user_states[chat_id]
            cb_data = f"zx_srv_{srv}" if existed else "manage_zenex_srv"
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": m_id}, "data": cb_data, "id": "internal"})
            return

        elif state == "wait_zx_rename_srv" and text:
            new_name, err = validate_service_name(text)
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            old_srv = temp_data.get(chat_id, {}).get("srv")
            if err:
                if m_id: edit_message(chat_id, m_id, render_body_text(err), reply_markup=get_cancel_kb())
                return
            del user_states[chat_id]
            if old_srv in bot_settings.get("zenex_services", {}) and new_name != old_srv:
                if new_name in bot_settings["zenex_services"]:
                    send_message(chat_id, render_body_text(f"❌ <b>{new_name}</b> already exists! Rename cancelled."))
                else:
                    bot_settings["zenex_services"][new_name] = bot_settings["zenex_services"].pop(old_srv)
                    save_db()
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": m_id}, "data": f"zx_srv_{new_name}", "id": "internal"})
            return

        elif state == "wait_zx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["zenex_services"][srv]: bot_settings["zenex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["zenex_services"][srv][cnt]:
                bot_settings["zenex_services"][srv][cnt].append(new_range)
                if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                if new_range not in bot_settings["zenex_search_countries"]: bot_settings["zenex_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel এর Login Link দিন:"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_reseller_key_name" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            name = text.strip()[:40]
            new_key = secrets.token_hex(24)
            kid = secrets.token_hex(3)
            bot_settings.setdefault("reseller_keys", {})[new_key] = {
                "name": name, "balance": 0.0, "cost_per_number": 0.0, "active": True,
                "used": 0, "ranges": None, "kid": kid, "created": time.time()
            }
            save_db()
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            txt = (f"✅ <b>New key created for {html.escape(name)}</b>\n\n"
                   f"<code>{new_key}</code>\n\n"
                   "⚠️ Save this now — it won't be shown in full again.")
            kb = {"inline_keyboard": [[{"text": "OK", "callback_data": "reseller_view_keys", "style": "success"}]]}
            if m_id:
                edit_message(chat_id, m_id, render_body_text(txt), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(txt), reply_markup=kb)
            return

        elif state == "wait_reseller_topup" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            kid = temp_data.get(chat_id, {}).get("kid")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            try:
                amt = float(text.strip())
            except ValueError:
                amt = None
            key, info = reseller_find_by_kid(kid) if kid else (None, None)
            if amt is not None and info:
                info["balance"] = round(float(info.get("balance", 0.0)) + amt, 4)
                save_db()
            if m_id and info:
                edit_message(chat_id, m_id, reseller_key_detail_text(key, info), reply_markup=reseller_key_detail_kb(kid, info))
            return

        elif state == "wait_reseller_cost" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            kid = temp_data.get(chat_id, {}).get("kid")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            try:
                cost = max(0.0, float(text.strip()))
            except ValueError:
                cost = None
            key, info = reseller_find_by_kid(kid) if kid else (None, None)
            if cost is not None and info:
                info["cost_per_number"] = cost
                save_db()
            if m_id and info:
                edit_message(chat_id, m_id, reseller_key_detail_text(key, info), reply_markup=reseller_key_detail_kb(kid, info))
            return

        elif state == "wait_reseller_ranges" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            kid = temp_data.get(chat_id, {}).get("kid")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            key, info = reseller_find_by_kid(kid) if kid else (None, None)
            if info:
                if text.strip().lower() == "all":
                    info["ranges"] = None
                else:
                    rngs = [hadi_norm_range(t) for t in re.split(r"[\s,;]+", text.strip())]
                    rngs = [r for r in rngs if r]
                    info["ranges"] = rngs or None
                save_db()
            if m_id and info:
                edit_message(chat_id, m_id, reseller_key_detail_text(key, info), reply_markup=reseller_key_detail_kb(kid, info))
            return

        elif state == "wait_reseller_expiry" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            kid = temp_data.get(chat_id, {}).get("kid")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            key, info = reseller_find_by_kid(kid) if kid else (None, None)
            if info:
                t = text.strip().lower()
                if t == "never":
                    info["expires_at"] = None
                    save_db()
                else:
                    try:
                        days = max(1, int(t))
                        info["expires_at"] = time.time() + days * 86400
                        save_db()
                    except ValueError:
                        pass
            if m_id and info:
                edit_message(chat_id, m_id, reseller_key_detail_text(key, info), reply_markup=reseller_key_detail_kb(kid, info))
            return

        elif state == "wait_for_hadi_range" and text:
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            man = bot_settings.setdefault("hadi_manual_ranges", {})
            added = 0
            for tok in re.split(r"[\s,;]+", text.strip()):
                r = hadi_norm_range(tok)
                if not r: continue
                name = hadi_country_for(re.sub(r"\D", "", r))
                lst = man.setdefault(name, [])
                if r not in lst:
                    lst.append(r)
                    added += 1
            save_db()
            delete_message(chat_id, msg["message_id"])
            m_id = temp_data.get(chat_id, {}).get("msg_id")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            if m_id:
                edit_message(chat_id, m_id, render_body_text(f"✅ Added {added} range(s)!\n\n") + hadi_control_text(), reply_markup=hadi_control_keyboard())
            else:
                send_message(chat_id, hadi_control_text(), reply_markup=hadi_control_keyboard())
            return

        elif state == "wait_for_hadi_api_prefix" and text:
            raw = text.strip().replace("+", "").replace(" ", "").upper()
            m = re.match(r"^(\d{3,12})X*$", raw)
            if not m:
                send_message(chat_id, render_body_text("❌ Send 3 to 12 digits like <code>7697</code> or <code>7697XXX</code>"))
                return
            digits = m.group(1)
            t_msg = temp_data.get(chat_id, {}).get("msg_id")
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
            delete_message(chat_id, msg["message_id"])
            if not bot_settings.get("hadi_keys") or not bot_settings.get("hadi_api_on", True):
                hadi_fail(None, chat_id, t_msg, "❌ API Number is not available right now!")
                return
            wait_txt = render_body_text("⌛ <i>Processing... Finding Number...</i>")
            if t_msg:
                edit_message(chat_id, t_msg, wait_txt)
            else:
                wm = send_message(chat_id, wait_txt)
                t_msg = wm.get("result", {}).get("message_id") if wm else None
            hadi_deliver(None, chat_id, t_msg, hadi_api_candidates(digits, raw), f"hadi_a_{digits}", "hadi_api_menu", "Change Range", shuffle=False)
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            # 🌟 ১. প্রথমে Local থেকে নাম্বার খুঁজবে (যে কোনো দেশের জন্য)
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                # 🌟 ২. যদি Local এ না পায়, তখন চেক করবে Voltx বা StexSMS থেকে আনা যাবে কি না
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                
                # ফিক্স: অ্যাডমিন প্যানেলে দেশ এড না থাকলে অটোমেটিক Block করে দেবে
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                
                # 🌟 প্রথমে Voltx চেক করবে
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    is_voltx_used = True
                                    global total_assigned_stats
                                    total_assigned_stats += 1
                                    break # শুধু api_key লুপ ব্রেক করবে, যাতে পরের নাম্বার আনতে পারে
                            except: continue

                # 🌟 Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    
                    for _ in range(req_count - len(fetched_nums)): 
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    total_assigned_stats += 1
                                    break 
                            except: continue
                        
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            custom_star_html = f'<tg-emoji emoji-id="5305517382138112561">⭐️</tg-emoji>'
            text_numbers = render_body_text(f"{country_emoji_html} {custom_star_html} NEW NUMBER\n")
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            else:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id")) # ইউজারের মেসেজ ডিলিট

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            
            # Save to Firestore for History
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id),
                        "amount": amount,
                        "method": method,
                        "status": "pending",
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                except: pass
                
            if bot_settings["w_group"]:
                admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amount} TK\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
                kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                send_message(bot_settings["w_group"], render_body_text(admin_msg), reply_markup=kb)
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)
        
        # --- PROCESS PENDING REFERRAL ---
        if db:
            doc = db.collection('users').document(str(chat_id)).get()
            if doc.exists:
                u_data = doc.to_dict()
                if u_data.get("referred_by") and not u_data.get("ref_paid"):
                    inviter = u_data["referred_by"]
                    db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                    reward = bot_settings.get("refer_reward", 0.2)
                    update_balance(inviter, reward)
                    db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                    if inviter in user_cache:
                        user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {reward} TK</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs)
        
        if not all_services and not bot_settings.get("hadi_keys"):
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            
            if bot_settings.get("hadi_keys"):
                kb.append([{"text": "Hadi Number", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "hadi_menu", "style": "success"}])
                if bot_settings.get("hadi_api_on", True):
                    kb.append([{"text": "API Number", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "hadi_api_menu", "style": "success"}])
            
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        # API সিস্টেম থেকে রিমুভ করা যাতে ইনবক্সে আর মেসেজ না যায়
        for num in nums:
            if num in stex_assigned_numbers: del stex_assigned_numbers[num]
            if num in voltx_assigned_numbers: del voltx_assigned_numbers[num]
            if num in zenex_assigned_numbers: del zenex_assigned_numbers[num]
            for _rid in [r for r, v in hadi_assigned_numbers.items() if str(v.get("number")) == str(num)]:
                del hadi_assigned_numbers[_rid]
        save_db()
        
        # আগের মেসেজ ইডিট করে Expired বাটন বসানো
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    # 🌟 Button Loading Fix: বাটন চাপার সাথে সাথেই টেলিগ্রামকে Response দিয়ে দেওয়া, যাতে বাটন আটকে না থাকে!
    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_") and not data.startswith("hadi_c_") and not data.startswith("hadi_a_") and data != "hadi_menu":
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            if db:
                doc = db.collection('users').document(str(chat_id)).get()
                if doc.exists:
                    u_data = doc.to_dict()
                    if u_data.get("referred_by") and not u_data.get("ref_paid"):
                        inviter = u_data["referred_by"]
                        db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                        reward = bot_settings.get("refer_reward", 0.2)
                        update_balance(inviter, reward)
                        db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                        if inviter in user_cache:
                            user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                        ref_msg = (
                            f"{PEM['gift']} <b>New Referral !</b>\n"
                            f"------------------\n"
                            f"🔥 <b>You Received {reward} TK</b>\n"
                            f"------------------\n"
                            f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                        )
                        send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    # 🌟 X রিমুভ করে ক্লিন রেঞ্জ নেওয়া হলো
                    num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        # শুধুমাত্র StexSMS Services থেকে রেঞ্জ নিবো (Search Countries নিবো না, কারণ ওগুলোতে শুধু দেশের কোড থাকে)
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    # 🌟 এখানেও সেভ করা রেঞ্জ থেকে X সরিয়ে নিচ্ছি
                    known_ranges.add(r.replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            # 🌟 বাটনে এবং কলব্যাকে যাতে কোনো X না থাকে তা নিশ্চিত করা হলো
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "callback_data": f"c_n_s_{clean_r}_{srv_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    # --- Menu Design Integration ---
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ আপনার ব্যালেন্স অপর্যাপ্ত! মিনিমাম {min_w} ৳ প্রয়োজন।", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ৳\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ৳):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 যেকোনো একটি Premium Emoji সেন্ড করুন (যেমন: 🇧🇩 বা 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
            return
        content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
            return
        content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "toggle_stex_auto":
        bot_settings["stex_auto"] = not bot_settings.get("stex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())
        answer_callback(call["id"], f"✅ Stex Auto Range is now {'ON' if bot_settings['stex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"},
                   {"text": "✏️ Rename", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"nx_ren_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_ren_srv_"):
        srv = data.replace("nx_ren_srv_", "")
        user_states[chat_id] = "wait_nx_rename_srv"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"✏️ Enter new name for <b>{srv}</b>:"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "toggle_voltx_auto":
        bot_settings["voltx_auto"] = not bot_settings.get("voltx_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())
        answer_callback(call["id"], f"✅ Voltx Auto Range is now {'ON' if bot_settings['voltx_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"},
                   {"text": "✏️ Rename", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"vx_ren_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_ren_srv_"):
        srv = data.replace("vx_ren_srv_", "")
        user_states[chat_id] = "wait_vx_rename_srv"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"✏️ Enter new name for <b>{srv}</b>:"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    # --- HADI (MK NETWORK) CALLBACKS ---
    elif data == "reseller_control" and is_admin(chat_id):
        edit_message(chat_id, msg_id, reseller_control_text(), reply_markup=reseller_control_keyboard())

    elif data == "reseller_gen_key" and is_admin(chat_id):
        user_states[chat_id] = "wait_reseller_key_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter a label for this new API key (e.g. <code>Rahim's Bot</code>):"), reply_markup=get_cancel_kb())

    elif data == "reseller_view_keys" and is_admin(chat_id):
        rk = bot_settings.get("reseller_keys", {})
        if not rk:
            answer_callback(call["id"], "No reseller keys yet.", show_alert=True)
            return
        kb = []
        for key, info in rk.items():
            status = "🟢" if info.get("active", True) else "🔴"
            label = f"{status} {info.get('name','Key')} ({info.get('used',0)} used)"
            kb.append([{"text": label, "callback_data": f"reseller_k_{info['kid']}", "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "reseller_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"🔑 <b>Reseller Keys ({len(rk)}):</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("reseller_k_") and is_admin(chat_id):
        kid = data[len("reseller_k_"):]
        key, info = reseller_find_by_kid(kid)
        if not info:
            answer_callback(call["id"], "Key not found (maybe deleted).", show_alert=True)
            return
        edit_message(chat_id, msg_id, reseller_key_detail_text(key, info), reply_markup=reseller_key_detail_kb(kid, info))

    elif data.startswith("reseller_toggle_") and is_admin(chat_id):
        kid = data[len("reseller_toggle_"):]
        key, info = reseller_find_by_kid(kid)
        if info:
            info["active"] = not info.get("active", True)
            save_db()
        handle_callback({"message": call["message"], "data": f"reseller_k_{kid}", "id": "internal"})

    elif data.startswith("reseller_del_") and is_admin(chat_id):
        kid = data[len("reseller_del_"):]
        key, info = reseller_find_by_kid(kid)
        if key:
            del bot_settings["reseller_keys"][key]
            save_db()
        handle_callback({"message": call["message"], "data": "reseller_view_keys", "id": "internal"})

    elif data.startswith("reseller_topup_") and is_admin(chat_id):
        kid = data[len("reseller_topup_"):]
        user_states[chat_id] = "wait_reseller_topup"
        temp_data[chat_id] = {"msg_id": msg_id, "kid": kid}
        edit_message(chat_id, msg_id, render_body_text("💰 Enter amount to add to balance (e.g. <code>50</code>):"), reply_markup=get_cancel_kb())

    elif data.startswith("reseller_cost_") and is_admin(chat_id):
        kid = data[len("reseller_cost_"):]
        user_states[chat_id] = "wait_reseller_cost"
        temp_data[chat_id] = {"msg_id": msg_id, "kid": kid}
        edit_message(chat_id, msg_id, render_body_text("💵 Enter cost per number for this key (e.g. <code>0.5</code>, or <code>0</code> for free):"), reply_markup=get_cancel_kb())

    elif data.startswith("reseller_ranges_") and is_admin(chat_id):
        kid = data[len("reseller_ranges_"):]
        user_states[chat_id] = "wait_reseller_ranges"
        temp_data[chat_id] = {"msg_id": msg_id, "kid": kid}
        txt = ("🌍 Send allowed ranges, one per line or space-separated (e.g. <code>880171XXX 91700XXX</code>).\n"
               "Send <code>all</code> to allow every range.")
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=get_cancel_kb())

    elif data.startswith("reseller_expiry_") and is_admin(chat_id):
        kid = data[len("reseller_expiry_"):]
        user_states[chat_id] = "wait_reseller_expiry"
        temp_data[chat_id] = {"msg_id": msg_id, "kid": kid}
        txt = "⏳ Send number of days until this key expires (e.g. <code>30</code>), or <code>never</code> for no expiry."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=get_cancel_kb())

    elif data.startswith("reseller_log_") and is_admin(chat_id):
        kid = data[len("reseller_log_"):]
        key, info = reseller_find_by_kid(kid)
        if not info:
            answer_callback(call["id"], "Key not found.", show_alert=True)
            return
        kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"reseller_k_{kid}", "style": "primary"}]]}
        edit_message(chat_id, msg_id, reseller_log_text(info), reply_markup=kb)

    elif data == "hadi_control" and is_admin(chat_id):
        if user_states.get(chat_id) in ("wait_for_add_hadi_key", "wait_for_hadi_range"):
            del user_states[chat_id]
            temp_data.pop(chat_id, None)
        edit_message(chat_id, msg_id, hadi_control_text(), reply_markup=hadi_control_keyboard())

    elif data == "toggle_hadi_auto" and is_admin(chat_id):
        bot_settings["hadi_auto"] = not bot_settings.get("hadi_auto", False)
        save_db()
        edit_message(chat_id, msg_id, hadi_control_text(), reply_markup=hadi_control_keyboard())
        answer_callback(call["id"], f"✅ Hadi Auto Range is now {'ON' if bot_settings['hadi_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_hadi_key" and is_admin(chat_id):
        user_states[chat_id] = "wait_for_add_hadi_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Hadi (MK Network) API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "hadi_control", "style": "danger"}]]})

    elif data == "view_hadi_keys" and is_admin(chat_id):
        kb = []
        for idx, key in enumerate(bot_settings.get("hadi_keys", [])):
            safe_name = key[:10] + "..." if len(key) > 10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_hadi_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "hadi_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Hadi Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_hadi_") and is_admin(chat_id):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("hadi_keys", [])):
            del bot_settings["hadi_keys"][idx]
            # এই কী-এর পেন্ডিং নম্বর ট্র্যাকিং বাদ দেওয়া (ইনডেক্স বদলে যায়)
            hadi_assigned_numbers.clear()
            save_db()
            answer_callback(call["id"], "✅ Hadi Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_hadi_keys", "id": call["id"]})

    elif data == "hadi_menu":
        all_r = hadi_get_all_ranges()
        countries = sorted(all_r.keys())
        if not bot_settings.get("hadi_keys") or not countries:
            msg_t = "❌ Hadi Number out of stock or range missing!"
            if is_admin(chat_id):
                msg_t += "\nAdmin: Hadi Control > Sync Now / Add Range"
            answer_callback(call["id"], msg_t, show_alert=True)
            return
        kb = []
        for c in countries:
            cb = f"hadi_c_{c}"
            if len(cb.encode("utf-8")) > 64:
                continue
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": cb, "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "primary"}])
        answer_callback(call["id"])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['pin']} Select Country"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("hadi_c_"):
        country = data[len("hadi_c_"):]
        ranges = list(hadi_get_all_ranges().get(country, []))
        if not ranges or not bot_settings.get("hadi_keys"):
            answer_callback(call["id"], "❌ Hadi Number out of stock or range missing!", show_alert=True)
            return
        hadi_deliver(call, chat_id, msg_id, ranges, f"hadi_c_{country}", "hadi_menu", "Change Country", shuffle=True)

    elif data == "hadi_api_menu":
        if not bot_settings.get("hadi_keys") or not bot_settings.get("hadi_api_on", True):
            answer_callback(call["id"], "❌ API Number is not available right now!", show_alert=True)
            return
        user_states[chat_id] = "wait_for_hadi_api_prefix"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = (f"{PEM['num']} <b>API Number</b>\n\n"
               "Send 3 to 12 digits.\nExample: <code>7697</code> or <code>7697XXX</code>")
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "hadi_api_cancel", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data == "hadi_api_cancel":
        if chat_id in user_states and user_states[chat_id] == "wait_for_hadi_api_prefix":
            del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        handle_callback({"message": call["message"], "data": "back_to_services", "id": "internal"})

    elif data.startswith("hadi_a_"):
        digits = re.sub(r"\D", "", data[len("hadi_a_"):])
        if len(digits) < 3 or not bot_settings.get("hadi_keys") or not bot_settings.get("hadi_api_on", True):
            answer_callback(call["id"], "❌ API Number is not available right now!", show_alert=True)
            return
        hadi_deliver(call, chat_id, msg_id, hadi_api_candidates(digits), f"hadi_a_{digits}", "hadi_api_menu", "Change Range", shuffle=False)

    elif data == "hadi_api_toggle" and is_admin(chat_id):
        bot_settings["hadi_api_on"] = not bot_settings.get("hadi_api_on", True)
        save_db()
        edit_message(chat_id, msg_id, hadi_control_text(), reply_markup=hadi_control_keyboard())

    elif data == "hadi_sync_now" and is_admin(chat_id):
        total, err = hadi_sync_ranges()
        edit_message(chat_id, msg_id, hadi_control_text(), reply_markup=hadi_control_keyboard())

    elif data == "add_hadi_range" and is_admin(chat_id):
        user_states[chat_id] = "wait_for_hadi_range"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "📝 Send Hadi ranges (one per line or separated by space/comma).\nExample:\n<code>880171XXX\n7697XXX</code>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "hadi_control", "style": "danger"}]]})

    elif data == "view_hadi_ranges" and is_admin(chat_id):
        flat = [(c, r) for c, lst in (bot_settings.get("hadi_manual_ranges") or {}).items() for r in lst]
        if not flat:
            edit_message(chat_id, msg_id, hadi_control_text(), reply_markup=hadi_control_keyboard())
            answer_callback(call["id"], "No manual ranges added yet.", show_alert=True)
            return
        kb = []
        for idx, (c, r) in enumerate(flat[:40]):
            kb.append([{"text": f"Delete {r} ({c})", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_hrng_{idx}", "style": "danger"}])
        kb.append([{"text": "Clear All", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "clear_hadi_ranges", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "hadi_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"🗑 <b>Manual Ranges ({len(flat)}):</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_hrng_") and is_admin(chat_id):
        try:
            idx = int(data[len("del_hrng_"):])
        except ValueError:
            return
        man = bot_settings.get("hadi_manual_ranges") or {}
        flat = [(c, r) for c, lst in man.items() for r in lst]
        if 0 <= idx < len(flat):
            c, r = flat[idx]
            man[c].remove(r)
            if not man[c]:
                del man[c]
            save_db()
        handle_callback({"message": call["message"], "data": "view_hadi_ranges", "id": "internal"})

    elif data == "clear_hadi_ranges" and is_admin(chat_id):
        bot_settings["hadi_manual_ranges"] = {}
        save_db()
        edit_message(chat_id, msg_id, hadi_control_text(), reply_markup=hadi_control_keyboard())

    elif data == "hadi_debug" and is_admin(chat_id):
        keys = bot_settings.get("hadi_keys", [])
        if not keys:
            send_message(chat_id, render_body_text("❌ No Hadi API key added!"))
            return
        try:
            res = requests.get(f"{HADI_BASE_URL}/access_list", params={"limit": 500}, headers={"mknetwork-key": keys[0]}, timeout=20)
            raw = res.text
            found = {}
            try:
                j = res.json()
                hadi_extract_ranges(j.get("data", j) if isinstance(j, dict) else j, found)
            except ValueError:
                pass
            total = sum(len(v) for v in found.values())
            send_document(chat_id, "hadi_access_list_raw.txt", f"HTTP {res.status_code}\n\n{raw}")
            summary = (f"🔍 <b>Hadi Debug</b>\nHTTP: {res.status_code}\nParsed: {len(found)} countries, {total} ranges\n"
                       f"Last API error: {html.escape(hadi_last_error['msg'] or 'none')}")
            send_message(chat_id, render_body_text(summary))
        except Exception as e:
            send_message(chat_id, render_body_text(f"❌ Debug failed: {html.escape(str(e))}"))

    # --- ZENEX CONTROL CALLBACKS ---
    elif data == "zenex_control":
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())

    elif data == "toggle_zenex_auto":
        bot_settings["zenex_auto"] = not bot_settings.get("zenex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())
        answer_callback(call["id"], f"✅ Zenex Auto Range is now {'ON' if bot_settings['zenex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_zenex_key":
        user_states[chat_id] = "wait_for_add_zenex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Zenex API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}]]})

    elif data == "view_zenex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("zenex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_znx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Zenex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_znx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_keys", [])):
            del bot_settings["zenex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_zenex_keys", "id": call["id"]})

    elif data == "zenex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("zenex_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_zsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Zenex Allowed Ranges:</b>\nOnly these codes will be allowed in Zenex Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_zenex_search_country":
        user_states[chat_id] = "wait_for_add_zsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Zenex Range Code (e.g. 447):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_search_country", "style": "danger"}]]})

    elif data.startswith("del_zsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_search_countries", [])):
            del bot_settings["zenex_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "zenex_search_country", "id": call["id"]})

    elif data == "manage_zenex_srv":
        kb = []
        for srv in bot_settings.get("zenex_services", {}):
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": "5257969839313526622", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "zx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("💠 <b>Zenex Services Manager</b>\nManage your API-based manual services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "zx_add_srv":
        user_states[chat_id] = "wait_zx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_srv_"):
        srv = data.replace("zx_srv_", "")
        kb = []
        for c in bot_settings.get("zenex_services", {}).get(srv, {}):
            kb.append([{"text": f"{c} ({len(bot_settings['zenex_services'][srv][c])} Ranges)", "icon_custom_emoji_id": "5780471598922337683", "callback_data": f"zx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_add_cnt_{srv}", "style": "success"},
                   {"text": "✏️ Rename", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"zx_ren_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_zenex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_ren_srv_"):
        srv = data.replace("zx_ren_srv_", "")
        user_states[chat_id] = "wait_zx_rename_srv"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"✏️ Enter new name for <b>{srv}</b>:"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_add_cnt_"):
        srv = data.replace("zx_add_cnt_", "")
        user_states[chat_id] = "wait_zx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. UK, USA):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["zenex_services"][srv].get(cnt, [])
        kb, row = [], []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"zx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_zx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 4473845XXX):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("zx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["zenex_services"].get(srv, {}).get(cnt, []):
            bot_settings["zenex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("zx_del_srv_"):
        srv = data.replace("zx_del_srv_", "")
        if srv in bot_settings["zenex_services"]: del bot_settings["zenex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_zenex_srv", "id": call["id"]})

    elif data.startswith("zx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["zenex_services"].get(srv, {}): del bot_settings["zenex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                p["api_url"] = try_url.replace(token, "{token}")
                                save_db()
                            break
                    except: pass
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>আমি ওই লিংকের সম্পূর্ণ (A-Z) ডাটা একটি Text File এ পাঠিয়েছি। ফাইলটি ওপেন করে সঠিক Column Number (যেমন: [1], [3]) চেক করে প্যানেলে আপডেট করে নাও।</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "dxa_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data == "back_to_services":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs)
        
        if not all_services and not bot_settings.get("hadi_keys"):
            answer_callback(call["id"], "❌ No numbers or services available!", show_alert=True)
            return
            
        c_msg = bot_settings["custom_messages"].get("get_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
        
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        for s in all_services:
            emoji_id = "5352694861990501856" 
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
        
        if bot_settings.get("hadi_keys"):
            kb.append([{"text": "Hadi Number", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "hadi_menu", "style": "success"}])
            if bot_settings.get("hadi_api_on", True):
                kb.append([{"text": "API Number", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "hadi_api_menu", "style": "success"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        zenex_cnts = set(bot_settings.get("zenex_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts).union(zenex_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683" # Default flag
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            
            otp_price = bot_settings.get("otp_reward", 0.0)
            # 🌟 ফাইলের নির্দিষ্ট কোনো রেট থাকলে সেটা নিয়ে আসবে
            for b in number_batches.values():
                if b.get("service") == service and b.get("country") == c and "rate" in b and b.get("numbers"):
                    otp_price = b.get("rate")
                    break
                    
            kb.append([{"text": f"{c} - {otp_price} TK/OTP", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        # ১. গ্লোবাল কুলডাউন চেক (সকল নাম্বার মেথডের জন্য)
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        # কুলডাউন আপডেট
        user_cooldowns[chat_id] = now
        
        # আগের নাম্বার এক্সপায়ার করা
        expire_previous_number(chat_id)

        # যদি সার্চ নাম্বার থেকে আসে
        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            clean_data = data[:-4] if is_voltx_req else data
            parts_s = clean_data.split("_", 4)
            
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            
            zenex_allowed = bot_settings.get("zenex_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            is_zenex_allowed = any(query.startswith(c) for c in zenex_allowed) if zenex_allowed else False
            is_zenex_req = data.endswith("_znx")
            
            if not is_voltx_req and not is_zenex_req and not is_stex_allowed and not is_voltx_allowed and not is_zenex_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)
                
                # প্রথমে Zenex চেক করবে
                if is_zenex_allowed or is_zenex_req:
                    zenex_keys = bot_settings.get("zenex_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in zenex_keys:
                            try:
                                headers = {"mapikey": api_key}
                                payload = {"range": query, "is_national": False, "remove_plus": False}
                                res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("full_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    zenex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_zenex_req = True 
                                    break
                            except: continue

                # তারপর Voltx চেক করবে
                if len(fetched_nums) < req_count and (is_voltx_allowed or is_voltx_req) and not is_zenex_req:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                payload = {"rid": query}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_voltx_req = True # মার্ক করে দিলাম যাতে পরবর্তীতে Voltx রিকোয়েস্ট হিসেবে কাজ করে
                                    break
                            except: continue

                # Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and (is_stex_allowed and not is_voltx_req and not is_zenex_req):
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    break
                            except: continue
                        
                if not api_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    
                    # 🌟 Save File Specific Rate
                    assigned_number_rates[num_str] = float(number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "primary"}])

            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
            vtx_ext = "_vtx" if is_voltx_req else "_znx" if is_zenex_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "danger"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            if service_from_cb:
                kb.append([{"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service_from_cb}", "style": "danger"}])
                
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            text_numbers = render_body_text(f"{country_emoji_html} NEW NUMBER\n")
            edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        # যদি আপলোড করা বা সার্ভিস থেকে আসে
        parts = data.split("_")
        service = parts[2]
        country = parts[3]

        available_indices = []
        # Check Local Stock First
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        # IF NO LOCAL STOCK, Check StexSMS, Voltx & Zenex Services
        if not available_indices:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            zenex_srv_data = bot_settings.get("zenex_services", {}).get(service, {}).get(country)
            
            target_range = None
            is_voltx = False
            is_zenex = False
            
            if stex_srv_data and len(stex_srv_data) > 0:
                target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0:
                target_range = random.choice(voltx_srv_data)
                is_voltx = True
            elif zenex_srv_data and len(zenex_srv_data) > 0:
                target_range = random.choice(zenex_srv_data)
                is_zenex = True
                
            if target_range:
                user_cooldowns[chat_id] = 0
                vtx_flag = "_vtx" if is_voltx else "_znx" if is_zenex else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            
            # 🌟 Save File Specific Rate
            assigned_number_rates[n_obj["num"]] = float(number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))
            
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True
                used_numbers_list.append(n_obj["num"])

        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "primary"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        country_emoji_html = ""
        for num in fetched_nums:
            char_flag, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            
            flag_emoji_id = "5780471598922337683" # Default Flag
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: 
                        flag_emoji_id = flag_data["id"]
                        country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                    break
            
            if not country_emoji_html: country_emoji_html = char_flag
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"}])
                   
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns: 
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service}", "style": "danger"}])
        kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        
        text_numbers = render_body_text(f"{country_emoji_html} NEW NUMBER\n")
        # সবসময় মেসেজ ইডিট করবে (Change Number করলেও নতুন মেসেজ আসবে না)
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums}
        except:
            # যদি মেসেজ ইডিট করা সম্ভব না হয় (যেমন অনেক আগের মেসেজ), তবে নতুন মেসেজ দিবে
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        # অ্যাডমিন চেক (User ID চেক করতে হবে)
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖DXA❖{num[-3:]}"
            else:
                masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} TK\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
            
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
            
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"})
                except: pass
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Polling Loop
# ==========================================
def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150): # 150 * 4 seconds = 10 Minutes Polling
        try:
            res = requests.get(f"{STEX_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10)
            data = res.json()
            if data.get("success") and data.get("otp"):
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                # 🌟 সম্পূর্ণ মেসেজ থেকে ড্যাশসহ বা বড় OTP খোঁজার ফিক্স
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                # 🌟 সম্পূর্ণ মেসেজ থেকে সার্ভিস/অ্যাপ চেনার ফিক্স
                app_name = data.get("service", "StexSMS Service")
                detected_app = detect_service(msg_text)
                if detected_app:
                    app_name = detected_app
                
                unique_id = f"POLL_{number_id}_{otp}"
                if unique_id not in processed_otps:
                    processed_otps.add(unique_id)
                    
                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                    
                    display_msg = build_otp_text(masked, iso, prem_app_html, app_full_name, lang_name, msg_text)
                    reward = float(assigned_number_rates.get(num_str, bot_settings.get("otp_reward", 0.0)))
                    
                    for fw in bot_settings.get("fw_groups", []):
                        kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                        temp_row = []
                        styles = ["danger", "success", "primary"]
                        for i, btn in enumerate(fw.get("buttons", [])):
                            b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                            if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                            temp_row.append(b_obj)
                            if len(temp_row) == 2:
                                kb.append(temp_row)
                                temp_row = []
                        if temp_row: kb.append(temp_row)
                        if reward > 0: kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                        kb.append(otp_footer_row())
                        send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                    
                    inbox_msg = build_otp_text(display_num, iso, prem_app_html, app_full_name, lang_name, msg_text)
                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                    
                    if reward > 0:
                        update_balance(owner_id, reward)
                    
                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                    
                    if db:
                        try: db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)})
                        except: pass
                break
        except: pass
        time.sleep(4)

def stex_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            if stex_keys:
                api_key = stex_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{STEX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"STEX_{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic for Stex every 2 minutes
                    if bot_settings.get("stex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
                        if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["stex_services"]:
                                bot_settings["stex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["stex_services"][srv]:
                                    bot_settings["stex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["stex_services"][srv][full_country_name]:
                                        bot_settings["stex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["search_countries"]:
                                        bot_settings["search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["stex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["stex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["stex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            if not bot_settings.get("voltx_on", True):
                time.sleep(5)
                continue
            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9] # 9 ডিজিটের বেশি হলে প্রথম 9 ডিজিট নেবে
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic every 2 minutes (120 seconds)
                    if bot_settings.get("voltx_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
                        if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                        
                        # --- ১. Auto ADD Logic ---
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)] # Top 6 Services
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["voltx_services"]:
                                bot_settings["voltx_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)] # Top 3 Countries
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["voltx_services"][srv]:
                                    bot_settings["voltx_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)] # Top 2 Ranges
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                        bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    # 🌟 শুধুমাত্র ৩ ডিজিট কান্ট্রি কোড অ্যাড করবে
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["voltx_search_countries"]:
                                        bot_settings["voltx_search_countries"].append(country_code)
                                        changed = True

                        # --- ২. Auto DELETE Logic (Only if NO traffic in the LAST 120 SECONDS) ---
                        services_to_remove = []
                        for srv, countries in list(bot_settings["voltx_services"].items()):
                            # চেক করবে গত ১২০ সেকেন্ডে কোনো ট্রাফিক আছে কি না
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["voltx_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["voltx_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = build_otp_text(masked, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                
                                reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    if reward > 0: kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    kb.append(otp_footer_row())
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    inbox_msg = build_otp_text(display_num, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)})
                                            if owner_id in user_cache:
                                                user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def zenex_sms_listener():
    global processed_otps, recent_traffic, zenex_assigned_numbers
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            for api_key in zenex_keys:
                try:
                    headers = {"mapikey": api_key}
                    res = requests.get(f"{ZENEX_BASE_URL}/v1/numsuccess/info", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("otp", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("nid", otp))
                            
                            app_name = "Zenex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"ZENEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = build_otp_text(masked, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                
                                reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    if reward > 0: kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    kb.append(otp_footer_row())
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for znx_n, n_owner in zenex_assigned_numbers.items():
                                        clean_znx = str(znx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_znx == clean_api_num or (len(clean_znx) >= 8 and clean_znx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_znx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    inbox_msg = build_otp_text(display_num, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)})
                                            if owner_id in user_cache:
                                                user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = build_otp_text(masked, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                
                                reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    if reward > 0: kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    kb.append(otp_footer_row())
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    inbox_msg = build_otp_text(display_num, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)})
                                            if owner_id in user_cache:
                                                user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def zenex_console_listener():
    global recent_traffic, bot_settings
    last_auto_update = time.time()
    zenex_last_hits = {} 
    
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            if zenex_keys:
                api_key = zenex_keys[0]
                headers = {"mapikey": api_key}
                res = requests.get(f"{ZENEX_BASE_URL}/v1/active-ranges", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("success") and "data" in data and "active_ranges" in data["data"]:
                    current_time = time.time()
                    new_hits_added = False
                    
                    for hit in data["data"]["active_ranges"]:
                        range_str = str(hit.get("range", "")).replace("X", "").replace("x", "")
                        sid = str(hit.get("service", "Unknown")).upper()
                        hits_count = int(hit.get("hits", 1))
                        
                        if range_str:
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, "")
                            
                            range_key = f"{range_str}_{app_full_name}"
                            prev_hits = zenex_last_hits.get(range_key, 0)
                            
                            if hits_count > prev_hits:
                                new_hits = hits_count - prev_hits
                            else:
                                new_hits = hits_count
                                
                            zenex_last_hits[range_key] = hits_count
                            if new_hits > 150: new_hits = 150
                            
                            for _ in range(new_hits):
                                recent_traffic.append({
                                    "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": f"{range_str}XXX", 
                                    "time": current_time,
                                    "real_range": range_str,
                                    "source": "zenex"
                                })
                                new_hits_added = True
                            
                    if new_hits_added:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    if bot_settings.get("zenex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
                        if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "zenex" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["zenex_services"]:
                                bot_settings["zenex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "zenex" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["zenex_services"][srv]:
                                    bot_settings["zenex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "zenex" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["zenex_services"][srv][full_country_name]:
                                        bot_settings["zenex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["zenex_search_countries"]:
                                        bot_settings["zenex_search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["zenex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and t.get("source") == "zenex" and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["zenex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["zenex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

# ==========================================
# HADI (MK NETWORK) CORE  -- rewritten
# ==========================================
HADI_RANGE_RE = re.compile(r"^\+?(\d{3,15})([Xx]*)$")
HADI_RANGE_KEYS = ("range", "ranges", "range_id", "prefix", "pattern", "number_range", "range_name")
HADI_COUNTRY_KEYS = ("country", "country_name", "countryName", "country_iso", "iso")
HADI_GENERIC_KEYS = ("data", "results", "items", "list", "access_list", "meta", "countries", "services")

hadi_last_error = {"msg": "", "time": 0}
hadi_last_sync = {"time": 0, "count": 0, "error": ""}
hadi_busy = set()
hadi_busy_lock = threading.Lock()


def hadi_log_error(msg):
    hadi_last_error["msg"] = str(msg)[:300]
    hadi_last_error["time"] = time.time()
    print(f"⚠️ [HADI] {msg}")


def hadi_norm_range(val):
    # "7697xxx" / "+7697XXX" / 7697 -> "7697XXX" / "7697". Returns None if it is not a range.
    s = str(val).strip().replace(" ", "")
    m = HADI_RANGE_RE.match(s)
    if not m:
        return None
    return m.group(1) + m.group(2).upper()


def hadi_country_for(digits, hint=None):
    if hint:
        h = str(hint).strip()
        if len(h) == 2 and h.isalpha():
            name = get_flag_info_html(h.upper(), return_full_name=True)
            return str(name).title() if name else h.upper()
        if h:
            return h.title()
    name = get_flag_info_html(digits, return_full_name=True)
    if not name or str(name).replace("+", "") == digits:
        return f"+{digits[:3]}"
    return str(name).title()


def _hadi_add_range(found, r, country):
    digits = re.sub(r"\D", "", r)
    name = hadi_country_for(digits, country)
    lst = found.setdefault(name, [])
    if r not in lst:
        lst.append(r)


def hadi_extract_ranges(obj, found, country_hint=None, in_range_key=False):
    # Tolerant parser: works with list/dict/nested/{country: [ranges]}/{range: {...}} shapes.
    if isinstance(obj, dict):
        country = country_hint
        for ck in HADI_COUNTRY_KEYS:
            v = obj.get(ck)
            if isinstance(v, str) and v.strip():
                country = v.strip()
                break
        for k, v in obj.items():
            ks = str(k)
            if ks in HADI_RANGE_KEYS:
                hadi_extract_ranges(v, found, country, in_range_key=True)
                continue
            r_key = hadi_norm_range(ks)
            if r_key:
                c2 = country
                if isinstance(v, dict):
                    for ck in HADI_COUNTRY_KEYS:
                        if isinstance(v.get(ck), str) and v.get(ck).strip():
                            c2 = v[ck].strip()
                            break
                _hadi_add_range(found, r_key, c2)
            if isinstance(v, (dict, list)):
                hint = country
                if ks not in HADI_GENERIC_KEYS and not r_key and ks not in HADI_COUNTRY_KEYS:
                    if isinstance(v, list) and v and all(isinstance(x, (str, int)) and not isinstance(x, bool) for x in v):
                        hint = ks
                hadi_extract_ranges(v, found, hint)
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, bool):
                continue
            if isinstance(it, str) or (in_range_key and isinstance(it, int)):
                r = hadi_norm_range(it)
                if r:
                    _hadi_add_range(found, r, country_hint)
            elif isinstance(it, (dict, list)):
                hadi_extract_ranges(it, found, country_hint, in_range_key)
    elif isinstance(obj, (str, int)) and in_range_key and not isinstance(obj, bool):
        r = hadi_norm_range(obj)
        if r:
            _hadi_add_range(found, r, country_hint)


def hadi_get_all_ranges():
    # auto (access_list) + manual (admin added) ranges merged: {country: [ranges]}
    merged = {}
    for src in (bot_settings.get("hadi_ranges") or {}, bot_settings.get("hadi_manual_ranges") or {}):
        for c, lst in src.items():
            for r in (lst or []):
                if r not in merged.setdefault(c, []):
                    merged[c].append(r)
    return {c: l for c, l in merged.items() if l}


def hadi_sync_ranges():
    keys = list(bot_settings.get("hadi_keys", []))
    found = {}
    errors = []
    for idx, api_key in enumerate(keys):
        try:
            res = requests.get(f"{HADI_BASE_URL}/access_list", params={"limit": 500},
                               headers={"mknetwork-key": api_key}, timeout=20)
            try:
                resp = res.json()
            except ValueError:
                errors.append(f"key{idx+1}: HTTP {res.status_code} (not JSON)")
                continue
            if isinstance(resp, dict):
                meta = resp.get("meta") or {}
                code = str(meta.get("code", res.status_code))
                if code != "200":
                    errors.append(f"key{idx+1}: {code} {meta.get('message') or meta.get('msg') or resp.get('message') or ''}".strip())
                    continue
                hadi_extract_ranges(resp.get("data", resp), found)
            else:
                hadi_extract_ranges(resp, found)
        except Exception as e:
            errors.append(f"key{idx+1}: {type(e).__name__}")
    total = sum(len(v) for v in found.values())
    if keys and not found and not errors:
        errors.append("No range found in access_list response (use Debug API)")
    err_text = "; ".join(errors)[:300]
    hadi_last_sync.update({"time": time.time(), "count": total, "error": err_text})
    if err_text:
        hadi_log_error(f"access_list: {err_text}")
    if found and found != bot_settings.get("hadi_ranges"):
        bot_settings["hadi_ranges"] = found
        save_local_db()
    return total, err_text


def hadi_range_updater():
    while True:
        try:
            if bot_settings.get("hadi_auto", False) and bot_settings.get("hadi_keys"):
                hadi_sync_ranges()
        except Exception as e:
            hadi_log_error(f"range updater: {e}")
        time.sleep(120)


def hadi_fetch_number(range_list, deadline, exclude=None):
    # Try ranges x keys until one gives a number. Returns ((request_id, number, key_idx), "") or (None, error)
    exclude = exclude or set()
    keys = list(bot_settings.get("hadi_keys", []))
    if not keys:
        return None, "No Hadi API key"
    if not range_list:
        return None, "No range"
    last_err = "Unknown error"
    bad_keys = set()
    for rng in range_list:
        for k_idx, api_key in enumerate(keys):
            if k_idx in bad_keys:
                continue
            if time.time() > deadline:
                return None, last_err
            for attempt in range(2):
                try:
                    headers = {"mknetwork-key": api_key, "Content-Type": "application/json"}
                    res = requests.post(f"{HADI_BASE_URL}/getnum/number", json={"range": rng}, headers=headers, timeout=12)
                    try:
                        resp = res.json()
                    except ValueError:
                        last_err = f"[{rng}] HTTP {res.status_code} (not JSON)"
                        hadi_log_error(last_err)
                        break
                    if not isinstance(resp, dict):
                        last_err = f"[{rng}] unexpected response"
                        hadi_log_error(last_err)
                        break
                    meta = resp.get("meta") or {}
                    code = str(meta.get("code", res.status_code))
                    d = resp.get("data") or {}
                    if not isinstance(d, dict):
                        d = {}
                    rid = d.get("request_id") if d.get("request_id") is not None else d.get("id")
                    num = re.sub(r"\D", "", str(d.get("full_number") or d.get("number") or ""))
                    if code == "200" and rid is not None and num:
                        if num in exclude:
                            last_err = f"[{rng}] duplicate number"
                            break
                        return (str(rid), num, k_idx), ""
                    msg = meta.get("message") or meta.get("msg") or resp.get("message") or resp.get("error") or ""
                    last_err = f"[{rng}] {code} {msg}".strip()
                    hadi_log_error(last_err)
                    if code in ("401", "403"):
                        bad_keys.add(k_idx)
                        break
                    if code == "429" and attempt == 0:
                        time.sleep(1.5)
                        continue
                    break
                except Exception as e:
                    last_err = f"[{rng}] {type(e).__name__}"
                    hadi_log_error(f"{last_err}: {e}")
                    if attempt == 0:
                        continue
    return None, last_err


def hadi_api_candidates(digits, raw=""):
    # Range strings to try for a member typed prefix like 7697 / 7697XXX
    cands = []
    exact = []
    for lst in hadi_get_all_ranges().values():
        for r in lst:
            if re.sub(r"\D", "", r).startswith(digits):
                exact.append(r)
    random.shuffle(exact)
    cands.extend(exact[:5])
    if raw and "X" in raw:
        cands.append(raw)
    cands.append(digits + "XXX")
    cands.append(digits)
    out = []
    for c in cands:
        if c not in out:
            out.append(c)
    return out[:8]


def hadi_fail(call, chat_id, msg_id, text, retry_cb=None):
    if call and call.get("id") and call.get("id") != "internal":
        answer_callback(call["id"], text[:190], show_alert=True)
        return
    kb = []
    if retry_cb:
        kb.append([{"text": "Try Again", "icon_custom_emoji_id": "5465368548702446780", "callback_data": retry_cb, "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "primary"}])
    if msg_id:
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup={"inline_keyboard": kb})
    else:
        send_message(chat_id, render_body_text(text), reply_markup={"inline_keyboard": kb})


def hadi_send_numbers_ui(chat_id, msg_id, nums, again_cb, change_cb, change_text):
    kb = [[{"text": "Hadi Number", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "ignore", "style": "primary"}]]
    flags_db = bot_settings.get("premium_flags", {})
    country_emoji_html = ""
    for num in nums:
        char_flag, iso = get_flag_and_code(num)
        display_num = f"+{num}"
        flag_emoji_id = "5780471598922337683"
        for flag_code, flag_data in flags_db.items():
            if iso == flag_data.get("iso"):
                if "id" in flag_data:
                    flag_emoji_id = flag_data["id"]
                    country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                break
        if not country_emoji_html:
            country_emoji_html = char_flag
        kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
    kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": again_cb, "style": "danger"}])
    kb.append([{"text": change_text, "icon_custom_emoji_id": "5305517382138112561", "callback_data": change_cb, "style": "danger"}])
    kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
    text_numbers = render_body_text(f"{country_emoji_html} NEW NUMBER\n")
    sent_id = None
    if msg_id:
        res = edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
        if res and res.get("ok"):
            sent_id = msg_id
    if sent_id is None:
        res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
        if res and "result" in res:
            sent_id = res["result"]["message_id"]
    if sent_id is not None:
        user_active_sessions[chat_id] = {"msg_id": sent_id, "nums": nums}


def hadi_deliver(call, chat_id, msg_id, range_list, again_cb, change_cb, change_text, shuffle=True):
    global total_assigned_stats
    now = time.time()
    cd = bot_settings.get("cooldown", 10)
    wait = cd - (now - user_cooldowns.get(chat_id, 0))
    if wait > 0:
        hadi_fail(call, chat_id, msg_id, f"⌛ Please wait {int(wait) + 1}s.", again_cb)
        return
    with hadi_busy_lock:
        if chat_id in hadi_busy:
            if call and call.get("id") and call.get("id") != "internal":
                answer_callback(call["id"], "⌛ Please wait...", show_alert=False)
            return
        hadi_busy.add(chat_id)
    try:
        if not bot_settings.get("hadi_keys") or not range_list:
            hadi_fail(call, chat_id, msg_id, "❌ Hadi Number out of stock or range missing!", again_cb)
            return
        try:
            req_count = max(1, int(bot_settings.get("num_req", 1)))
        except Exception:
            req_count = 1
        deadline = time.time() + 35
        got = []
        last_err = ""
        for _ in range(req_count):
            rl = list(range_list)
            if shuffle:
                random.shuffle(rl)
                rl = rl[:6]
            item, err = hadi_fetch_number(rl, deadline, exclude={g[1] for g in got})
            if not item:
                last_err = err
                break
            got.append(item)
        if not got:
            msg = "❌ No number available right now! Try again."
            if is_admin(chat_id) and last_err:
                msg += f"\n{last_err}"
            hadi_fail(call, chat_id, msg_id, msg, again_cb)
            return
        # success: expire the old number first, then register the new ones
        expire_previous_number(chat_id)
        t_now = time.time()
        nums = []
        for rid, num, k_idx in got:
            hadi_assigned_numbers[rid] = {"owner": chat_id, "number": num, "key_idx": k_idx, "time": t_now}
            assigned_number_rates[num] = float(bot_settings.get("otp_reward", 0.0))
            total_assigned_stats += 1
            nums.append(num)
        user_cooldowns[chat_id] = t_now
        save_db()
        if call and call.get("id") and call.get("id") != "internal":
            answer_callback(call["id"])
        hadi_send_numbers_ui(chat_id, msg_id, nums, again_cb, change_cb, change_text)
    finally:
        with hadi_busy_lock:
            hadi_busy.discard(chat_id)


# ==========================================
# RESELLER API (my bot acts as a panel for other bots)
# ==========================================
def reseller_find_key(raw_key):
    rk = bot_settings.get("reseller_keys", {})
    info = rk.get(raw_key)
    if not info or not info.get("active", True):
        return None
    exp = info.get("expires_at")
    if exp and time.time() > exp:
        return None
    return info

def reseller_log_event(info, request_id, number, otp=None):
    log = info.setdefault("log", [])
    log.insert(0, {"time": time.time(), "request_id": request_id, "number": number, "otp": otp})
    del log[50:]

def reseller_log_set_otp(info, request_id, otp):
    for row in info.get("log", []):
        if row.get("request_id") == request_id:
            row["otp"] = otp
            return

def reseller_api_error(code, message, http=200):
    return jsonify({"meta": {"code": str(code), "message": message}}), http

flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def reseller_root():
    return jsonify({"status": "ok", "service": "Reseller API"})

@flask_app.route("/api/v1/access_list", methods=["GET"])
def reseller_access_list():
    key = request.args.get("key", "")
    info = reseller_find_key(key)
    if not info:
        return reseller_api_error(401, "Invalid or inactive API key")
    allowed = info.get("ranges")  # None = all ranges allowed
    all_r = hadi_get_all_ranges()
    if allowed:
        all_r = {c: [r for r in lst if r in allowed] for c, lst in all_r.items()}
        all_r = {c: l for c, l in all_r.items() if l}
    return jsonify({"meta": {"code": "200"}, "data": all_r})

@flask_app.route("/api/v1/getnum/number", methods=["GET", "POST"])
def reseller_get_number():
    key = request.values.get("key", "")
    rng = request.values.get("range", "")
    info = reseller_find_key(key)
    if not info:
        return reseller_api_error(401, "Invalid or inactive API key")
    digits = re.sub(r"\D", "", rng)
    if len(digits) < 2:
        return reseller_api_error(400, "Missing or invalid 'range' parameter")
    cost = float(info.get("cost_per_number", 0.0))
    if cost > 0 and float(info.get("balance", 0.0)) < cost:
        return reseller_api_error(402, "Insufficient balance")
    allowed = info.get("ranges")
    candidates = hadi_api_candidates(digits, rng)
    if allowed:
        candidates = [c for c in candidates if c in allowed] or [r for r in allowed if r.startswith(digits)]
        if not candidates:
            return reseller_api_error(403, "Range not allowed for this key")
    item, err = hadi_fetch_number(candidates, time.time() + 25)
    if not item:
        return reseller_api_error(404, err or "No number available")
    rid, num, k_idx = item
    hadi_assigned_numbers[rid] = {"owner": f"api:{key}", "number": num, "key_idx": k_idx, "time": time.time()}
    if cost > 0:
        info["balance"] = round(float(info.get("balance", 0.0)) - cost, 4)
    info["used"] = int(info.get("used", 0)) + 1
    reseller_log_event(info, rid, f"+{num}")
    save_db()
    return jsonify({"meta": {"code": "200"}, "data": {"request_id": rid, "full_number": f"+{num}"}})

@flask_app.route("/api/v1/check/status", methods=["GET"])
def reseller_check_status():
    key = request.args.get("key", "")
    rid = request.args.get("request_id", "")
    info = reseller_find_key(key)
    if not info:
        return reseller_api_error(401, "Invalid or inactive API key")
    assign = hadi_assigned_numbers.get(rid)
    if not assign or assign.get("owner") != f"api:{key}":
        return reseller_api_error(404, "Unknown request_id for this key")
    hit = api_otp_inbox.get(rid)
    if not hit:
        return jsonify({"meta": {"code": "200"}, "data": {"status": "waiting", "messages": []}})
    reseller_log_set_otp(info, rid, hit["otp"])
    save_db()
    return jsonify({"meta": {"code": "200"}, "data": {
        "status": "received",
        "messages": [{"sms_id": rid, "otp_code": hit["otp"], "full_sms": hit["message"], "service": hit["service"]}]
    }})

@flask_app.route("/api/v1/balance", methods=["GET"])
def reseller_balance():
    key = request.args.get("key", "")
    info = reseller_find_key(key)
    if not info:
        return reseller_api_error(401, "Invalid or inactive API key")
    return jsonify({"meta": {"code": "200"}, "data": {
        "name": info.get("name", ""), "balance": info.get("balance", 0.0), "used": info.get("used", 0)
    }})

def run_reseller_api():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def reseller_find_by_kid(kid):
    for key, info in bot_settings.get("reseller_keys", {}).items():
        if info.get("kid") == kid:
            return key, info
    return None, None

def reseller_control_text():
    rk = bot_settings.get("reseller_keys", {})
    active = sum(1 for v in rk.values() if v.get("active", True))
    lines = [
        "🌐 <b>Reseller API Panel</b>\n",
        f"Public URL: <code>{html.escape(os.environ.get('RESELLER_PUBLIC_URL', 'https://nishat-x-fast-production.up.railway.app'))}</code>",
        f"Total Keys: {len(rk)} | Active: {active}",
        "\nOther bots can connect using these endpoints:",
        "• GET /api/v1/access_list?key=XXXX",
        "• GET /api/v1/getnum/number?key=XXXX&range=XXXX",
        "• GET /api/v1/check/status?key=XXXX&request_id=XXXX",
        "• GET /api/v1/balance?key=XXXX",
    ]
    return render_body_text("\n".join(lines))

def reseller_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Generate New Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "reseller_gen_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "reseller_view_keys", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def reseller_key_detail_text(key, info):
    status = "ON 🟢" if info.get("active", True) else "OFF 🔴"
    exp = info.get("expires_at")
    exp_txt = datetime.fromtimestamp(exp).strftime("%d %b %Y") if exp else "Never"
    ranges = info.get("ranges")
    ranges_txt = ", ".join(ranges) if ranges else "All ranges"
    lines = [
        f"🔑 <b>{html.escape(info.get('name','Key'))}</b>\n",
        f"API Key: <code>{key}</code>",
        f"Status: {status}",
        f"Balance: {info.get('balance', 0.0)} tk",
        f"Cost / Number: {info.get('cost_per_number', 0.0)} tk",
        f"Numbers Used: {info.get('used', 0)}",
        f"Expires: {exp_txt}",
        f"Allowed Ranges: {html.escape(ranges_txt)}",
    ]
    return render_body_text("\n".join(lines))

def reseller_key_detail_kb(kid, info):
    status_txt = "Disable" if info.get("active", True) else "Enable"
    return {"inline_keyboard": [
        [{"text": "💰 Add Balance", "callback_data": f"reseller_topup_{kid}", "style": "success"},
         {"text": "💵 Set Cost/Number", "callback_data": f"reseller_cost_{kid}", "style": "primary"}],
        [{"text": "🌍 Set Ranges", "callback_data": f"reseller_ranges_{kid}", "style": "primary"},
         {"text": "⏳ Set Expiry", "callback_data": f"reseller_expiry_{kid}", "style": "primary"}],
        [{"text": "📋 View Log", "callback_data": f"reseller_log_{kid}", "style": "success"}],
        [{"text": status_txt, "callback_data": f"reseller_toggle_{kid}", "style": "primary"},
         {"text": "Delete Key", "callback_data": f"reseller_del_{kid}", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "reseller_view_keys", "style": "primary"}]
    ]}

def reseller_log_text(info):
    log = info.get("log", [])
    if not log:
        return render_body_text("📋 <b>No usage yet for this key.</b>")
    lines = [f"📋 <b>Last {len(log)} requests:</b>\n"]
    for row in log[:20]:
        t = datetime.fromtimestamp(row["time"]).strftime("%d %b %H:%M")
        otp = row.get("otp") or "—"
        lines.append(f"• {t} | {html.escape(str(row['number']))} | OTP: {html.escape(str(otp))}")
    return render_body_text("\n".join(lines))


def hadi_sms_listener():
    global processed_otps, recent_traffic
    while True:
        try:
            now = time.time()
            keys = bot_settings.get("hadi_keys", [])
            # মেয়াদ শেষ (১৫ মিনিটের বেশি) ট্র্যাকিং পরিষ্কার
            for rid in [r for r, v in hadi_assigned_numbers.items() if now - v.get("time", now) > 960]:
                hadi_assigned_numbers.pop(rid, None)
            by_key = {}
            for rid, v in list(hadi_assigned_numbers.items()):
                by_key.setdefault(v.get("key_idx", 0), []).append(rid)
            for k_idx, rids in by_key.items():
                if not (0 <= k_idx < len(keys)): continue
                for i in range(0, len(rids), 100):
                    batch_ids = rids[i:i+100]
                    try:
                        headers = {"mknetwork-key": keys[k_idx], "Content-Type": "application/json"}
                        res = requests.post(f"{HADI_BASE_URL}/check/status", json={"request_ids": [int(x) if str(x).isdigit() else x for x in batch_ids]}, headers=headers, timeout=10)
                        resp = res.json()
                        if str((resp.get("meta") or {}).get("code")) != "200":
                            hadi_log_error(f"check/status: {(resp.get('meta') or {}).get('code')} {(resp.get('meta') or {}).get('message', '')}")
                            continue
                        for item in (resp.get("data") or {}).get("results", []):
                            rid = str(item.get("request_id"))
                            if item.get("status") in ("expired", "not_found"):
                                hadi_assigned_numbers.pop(rid, None)
                                continue
                            owner = (hadi_assigned_numbers.get(rid) or {}).get("owner")
                            num = str(item.get("number", "")).replace("+", "")
                            for m in item.get("messages", []) or []:
                                sms_id = str(m.get("sms_id", ""))
                                unique_id = f"HADI_{rid}_{sms_id}"
                                if not sms_id or unique_id in processed_otps: continue
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                msg_text = str(m.get("full_sms", ""))
                                otp = str(m.get("otp_code") or "") or extract_otp_code(msg_text) or "CODE"
                                app_name = detect_service(msg_text) or "Hadi Service"
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                display_num = f"+{num}"
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = build_otp_text(masked, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "success"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for bi, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[bi % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    if reward > 0: kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    kb.append(otp_footer_row())
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                if isinstance(owner, str) and owner.startswith("api:"):
                                    api_otp_inbox[rid] = {"otp": otp, "number": display_num, "service": app_full_name, "message": msg_text, "time": current_time}
                                elif owner:
                                    inbox_msg = build_otp_text(display_num, iso, prem_app_html, app_full_name, lang_name, msg_text)
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    if reward > 0:
                                        update_balance(owner, reward)
                                    send_message(owner, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    if db:
                                        try:
                                            db.collection('users').document(str(owner)).update({"total_otps": firestore.Increment(1)})
                                            if owner in user_cache:
                                                user_cache[owner]["total_otps"] = user_cache[owner].get("total_otps", 0) + 1
                                        except: pass
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(4)

def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")

    invalid_srvs = scan_invalid_services()
    if invalid_srvs:
        lines = "\n".join(f"• <code>{html.escape(n)}</code> (from {p})" for p, n in invalid_srvs)
        send_message(OWNER_ID, render_body_text(
            f"⚠️ <b>Found {len(invalid_srvs)} invalid service name(s):</b>\n{lines}\n\nSend /cleanup_services to remove them."))
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=stex_console_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    threading.Thread(target=zenex_sms_listener, daemon=True).start()
    threading.Thread(target=zenex_console_listener, daemon=True).start()
    threading.Thread(target=hadi_range_updater, daemon=True).start()
    threading.Thread(target=hadi_sms_listener, daemon=True).start()
    threading.Thread(target=run_reseller_api, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    print(f"🌐 Reseller API listening on port {os.environ.get('PORT', 8080)}")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()    