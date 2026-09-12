import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# ضبط ترميز UTF-8 لويندوز
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import database
from catalog import CATEGORIES, SERVICES, PAYMENT_METHODS

# إعداد السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("MZ_Store_Bot")

# تحميل المتغيرات
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(ENV_FILE)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8814482309:AAFj_EMkmi5aRAkOAvm4tSjQvN_3QYZqQMU")
ORDERS_GROUP_ID = os.getenv("ORDERS_GROUP_ID", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")


def update_env_group_id(group_id: str) -> None:
    """حفظ معرف المجموعة في ملف .env"""
    try:
        lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        found = False
        new_lines = []
        for line in lines:
            if line.startswith("ORDERS_GROUP_ID="):
                new_lines.append(f"ORDERS_GROUP_ID={group_id}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"ORDERS_GROUP_ID={group_id}\n")
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        logger.warning(f"تعذر تحديث ORDERS_GROUP_ID في .env: {e}")


# سيرفر فحص الصحة السحابي للاستضافات المجانية
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"MZ Store Telegram Bot is Running 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def start_health_check_server() -> None:
    """تشغيل خادم ويب خفيف في الخلفية لضمان عمل البوت على السيرفرات السحابية"""
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"سيرفر فحص الصحة لمتجر MZ يعمل على المنفذ {port}")
    except Exception as e:
        logger.warning(f"تعذر تشغيل سيرفر فحص الصحة على المنفذ {port}: {e}")


# حالات المحادثة
STATE_INPUT_DELIVERY, STATE_SELECT_PAYMENT, STATE_CONFIRM_ORDER = range(3)
STATE_TRACK_INPUT = 10
STATE_SEARCH_INPUT = 20


# دالة مساعدة لتعديل الرسائل بأمان
async def safe_edit_message(
    query,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: str = "Markdown",
) -> None:
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            logger.warning(f"تعذر تعديل الرسالة: {e}")
            try:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception:
                pass


# -------------------------------------------------------------
# 1. لوحات الأزرار والقوائم (Keyboards)
# -------------------------------------------------------------

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """القائمة الرئيسية لمتجر MZ للخدمات الرقمية"""
    keyboard = [
        [
            InlineKeyboardButton("🛍️ تصفح الكتالوج والأقسام الرقمية (150+ خدمة)", callback_data="menu_catalog"),
        ],
        [
            InlineKeyboardButton("🔎 بحث سريع عن خدمة أو تطبيق", callback_data="menu_search"),
            InlineKeyboardButton("🔍 متابعة حالة طلبي", callback_data="menu_track"),
        ],
        [
            InlineKeyboardButton("🎟️ كود خصم 10% ترحيبي", callback_data="menu_promo"),
            InlineKeyboardButton("💳 طرق الدفع المعتمدة", callback_data="menu_payment_info"),
        ],
        [
            InlineKeyboardButton("📦 سجل طلباتي", callback_data="menu_my_orders"),
            InlineKeyboardButton("💬 الدعم الفني وخدمة العملاء", callback_data="menu_support"),
        ],
        [
            InlineKeyboardButton("🍋 عن ليمونة تيك وماركت هب", callback_data="menu_about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """زر العودة للقائمة الرئيسية"""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")]]
    )


def categories_keyboard() -> InlineKeyboardMarkup:
    """أزرار أقسام متجر MZ"""
    keyboard = [
        [
            InlineKeyboardButton("🎬 اشتراكات الترفيه والبث", callback_data="cat_entertainment"),
            InlineKeyboardButton("🤖 الذكاء الاصطناعي والتصميم", callback_data="cat_ai_design"),
        ],
        [
            InlineKeyboardButton("🎮 شحن الألعاب والبطاقات", callback_data="cat_gaming"),
            InlineKeyboardButton("💻 البرامج والتراخيص الأصلية", callback_data="cat_software"),
        ],
        [
            InlineKeyboardButton("✈️ تيلجرام والسوشيال ميديا", callback_data="cat_social"),
            InlineKeyboardButton("🍋 خدمات ليمونة تيك وماركت هب", callback_data="cat_agency"),
        ],
        [
            InlineKeyboardButton("🔎 بحث سريع عن خدمة أو تطبيق", callback_data="menu_search"),
        ],
        [
            InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def services_in_category_keyboard(cat_id: str, page: int = 0, page_size: int = 6) -> InlineKeyboardMarkup:
    """أزرار الخدمات داخل قسم معين مع دعم التنقل بين الصفحات (Pagination)"""
    cat_services = [
        (srv_id, srv_data)
        for srv_id, srv_data in SERVICES.items()
        if srv_data["category"] == cat_id
    ]

    total_services = len(cat_services)
    total_pages = max(1, (total_services + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))

    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_items = cat_services[start_idx:end_idx]

    keyboard = []
    for srv_id, srv_data in page_items:
        keyboard.append(
            [InlineKeyboardButton(f"{srv_data['icon']} {srv_data['name']}", callback_data=f"view_{srv_id}")]
        )

    # أزرار التنقل بين الصفحات إن كان هناك أكثر من صفحة
    if total_pages > 1:
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{cat_id}_{page - 1}"))
        nav_row.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="ignore_click"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{cat_id}_{page + 1}"))
        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton("🔎 بحث بالاسم", callback_data="menu_search"),
        InlineKeyboardButton("🔙 عودة للأقسام", callback_data="menu_catalog"),
    ])
    return InlineKeyboardMarkup(keyboard)


def service_details_keyboard(srv_id: str, cat_id: str) -> InlineKeyboardMarkup:
    """أزرار باقات الخدمة المختارة للشراء المباشر"""
    keyboard = []
    srv = SERVICES.get(srv_id, {})
    for pkg in srv.get("packages", []):
        btn_text = f"🛒 {pkg['name']} — {pkg['price']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_{srv_id}_{pkg['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقسم", callback_data=cat_id)])
    return InlineKeyboardMarkup(keyboard)


def payment_methods_keyboard() -> InlineKeyboardMarkup:
    """أزرار اختيار طريقة الدفع"""
    keyboard = []
    for pm in PAYMENT_METHODS:
        keyboard.append([InlineKeyboardButton(pm["name"], callback_data=pm["id"])])
    keyboard.append([InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel_order")])
    return InlineKeyboardMarkup(keyboard)


# -------------------------------------------------------------
# 2. معالجات الأوامر الأساسية (Commands)
# -------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """رسالة الترحيب بمتجر MZ للخدمات الرقمية"""
    context.user_data.clear()
    user = update.effective_user

    text = (
        f"👑 **أهلاً بك يا {user.first_name} في متجر MZ للخدمات الرقمية** 🛍️✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🍋 **التابع لشركة ليمونة تيك (Laymouna Tech) ومنصة ماركت هب (Market Hub).**\n\n"
        "🎯 **وجهتك الأولى لأكثر من 150 اشتراك ومنصة رقمية أصلية ومضمونة:**\n"
        "• 🎬 اشتراكات ترفيه (Netflix 4K, Shahid VIP, YouTube Premium, Spotify).\n"
        "• 🤖 أدوات الذكاء الاصطناعي والتصميم (Google Gemini Advanced, ChatGPT Plus, Claude, Midjourney, Canva Pro).\n"
        "• 🎮 شحن شدات ببجي، فري فاير، بطاقات بلايستيشن وستيم بأرخص الأسعار.\n"
        "• 💻 تراخيص Windows الأصلية وحزم Office 365 وشبكات VPN العالمية.\n"
        "• ✈️ تيلجرام بريميوم، خدمات المتابعين، وحلول ليمونة تيك وماركت هب البرمجية.\n\n"
        "🎁 **كود خصم ترحيبي:** استخدم الكود `MZ10` واحصل على خصم 10% على أي طلب!\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 **اختر من القائمة أو استخدم البحث السريع للطلب فوراً:**"
    )

    if update.callback_query:
        try:
            await update.callback_query.answer()
        except Exception:
            pass
        await safe_edit_message(update.callback_query, text, reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر المساعدة ودليل الاستخدام"""
    text = (
        "📖 **دليل استخدام متجر MZ الرقمي (150+ خدمة):**\n\n"
        "• `/start` - القائمة الرئيسية وتصفح الأقسام\n"
        "• `/catalog` - استعراض جميع الخدمات والتطبيقات المتاحة (150+ منصة)\n"
        "• `/search <الاسم>` - البحث الفوري عن أي تطبيق أو اشتراك (مثال: `/search gemini`)\n"
        "• `/track <كود_الطلب>` - الاستعلام عن حالة طلبك\n"
        "• `/support` - التواصل المباشر مع الدعم الفني\n"
        "• `/setgroup` - ربط مجموعة التيلجرام لتلقي إشعارات الطلبات الجديدة (لفريق العمل)\n\n"
        "⚡ جميع الطلبات يتم تسليمها فورياً وبضمان كامل طوال فترة الاشتراك!"
    )
    await update.message.reply_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")


# -------------------------------------------------------------
# 3. مسار الشراء وأخذ الطلب (Order Conversation Flow)
# -------------------------------------------------------------

async def start_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء عملية شراء باقة معينة"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    data = query.data  # buy_{srv_id}_{pkg_id}
    parts = data.split("_")
    # Format: buy_srv_{name}_pkg_{name}
    srv_key = None
    pkg_key = None

    for s_id in SERVICES:
        if data.startswith(f"buy_{s_id}_"):
            srv_key = s_id
            pkg_key = data.replace(f"buy_{s_id}_", "")
            break

    if not srv_key or srv_key not in SERVICES:
        await safe_edit_message(query, "❌ حدث خطأ في اختيار الخدمة، يرجى إعادة المحاولة.", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

    srv = SERVICES[srv_key]
    target_pkg = None
    for p in srv.get("packages", []):
        if p["id"] == pkg_key:
            target_pkg = p
            break

    if not target_pkg:
        target_pkg = srv["packages"][0]

    context.user_data["srv_key"] = srv_key
    context.user_data["srv_name"] = srv["name"]
    context.user_data["pkg_name"] = target_pkg["name"]
    context.user_data["pkg_price"] = target_pkg["price"]
    context.user_data["pkg_val"] = target_pkg["price_val"]

    prompt = srv.get("delivery_prompt", "✍️ يرجى إرسال بريدك الإلكتروني أو رقم هاتفك لتسليم الطلب:")
    text = (
        f"🛒 **طلب شراء: {srv['name']}**\n"
        f"📦 **الباقة:** {target_pkg['name']}\n"
        f"💰 **السعر:** **{target_pkg['price']}**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{prompt}\n\n"
        "*(أرسل البيانات في رسالة نصية أدناه للتسليم السريع)*:"
    )
    cancel_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel_order")]]
    )
    await safe_edit_message(query, text, reply_markup=cancel_kb)
    return STATE_INPUT_DELIVERY


async def input_delivery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """استلام بيانات التسليم والانتقال لاختيار وسيلة الدفع"""
    delivery_info = update.message.text.strip()
    context.user_data["delivery_info"] = delivery_info

    srv_name = context.user_data.get("srv_name", "خدمة رقمية")
    pkg_name = context.user_data.get("pkg_name", "باقة")
    pkg_price = context.user_data.get("pkg_price", "")

    text = (
        f"✅ تم حفظ بيانات التسليم: `{delivery_info}`\n\n"
        f"💳 **يرجى اختيار وسيلة الدفع المناسبة لك لإتمام طلبك:**\n"
        f"• **الطلب:** {srv_name} ({pkg_name})\n"
        f"• **المبلغ المطلوب:** **{pkg_price}**\n\n"
        "اختر وسيلة الدفع من القائمة أدناه:"
    )
    await update.message.reply_text(text, reply_markup=payment_methods_keyboard(), parse_mode="Markdown")
    return STATE_SELECT_PAYMENT


async def select_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة وسيلة الدفع وعرض الفاتورة والتأكيد النهائي"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    data = query.data
    if data == "cancel_order":
        await safe_edit_message(query, "❌ تم إلغاء الطلب.", reply_markup=back_to_main_keyboard())
        context.user_data.clear()
        return ConversationHandler.END

    payment_name = "محفظة إلكترونية / كليك"
    for pm in PAYMENT_METHODS:
        if pm["id"] == data:
            payment_name = pm["name"]
            break

    context.user_data["payment_method"] = payment_name

    srv_name = context.user_data.get("srv_name")
    pkg_name = context.user_data.get("pkg_name")
    pkg_price = context.user_data.get("pkg_price")
    delivery_info = context.user_data.get("delivery_info")

    summary_text = (
        "🧾 **فاتورة وملخص طلب متجر MZ الرقمي:**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🛍️ **الخدمة:** {srv_name}\n"
        f"📦 **الباقة:** {pkg_name}\n"
        f"💵 **القيمة:** **{pkg_price}**\n"
        f"🎁 **كود الخصم:** `MZ10` (مطبق تلقائياً)\n"
        f"📍 **بيانات التسليم:** `{delivery_info}`\n"
        f"💳 **طريقة الدفع:** {payment_name}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "هل تود تأكيد الطلب لإرسال تفاصيل الدفع وبيانات الحساب فوراً؟"
    )
    confirm_kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ نعم، تأكيد وإتمام الطلب", callback_data="confirm_mz_order")],
            [InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel_order")],
        ]
    )
    await safe_edit_message(query, summary_text, reply_markup=confirm_kb)
    return STATE_CONFIRM_ORDER


async def confirm_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """حفظ الطلب في قاعدة البيانات وإرسال التنبيه للمجموعة والعميل"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    data = query.data
    if data == "cancel_order":
        await safe_edit_message(query, "❌ تم إلغاء الطلب.", reply_markup=back_to_main_keyboard())
        context.user_data.clear()
        return ConversationHandler.END

    user = update.effective_user
    srv_name = context.user_data.get("srv_name", "خدمة رقمية")
    pkg_name = context.user_data.get("pkg_name", "باقة")
    pkg_price = context.user_data.get("pkg_price", "")
    delivery_info = context.user_data.get("delivery_info", "غير محدد")
    payment_method = context.user_data.get("payment_method", "غير محدد")

    # حفظ في SQLite
    order_code = database.save_order(
        user_id=user.id,
        user_name=user.username or user.first_name,
        client_name=user.full_name,
        service_name=srv_name,
        package_name=pkg_name,
        price=pkg_price,
        delivery_info=delivery_info,
        payment_method=payment_method,
    )

    # رسالة للعميل
    client_receipt = (
        "🎉 **تم تسجيل طلبك بنجاح في متجر MZ!** 🛍️✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ **كود الطلب الرسمي:** `{order_code}`\n"
        f"📦 **المنتج:** {srv_name} - {pkg_name}\n"
        f"💰 **المبلغ:** {pkg_price}\n"
        f"📍 **بيانات الاستلام:** `{delivery_info}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ **خطوة إتمام الدفع والتسليم:**\n"
        "1. سيتواصل معك فريق التسليم فوراً عبر التيلجرام أو الواتساب لتزويدك بالحساب أو الكود.\n"
        "2. يمكنك الاستعلام عن حالة طلبك في أي وقت بكتابة:\n"
        f"   `/track {order_code}`\n\n"
        "شكراً لتسوقك من متجر MZ برعاية ليمونة تيك وماركت هب 🍋❤️"
    )
    await safe_edit_message(query, client_receipt, reply_markup=back_to_main_keyboard())

    # إرسال إشعار فوري لمجموعة الإدارة
    group_alert = (
        "🚨 **طلب رقمي جديد وصل لمتجر MZ!** 🛒🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ **كود الطلب:** `{order_code}`\n"
        f"👤 **العميل:** {user.full_name} " + (f"(@{user.username})" if user.username else "") + "\n"
        f"🛍️ **الخدمة:** {srv_name}\n"
        f"📦 **الباقة:** {pkg_name} — **{pkg_price}**\n"
        f"📍 **بيانات التسليم:** `{delivery_info}`\n"
        f"💳 **وسيلة الدفع:** {payment_method}\n"
        f"🆔 **معرف تيلجرام:** `{user.id}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔄 **الحالة:** ⏳ قيد التنفيذ والتسليم"
    )

    clean_digits = "".join(ch for ch in delivery_info if ch.isdigit())
    action_btns = []
    if clean_digits and len(clean_digits) >= 8:
        action_btns.append([InlineKeyboardButton("💬 مراسلة واتساب", url=f"https://wa.me/{clean_digits}")])
    if user.username:
        action_btns.append([InlineKeyboardButton("💬 مراسلة العميل تيلجرام", url=f"https://t.me/{user.username}")])
    action_btns.append([InlineKeyboardButton("✅ تم التسليم بنجاح", callback_data=f"mz_done_{order_code}")])

    target_chat = ORDERS_GROUP_ID if ORDERS_GROUP_ID else ADMIN_CHAT_ID
    if target_chat:
        try:
            await context.bot.send_message(
                chat_id=target_chat,
                text=group_alert,
                reply_markup=InlineKeyboardMarkup(action_btns),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"تعذر إرسال الطلب للمجموعة {target_chat}: {e}")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء عملية الشراء بأمان"""
    context.user_data.clear()
    text = "❌ تم إلغاء الطلب. يمكنك تصفح باقي خدمات متجر MZ في أي وقت."
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except Exception:
            pass
        await safe_edit_message(update.callback_query, text, reply_markup=back_to_main_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END


# -------------------------------------------------------------
# 4. محادثة متابعة حالة الطلب (Order Tracking)
# -------------------------------------------------------------

async def start_track_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء محادثة تتبع الطلب"""
    text = (
        "🔍 **متابعة واستعلام حالة طلبك في متجر MZ:**\n\n"
        "يرجى إرسال **كود الطلب** الخاص بك في رسالة نصية:\n"
        "*(مثال: `MZ-1234`)*"
    )
    cancel_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")]]
    )
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except Exception:
            pass
        await safe_edit_message(update.callback_query, text, reply_markup=cancel_kb)
    else:
        await update.message.reply_text(text, reply_markup=cancel_kb, parse_mode="Markdown")
    return STATE_TRACK_INPUT


async def process_track_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة كود الطلب وإرجاع التفاصيل"""
    code_input = update.message.text.strip().upper()
    order = database.get_order_by_code(code_input)

    if not order:
        text = (
            f"❌ عذراً، لم يتم العثور على أي طلب بالكود: `{code_input}`\n\n"
            "يرجى التأكد من كتابة الكود بشكل صحيح أو التواصل مع الدعم."
        )
        retry_kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔄 محاولة أخرى", callback_data="menu_track")],
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")],
            ]
        )
        await update.message.reply_text(text, reply_markup=retry_kb, parse_mode="Markdown")
        return ConversationHandler.END

    text = (
        f"📊 **تفاصيل الطلب: `{order['order_code']}`**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🛍️ **الخدمة:** {order['service_name']}\n"
        f"📦 **الباقة:** {order['package_name']}\n"
        f"💵 **السعر:** {order['price']}\n"
        f"📅 **تاريخ الطلب:** {order['created_at']}\n"
        f"🔄 **الحالة:** 🟢 **{order['status']}**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "إذا واجهتك أي مشكلة، فريق الدعم الفني جاهز لمساعدتك دائماً."
    )
    await update.message.reply_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END


async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر /track المباشر"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ الرجاء كتابة كود الطلب بعد الأمر، مثال:\n`/track MZ-1234`",
            parse_mode="Markdown",
        )
        return

    order_code = context.args[0].strip().upper()
    order = database.get_order_by_code(order_code)
    if not order:
        await update.message.reply_text(f"❌ لا يوجد طلب بالكود `{order_code}`.", parse_mode="Markdown")
        return

    text = (
        f"📊 **تفاصيل الطلب: `{order['order_code']}`**\n"
        f"• **الخدمة:** {order['service_name']} ({order['package_name']})\n"
        f"• **السعر:** {order['price']}\n"
        f"• **الحالة:** 🟢 **{order['status']}**\n"
        f"• **التاريخ:** {order['created_at']}"
    )
    await update.message.reply_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")


# -------------------------------------------------------------
# 5. محادثة والبحث السريع في الكتالوج (Search Services Flow)
# -------------------------------------------------------------

def search_services(query: str, max_results: int = 8):
    """البحث في أكثر من 150 خدمة وتطبيق رقمي بالاسم والوصف والكلمات المفتاحية"""
    query = query.strip().lower()
    if not query:
        return []
    
    results = []
    for srv_id, srv_data in SERVICES.items():
        score = 0
        name = srv_data["name"].lower()
        desc = srv_data["desc"].lower()
        keywords = [k.lower() for k in srv_data.get("keywords", [])]

        if query in name:
            score += 10
        if any(query in kw for kw in keywords):
            score += 5
        if query in desc:
            score += 2

        if score > 0:
            results.append((score, srv_id, srv_data))

    results.sort(key=lambda x: x[0], reverse=True)
    return [item[1:] for item in results[:max_results]]


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء محادثة البحث السريع"""
    text = (
        "🔎 **البحث الفوري في متجر MZ للخدمات الرقمية:**\n\n"
        "أدخل اسم التطبيق، المنصة، أو الخدمة التي تبحث عنها:\n"
        "*(مثال: `Gemini`، `نتفلكس`، `ببجي`، `شاهد`، `ChatGPT`، `Canva`)*"
    )
    cancel_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")]]
    )
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except Exception:
            pass
        await safe_edit_message(update.callback_query, text, reply_markup=cancel_kb)
    else:
        await update.message.reply_text(text, reply_markup=cancel_kb, parse_mode="Markdown")
    return STATE_SEARCH_INPUT


async def process_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة نص البحث وعرض الخدمات المطابقة"""
    search_query = update.message.text.strip()
    matches = search_services(search_query, max_results=8)

    if not matches:
        text = (
            f"🔍 لم نعثر على أي خدمة مطابقة لـ: **{search_query}** 😕\n\n"
            "يمكنك تجربة كتابة اسم التطبيق بالإنجليزية أو تصفح الأقسام الكاملة (150+ منصة)."
        )
        retry_kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔄 بحث عن خدمة أخرى", callback_data="menu_search")],
                [InlineKeyboardButton("🛍️ تصفح كافة الأقسام", callback_data="menu_catalog")],
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")],
            ]
        )
        await update.message.reply_text(text, reply_markup=retry_kb, parse_mode="Markdown")
        return ConversationHandler.END

    text = (
        f"🎯 **نتائج البحث عن:** `{search_query}` ({len(matches)} نتائج):\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "اضغط على أي خدمة أدناه للاطلاع على التفاصيل والأسعار والطلب الفوري:"
    )
    keyboard = []
    for srv_id, srv_data in matches:
        keyboard.append([
            InlineKeyboardButton(f"{srv_data['icon']} {srv_data['name']}", callback_data=f"view_{srv_id}")
        ])
    keyboard.append([
        InlineKeyboardButton("🔎 بحث جديد", callback_data="menu_search"),
        InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu_main"),
    ])

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر /search المباشر"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ الرجاء كتابة اسم الخدمة بعد الأمر، مثال:\n`/search gemini` أو `/search نتفلكس`",
            parse_mode="Markdown",
        )
        return

    query_str = " ".join(context.args).strip()
    matches = search_services(query_str, max_results=8)
    if not matches:
        text = f"🔍 لم نجد أي نتائج لـ: `{query_str}`. جرب كلمة أخرى أو تصفح /catalog."
        await update.message.reply_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
        return

    text = f"🎯 **نتائج البحث عن:** `{query_str}`:"
    keyboard = []
    for srv_id, srv_data in matches:
        keyboard.append([
            InlineKeyboardButton(f"{srv_data['icon']} {srv_data['name']}", callback_data=f"view_{srv_id}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# -------------------------------------------------------------
# 5. معالجات القوائم العامة (Menu Callbacks)
# -------------------------------------------------------------

async def menu_callbacks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة جميع ضغطات الأزرار واستعراض الكتالوج والخدمات"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    data = query.data

    # القائمة الرئيسية
    if data == "menu_main":
        user = update.effective_user
        text = (
            f"👑 **مرحباً بك مجدداً في متجر MZ للخدمات الرقمية** 🛍️\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "اختر من الأقسام والخدمات أدناه:"
        )
        await safe_edit_message(query, text, reply_markup=main_menu_keyboard())

    # استعراض الكتالوج
    elif data == "menu_catalog":
        text = (
            "📂 **أقسام الكتالوج الرقمي لمتجر MZ:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "اختر القسم الذي ترغب في استعراض خدماته وتطبيقاته:"
        )
        await safe_edit_message(query, text, reply_markup=categories_keyboard())

    # استعراض خدمات قسم معين
    elif data in CATEGORIES:
        cat = CATEGORIES[data]
        text = (
            f"{cat['icon']} **{cat['title']}**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{cat['desc']}\n\n"
            "👇 **اختر التطبيق أو الخدمة المطلوبة للاطلاع على الباقات والأسعار:**"
        )
        await safe_edit_message(query, text, reply_markup=services_in_category_keyboard(data, page=0))

    # تقليب صفحات الخدمات داخل القسم (Pagination)
    elif data.startswith("page_"):
        parts = data.split("_")
        # Format: page_{cat_id}_{page_num} -> cat_id has prefix cat_ e.g. cat_entertainment
        # parts: ['page', 'cat', 'entertainment', '1']
        page_num = int(parts[-1])
        cat_id = "_".join(parts[1:-1])
        if cat_id in CATEGORIES:
            cat = CATEGORIES[cat_id]
            text = (
                f"{cat['icon']} **{cat['title']}**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{cat['desc']}\n\n"
                "👇 **اختر التطبيق أو الخدمة المطلوبة للاطلاع على الباقات والأسعار:**"
            )
            await safe_edit_message(query, text, reply_markup=services_in_category_keyboard(cat_id, page=page_num))

    # تجاهل الضغط على مؤشر الصفحة الحالي
    elif data == "ignore_click":
        pass

    # استعراض تفاصيل وباقات خدمة معينة
    elif data.startswith("view_"):
        srv_id = data.replace("view_", "")
        if srv_id in SERVICES:
            srv = SERVICES[srv_id]
            cat_id = srv["category"]
            pkg_text = ""
            for p in srv.get("packages", []):
                pkg_text += f"• **{p['name']}** ⬅️ `{p['price']}`\n"

            text = (
                f"{srv['icon']} **{srv['name']}**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📝 **الوصف والمميزات:**\n{srv['desc']}\n\n"
                f"💰 **الباقات والأسعار المتوفرة:**\n{pkg_text}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👇 **اضغط على الباقة التي تريدها للطلب الفوري:**"
            )
            await safe_edit_message(query, text, reply_markup=service_details_keyboard(srv_id, cat_id))

    # كود الخصم الترحيبي
    elif data == "menu_promo":
        text = (
            "🎟️ **قسيمة خصم ترحيبية خاصة بمتجر MZ** 🎁\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 **كود الخصم:** `MZ10`\n"
            "💎 **القيمة:** **خصم 10%** على أي خدمة أو تطبيق رقمي تطلبه!\n"
            "⏳ **الصلاحية:** متاح لجميع المشتركين والعملاء الجدد.\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **كيفية الاستخدام:**\n"
            "الكود مفعل تلقائياً على حسابك! تصفح الكتالوج واطلب أي باقة وسيطبق الخصم فوراً!"
        )
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛍️ تصفح الخدمات واطلب الآن", callback_data="menu_catalog")],
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")],
            ]
        )
        await safe_edit_message(query, text, reply_markup=kb)

    # معلومات الدفع
    elif data == "menu_payment_info":
        text = (
            "💳 **طرق الدفع المعتمدة لدى متجر MZ:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "نوفر وسائل دفع متعددة ومرنة تناسب جميع الدول:\n\n"
            "1️⃣ **المحافظ الإلكترونية:** (CliQ كليك، فودافون كاش، زين كاش، STC Pay، أمنية).\n"
            "2️⃣ **العملات الرقمية (Crypto):** USDT (TRC-20 / BEP-20) و Binance Pay بدون عمولات.\n"
            "3️⃣ **التحويلات البنكية المباشرة.**\n"
            "4️⃣ **البطاقات البنكية:** فيزا وماستر كارد وباي بال.\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 جميع المعاملات آمنة ومضمونة 100%."
        )
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛍️ ابدأ التسوق الآن", callback_data="menu_catalog")],
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_main")],
            ]
        )
        await safe_edit_message(query, text, reply_markup=kb)

    # طلباتي السابقة
    elif data == "menu_my_orders":
        user = update.effective_user
        orders = database.get_orders_by_user(user.id)
        if orders:
            orders_text = "📦 **سجل طلباتك في متجر MZ:**\n━━━━━━━━━━━━━━━━━━━━\n"
            for o in orders:
                orders_text += f"• `{o['order_code']}` | {o['service_name']} ({o['package_name']})\n  الحالة: 🟢 {o['status']}\n\n"
        else:
            orders_text = "📭 ليس لديك أي طلبات سابقة مسجلة حتى الآن.\nتصفح الكتالوج واختر ما يناسبك!"

        await safe_edit_message(query, orders_text, reply_markup=back_to_main_keyboard())

    # عن الشركة
    elif data == "menu_about":
        text = (
            "🍋 **عن متجر MZ وليمونة تيك وماركت هب:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✨ **متجر MZ** هو الذراع المتخصص في توفير كافة الخدمات والاشتراكات الرقمية والحلول التقنية بأعلى جودة وأفضل سعر في الوطن العربي.\n\n"
            "🏢 **الشركة الأم:** ليمونة تيك (Laymouna Tech) للحلول البرمجية والتقنية.\n"
            "🌐 **المنصة الشريكة:** ماركت هب (Market Hub) لحلول التجارة والأعمال الرقمية.\n\n"
            "🎯 هدفنا: تسهيل وصولك لأحدث أدوات الترفيه والذكاء الاصطناعي والتجارة بضمان وثقة."
        )
        await safe_edit_message(query, text, reply_markup=back_to_main_keyboard())

    # الدعم الفني
    elif data == "menu_support":
        text = (
            "💬 **فريق خدمة العملاء والدعم الفني لمتجر MZ:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "نحن هنا لخدمتك على مدار الساعة للإجابة عن أي استفسار أو متابعة تسليم طلبك.\n\n"
            "• **المعرف المباشر للدعم:** [@MZ_StoreHub_Bot](https://t.me/MZ_StoreHub_Bot)\n"
            "• **سرعة الرد:** خلال دقائق معدودة.\n\n"
            "👇 يمكنك إرسال رسالتك مباشرة هنا في الشات وسيقوم المشرف بالرد عليك فوراً!"
        )
        await safe_edit_message(query, text, reply_markup=back_to_main_keyboard())

    # زر إنجاز الطلب في مجموعة الإدارة
    elif data.startswith("mz_done_"):
        order_code = data.replace("mz_done_", "")
        clicker = update.effective_user
        database.update_order_status(order_code, f"تم التسليم بنجاح ✅ بواسطة {clicker.full_name}")

        orig_text = query.message.text
        lines = orig_text.split("\n")
        new_lines = []
        for line in lines:
            if "الحالة:" in line:
                new_lines.append(f"🔄 **الحالة:** ✅ **تم التسليم بنجاح** (بواسطة {clicker.full_name})")
            else:
                new_lines.append(line)
        updated_text = "\n".join(new_lines)
        await safe_edit_message(query, updated_text)

    return ConversationHandler.END


