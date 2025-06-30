import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")

if not VK_TOKEN:
    raise ValueError("VK_TOKEN не найден в .env файле. Пожалуйста, добавьте его.")

try:
    ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_RAW.split(',') if admin_id.strip()]
except ValueError:
    print("Предупреждение: ADMIN_IDS в .env файле содержит нечисловые значения или некорректно отформатирован. Список администраторов может быть пустым.")
    ADMIN_IDS = []

MAX_MESSAGE_LENGTH = 4096 

STATE_MAIN_MENU = "main_menu"
STATE_ADMIN_PANEL = "admin_panel"
STATE_ADMIN_ADD_CHAR_TAG = "admin_add_char_tag"
STATE_ADMIN_ADD_CHAR_NAME = "admin_add_char_name"
STATE_ADMIN_ADD_CHAR_AGE = "admin_add_char_age"
STATE_ADMIN_ADD_CHAR_GENDER = "admin_add_char_gender"
STATE_ADMIN_ADD_CHAR_FACTION = "admin_add_char_faction"
STATE_ADMIN_ADD_CHAR_APPEARANCE = "admin_add_char_appearance"
STATE_ADMIN_ADD_CHAR_STATS_CER = "admin_add_char_stats_cer" 
STATE_ADMIN_ADD_CHAR_STATS_CEO = "admin_add_char_stats_ceo" 
STATE_ADMIN_ADD_CHAR_STATS_CEC = "admin_add_char_stats_cec" 
STATE_ADMIN_ADD_CHAR_STATS_BS = "admin_add_char_stats_bs"   
STATE_ADMIN_ADD_CHAR_STATS_BD = "admin_add_char_stats_bd"   
STATE_ADMIN_ADD_CHAR_STATS_BSP = "admin_add_char_stats_bsp" 
STATE_ADMIN_ADD_CHAR_STATS_STM = "admin_add_char_stats_stm" 
STATE_ADMIN_ADD_CHAR_STATS_CTM = "admin_add_char_stats_ctm" 
STATE_ADMIN_ADD_CHAR_STATS_TR = "admin_add_char_stats_tr"   
STATE_ADMIN_ADD_CHAR_STATS_TBS = "admin_add_char_stats_tbs" 
STATE_ADMIN_ADD_CHAR_STATS_RCTO = "admin_add_char_stats_rcto" 
STATE_ADMIN_ADD_CHAR_STATS_RCTE = "admin_add_char_stats_rcte" 
STATE_ADMIN_ADD_CHAR_STATS_BFC = "admin_add_char_stats_bfc" 
STATE_ADMIN_ADD_CHAR_STATS_BFL = "admin_add_char_stats_bfl" 
STATE_ADMIN_ADD_CHAR_CURSED_TECHNIQUE = "admin_add_char_cursed_technique"
STATE_ADMIN_ADD_CHAR_EQUIPMENT = "admin_add_char_equipment"

STATE_ADMIN_EDIT_CHOOSE_CHAR = "admin_edit_choose_char"
STATE_ADMIN_EDIT_CHOOSE_ACTION = "admin_edit_choose_action"
STATE_ADMIN_EDIT_FIELD_VALUE = "admin_edit_field_value"
STATE_ADMIN_EDIT_STAT_VALUE = "admin_edit_stat_value"
STATE_ADMIN_EDIT_RP_POINTS = "admin_edit_rp_points"
STATE_ADMIN_EDIT_BALANCE = "admin_edit_balance"
STATE_ADMIN_EDIT_CURSED_TECHNIQUE = "admin_edit_cursed_technique"
STATE_ADMIN_EDIT_EQUIPMENT = "admin_edit_equipment"
STATE_ADMIN_EDIT_LEARNED_TECHNIQUE = "admin_edit_learned_technique"

STATE_ADMIN_VIEW_CHOOSE_CHAR = "admin_view_choose_char" 
STATE_ADMIN_VIEW_CHARACTER = "admin_view_character" 

STATE_USER_CHOOSE_CHARACTER_ACTION = "user_choose_character_action" 
STATE_USER_SPEND_RP_CHOOSE_STAT = "user_spend_rp_choose_stat"
STATE_USER_SPEND_RP_ENTER_AMOUNT = "user_spend_rp_enter_amount"
STATE_USER_SPEND_RP_CONFIRM = "user_spend_rp_confirm"

PENDING_TEXT_CURSED_TECHNIQUE = "cursed_technique"
PENDING_TEXT_EQUIPMENT = "equipment"