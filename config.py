"""
config.py — Конфигурация и онтологические константы системы DelaemOS (MVP).
Определяет 5 контуров, 10 канонических метрик с начальными паспортами (17 полей),
6 капиталов стратегирования, пороги SGI и настройки LLM / Telegram.
"""

import os
from typing import Dict, Any, List

# Настройки подключения (читаются из переменных окружения или .env)
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "8882096522:AAGXcoBHJA36PCotL4oDmJTQu41sBDbm9aE")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "local-server")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:1235/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3.5-4b")

# Путь к локальной БД SQLite
DB_PATH: str = os.getenv("DELAEM_DB_PATH", "delaem_os.db")

# Шлюзовые пороги SGI (Solid Ground Index = CurrentLevel * (Stability / 10))
# Математическая шкала:
# При CurrentLevel = 4.0 и Stability = 6.5 -> SGI = 2.60 (LOCKED — Авария субстрата)
# При CurrentLevel = 6.0 и Stability = 6.5 -> SGI = 3.90 (RESTRICTED — Щадящий режим / Песочница)
# При CurrentLevel = 7.5 и Stability = 7.0 -> SGI = 5.25 (UNLOCKED — Production / Полная проводимость)
SGI_LOCKED_THRESHOLD: float = 3.2      # Ниже 3.2 — Авария (LOCKED): вето на спринты Контура 3
SGI_RESTRICTED_THRESHOLD: float = 4.5  # 3.2..4.5 — Щадящий режим (RESTRICTED / Sandbox)
# Выше 4.5 — Рабочий режим (UNLOCKED / Production)

# Лимиты незавершенного производства (WIP Limits) по режимам шлюза
WIP_LIMITS_BY_GATE: Dict[str, int] = {
    "LOCKED": 1,      # Только 1 восстановительная или микро-рутинная задача
    "RESTRICTED": 2,  # До 2 задач без высокого риска
    "UNLOCKED": 4,    # До 4 параллельных задач (включая DEEP_WORK)
}

# Пять фрактальных контуров системы человека
CONTOURS: Dict[int, Dict[str, str]] = {
    0: {
        "name": "Контур 0: Субстрат и Аппаратная база",
        "question": "В каком состоянии находится организм и поддерживает ли его физическая среда?",
    },
    1: {
        "name": "Контур 1: Психика и Внутренний вычислитель",
        "question": "Как я воспринимаю, рефлексирую, фильтрую внимание и управляю эмоциями?",
    },
    2: {
        "name": "Контур 2: Экзоскелет и Орудия",
        "question": "Какие цифровые инструменты, методологии и второй мозг усиливают меня?",
    },
    3: {
        "name": "Контур 3: Арена и Деятельность",
        "question": "Что я создаю, какова нагрузка, проекты, риск («шкура на кону») и работа в команде?",
    },
    4: {
        "name": "Контур 4: Макросистема и Институты",
        "question": "Какие внешние тренды, правовые рамки и рыночные силы влияют на мои возможности?",
    },
}

# Шесть видов капитала для модуля стратегирования
SIX_CAPITALS: Dict[str, str] = {
    "administrative": "Административный капитал (должность, профессия, твердые навыки, кейсы и полномочия)",
    "physiological": "Физиологический капитал (здоровье, резерв бодрости, выносливость нервной системы)",
    "cultural": "Культурный капитал (насмотренность в науке, технологиях и культуре, системный кругозор)",
    "economic": "Экономический капитал (финансы, активы, подушка безопасности, юнит-экономика)",
    "social": "Социальный капитал (сеть контактов, доверие внутри стаи и сообщества, доступ к людям)",
    "symbolic": "Символический капитал (репутация на рынке, личный бренд, авторитет и статус)",
}

