import os, random, logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from subjects import subjects_for_grade
from database import init_db, save_student, add_question, eligible_cards, get_test_questions, question_stats
from certificate import make_certificate

BASE = Path(__file__).resolve().parent
os.chdir(BASE)
load_dotenv(BASE / '.env')
TOKEN = os.getenv('BOT_TOKEN', '').strip()
ADMIN_IDS = {int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip().isdigit()}
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
SCHOOL, GRADE, FULL_NAME, SUBJECT = range(4)
A_GRADE, A_SUBJECT, A_CARD, A_TYPE, A_QUESTION, A_OPT1, A_OPT2, A_OPT3, A_OPT4, A_CORRECT = range(10,20)

def admin(uid): return uid in ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text('Assalomu alaykum! Test botiga xush kelibsiz.\nMaktab nomi yoki raqamini kiriting:')
    return SCHOOL

async def school_received(update, context):
    v=update.message.text.strip()
    if len(v)<2:
        await update.message.reply_text('Maktab nomini to‘liqroq kiriting:'); return SCHOOL
    context.user_data['school']=v
    kb=[[str(i) for i in range(1,4)],[str(i) for i in range(4,7)],[str(i) for i in range(7,10)],['10','11']]
    await update.message.reply_text('Sinfingizni tanlang:',reply_markup=ReplyKeyboardMarkup(kb,resize_keyboard=True,one_time_keyboard=True))
    return GRADE

async def grade_received(update, context):
    try: g=int(update.message.text.strip()); assert 1<=g<=11
    except: await update.message.reply_text('1 dan 11 gacha sinfni tanlang.'); return GRADE
    context.user_data['grade']=g
    await update.message.reply_text('F.I.SH. ni kiriting:',reply_markup=ReplyKeyboardRemove()); return FULL_NAME

async def name_received(update, context):
    name=' '.join(update.message.text.split())
    if len(name)<5: await update.message.reply_text('F.I.SH. ni to‘liq kiriting:'); return FULL_NAME
    context.user_data['full_name']=name
    g=context.user_data['grade']; save_student(update.effective_user.id,context.user_data['school'],g,name)
    subjects=subjects_for_grade(g)
    kb=[[InlineKeyboardButton(s,callback_data='sub:'+s)] for s in subjects]
    await update.message.reply_text(f'{g}-sinf uchun fanni tanlang:',reply_markup=InlineKeyboardMarkup(kb)); return SUBJECT

async def subject_selected(update, context):
    q=update.callback_query; await q.answer(); subject=q.data[4:]
    context.user_data['subject']=subject; g=context.user_data['grade']
    cards=eligible_cards(g,subject)
    if not cards:
        await q.message.reply_text(f'{g}-sinf {subject} fanida test savollari hali yetarli emas. Admin /addquestion orqali savollar kiritishi kerak. Har bir karta uchun 18 ta fan va 7 ta IQ savoli kerak.')
        return ConversationHandler.END
    card=random.choice(cards); context.user_data['test']=get_test_questions(g,subject,card); context.user_data['pos']=0; context.user_data['fan']=0; context.user_data['iq']=0
    await q.message.reply_text(f'Test boshlandi! 25 ta savol. Karta: {card}')
    await send_question(q.message.chat_id,context,q.get_bot()); return ConversationHandler.END

async def send_question(chat_id, context, bot):
    test=context.user_data['test']; i=context.user_data['pos']; item=test[i]
    opts=item['options']; kb=[[InlineKeyboardButton(f'{n+1}. {v}',callback_data=f'ans:{i}:{n}')] for n,v in enumerate(opts)]
    await bot.send_message(chat_id,f'{i+1}/25 | {item["qtype"].upper()}\n\n{item["question"]}',reply_markup=InlineKeyboardMarkup(kb))

async def answer(update, context):
    q=update.callback_query; await q.answer()
    try: _,si,oi=q.data.split(':'); i=int(si); chosen=int(oi)
    except: return
    if i != context.user_data.get('pos'): return
    item=context.user_data['test'][i]
    if chosen==item['correct']:
        context.user_data['fan' if item['qtype']=='fan' else 'iq']+=1
    context.user_data['pos']+=1
    if context.user_data['pos']<25:
        await q.edit_message_reply_markup(reply_markup=None)
        await send_question(q.message.chat_id,context,q.get_bot()); return
    fan=context.user_data['fan']; iq=context.user_data['iq']; total=fan+iq
    await q.message.reply_text(f'Test yakunlandi!\nFan: {fan}/18\nIQ: {iq}/7\nJami: {total}/25 ({round(total/25*100)}%)')
    path=BASE/'data'/f'certificate_{q.from_user.id}.pdf'; path.parent.mkdir(exist_ok=True)
    make_certificate(path,context.user_data.get('full_name','O‘quvchi'),context.user_data.get('school',''),context.user_data.get('grade',0),context.user_data.get('subject',''),fan,iq,datetime.now().strftime('%d.%m.%Y'))
    with open(path,'rb') as f: await q.message.reply_document(f,filename='sertifikat.pdf')

async def admin_panel(update, context):
    if not admin(update.effective_user.id): return await update.message.reply_text('Bu buyruq faqat admin uchun.')
    total,grades,cards=question_stats()
    await update.message.reply_text(f'ADMIN PANEL\nSavollar: {total}\nSinflar: {grades}\nKartalar: {cards}\n\n/addquestion — savol qo‘shish\n/stats — statistika')

