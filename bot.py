from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio, logging
from config import token

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()

CATEGORIES = {
    'Автозапчасти': {
        'Аккумулятор': 5000,
        'Фильтр масла': 800,
        'Шины': 7000
    },
    'Мобильные запчасти': {
        'Экран': 3000,
        'Аккумулятор': 1200,
        'Чехол': 500
    }
}

orders = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    for category in CATEGORIES.keys():
        builder.button(text=category, callback_data=f"category_{category}")
    builder.adjust(1)

    await message.answer(
        "Добро пожаловать в онлайн-магазин! Выберите категорию товаров:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    products = CATEGORIES[category]

    builder = InlineKeyboardBuilder()
    for product, price in products.items():
        builder.button(text=f"{product} - {price} сом", callback_data=f"product_{category}_{product}")
    builder.adjust(1)

    await callback.message.answer(
        f"Категория: {category}. Выберите товар:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("product_"))
async def confirm_product(callback: types.CallbackQuery):
    _, category, product = callback.data.split("_")
    price = CATEGORIES[category][product]

    orders[callback.from_user.id] = {"category": category, "product": product, "price": price}

    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить заказ", callback_data="confirm_order")
    builder.button(text="Отмена", callback_data="cancel_order")
    builder.adjust(1)

    await callback.message.answer(
        f"Вы выбрали: {product} из категории {category}. Цена: {price} сом.\nПодтвердите заказ?",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in orders:
        order = orders[user_id]
        category, product, price = order["category"], order["product"], order["price"]
        del orders[user_id]

        await callback.message.answer(
            f"Ваш заказ подтверждён!\nКатегория: {category}\nТовар: {product}\nЦена: {price} сом.\nСпасибо за покупку!"
        )

@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in orders:
        del orders[user_id]
        await callback.message.answer("Ваш заказ отменён.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
