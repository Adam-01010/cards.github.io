from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select

from cards_bot.database import async_session
from cards_bot.models import Deck, Card

router = Router()

# --- Состояния FSM ---
class DeckForm(StatesGroup):
    waiting_for_title = State()
    waiting_for_card_deck = State()
    waiting_for_card_text = State()
    waiting_for_study_deck = State()
    studying = State()

# /start
@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "👋 Привет! Я бот для изучения карточек.\n\n"
        "Команды:\n"
        "/newdeck – создать колоду\n"
        "/addcard – добавить карточку\n"
        "/study – изучать слова"
    )

# --- Создание колоды ---
@router.message(Command("newdeck"))
async def new_deck(msg: Message, state: FSMContext):
    await msg.answer("Введите название новой колоды:")
    await state.set_state(DeckForm.waiting_for_title)

@router.message(DeckForm.waiting_for_title, F.text)
async def save_deck_title(msg: Message, state: FSMContext):
    async with async_session() as session:
        deck = Deck(title=msg.text, author_id=msg.from_user.id)
        session.add(deck)
        await session.commit()
    await msg.answer(f"✅ Колода '{msg.text}' создана!")
    await state.clear()

# --- Добавление карточек ---
@router.message(Command("addcard"))
async def add_card(msg: Message, state: FSMContext):
    await msg.answer("Введите название колоды:")
    await state.set_state(DeckForm.waiting_for_card_deck)

@router.message(DeckForm.waiting_for_card_deck, F.text)
async def get_deck(msg: Message, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(select(Deck).where(Deck.title == msg.text))
        deck = result.scalar_one_or_none()
        if not deck:
            await msg.answer("❌ Колода не найдена.")
            await state.clear()
            return
        await state.update_data(deck_id=deck.id)
    await msg.answer("Теперь введите карточку в формате:\n`слово – значение`")
    await state.set_state(DeckForm.waiting_for_card_text)

@router.message(DeckForm.waiting_for_card_text, F.text)
async def save_card(msg: Message, state: FSMContext):
    data = await state.get_data()
    try:
        term, answer = msg.text.split("–", 1)
    except:
        await msg.answer("⚠️ Используй формат: слово – значение")
        return
    async with async_session() as session:
        card = Card(term=term.strip(), answer=answer.strip(), deck_id=data["deck_id"])
        session.add(card)
        await session.commit()
    await msg.answer(f"✅ Добавлено: {term.strip()} → {answer.strip()}")
    await state.clear()

# --- Изучение колоды ---
@router.message(Command("study"))
async def study(msg: Message, state: FSMContext):
    await msg.answer("Введите название колоды для изучения:")
    await state.set_state(DeckForm.waiting_for_study_deck)


@router.message(Command('google'))
async def command_google_handler(message: Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton( 
                    text='Open',
                    web_app=WebAppInfo(url='https://adam-01010.github.io/cards.github.io/'),
                )
            ]
        ]
    )
    await message.answer('Start', reply_markup=markup)


@router.message(DeckForm.waiting_for_study_deck, F.text)
async def start_study(msg: Message, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(select(Deck).where(Deck.title == msg.text))
        deck = result.scalar_one_or_none()
        if not deck:
            await msg.answer("❌ Колода не найдена.")
            await state.clear()
            return
        if not deck.cards:
            await msg.answer("📭 В колоде нет карточек.")
            await state.clear()
            return
        await state.update_data(deck_cards=[{"term": c.term, "answer": c.answer} for c in deck.cards], index=0)
    await send_card(msg, state)

async def send_card(msg: Message, state: FSMContext):
    data = await state.get_data()
    cards = data["deck_cards"]
    index = data["index"]

    if index >= len(cards):
        await msg.answer("✅ Изучение завершено!")
        await state.clear()
        return

    term = cards[index]["term"]

    kb = InlineKeyboardBuilder()
    kb.button(text="Показать ответ 💡", callback_data="show_answer")
    await msg.answer(f"❓ {term}", reply_markup=kb.as_markup())
    await state.set_state(DeckForm.studying)

@router.callback_query(F.data == "show_answer")
async def show_answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data["index"]
    card = data["deck_cards"][index]

    kb = InlineKeyboardBuilder()
    kb.button(text="➡️ Далее", callback_data="next_card")

    await cb.message.edit_text(f"❓ {card['term']}\n💡 Ответ: {card['answer']}", reply_markup=kb.as_markup())

@router.callback_query(F.data == "next_card")
async def next_card(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["index"] += 1
    await state.update_data(index=data["index"])
    await cb.message.delete()
    await send_card(cb.message, state)
