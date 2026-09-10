"""
كتالوج المنتجات والخدمات الرقمية لمتجر MZ
تابع لشركة ليمونة تيك (Laymouna Tech) ومنصة ماركت هب (Market Hub)
"""

CATEGORIES = {
    "cat_entertainment": {
        "title": "🎬 اشتراكات الترفيه والبث",
        "desc": "حسابات رسمية ومضمونة لأفضل منصات الأفلام والمسلسلات والموسيقى والقنوات.",
        "icon": "🎬",
    },
    "cat_ai_design": {
        "title": "🤖 الذكاء الاصطناعي والتصميم",
        "desc": "أدوات وحسابات احترافية لزيادة الإنتاجية وصناعة المحتوى والتصميم.",
        "icon": "🤖",
    },
    "cat_gaming": {
        "title": "🎮 شحن الألعاب والبطاقات",
        "desc": "شحن فوري بالآيدي (ID) لأشهر الألعاب وبطاقات المتاجر الرقمية العالمية.",
        "icon": "🎮",
    },
    "cat_software": {
        "title": "💻 البرامج والتراخيص الأصلية",
        "desc": "مفاتيح تفعيل رقمية دائمة لأنظمة ويندوز وحزم مايكروسوفت أوفيس الأصلية.",
        "icon": "💻",
    },
    "cat_social": {
        "title": "✈️ تيلجرام والسوشيال ميديا",
        "desc": "اشتراكات تيلجرام بريميوم وخدمات رفع التفاعل والمتابعين للحسابات والقنوات.",
        "icon": "✈️",
    },
    "cat_agency": {
        "title": "🍋 خدمات ليمونة تيك وماركت هب",
        "desc": "حلول برمجية وتأسيس متاجر إلكترونية وحملات تسويقية لأصحاب الأعمال.",
        "icon": "🍋",
    },
}