# -------------------------------------------------------------
# 6. أوامر الإدارة والمجموعات (Admin & Groups)
# -------------------------------------------------------------

async def set_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر /setgroup لربط مجموعة التيلجرام الخاصة بفريق متجر MZ"""
    global ORDERS_GROUP_ID
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "⚠️ يجب استخدام هذا الأمر **داخل مجموعة تيلجرام** الخاصة بفريق عمل متجر MZ!",
            parse_mode="Markdown",
        )
        return

    group_id = str(chat.id)
    ORDERS_GROUP_ID = group_id
    update_env_group_id(group_id)

    text = (
        "🎉 **تم ربط هذه المجموعة بنجاح بمتجر MZ الرقمي!** 🛍️\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏢 **اسم المجموعة:** {chat.title}\n"
        f"🆔 **معرف المجموعة:** `{group_id}`\n\n"
        "⚡ من الآن، سيتم إرسال جميع طلبات العملاء الجديدة والاشتراكات فوراً إلى هذه المجموعة للمتابعة والتسليم السريع!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر /stats لإحصائيات متجر MZ"""
    stats = database.get_stats()
    text = (
        "📊 **إحصائيات وأداء متجر MZ الرقمي** 🛍️\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **إجمالي الطلبات:** `{stats['total_orders']}` طلب\n"
        f"👥 **إجمالي العملاء:** `{stats['total_clients']}` عميل\n"
        f"✅ **طلبات تم تسليمها بنجاح:** `{stats['delivered_orders']}` طلب\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 **حالة السيرفر:** يعمل على مدار الساعة 24/7"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# -------------------------------------------------------------
# 7. الردود الذكية على النصوص (Auto-Replies)
# -------------------------------------------------------------

async def smart_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """الرد على الرسائل التلقائية واستفسارات العملاء"""
    msg = update.message.text.strip().lower()
    user_name = update.effective_user.first_name

    if any(greet in msg for greet in ["السلام عليكم", "سلام", "سلام عليكم"]):
        response = (
            f"وعليكم السلام ورحمة الله وبركاته! أهلاً بك يا {user_name} في **متجر MZ للخدمات الرقمية** 🌸\n"
            "يسعدنا خدمتك بأفضل الاشتراكات والتطبيقات الرقمية الأصلية.\n"
            "اضغط على /start لفتح الكتالوج واستعراض المنتجات."
        )
    elif any(greet in msg for greet in ["مرحبا", "مرحباً", "اهلا", "أهلا", "أهلاً", "هاي", "hello", "hi"]):
        response = (
            f"أهلاً وسهلاً بك يا {user_name}! كيف يمكن لـ **متجر MZ** مساعدتك اليوم؟ 😊\n"
            "تفضل باختيار الخدمة أو الباقة من خلال /start."
        )
    elif any(kw in msg for kw in ["نتفلكس", "شاهد", "يوتيوب", "ببجي", "شدات", "كانفا", "chatgpt"]):
        response = (
            "✨ جميع هذه الاشتراكات والتطبيقات متوفرة فورياً بأرخص الأسعار في متجر MZ!\n"
            "اضغط على /start واختر القسم المطلوب للشراء المباشر والتسليم الفوري."
        )
    elif any(kw in msg for kw in ["دفع", "طرق الدفع", "كليك", "تحويل", "فودافون"]):
        response = (
            "💳 نقبل جميع طرق الدفع: (CliQ كليك، المحافظ الإلكترونية، USDT كريبتو، والتحويلات البنكية).\n"
            "اضغط على /start واختر 'طرق الدفع المعتمدة' للتفاصيل."
        )
    elif any(kw in msg for kw in ["شكرا", "شكراً", "تسلم", "يعطيك العافيه"]):
        response = "العفو دائماً وأبداً! سعداء بخدمتك في متجر MZ 🌹"
    else:
        response = (
            f"أهلاً بك يا {user_name}! وصلتنا رسالتك 👍\n"
            "لتصفح جميع الخدمات والمنتجات الرقمية والطلب الفوري، تفضل بالضغط على:\n👉 /start"
        )

    await update.message.reply_text(response, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("خطأ أثناء معالجة التحديث في بوت MZ:", exc_info=context.error)


# -------------------------------------------------------------
# 8. نقطة الانطلاق الرئيسية (Main)
# -------------------------------------------------------------

def main() -> None:
    """تشغيل بوت متجر MZ للخدمات الرقمية"""
    if not TOKEN or TOKEN == "your_bot_token_here":
        print("[ERROR] لم يتم تعيين TELEGRAM_BOT_TOKEN في ملف .env!")
        return

    print("[INFO] جاري تشغيل بوت متجر MZ للخدمات الرقمية...")

    start_health_check_server()

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    application = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .build()
    )

    # محادثة الشراء والطلب
    order_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_buy_callback, pattern="^buy_.*"),
        ],
        states={
            STATE_INPUT_DELIVERY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_delivery_handler),
                CallbackQueryHandler(cancel_conversation, pattern="^cancel_order$"),
            ],
            STATE_SELECT_PAYMENT: [
                CallbackQueryHandler(select_payment_callback, pattern="^(pay_.*|cancel_order)$"),
            ],
            STATE_CONFIRM_ORDER: [
                CallbackQueryHandler(confirm_order_callback, pattern="^(confirm_mz_order|cancel_order)$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conversation),
            CommandHandler("start", start_command),
            CallbackQueryHandler(cancel_conversation, pattern="^(cancel_order|menu_main)$"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^menu_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^cat_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^view_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^page_.*"),
        ],
        per_chat=True,
        per_user=True,
        per_message=False,
    )

    # محادثة التتبع
    track_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_track_order, pattern="^menu_track$"),
        ],
        states={
            STATE_TRACK_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_track_input),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conversation),
            CommandHandler("start", start_command),
            CallbackQueryHandler(cancel_conversation, pattern="^(cancel_order|menu_main)$"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^menu_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^cat_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^view_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^page_.*"),
        ],
        per_chat=True,
        per_user=True,
        per_message=False,
    )

    # محادثة البحث الفوري
    search_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_search, pattern="^menu_search$"),
        ],
        states={
            STATE_SEARCH_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_search_input),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conversation),
            CommandHandler("start", start_command),
            CallbackQueryHandler(cancel_conversation, pattern="^(cancel_order|menu_main)$"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^menu_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^cat_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^view_.*"),
            CallbackQueryHandler(menu_callbacks_handler, pattern="^page_.*"),
        ],
        per_chat=True,
        per_user=True,
        per_message=False,
    )

    application.add_handler(order_conv)
    application.add_handler(track_conv)
    application.add_handler(search_conv)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("catalog", lambda u, c: menu_callbacks_handler(u, c)))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("track", track_command))
    application.add_handler(CommandHandler("setgroup", set_group_command))
    application.add_handler(CommandHandler("stats", stats_command))

    application.add_handler(CallbackQueryHandler(menu_callbacks_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_text_handler))
    application.add_error_handler(error_handler)

    print("[SUCCESS] تم تشغيل بوت متجر MZ بنجاح!")
    print("[INFO] رابط البوت على تيلجرام: https://t.me/MZ_StoreHub_Bot")

    application.run_polling()


if __name__ == "__main__":
    main()
