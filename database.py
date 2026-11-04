"""
database.py — Реляционно-графовое хранилище DelaemOS на базе SQLite.
Хранит:
- Профили пользователей и статус команды (Zero-Knowledge Team Extension)
- Паспорта метрик (17 полей шаблона) и временные ряды наблюдений (для расчета личного Baseline)
- Задачи и события с когнитивной маркировкой (DEEP_WORK, SYNC, ROUTINE)
- 3-уровневую стратегию по 6 капиталам (Образ будущего, Контрольные точки, Гипотезы, Риски)
- Лабораторию личных экспериментов (до/после, цена, вывод)
- Темы умного контента и базу исследований
- Журнал аудита решений ИИ-штурмана и срабатываний шлюзов (для грантовой отчетности)
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import DB_PATH, DEFAULT_METRICS_CATALOG, SIX_CAPITALS


class DelaemDatabase:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # 1. Пользователи и участники тестовой группы (2-3 человека)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    role_in_team TEXT DEFAULT 'Участник пилота',
                    intensive_mode INTEGER DEFAULT 0,
                    intensive_recovery_date TEXT DEFAULT NULL,
                    content_filters_json TEXT DEFAULT '{}',
                    created_at TEXT
                )
                """
            )

            # 2. Паспорта метрик (все 17 полей спецификации + маркеры и атомарный шаг)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metric_passports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    metric_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    contour INTEGER NOT NULL,
                    metric_type TEXT NOT NULL,           -- Target / Buffer / Hygiene
                    dependent_on_json TEXT NOT NULL,     -- Граф зависимостей (JSON-список metric_id)
                    experience REAL DEFAULT 0.0,         -- Исторический багаж (-10..10)
                    decay_rate REAL DEFAULT 5.0,         -- Скорость деградации (1..10)
                    impact REAL DEFAULT 80.0,            -- Сила системного влияния (1..100)
                    difficulty REAL DEFAULT 50.0,        -- Инерция и сложность (1..100)
                    safety_threshold REAL DEFAULT 4.5,   -- Красная черта (динамически калибруется)
                    metric_cost TEXT DEFAULT '',         -- Цена изменения
                    current_level REAL DEFAULT 6.5,      -- Текущий уровень (1..10)
                    stability REAL DEFAULT 6.0,          -- Степень укоренения (1..10)
                    phase TEXT DEFAULT 'Stabilization',  -- Exploration / Stabilization / Expansion / Default / Relapse
                    time_needed INTEGER DEFAULT 2,       -- Когорты времени (1..10)
                    ability REAL DEFAULT 7.0,            -- Объективная возможность (1..10)
                    motivation REAL DEFAULT 7.0,         -- Субъективный драйв (1..10)
                    recommendation_id TEXT DEFAULT '',   -- Ссылка на рекомендацию HowToLiveBetter
                    recommendation_impact REAL DEFAULT 75.0,
                    description TEXT DEFAULT '',
                    failure_markers TEXT DEFAULT '',
                    atomic_action TEXT DEFAULT '',
                    updated_at TEXT,
                    UNIQUE(user_id, metric_id)
                )
                """
            )

            # 3. Временные ряды замеров метрик (для расчета личной нормы Baseline и сигмы)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metric_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    metric_id TEXT NOT NULL,
                    value REAL NOT NULL,
                    stability REAL NOT NULL,
                    sgi REAL NOT NULL,
                    source TEXT DEFAULT 'manual_checkin', -- manual_checkin / wearable / agent_inference
                    note TEXT DEFAULT '',
                    recorded_at TEXT NOT NULL
                )
                """
            )

            # 4. Задачи и события (Контур 3 — Адаптивный Task Flow)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    cognitive_type TEXT DEFAULT 'DEEP_WORK', -- DEEP_WORK / SYNC / ROUTINE / RECOVERY
                    resistance_level INTEGER DEFAULT 5,      -- Сопротивление старту (1..10)
                    estimated_minutes INTEGER DEFAULT 60,
                    completion_criteria TEXT DEFAULT '',
                    deadline_stiffness TEXT DEFAULT 'Flex',  -- Hard / Soft / Flex
                    status TEXT DEFAULT 'ACTIVE',            -- ACTIVE / DONE / DEFERRED / SANDBOXED
                    gate_mode_at_creation TEXT DEFAULT 'UNLOCKED',
                    forced_by_user INTEGER DEFAULT 0,        -- 1 если взято под свою ответственность при Soft Gating
                    created_at TEXT NOT NULL,
                    completed_at TEXT DEFAULT NULL
                )
                """
            )

            # 5. Элементы стратегии и 6 капиталов
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS strategy_elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    element_type TEXT NOT NULL, -- future_vision / checkpoint / hypothesis / risk_diagnosis
                    capital_type TEXT NOT NULL, -- administrative / physiological / cultural / economic / social / symbolic
                    title TEXT NOT NULL,
                    current_state TEXT DEFAULT '',
                    target_state TEXT DEFAULT '',
                    metric_criteria TEXT DEFAULT '',
                    resources_needed TEXT DEFAULT '',
                    risks_and_mitigation TEXT DEFAULT '',
                    status TEXT DEFAULT 'ACTIVE',
                    created_at TEXT NOT NULL
                )
                """
            )

            # 6. Лаборатория личных микро-экспериментов
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    metric_id TEXT NOT NULL,
                    recommendation_id TEXT NOT NULL,
                    hypothesis TEXT NOT NULL,
                    protocol_action TEXT NOT NULL,
                    baseline_before REAL NOT NULL,
                    value_after REAL DEFAULT NULL,
                    duration_days INTEGER DEFAULT 7,
                    status TEXT DEFAULT 'ACTIVE', -- ACTIVE / COMPLETED / ABORTED
                    user_feedback TEXT DEFAULT '',
                    started_at TEXT NOT NULL,
                    finished_at TEXT DEFAULT NULL
                )
                """
            )

            # 7. Умный контент и база исследований (/Умный_контент)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS smart_research (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    entry_type TEXT NOT NULL, -- topic / research_request
                    title TEXT NOT NULL,
                    why_context TEXT DEFAULT '',
                    interest_level INTEGER DEFAULT 8,
                    output_format TEXT DEFAULT 'message', -- document / table / message
                    status TEXT DEFAULT 'READY',          -- PENDING / READY
                    result_summary TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )

            # 8. Журнал аудита и телеметрии (для проверки гипотез и выгрузки в грант)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL, -- GATE_CHECK / SOFT_GATING / D_INDEX_PROBE / TEN_MIN_CONTRACT / TOOL_CALL
                    contour_0_sgi REAL,
                    gate_mode TEXT,
                    d_index REAL DEFAULT 0.0,
                    payload_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    # -------------------------------------------------------------------------
    # Управление пользователями и инициализация паспортов
    # -------------------------------------------------------------------------
    def ensure_user(
        self,
        user_id: int,
        username: str = "pilot_user",
        full_name: str = "Участник Пилота",
        role_in_team: str = "Исследователь",
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                default_filters = json.dumps(
                    {
                        "trust_level": "Официальные и проверенные научные источники",
                        "frequency": "Раз в 3 дня",
                        "region": "РФ / Глобальный",
                        "tone": "Выжимка в строгом аналитическом стиле",
                    },
                    ensure_ascii=False,
                )
                cursor.execute(
                    """
                    INSERT INTO users (user_id, username, full_name, role_in_team, content_filters_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, username, full_name, role_in_team, default_filters, now),
                )
                conn.commit()
                self._seed_default_metrics(user_id, conn)
                self._seed_default_strategy(user_id, conn)
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
            return dict(row)

    def _seed_default_metrics(self, user_id: int, conn: sqlite3.Connection) -> None:
        now = datetime.utcnow().isoformat()
        cursor = conn.cursor()
        for m in DEFAULT_METRICS_CATALOG:
            cursor.execute(
                """
                INSERT OR IGNORE INTO metric_passports (
                    user_id, metric_id, name, contour, metric_type, dependent_on_json,
                    experience, decay_rate, impact, difficulty, safety_threshold,
                    metric_cost, current_level, stability, phase, time_needed,
                    ability, motivation, recommendation_id, recommendation_impact,
                    description, failure_markers, atomic_action, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    m["metric_id"],
                    m["name"],
                    m["contour"],
                    m["metric_type"],
                    json.dumps(m["dependent_on"], ensure_ascii=False),
                    m["experience"],
                    m["decay_rate"],
                    m["impact"],
                    m["difficulty"],
                    m["safety_threshold"],
                    m["metric_cost"],
                    m["current_level"],
                    m["stability"],
                    m["phase"],
                    m["time_needed"],
                    m["ability"],
                    m["motivation"],
                    m["recommendation_id"],
                    m["recommendation_impact"],
                    m["description"],
                    m["failure_markers"],
                    m["atomic_action"],
                    now,
                ),
            )
            sgi = round(m["current_level"] * (m["stability"] / 10.0), 2)
            cursor.execute(
                """
                INSERT INTO metric_history (user_id, metric_id, value, stability, sgi, source, note, recorded_at)
                VALUES (?, ?, ?, ?, ?, 'initial_seed', 'Калибровка стартового паспорта', ?)
                """,
                (user_id, m["metric_id"], m["current_level"], m["stability"], sgi, now),
            )
        conn.commit()

    def _seed_default_strategy(self, user_id: int, conn: sqlite3.Connection) -> None:
        now = datetime.utcnow().isoformat()
        cursor = conn.cursor()
        starter_elements = [
            (
                "future_vision",
                "administrative",
                "Выигрыш гранта и запуск ядра DelaemOS",
                "Прототип на стадии тестирования (TRL 4)",
                "Успешная защита заявки, грантовое финансирование и работающий пилот на команде",
                "Завершенный 14-дневный пилот + подтвержденная динамика SGI",
                "Фокусные слоты DEEP_WORK без выгорания Контура 0",
                "Риск перегрузки перед дедлайном -> Митигация через Soft Gating и 10-минутные контракты",
            ),
            (
                "checkpoint",
                "physiological",
                "Удержание Контура 0 в коридоре SGI >= 6.2 на протяжении пилота",
                "Периодические просадки сна при вечерних спринтах",
                "Стабильный сон >= 7.5ч и отсутствие аварийных блокировок LOCKED",
                "0 срывов ниже личного SafetyThreshold за 14 дней",
                "Вечерний чек-ин и гигиена света за 90 минут до сна",
                "Поздние созвоны -> Перенос синхронизаций на первую половину дня",
            ),
            (
                "hypothesis",
                "symbolic",
                "Гипотеза: демонстрация математического аудита SGI и D-Index повысит оценку НТН в гранте",
                "Концептуальное описание в документе",
                "Живой лог телеметрии 3 тестировщиков с графиками предотвращенных срывов",
                "Наличие >30 записей калибровки и минимум 3 успешных микро-экспериментов",
                "Ежедневный чек-ин команды в Telegram-боте",
                "Пропуск чек-инов -> Автоматическое напоминание и 40-секундный кнопочный ввод",
            ),
        ]
        for el in starter_elements:
            cursor.execute(
                """
                INSERT INTO strategy_elements (
                    user_id, element_type, capital_type, title,
                    current_state, target_state, metric_criteria,
                    resources_needed, risks_and_mitigation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, *el, now),
            )
        conn.commit()

    # -------------------------------------------------------------------------
    # Работа с метриками и историей
    # -------------------------------------------------------------------------
    def get_user_metrics(self, user_id: int, contour: Optional[int] = None) -> List[Dict[str, Any]]:
        self.ensure_user(user_id)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if contour is not None:
                cursor.execute(
                    "SELECT * FROM metric_passports WHERE user_id = ? AND contour = ? ORDER BY impact DESC",
                    (user_id, contour),
                )
            else:
                cursor.execute(
                    "SELECT * FROM metric_passports WHERE user_id = ? ORDER BY contour ASC, impact DESC",
                    (user_id,),
                )
            rows = [dict(r) for r in cursor.fetchall()]
            for r in rows:
                r["dependent_on"] = json.loads(r.get("dependent_on_json") or "[]")
                r["sgi"] = round(r["current_level"] * (r["stability"] / 10.0), 2)
            return rows

    def get_metric(self, user_id: int, metric_id: str) -> Optional[Dict[str, Any]]:
        self.ensure_user(user_id)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM metric_passports WHERE user_id = ? AND metric_id = ?",
                (user_id, metric_id),
            )
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["dependent_on"] = json.loads(d.get("dependent_on_json") or "[]")
            d["sgi"] = round(d["current_level"] * (d["stability"] / 10.0), 2)
            return d

    def update_metric_value(
        self,
        user_id: int,
        metric_id: str,
        current_level: float,
        stability: Optional[float] = None,
        source: str = "manual_checkin",
        note: str = "",
        timestamp_override: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        metric = self.get_metric(user_id, metric_id)
        if not metric:
            return None

        lvl = max(1.0, min(10.0, float(current_level)))
        stab = (
            max(1.0, min(10.0, float(stability)))
            if stability is not None
            else float(metric["stability"])
        )
        # Автоматическая адаптация фазы жизненного цикла метрики
        if lvl < metric["safety_threshold"]:
            phase = "Relapse"
        elif stab >= 8.0 and lvl >= 7.5:
            phase = "Default"
        elif stab >= 6.5 and lvl >= 6.5:
            phase = "Expansion"
        elif lvl >= 5.5:
            phase = "Stabilization"
        else:
            phase = "Exploration"

        sgi = round(lvl * (stab / 10.0), 2)
        now = timestamp_override or datetime.utcnow().isoformat()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE metric_passports
                SET current_level = ?, stability = ?, phase = ?, updated_at = ?
                WHERE user_id = ? AND metric_id = ?
                """,
                (lvl, stab, phase, now, user_id, metric_id),
            )
            cursor.execute(
                """
                INSERT INTO metric_history (user_id, metric_id, value, stability, sgi, source, note, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, metric_id, lvl, stab, sgi, source, note, now),
            )
            conn.commit()
        return self.get_metric(user_id, metric_id)

    def get_metric_history(
        self, user_id: int, metric_id: str, limit: int = 30
    ) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM metric_history
                WHERE user_id = ? AND metric_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (user_id, metric_id, limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Задачи (Task Flow)
    # -------------------------------------------------------------------------
    def get_active_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tasks
                WHERE user_id = ? AND status IN ('ACTIVE', 'SANDBOXED')
                ORDER BY id ASC
                """,
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]

    def create_task(
        self,
        user_id: int,
        title: str,
        cognitive_type: str = "DEEP_WORK",
        resistance_level: int = 5,
        estimated_minutes: int = 60,
        completion_criteria: str = "Готовый проверенный артефакт",
        deadline_stiffness: str = "Flex",
        status: str = "ACTIVE",
        gate_mode_at_creation: str = "UNLOCKED",
        forced_by_user: int = 0,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (
                    user_id, title, cognitive_type, resistance_level,
                    estimated_minutes, completion_criteria, deadline_stiffness,
                    status, gate_mode_at_creation, forced_by_user, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    title,
                    cognitive_type,
                    resistance_level,
                    estimated_minutes,
                    completion_criteria,
                    deadline_stiffness,
                    status,
                    gate_mode_at_creation,
                    forced_by_user,
                    now,
                ),
            )
            task_id = cursor.lastrowid
            conn.commit()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            return dict(cursor.fetchone())

    def complete_task(self, user_id: int, task_id: int) -> bool:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = 'DONE', completed_at = ? WHERE id = ? AND user_id = ?",
                (now, task_id, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    # -------------------------------------------------------------------------
    # Стратегирование и 6 капиталов
    # -------------------------------------------------------------------------
    def get_strategy_elements(self, user_id: int) -> List[Dict[str, Any]]:
        self.ensure_user(user_id)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM strategy_elements WHERE user_id = ? ORDER BY id ASC",
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]

    def add_strategy_element(
        self,
        user_id: int,
        element_type: str,
        capital_type: str,
        title: str,
        current_state: str,
        target_state: str,
        metric_criteria: str,
        resources_needed: str,
        risks_and_mitigation: str,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        if capital_type not in SIX_CAPITALS:
            capital_type = "administrative"
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO strategy_elements (
                    user_id, element_type, capital_type, title,
                    current_state, target_state, metric_criteria,
                    resources_needed, risks_and_mitigation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    element_type,
                    capital_type,
                    title,
                    current_state,
                    target_state,
                    metric_criteria,
                    resources_needed,
                    risks_and_mitigation,
                    now,
                ),
            )
            el_id = cursor.lastrowid
            conn.commit()
            cursor.execute("SELECT * FROM strategy_elements WHERE id = ?", (el_id,))
            return dict(cursor.fetchone())

    # -------------------------------------------------------------------------
    # Личные эксперименты (HowToLiveBetter)
    # -------------------------------------------------------------------------
    def start_experiment(
        self,
        user_id: int,
        metric_id: str,
        recommendation_id: str,
        hypothesis: str,
        protocol_action: str,
        duration_days: int = 7,
    ) -> Dict[str, Any]:
        metric = self.get_metric(user_id, metric_id)
        baseline_before = metric["current_level"] if metric else 5.0
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO experiments (
                    user_id, metric_id, recommendation_id, hypothesis,
                    protocol_action, baseline_before, duration_days, status, started_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (
                    user_id,
                    metric_id,
                    recommendation_id,
                    hypothesis,
                    protocol_action,
                    baseline_before,
                    duration_days,
                    now,
                ),
            )
            exp_id = cursor.lastrowid
            conn.commit()
            cursor.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
            return dict(cursor.fetchone())

    def finish_experiment(
        self, user_id: int, exp_id: int, value_after: float, user_feedback: str
    ) -> Optional[Dict[str, Any]]:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE experiments
                SET value_after = ?, status = 'COMPLETED', user_feedback = ?, finished_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (value_after, user_feedback, now, exp_id, user_id),
            )
            conn.commit()
            cursor.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_experiments(self, user_id: int) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM experiments WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Умный контент и исследования
    # -------------------------------------------------------------------------
    def add_smart_research(
        self,
        user_id: int,
        entry_type: str,
        title: str,
        why_context: str,
        interest_level: int = 8,
        output_format: str = "message",
        result_summary: str = "",
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        status = "READY" if result_summary else "PENDING"
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO smart_research (
                    user_id, entry_type, title, why_context,
                    interest_level, output_format, status, result_summary, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    entry_type,
                    title,
                    why_context,
                    interest_level,
                    output_format,
                    status,
                    result_summary,
                    now,
                ),
            )
            item_id = cursor.lastrowid
            conn.commit()
            cursor.execute("SELECT * FROM smart_research WHERE id = ?", (item_id,))
            return dict(cursor.fetchone())

    def get_smart_research(self, user_id: int) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM smart_research WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Командный режим и Интенсивы
    # -------------------------------------------------------------------------
    def set_intensive_mode(
        self, user_id: int, enabled: bool, recovery_date: Optional[str] = None
    ) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET intensive_mode = ?, intensive_recovery_date = ?
                WHERE user_id = ?
                """,
                (1 if enabled else 0, recovery_date, user_id),
            )
            conn.commit()

    def get_all_users(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY user_id ASC")
            return [dict(r) for r in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Аудит событий (для грантовой аналитики)
    # -------------------------------------------------------------------------
    def log_audit_event(
        self,
        user_id: int,
        event_type: str,
        contour_0_sgi: float,
        gate_mode: str,
        d_index: float = 0.0,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_events (user_id, event_type, contour_0_sgi, gate_mode, d_index, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    event_type,
                    contour_0_sgi,
                    gate_mode,
                    d_index,
                    json.dumps(payload or {}, ensure_ascii=False),
                    now,
                ),
            )
            conn.commit()

    def get_audit_events(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,))
            rows = [dict(r) for r in cursor.fetchall()]
            for r in rows:
                r["payload"] = json.loads(r.get("payload_json") or "{}")
            return rows