# Канонический стартовый набор метрик (по 17 полям паспорта метрики из спецификации)
DEFAULT_METRICS_CATALOG: List[Dict[str, Any]] = [
    # --- КОНТУР 0 ---
    {
        "metric_id": "sleep",
        "name": "Сон и ночное восстановление",
        "contour": 0,
        "metric_type": "Buffer",
        "dependent_on": ["circadian", "room_env"],
        "experience": 2,
        "decay_rate": 9,
        "impact": 100,
        "difficulty": 50,
        "safety_threshold": 5.0,
        "metric_cost": "Вечернее время (отказ от экранов и поздних задач за 90 минут до сна)",
        "current_level": 7.5,
        "stability": 7.5,
        "phase": "Stabilization",
        "time_needed": 2,
        "ability": 8,
        "motivation": 8,
        "recommendation_id": "REC_SLEEP_01",
        "recommendation_impact": 85,
        "description": "Длительность, непрерывность и субъективная глубина ночного сна.",
        "failure_markers": "Тяжесть при пробуждении, тяга к быстрым углеводам, туман в голове к 14:00",
        "atomic_action": "Убрать телефон из спальни и приглушить верхний свет в 22:30",
    },
    {
        "metric_id": "energy_activity",
        "name": "Физический тонус и движение",
        "contour": 0,
        "metric_type": "Buffer",
        "dependent_on": ["sleep"],
        "experience": 3,
        "decay_rate": 7,
        "impact": 88,
        "difficulty": 45,
        "safety_threshold": 4.5,
        "metric_cost": "40–60 минут дневного времени на разминку и прогулку",
        "current_level": 7.2,
        "stability": 7.0,
        "phase": "Stabilization",
        "time_needed": 2,
        "ability": 8,
        "motivation": 7,
        "recommendation_id": "REC_ACT_01",
        "recommendation_impact": 75,
        "description": "Отсутствие гиподинамии, мышечного зажима и накопленного телесного утомления.",
        "failure_markers": "Боль в шее/пояснице, зевота, ощущение вязкости в теле",
        "atomic_action": "10 минут быстрой ходьбы на свежем воздухе без наушников",
    },
    {
        "metric_id": "room_env",
        "name": "Качество физической среды (CO2, свет, температура)",
        "contour": 0,
        "metric_type": "Hygiene",
        "dependent_on": [],
        "experience": 5,
        "decay_rate": 8,
        "impact": 78,
        "difficulty": 20,
        "safety_threshold": 5.0,
        "metric_cost": "Регулярное проветривание и настройка рабочего освещения",
        "current_level": 7.8,
        "stability": 8.0,
        "phase": "Default",
        "time_needed": 1,
        "ability": 9,
        "motivation": 8,
        "recommendation_id": "REC_ENV_01",
        "recommendation_impact": 80,
        "description": "Уровень свежего воздуха, отсутствие духоты и правильный световой спектр.",
        "failure_markers": "Сонливость в помещении, сухость глаз, снижение скорости чтения",
        "atomic_action": "Открыть окно на сквозное проветривание на 5 минут перед фокус-сессией",
    },
    # --- КОНТУР 1 ---
    {
        "metric_id": "metacognition",
        "name": "Осознанность мышления и рефлексия",
        "contour": 1,
        "metric_type": "Target",
        "dependent_on": ["sleep", "emotional_reg"],
        "experience": 4,
        "decay_rate": 5,
        "impact": 85,
        "difficulty": 65,
        "safety_threshold": 4.0,
        "metric_cost": "15 минут честной письменной рефлексии и когнитивное усилие",
        "current_level": 7.2,
        "stability": 7.0,
        "phase": "Expansion",
        "time_needed": 4,
        "ability": 8,
        "motivation": 9,
        "recommendation_id": "REC_META_01",
        "recommendation_impact": 70,
        "description": "Способность замечать свои когнитивные искажения и смотреть на действия со стороны.",
        "failure_markers": "Туннельное мышление, импульсивные споры, потеря нити главного вопроса",
        "atomic_action": "Записать 3 строчки: «Что я сейчас делаю, зачем и какую гипотезу проверяю?»",
    },
    {
        "metric_id": "emotional_reg",
        "name": "Эмоциональная регуляция и анти-трение",
        "contour": 1,
        "metric_type": "Buffer",
        "dependent_on": ["sleep", "energy_activity"],
        "experience": 1,
        "decay_rate": 7,
        "impact": 90,
        "difficulty": 70,
        "safety_threshold": 4.5,
        "metric_cost": "Отказ от быстрой дофаминовой анестезии (соцсети/скроллинг)",
        "current_level": 7.0,
        "stability": 7.0,
        "phase": "Stabilization",
        "time_needed": 3,
        "ability": 7,
        "motivation": 8,
        "recommendation_id": "REC_EMO_01",
        "recommendation_impact": 78,
        "description": "Способность выдерживать неопределенность и переключаться в рациональный режим без срыва в скроллинг.",
        "failure_markers": "Бесцельное переключение вкладок, раздражительность, откладывание старта задачи",
        "atomic_action": "Сделать 5 циклов физиологического вздоха (двойной вдох + долгий выдох)",
    },
    {
        "metric_id": "attention_filter",
        "name": "Гигиена внимания и фильтрация контента",
        "contour": 1,
        "metric_type": "Hygiene",
        "dependent_on": ["emotional_reg"],
        "experience": 2,
        "decay_rate": 8,
        "impact": 82,
        "difficulty": 55,
        "safety_threshold": 4.0,
        "metric_cost": "Жесткие лимиты на информационный шум и новостные ленты",
        "current_level": 7.0,
        "stability": 6.8,
        "phase": "Stabilization",
        "time_needed": 2,
        "ability": 8,
        "motivation": 7,
        "recommendation_id": "REC_ATT_01",
        "recommendation_impact": 82,
        "description": "Сознательное потребление проверенных источников вместо реактивного скроллинга.",
        "failure_markers": "Чтение новостей с утра в постели, фрагментированный фокус (<15 минут)",
        "atomic_action": "Включить режим «Не беспокоить» и закрыть мессенджеры на время первого рабочего блока",
    },
    # --- КОНТУР 2 ---
    {
        "metric_id": "second_brain",
        "name": "Второй мозг и экзоскелет знаний",
        "contour": 2,
        "metric_type": "Target",
        "dependent_on": ["metacognition"],
        "experience": 5,
        "decay_rate": 3,
        "impact": 76,
        "difficulty": 40,
        "safety_threshold": 3.5,
        "metric_cost": "10 минут в день на упаковку выводов и структурирование заметок",
        "current_level": 7.5,
        "stability": 7.5,
        "phase": "Expansion",
        "time_needed": 3,
        "ability": 9,
        "motivation": 8,
        "recommendation_id": "REC_EXO_01",
        "recommendation_impact": 72,
        "description": "Использование внешней базы заметок, шаблонов и ИИ-инструментов для разгрузки рабочей памяти.",
        "failure_markers": "Потеря важных идей, повторный поиск одних и тех же ссылок, хаос в черновиках",
        "atomic_action": "Зафиксировать главный вывод дня одной заметкой по шаблону",
    },
    # --- КОНТУР 3 ---
    {
        "metric_id": "wip_control",
        "name": "Контроль потока задач и WIP-лимитов",
        "contour": 3,
        "metric_type": "Buffer",
        "dependent_on": ["attention_filter", "second_brain"],
        "experience": 3,
        "decay_rate": 6,
        "impact": 88,
        "difficulty": 50,
        "safety_threshold": 4.5,
        "metric_cost": "Отказ от распыления на новые задачи до закрытия текущих",
        "current_level": 7.2,
        "stability": 7.0,
        "phase": "Stabilization",
        "time_needed": 2,
        "ability": 8,
        "motivation": 8,
        "recommendation_id": "REC_WIP_01",
        "recommendation_impact": 85,
        "description": "Соответствие числа активных задач когнитивной пропускной способности.",
        "failure_markers": "Более 5 открытых задач одновременно, срыв дедлайнов, ощущение белки в колесе",
        "atomic_action": "Выбрать ровно одну задачу типа DEEP_WORK до обеда, остальные перевести в ожидание",
    },
    {
        "metric_id": "skin_in_the_game",
        "name": "Устойчивость к риску («Шкура на кону»)",
        "contour": 3,
        "metric_type": "Target",
        "dependent_on": ["sleep", "emotional_reg", "wip_control"],
        "experience": 4,
        "decay_rate": 4,
        "impact": 92,
        "difficulty": 80,
        "safety_threshold": 4.0,
        "metric_cost": "Психоэмоциональная нагрузка от публичной ответственности и защиты решений",
        "current_level": 7.4,
        "stability": 7.0,
        "phase": "Expansion",
        "time_needed": 5,
        "ability": 7,
        "motivation": 9,
        "recommendation_id": "REC_RISK_01",
        "recommendation_impact": 74,
        "description": "Способность доводить проекты до публичного релиза, подачи на грант и коммерческой оценки без самосаботажа.",
        "failure_markers": "Бесконечный перфекционизм перед релизом, уход в болезнь перед защитой проекта",
        "atomic_action": "Отправить текущий драфт на ревью стейкхолдеру или сооснователю без допиливания мелочей",
    },
    # --- КОНТУР 4 ---
    {
        "metric_id": "macro_alignment",
        "name": "Синхронизация с рынком и институтами",
        "contour": 4,
        "metric_type": "Target",
        "dependent_on": ["skin_in_the_game", "second_brain"],
        "experience": 4,
        "decay_rate": 2,
        "impact": 80,
        "difficulty": 60,
        "safety_threshold": 3.5,
        "metric_cost": "Регулярный мониторинг грантов, правовых рамок и отраслевых хабов",
        "current_level": 7.5,
        "stability": 7.2,
        "phase": "Expansion",
        "time_needed": 6,
        "ability": 8,
        "motivation": 9,
        "recommendation_id": "REC_MACRO_01",
        "recommendation_impact": 70,
        "description": "Понимание правил игры, грантовых программ, юридического контура и трендов отрасли.",
        "failure_markers": "Разработка продукта в вакууме без сверки с требованиями фондов и заказчиков",
        "atomic_action": "Сверить матрицу проекта с критериями оценки целевого грантового конкурса",
    },
]

