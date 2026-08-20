from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiohttp import ClientResponseError
from tg_bot.services.api_client import backend_client
from tg_bot.utils.notification import render_notifications_keyboard
from tg_bot.keyboards.inline.settings import get_settings_keyboard
from tg_bot.states.notification import NotificationStates
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "notifications_menu")
async def show_notifications_menu(callback, state):
    """
    Показать меню уведомлений
    """
    try:
        await state.set_state(NotificationStates.main)
        
        settings = await backend_client.get_notifications(callback.from_user.id)
        if not settings:
            await callback.message.edit_text("❌ Не удалось загрузить настройки.")
            await callback.answer()
            return
        
        await render_notifications_keyboard(
            callback,
            state,
            settings.get("enabled_sessions", []),
            settings.get("enabled_reminders", [])
        )
        await callback.answer()
    except ClientResponseError as e:
        if e.status == 404:
            await callback.message.edit_text("Пользователь не найден. Пожалуйста, перезапустите бота командой /start.")
        else:
            logger.error(f"HTTP ошибка при загрузке настроек уведомлений: {e.status}")
            await callback.message.edit_text("Сервис временно недоступен. Попробуйте позже.")
        await callback.answer()
    except Exception as e:
        logger.exception(f"Ошибка при загрузке настроек уведомлений: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте позже.")
        await callback.answer()


@router.callback_query(NotificationStates.main, F.data.startswith("notif:"))
async def handle_notification_action(callback, state):
    """
    Обработать действие в меню уведомлений
    """
    try:
        parts = callback.data.split(":")
        if len(parts) != 4:
            await callback.answer("❌ Некорректные данные.")
            return
        
        _, kind, value, current_state_str  = parts
        current_state = bool(int(current_state_str))
        new_enabled = not current_state

        state_data = await state.get_data()
        enabled_sessions = state_data.get("enabled_sessions", [])
        enabled_reminders = state_data.get("enabled_reminders", [])

        if kind == "session":
            if new_enabled:
                if value not in enabled_sessions:
                    enabled_sessions.append(value)
            else:
                if value in enabled_sessions:
                    enabled_sessions.remove(value)
        else:
            value_int = int(value)
            if new_enabled:
                if value_int not in enabled_reminders:
                    enabled_reminders.append(value_int)
            else:
                if value_int in enabled_reminders:
                    enabled_reminders.remove(value_int)

        result = await backend_client.sync_notifications(
            callback.from_user.id,
            enabled_sessions,
            enabled_reminders
        )

        if result and result.get("success"):
            # Обновляем FSM новыми данными
            await state.update_data(
                enabled_sessions=result["enabled_sessions"],
                enabled_reminders=result["enabled_reminders"]
            )
            # Перерисовываем клавиатуру
            await render_notifications_keyboard(
                callback,
                state,
                result["enabled_sessions"],
                result["enabled_reminders"]
            )
        else:
            await callback.answer("❌ Не удалось обновить настройки.")

        await callback.answer()
    except ClientResponseError as e:
        if e.status == 404:
            await callback.message.edit_text("Пользователь не найден. Перезапустите бота командой /start.")
        else:
            logger.error(f"HTTP ошибка при обновлении уведомлений: {e.status}")
            await callback.message.edit_text("Сервис временно недоступен. Попробуйте позже.")
        await callback.answer()
    except Exception as e:
        logger.exception(f"Ошибка при обновлении уведомлений: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте позже.")
        await callback.answer()


@router.callback_query(F.data == "notif_back")
async def back_to_settings(callback, state):
    """
    Вернуться в меню настроек
    """
    await state.clear()
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\nВыберите параметр для настройки:",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer()

    
@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()