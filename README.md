# Xeo OTP Bot — Railway + GitHub Deploy

## ১. GitHub-এ আপলোড
1. GitHub-এ একটা **Private** রিপো বানান।
2. এই ফোল্ডারের ফাইলগুলো আপলোড করুন: `main.py`, `requirements.txt`, `Procfile`, `.python-version`, `.gitignore`, `README.md`।
3. টোকেন বা Firebase কী কখনো কোডে লিখে পুশ করবেন না। সেগুলো নিচের Variables-এ দেবেন।

## ২. Railway-তে ডেপ্লয়
1. railway.com → **New Project** → **Deploy from GitHub repo** → রিপো বাছুন।
2. সার্ভিসের **Variables** ট্যাবে এগুলো যোগ করুন:

| Variable | মান |
|---|---|
| `BOT_TOKEN` | BotFather থেকে পাওয়া টোকেন |
| `OWNER_ID` | আপনার Telegram User ID |
| `FIREBASE_CREDENTIALS` | Firebase service account JSON-এর পুরো লেখা (এক লাইনে) |
| `DB_FILE` | `/data/bot_data.json` |

3. **Volume** যোগ করুন (Mount path: `/data`)। এটা না দিলে প্রতিবার ডেপ্লয়ে `bot_data.json` মুছে যাবে।
4. Start Command লাগলে Settings → Deploy → Custom Start Command-এ `python main.py` দিন (Procfile থাকলে সাধারণত লাগে না)।
5. Deploy শেষ হলে **Logs**-এ `🤖 Bot is starting...` দেখলে বট চালু।

## ৩. জরুরি
- একই টোকেনে একসাথে দুই জায়গায় বট চালাবেন না। আগের সার্ভার বা পিসিতে চলা বট বন্ধ করুন, না হলে আপডেট নিয়ে সংঘর্ষ হবে।
- `FIREBASE_CREDENTIALS`-এ JSON এক লাইনে বসান। `private_key`-এর ভেতরের `\n` যেমন আছে তেমনই রাখুন।
- কোড আপডেট করলে GitHub-এ পুশ করুন, Railway নিজে নতুন ডেপ্লয় করবে।