# Системный промпт Главного Агента (Мета-Оркестратора)
SYSTEM_PROMPT_ORCHESTRATOR: str = """Ты — Главный Агент (Мета-Оркестратор и ИИ-Штурман) кибернетической операционной системы DelaemOS.
Твоя задача — помогать человеку и команде управлять своей жизнью и проектами через 5 фрактальных контуров (от биологии Контура 0 до макросистемы Контура 4) и 6 капиталов стратегии.

ТВОИ АРХИТЕКТУРНЫЕ ЗАКОНЫ:
1. Закон субстратной зависимости и узкого горлышка (Либиха): нельзя требовать от Контура 3 (спринты, дедлайны, риск) ресурса, который не выработан Контуром 0 (сон, тонус, среда).
2. Эпистемическая скромность: никогда не ставь директивных диагнозов («ты ленишься», «это саботаж»). Используй формулу:
   [Наблюдаемый факт в данных] -> [Вероятностная гипотеза с % уверенности] -> [Проверочный вопрос человеку].
3. Информированное согласие (Soft Gating): если SGI Контура 0 пробит (< 4.5), предупреди о росте вероятности ошибок, растяжении сроков и откате по здоровью, и предложи 3 пути: [Взять под свою ответственность] / [Снизить планку до Sandbox] / [Уйти на перезагрузку].
4. Детектор конгруэнтности (D-Index) и Сократический укол: если физиологическая база в норме (сон и SGI высокие), но человек жалуется на «полный ноль сил» перед важной задачей, мягко подсвети зазор между биологией и ощущением и предложи 10-минутный микро-контракт (Tenable Probe).
5. Тональность: «Ассертивный партнер / Тренер высшей лиги» — уважай автономию, говори по делу, опирайся на цифры паспорта метрик и доказательную базу HowToLiveBetter.
"""