SERVICES = {
    # ------------------ 1. الترفيه والمشاهدة ------------------
    "srv_netflix": {
        "category": "cat_entertainment",
        "name": "Netflix 4K Ultra HD",
        "icon": "🍿",
        "desc": "اشتراك نتفلكس بأعلى دقة 4K UHD، مع ضمان كامل طوال فترة الاشتراك وبدون انقطاع.",
        "delivery_prompt": "📧 أرسل بريدك الإلكتروني (أو رقم الواتساب) لاستلام بيانات الحساب:",
        "packages": [
            {"id": "pkg_nf_1m_screen", "name": "شاشة خاصة (شهر واحد)", "price": "3.50$", "price_val": 3.5},
            {"id": "pkg_nf_3m_screen", "name": "شاشة خاصة (3 شهور)", "price": "9.50$", "price_val": 9.5},
            {"id": "pkg_nf_1m_full", "name": "حساب كامل خاص بك (شهر واحد)", "price": "12.00$", "price_val": 12.0},
        ],
    },
    "srv_shahid": {
        "category": "cat_entertainment",
        "name": "شاهد VIP (Shahid VIP)",
        "icon": "🌟",
        "desc": "اشتراك شاهد VIP الشامل للمسلسلات الحصرية، مع باقة الرياضة وقنوات البث المباشر بدقة Full HD.",
        "delivery_prompt": "📧 أرسل بريدك الإلكتروني لتفعيل الاشتراك عليه مباشرة:",
        "packages": [
            {"id": "pkg_sh_1m", "name": "اشتراك شهر كامل (شاشة خاصة)", "price": "3.00$", "price_val": 3.0},
            {"id": "pkg_sh_3m", "name": "اشتراك 3 شهور VIP", "price": "7.50$", "price_val": 7.5},
            {"id": "pkg_sh_1y", "name": "اشتراك سنوي كامل (12 شهر)", "price": "22.00$", "price_val": 22.0},
        ],
    },
    "srv_youtube": {
        "category": "cat_entertainment",
        "name": "YouTube Premium",
        "icon": "▶️",
        "desc": "يوتيوب بريميوم رسمي على إيميلك الشخصي: بدون إعلانات، تشغيل في الخلفية، وتحميل وتطبيق YouTube Music.",
        "delivery_prompt": "📧 أرسل إيميل حسابك في جوجل (Gmail) لإرسال دعوة التفعيل الرسمية:",
        "packages": [
            {"id": "pkg_yt_1m", "name": "اشتراك شهر واحد", "price": "2.00$", "price_val": 2.0},
            {"id": "pkg_yt_6m", "name": "اشتراك 6 شهور", "price": "8.00$", "price_val": 8.0},
            {"id": "pkg_yt_1y", "name": "اشتراك سنة كاملة (12 شهر)", "price": "14.00$", "price_val": 14.0},
        ],
    },
    "srv_spotify": {
        "category": "cat_entertainment",
        "name": "Spotify Premium",
        "icon": "🎵",
        "desc": "استمتع بملايين الأغاني والبودكاست بأعلى جودة صوت، بدون فواصل إعلانية وبإمكانية التحميل والاستماع أوفلاين.",
        "delivery_prompt": "📧 أرسل إيميل حسابك في سبوتيفاي لتفعيله مباشرة:",
        "packages": [
            {"id": "pkg_sp_3m", "name": "اشتراك 3 شهور بريميوم", "price": "5.00$", "price_val": 5.0},
            {"id": "pkg_sp_6m", "name": "اشتراك 6 شهور بريميوم", "price": "9.00$", "price_val": 9.0},
            {"id": "pkg_sp_1y", "name": "اشتراك سنة كاملة (12 شهر)", "price": "15.00$", "price_val": 15.0},
        ],
    },
    "srv_iptv": {
        "category": "cat_entertainment",
        "name": "سيرفر IPTV 4K القنوات والمباريات",
        "icon": "📺",
        "desc": "سيرفر فائق السرعة بدون تقطيع يضم أكثر من 10,000 قناة عربية وعالمية وقنوات الرياضة ومكتبة أفلام ومسلسلات ضخمة.",
        "delivery_prompt": "📱 أرسل نوع جهازك (شاشة سمارت، أندرويد، آيفون، TV Box) ورقم الواتساب:",
        "packages": [
            {"id": "pkg_ip_3m", "name": "اشتراك 3 شهور IPTV 4K", "price": "8.00$", "price_val": 8.0},
            {"id": "pkg_ip_6m", "name": "اشتراك 6 شهور IPTV 4K", "price": "13.00$", "price_val": 13.0},
            {"id": "pkg_ip_1y", "name": "اشتراك سنة كاملة + شهرين مجاناً", "price": "22.00$", "price_val": 22.0},
        ],
    },

    # ------------------ 2. الذكاء الاصطناعي والتصميم ------------------
    "srv_chatgpt": {
        "category": "cat_ai_design",
        "name": "ChatGPT Plus (GPT-4o)",
        "icon": "🧠",
        "desc": "الوصول غير المحدود لأقوى نماذج الذكاء الاصطناعي، توليد الصور بـ DALL-E 3، تحليل المستندات، والتصفح والبرمجة.",
        "delivery_prompt": "📧 أرسل بريدك الإلكتروني لتسليمك الحساب فوراً:",
        "packages": [
            {"id": "pkg_gpt_share", "name": "حساب مشترك خاص (شهر واحد)", "price": "6.00$", "price_val": 6.0},
            {"id": "pkg_gpt_private", "name": "حساب خاص بك بالكامل (شهر واحد)", "price": "18.00$", "price_val": 18.0},
        ],
    },
    "srv_canva": {
        "category": "cat_ai_design",
        "name": "Canva Pro (تفعيل رسمي)",
        "icon": "🎨",
        "desc": "تفعيل كانفا برو الرسمي على إيميلك الشخصي مدى الحياة أو سنوي: قوالب مدفوعة، إزالة الخلفيات بضغطة زر، وخطوط حصرية.",
        "delivery_prompt": "📧 أرسل إيميل حسابك في Canva لتصلك دعوة التفعيل الفورية:",
        "packages": [
            {"id": "pkg_canva_1y", "name": "اشتراك سنة كاملة (12 شهر)", "price": "4.50$", "price_val": 4.5},
            {"id": "pkg_canva_life", "name": "تفعيل مدى الحياة (Lifetime)", "price": "9.00$", "price_val": 9.0},
        ],
    },
    "srv_capcut": {
        "category": "cat_ai_design",
        "name": "CapCut Pro مونتاج احترافي",
        "icon": "✂️",
        "desc": "النسخة المدفوعة من تطبيق المونتاج الأشهر: تأثيرات حصرية، إزالة الضوضاء بالذكاء الاصطناعي، وتصدير بجودة 4K 60fps.",
        "delivery_prompt": "📧 أرسل بريدك الإلكتروني لاستلام بيانات الحساب:",
        "packages": [
            {"id": "pkg_cap_1m", "name": "اشتراك شهر كامل Pro", "price": "3.50$", "price_val": 3.5},
            {"id": "pkg_cap_1y", "name": "اشتراك سنوي كامل (12 شهر)", "price": "16.00$", "price_val": 16.0},
        ],
    },
    "srv_duolingo": {
        "category": "cat_ai_design",
        "name": "Duolingo Super لتعلم اللغات",
        "icon": "🦉",
        "desc": "تعلم أي لغة في العالم بقلوب لا نهائية وبدون إعلانات مع ميزة مراجعة الأخطاء المتقدمة.",
        "delivery_prompt": "📧 أرسل إيميل حسابك في دولينجو لتفعيله مباشرة:",
        "packages": [
            {"id": "pkg_duo_6m", "name": "اشتراك 6 شهور Super", "price": "5.00$", "price_val": 5.0},
            {"id": "pkg_duo_1y", "name": "اشتراك سنة كاملة (12 شهر)", "price": "8.50$", "price_val": 8.5},
        ],
    },

    # ------------------ 3. الألعاب والبطاقات ------------------
    "srv_pubg": {
        "category": "cat_gaming",
        "name": "شدات ببجي (PUBG Mobile UC)",
        "icon": "🔫",
        "desc": "شحن شدات ببجي الرسمي الفوري برقم الآيدي (Player ID) فقط بدون الحاجة لكلمة المرور.",
        "delivery_prompt": "🆔 أرسل رقم الآيدي (Player ID) في اللعبة مع اسم اللاعب:",
        "packages": [
            {"id": "pkg_uc_60", "name": "60 شدة UC", "price": "1.10$", "price_val": 1.1},
            {"id": "pkg_uc_325", "name": "325 شدة UC (300+25)", "price": "4.80$", "price_val": 4.8},
            {"id": "pkg_uc_660", "name": "660 شدة UC (رويال باس)", "price": "9.20$", "price_val": 9.2},
            {"id": "pkg_uc_1800", "name": "1800 شدة UC (1500+300)", "price": "23.50$", "price_val": 23.5},
            {"id": "pkg_uc_3850", "name": "3850 شدة UC (3000+850)", "price": "46.00$", "price_val": 46.0},
        ],
    },
    "srv_freefire": {
        "category": "cat_gaming",
        "name": "جواهر فري فاير (Free Fire)",
        "icon": "💎",
        "desc": "شحن جواهر فري فاير فوري عبر الآيدي (Player ID) الرسمي ومباشر في حسابك.",
        "delivery_prompt": "🆔 أرسل معرف اللاعب (ID) في فري فاير:",
        "packages": [
            {"id": "pkg_ff_110", "name": "110 جوهرة (100+10 بونص)", "price": "1.20$", "price_val": 1.2},
            {"id": "pkg_ff_231", "name": "231 جوهرة (210+21 بونص)", "price": "2.30$", "price_val": 2.3},
            {"id": "pkg_ff_583", "name": "583 جوهرة (530+53 بونص)", "price": "5.40$", "price_val": 5.4},
            {"id": "pkg_ff_1188", "name": "1188 جوهرة (1080+108 بونص)", "price": "10.50$", "price_val": 10.5},
        ],
    },
    "srv_playstation": {
        "category": "cat_gaming",
        "name": "بطاقات بلايستيشن (PlayStation Network)",
        "icon": "🎮",
        "desc": "كود رقمي فوري لشحن رصيد ستور بلايستيشن (ريتيل رسمي). متوفر للمتجر الأمريكي والسعودي والإماراتي.",
        "delivery_prompt": "🌍 حدد ريجن حسابك (أمريكي / سعودي / إماراتي) ورقم الواتساب لاستلام الكود:",
        "packages": [
            {"id": "pkg_ps_10", "name": "بطاقة 10$ ستور", "price": "11.00$", "price_val": 11.0},
            {"id": "pkg_ps_25", "name": "بطاقة 25$ ستور", "price": "26.50$", "price_val": 26.5},
            {"id": "pkg_ps_50", "name": "بطاقة 50$ ستور", "price": "52.00$", "price_val": 52.0},
            {"id": "pkg_ps_100", "name": "بطاقة 100$ ستور", "price": "102.00$", "price_val": 102.0},
        ],
    },
    "srv_steam": {
        "category": "cat_gaming",
        "name": "بطاقات ستيم (Steam Wallet)",
        "icon": "🕹️",
        "desc": "أكواد شحن محفظة ستيم العالمية لشراء الألعاب والأسلحة والإضافات فوراً.",
        "delivery_prompt": "📱 أرسل رقم الواتساب لاستلام الكود الرقمي وطريقة التفعيل:",
        "packages": [
            {"id": "pkg_stm_5", "name": "بطاقة 5$ ستيم عالمية", "price": "5.80$", "price_val": 5.8},
            {"id": "pkg_stm_10", "name": "بطاقة 10$ ستيم عالمية", "price": "11.20$", "price_val": 11.2},
            {"id": "pkg_stm_25", "name": "بطاقة 25$ ستيم عالمية", "price": "27.00$", "price_val": 27.0},
        ],
    },

    # ------------------ 4. البرامج والأنظمة الأصلية ------------------
    "srv_windows": {
        "category": "cat_software",
        "name": "مفاتيح Windows 10 / 11 Pro",
        "icon": "🪟",
        "desc": "مفتاح تنشيط أصلي 100% من مايكروسوفت يرتبط باللوحة الأم لجهازك مدى الحياة مع التحديثات الرسمية.",
        "delivery_prompt": "💻 حدد إصدار جهازك (Windows 10 Pro أو Windows 11 Pro) ورقم الواتساب:",
        "packages": [
            {"id": "pkg_win_10", "name": "مفتاح Windows 10 Pro أصلي (مدى الحياة)", "price": "4.50$", "price_val": 4.5},
            {"id": "pkg_win_11", "name": "مفتاح Windows 11 Pro أصلي (مدى الحياة)", "price": "5.50$", "price_val": 5.5},
            {"id": "pkg_win_combo", "name": "باقة Windows 11 Pro + Office 365 معا", "price": "8.50$", "price_val": 8.5},
        ],
    },
    "srv_office": {
        "category": "cat_software",
        "name": "Microsoft Office 365 Pro",
        "icon": "📑",
        "desc": "حساب أوفيس أصلي يشمل (Word, Excel, PowerPoint, Outlook) يعمل على 5 أجهزة مع مساحة سحابية 1TB OneDrive.",
        "delivery_prompt": "📧 أرسل بريدك الإلكتروني أو رقم هاتفك لاستلام بيانات الحساب والتعليمات:",
        "packages": [
            {"id": "pkg_off_user", "name": "حساب خاص أصلي (تفعيل دائم 5 أجهزة)", "price": "6.00$", "price_val": 6.0},
        ],
    },

    # ------------------ 5. تيلجرام والسوشيال ميديا ------------------
    "srv_tg_premium": {
        "category": "cat_social",
        "name": "تيلجرام بريميوم (Telegram Premium)",
        "icon": "⭐",
        "desc": "تفعيل رسمي ومباشر بدون كلمة سر: شارة النجمة بجانب اسمك، سرعة تحميل مضاعفة، تحويل الصوت إلى نصوص، ورفع ملفات حتى 4GB.",
        "delivery_prompt": "👤 أرسل يوزر حسابك على تيلجرام (مثال: @username) للإهداء الفوري:",
        "packages": [
            {"id": "pkg_tg_3m", "name": "اشتراك 3 شهور بريميوم", "price": "10.50$", "price_val": 10.5},
            {"id": "pkg_tg_6m", "name": "اشتراك 6 شهور بريميوم", "price": "17.00$", "price_val": 17.0},
            {"id": "pkg_tg_1y", "name": "اشتراك سنة كاملة (12 شهر)", "price": "29.00$", "price_val": 29.0},
        ],
    },
    "srv_social_growth": {
        "category": "cat_social",
        "name": "خدمات المتابعين والتفاعل (سوشيال)",
        "icon": "📈",
        "desc": "باقات زيادة متابعين ولايكات ومشاهدات حقيقية لحسابات إنستغرام، تيك توك، وقنوات تيلجرام مع ضمان عدم النقصان.",
        "delivery_prompt": "🔗 أرسل رابط الحساب أو القناة المراد تزويدها:",
        "packages": [
            {"id": "pkg_soc_1k_ig", "name": "1,000 متابع إنستغرام جودة عالية", "price": "2.50$", "price_val": 2.5},
            {"id": "pkg_soc_5k_ig", "name": "5,000 متابع إنستغرام جودة عالية", "price": "10.00$", "price_val": 10.0},
            {"id": "pkg_soc_1k_tg", "name": "1,000 عضو قناة/جروب تيلجرام", "price": "3.00$", "price_val": 3.0},
            {"id": "pkg_soc_10k_views", "name": "10,000 مشاهدة تيك توك/ريلز", "price": "1.50$", "price_val": 1.5},
        ],
    },

    # ------------------ 6. خدمات ليمونة تيك وماركت هب ------------------
    "srv_laymouna_store": {
        "category": "cat_agency",
        "name": "تأسيس متجر إلكتروني متكامل",
        "icon": "🛒",
        "desc": "من ليمونة تيك وماركت هب: تصميم وبرمجة وتجهيز متجرك الإلكتروني بالكامل (سلة، زد، شوبيفاي، أو ووكومرس) جاهز للبيع.",
        "delivery_prompt": "📞 أرسل اسم نشاطك ورقم هاتفك لمناقشة الخطة وتقديم العرض الفني:",
        "packages": [
            {"id": "pkg_lay_store_basic", "name": "باقة إطلاق المتجر الأساسية", "price": "75.00$", "price_val": 75.0},
            {"id": "pkg_lay_store_pro", "name": "باقة المتجر الاحترافي الشامل للربط وبوابات الدفع", "price": "180.00$", "price_val": 180.0},
        ],
    },
    "srv_laymouna_bot": {
        "category": "cat_agency",
        "name": "برمجة شات بوت وتطبيقات أتمتة AI",
        "icon": "🤖",
        "desc": "حلول برمجية مخصصة من ليمونة تيك: بوتات تيلجرام وواتساب للأعمال، أنظمة CRM، وربط الذكاء الاصطناعي مع قاعدة بياناتك.",
        "delivery_prompt": "✍️ أرسل وصفاً مختصراً للمشروع ورقم الواتساب لتحديد التكلفة والخطة:",
        "packages": [
            {"id": "pkg_lay_bot_custom", "name": "استشارة وبرمجة نظام أتمتة مخصص", "price": "90.00$", "price_val": 90.0},
        ],
    },
}

PAYMENT_METHODS = [
    {"id": "pay_wallet", "name": "📱 محفظة إلكترونية (CliQ / فودافون كاش / زين كاش / STC Pay)"},
    {"id": "pay_crypto", "name": "💎 عملات رقمية (USDT - TRC20 / Binance Pay)"},
    {"id": "pay_bank", "name": "🏦 تحويل بنكي مباشر"},
    {"id": "pay_card", "name": "💳 بطاقة فيزا / ماستر كارد / بايبال"},
]