async def stats(update, context):
    if not admin(update.effective_user.id): return
    total,grades,cards=question_stats(); await update.message.reply_text(f'Jami savol: {total}\nQamrab olingan sinflar: {grades}\nKartalar: {cards}')

async def aq_start(update, context):
    if not admin(update.effective_user.id): await update.message.reply_text('Ruxsat yo‘q.'); return ConversationHandler.END
    await update.message.reply_text('Qaysi sinf? (1–11)'); return A_GRADE
async def aq_grade(update, context):
    try: g=int(update.message.text); assert 1<=g<=11
    except: await update.message.reply_text('1–11 oralig‘ida kiriting.'); return A_GRADE
    context.user_data['ag']=g
    subs=subjects_for_grade(g); await update.message.reply_text('Fan nomini aynan ro‘yxatdan kiriting:\n'+'\n'.join(subs)); return A_SUBJECT
async def aq_subject(update, context):
    s=update.message.text.strip(); g=context.user_data['ag']
    if s not in subjects_for_grade(g): await update.message.reply_text('Fan ro‘yxatda yo‘q. Qayta kiriting.'); return A_SUBJECT
    context.user_data['as']=s; await update.message.reply_text('Karta raqami (1–4):'); return A_CARD
async def aq_card(update, context):
    try: n=int(update.message.text); assert 1<=n<=4
    except: await update.message.reply_text('1–4 kiriting.'); return A_CARD
    context.user_data['ac']=n; await update.message.reply_text('Savol turi: fan yoki iq'); return A_TYPE
async def aq_type(update, context):
    t=update.message.text.strip().lower()
    if t not in ('fan','iq'): await update.message.reply_text('Faqat fan yoki iq.'); return A_TYPE
    context.user_data['at']=t; await update.message.reply_text('Savol matnini yuboring:'); return A_QUESTION
async def aq_question(update, context):
    context.user_data['aq']=update.message.text.strip(); await update.message.reply_text('1-variant:'); return A_OPT1
async def aq_opt1(update, context): context.user_data['o1']=update.message.text.strip(); await update.message.reply_text('2-variant:'); return A_OPT2
async def aq_opt2(update, context): context.user_data['o2']=update.message.text.strip(); await update.message.reply_text('3-variant:'); return A_OPT3
async def aq_opt3(update, context): context.user_data['o3']=update.message.text.strip(); await update.message.reply_text('4-variant:'); return A_OPT4
async def aq_opt4(update, context): context.user_data['o4']=update.message.text.strip(); await update.message.reply_text('To‘g‘ri javob raqami (1–4):'); return A_CORRECT
async def aq_correct(update, context):
    try: c=int(update.message.text)-1; assert 0<=c<=3
    except: await update.message.reply_text('1–4 oralig‘ida kiriting.'); return A_CORRECT
    add_question(context.user_data['ag'],context.user_data['as'],context.user_data['ac'],context.user_data['at'],context.user_data['aq'],[context.user_data[f'o{i}'] for i in range(1,5)],c)
    await update.message.reply_text('Savol bazaga saqlandi! Yana savol uchun /addquestion.'); return ConversationHandler.END
async def cancel(update, context): await update.message.reply_text('Bekor qilindi.'); return ConversationHandler.END

def main():
    if not TOKEN or TOKEN.lower() in ('token','your_bot_token','bu_yerga_token'): raise RuntimeError('.env faylida haqiqiy BOT_TOKEN kiriting.')
    init_db()
    request = HTTPXRequest(connect_timeout=40, read_timeout=40, write_timeout=40, pool_timeout=40)
    get_updates_request = HTTPXRequest(connect_timeout=40, read_timeout=40, write_timeout=40, pool_timeout=40)
    app = (Application.builder()
           .token(TOKEN)
           .request(request)
           .get_updates_request(get_updates_request)
           .build())
    student=ConversationHandler(entry_points=[CommandHandler('start',start)],states={SCHOOL:[MessageHandler(filters.TEXT&~filters.COMMAND,school_received)],GRADE:[MessageHandler(filters.TEXT&~filters.COMMAND,grade_received)],FULL_NAME:[MessageHandler(filters.TEXT&~filters.COMMAND,name_received)],SUBJECT:[CallbackQueryHandler(subject_selected,pattern=r'^sub:')]},fallbacks=[CommandHandler('start',start)])
    admin_conv=ConversationHandler(entry_points=[CommandHandler('addquestion',aq_start)],states={A_GRADE:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_grade)],A_SUBJECT:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_subject)],A_CARD:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_card)],A_TYPE:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_type)],A_QUESTION:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_question)],A_OPT1:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_opt1)],A_OPT2:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_opt2)],A_OPT3:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_opt3)],A_OPT4:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_opt4)],A_CORRECT:[MessageHandler(filters.TEXT&~filters.COMMAND,aq_correct)]},fallbacks=[CommandHandler('cancel',cancel)])
    app.add_handler(student); app.add_handler(admin_conv); app.add_handler(CallbackQueryHandler(answer,pattern=r'^ans:'))
    app.add_handler(CommandHandler('admin',admin_panel)); app.add_handler(CommandHandler('stats',stats)); app.add_handler(CommandHandler('cancel',cancel))
    print('Bot ishga tushdi.'); app.run_polling()
if __name__=='__main__': main()
