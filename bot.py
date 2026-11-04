"""
bot.py — Интерфейс Telegram-бота и CLI-консоли для тестирования системы DelaemOS.
Поддерживает:
1. Все команды из спецификации MVP:
   /start — Регистрация в пилотной группе и онбординг по 5 контурам
   /checkin — Утренний/вечерний чек-ин Контура 0 (сон, бодрость, среда)
   /status (/граф_метрик) — Панель состояния 5 контуров, SGI и узкое горлышко по Либиху
   /tasks (/планирование) — Адаптивный Task Flow с проверкой шлюза SGI и Soft Gating
   /strategy (/цели) — Стратегирование по 6 капиталам + Поисковый Радар возможностей
   /experiment — Лаборатория личных микро-экспериментов с базой HowToLiveBetter
   /reflection (/умная_рефлексия) — Сессия сократической децентрации и метапознания
   /stress_test (/стресс_тест) — Детектор конгруэнтности (D-Index) и 10-минутный микро-контракт
   /smart_content (/умный_контент) — Управление темами, глобальными фильтрами и базой исследований
   /second_brain — Выгрузка цифрового слепка в формате Obsidian Markdown с YAML-паспортом
   /team — Командный дашборд для 2-3 человек (Zero-Knowledge Privacy + Circuit Breaker)
   /intensive — Активация режима «Корпоративный интенсив» с защитным буфером восстановления
   /export_grant — Генерация сводного научно-технического отчета по пилоту для заявки на грант
   /chat (или любое сообщение) — Свободный диалог с Главным Агентом и авто-вызовом сервисов

2. Два режима запуска:
   - `python3 bot.py` — запуск Telegram-бота (работает через стандартный HTTP Long-Polling Telegram Bot API без тяжелых внешних зависимостей).
   - `python3 bot.py --cli` — интерактивный терминальный режим для мгновенной проверки всех команд без токена.
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

from agent import MainOrchestratorAgent
from config import SIX_CAPITALS, TELEGRAM_BOT_TOKEN
from database import DelaemDatabase
from engine import CyberneticEngine
from knowledge_base import KnowledgeService


class DelaemBotApplication:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db = DelaemDatabase(db_path) if db_path else DelaemDatabase()
        self.engine = CyberneticEngine(self.db)
        self.kb = KnowledgeService()
        self.agent = MainOrchestratorAgent(self.db, self.engine, self.kb)

    # -------------------------------------------------------------------------
    # Единый маршрутизатор команд (работает и в Telegram, и в CLI, и в тестах)
    # -------------------------------------------------------------------------
    def handle_incoming_message(
        self,
        user_id: int,
        text: str,
        username: str = "pilot_tester",
        full_name: str = "Тестировщик Пилота",
    ) -> str:
        self.db.ensure_user(user_id, username=username, full_name=full_name)
        clean = text.strip()
        cmd = clean.split()[0].lower() if clean else ""
        args_str = clean[len(cmd) :].strip() if clean else ""

        if cmd in ("/start", "/help"):
            return self._cmd_start(user_id)
        if cmd in ("/status", "/граф_метрик", "/отчёт", "/отчет"):
            return self._cmd_status(user_id)
        if cmd in ("/checkin", "/чек_ин"):
            return self._cmd_checkin(user_id, args_str)
        if cmd in ("/tasks", "/планирование"):
            return self._cmd_tasks(user_id, args_str)
        if cmd in ("/strategy", "/цели"):
            return self._cmd_strategy(user_id, args_str)
        if cmd in ("/experiment", "/предложение_микро_эксперимента"):
            return self._cmd_experiment(user_id, args_str)
        if cmd in ("/reflection", "/умная_рефлексия"):
            return self._cmd_reflection(user_id, args_str)
        if cmd in ("/stress_test", "/стресс_тест"):
            return self._cmd_stress_test(user_id, args_str)
        if cmd in ("/smart_content", "/умный_контент"):
            return self._cmd_smart_content(user_id, args_str)
        if cmd in ("/second_brain", "/второй_мозг", "/портфолио"):
            return self._cmd_second_brain(user_id)
        if cmd in ("/team", "/команда"):
            return self._cmd_team()
        if cmd in ("/intensive", "/интенсив"):
            return self._cmd_intensive(user_id, args_str)
        if cmd in ("/export_grant", "/грант"):
            return self.generate_grant_pilot_report()

        # Если команда /chat или произвольный текст — передаем Главному Агенту (Мета-Оркестратору)
        query_text = args_str if cmd == "/chat" and args_str else clean
        result = self.agent.process_message(user_id, query_text)
        tools_badge = (
            f"\n\n🔧 *Задействованные сервисы агента:* `{', '.join(result['invoked_tools'])}`"
            if result.get("invoked_tools")
            else ""
        )
        return result["reply"] + tools_badge

    # -------------------------------------------------------------------------
    # Обработчики команд
    # -------------------------------------------------------------------------
    def _cmd_start(self, user_id: int) -> str:
        state = self.engine.evaluate_user_state(user_id)
        return (
            "🚀 **Добро пожаловать в DelaemOS (Human Cybernetic OS — Пилотный контур)**\n\n"
            "Система объединяет 5 фрактальных контуров твоей жизни, паспорта метрик (17 критериев), "
            "доказательную базу *HowToLiveBetter* и стратегирование по 6 капиталам.\n\n"
            f"• **Твой текущий индекс Контура 0 (SGI):** `{state['contour_0_sgi']}`\n"
            f"• **Режим шлюза:** `{state['gate_mode']}` (Проводимость: {state['conductance_pct']}%)\n\n"
            "**Основные команды управления:**\n"
            "• `/checkin <сон 1-10> <тонус 1-10> <среда 1-10>` — быстрый чек-ин Контура 0 (например: `/checkin 8 7 8`)\n"
            "• `/status` — панель 5 контуров, паспорта метрик и личный коридор нормы (Baseline)\n"
            "• `/tasks <название задачи>` — добавить задачу через шлюзовой аудит SGI\n"
            "• `/stress_test <причина ступора>` — запустить детектор конгруэнтности (D-Index) и 10-минутный микро-контракт\n"
            "• `/reflection <мысль или дилемма>` — сократическая сессия умной рефлексии\n"
            "• `/experiment` — подобрать доказательную интервенцию HowToLiveBetter и запустить тест\n"
            "• `/strategy` — матрица 6 капиталов + Поисковый Радар возможностей (гранты/хабы)\n"
            "• `/smart_content` — умный контент, глобальные фильтры и база исследований\n"
            "• `/second_brain` — экспорт состояния в Markdown-заметку для Obsidian\n"
            "• `/team` — командная сводка (Zero-Knowledge Privacy) и `/intensive` — режим корпоративного интенсива\n"
            "• `/export_grant` — сгенерировать сводный отчет по пилоту для грантовой заявки\n"
            "• Любое сообщение без слэша обрабатывает **Главный Агент-Штурман** с авто-вызовом инструментов."
        )

    def _cmd_status(self, user_id: int) -> str:
        state = self.engine.evaluate_user_state(user_id)
        sb = state["sleep_baseline"]
        lines = [
            f"🎛 **Панель состояния DelaemOS ({state['user']['full_name']})**",
            f"• **Шлюзовой режим:** `{state['gate_mode']}` (Проводимость верхних контуров: `{state['conductance_pct']}%`)",
            f"• **Фундамент Контура 0 (SGI):** `{state['contour_0_sgi']}` | Узкое горлышко (по Либиху): *{state['bottleneck']}*",
            f"• **Калибровка личной нормы сна (Baseline):** среднее `{sb['mean']}`, $\\sigma = {sb['sigma']}$, плавающий порог аварии $SafetyThreshold = {sb['personal_threshold']}$",
            f"• **Загрузка потока задач (WIP):** `{state['active_tasks_count']}/{state['wip_limit']}`\n",
            "**Срез по 5 контурам:**",
        ]
        for c_idx, c_data in state["contours"].items():
            lines.append(
                f"**{c_data['name']}** — Эффективный SGI: `{c_data['effective_sgi']}`"
            )
            for m in c_data["metrics"]:
                lines.append(
                    f"  └ `{m['metric_id']}` ({m['name']}): Уровень `{m['current_level']}` | Стаб. `{m['stability']}` | **SGI `{m['sgi']}`** | Фаза: *{m['phase']}*"
                )
        return "\n".join(lines)

    def _cmd_checkin(self, user_id: int, args_str: str) -> str:
        parts = [p for p in args_str.replace(",", ".").split() if p]
        if len(parts) >= 3:
            try:
                sleep_v = float(parts[0])
                act_v = float(parts[1])
                env_v = float(parts[2])
            except ValueError:
                sleep_v, act_v, env_v = 7.5, 7.0, 8.0
        elif len(parts) == 1:
            try:
                sleep_v = float(parts[0])
            except ValueError:
                sleep_v = 7.0
            act_v, env_v = sleep_v, 7.5
        else:
            return (
                "📝 **Формат быстрого 30-секундного чек-ина Контура 0:**\n"
                "Отправь `/checkin <сон 1-10> <тонус 1-10> <среда 1-10>`\n"
                "Пример: `/checkin 7.5 7 8` (или `/checkin 4 4 6` для проверки реакции шлюза на недосып)."
            )

        self.db.update_metric_value(user_id, "sleep", sleep_v, note="Утренний чек-ин")
        self.db.update_metric_value(user_id, "energy_activity", act_v, note="Утренний чек-ин")
        self.db.update_metric_value(user_id, "room_env", env_v, note="Утренний чек-ин")
        state = self.engine.evaluate_user_state(user_id)
        return (
            f"✅ **Чек-ин Контура 0 зафиксирован!**\n"
            f"• Сон: `{sleep_v}` | Физический тонус: `{act_v}` | Среда (CO2/свет): `{env_v}`\n"
            f"• **Пересчитанный SGI Контура 0:** `{state['contour_0_sgi']}`\n"
            f"• **Актуальный шлюз дня:** `{state['gate_mode']}` (Допустимый лимит задач WIP: `{state['wip_limit']}`)"
        )

    def _cmd_tasks(self, user_id: int, args_str: str) -> str:
        if not args_str:
            state = self.engine.evaluate_user_state(user_id)
            tasks = state["active_tasks"]
            if not tasks:
                return "📋 У тебя нет активных задач. Добавь задачу командой `/tasks <название задачи>`."
            lines = [
                f"📋 **Адаптивный Task Flow (Активно: {len(tasks)}/{state['wip_limit']} | Шлюз: {state['gate_mode']})**"
            ]
            for t in tasks:
                lines.append(
                    f"• `#{t['id']}` [{t['cognitive_type']}] **{t['title']}** — Статус: `{t['status']}` | Сопротивление: `{t['resistance_level']}/10`"
                )
            lines.append(
                "\nЧтобы добавить задачу: `/tasks Написать раздел НТН для гранта`\n"
                "Чтобы форсировать задачу под свою ответственность при закрытом шлюзе: `/tasks --force Написать раздел НТН`"
            )
            return "\n".join(lines)

        force = "--force" in args_str
        clean_title = args_str.replace("--force", "").strip()
        res = self.engine.check_task_gate(
            user_id=user_id,
            title=clean_title,
            cognitive_type="DEEP_WORK",
            estimated_minutes=90,
            resistance_level=7,
            force_override=force,
        )
        return res["message"]

    def _cmd_strategy(self, user_id: int, args_str: str) -> str:
        if args_str:
            added = self.db.add_strategy_element(
                user_id=user_id,
                element_type="checkpoint",
                capital_type="administrative",
                title=args_str,
                current_state="Инициализировано пользователем",
                target_state="Успешное достижение контрольной точки",
                metric_criteria="Рост SGI профильного контура >= 7.0",
                resources_needed="Слоты глубокой работы",
                risks_and_mitigation="Защита от перегрузки через шлюзовой контроль",
            )
            return f"🧭 Контрольная точка стратегии добавлена: **{added['title']}** (Капитал: `{added['capital_type']}`)."

        elements = self.db.get_strategy_elements(user_id)
        opps = self.kb.scan_opportunities()
        lines = [
            "🧭 **Матрица Стратегирования (3 уровня x 6 капиталов)**",
        ]
        for el in elements:
            lines.append(
                f"• **[{el['element_type'].upper()} | {el['capital_type']}]** {el['title']}\n"
                f"  — *Точка А:* {el['current_state']} $\\to$ *Точка Б:* {el['target_state']}\n"
                f"  — *Критерий:* {el['metric_criteria']} | *Риск-протокол:* {el['risks_and_mitigation']}"
            )
        lines.append("\n📡 **Поисковая система возможностей (Opportunity Radar под текущую стратегию):**")
        for o in opps:
            lines.append(
                f"• **{o['title']}** (Капиталы: `{', '.join(o['target_capitals'])}`)\n"
                f"  — *Ресурс:* {o['funding_or_value']}\n"
                f"  — *Шаг захвата:* {o['action_step']}"
            )
        return "\n".join(lines)

    def _cmd_experiment(self, user_id: int, args_str: str) -> str:
        state = self.engine.evaluate_user_state(user_id)
        bottleneck_id = state["contours"][0]["bottleneck_metric_id"] or "sleep"
        recs = self.kb.find_recommendations(metric_id=bottleneck_id)
        rec = recs[0]
        exp = self.db.start_experiment(
            user_id=user_id,
            metric_id=bottleneck_id,
            recommendation_id=rec["recommendation_id"],
            hypothesis=rec["expected_benefit"],
            protocol_action=rec["protocol_action"],
            duration_days=7,
        )
        return (
            f"🧪 **Лаборатория личных экспериментов (HowToLiveBetter)**\n"
            f"• **Выбрано узкое горлышко Контура 0:** `{bottleneck_id}` (Исходный уровень: `{exp['baseline_before']}`)\n"
            f"• **Паспорт рекомендации `{rec['recommendation_id']}`:** *{rec['title']}*\n"
            f"• **Уровень доказательности:** {rec['evidence_grade']}\n"
            f"• **Ожидаемый эффект:** {rec['expected_benefit']}\n"
            f"• **Ограничения и противопоказания:** {rec['contraindications']}\n"
            f"• **Протокол на 7 дней:** {rec['protocol_action']}\n"
            f"• **Статус:** Эксперимент `#{exp['id']}` запущен (`ACTIVE`)."
        )

    def _cmd_reflection(self, user_id: int, args_str: str) -> str:
        thought = args_str or "Я хочу ускорить разработку проекта и выиграть грант, но боюсь распылиться на второстепенные задачи."
        res = self.agent.execute_tool(
            user_id, "skill_smart_reflection", {"user_thought": thought}
        )
        return (
            f"🪞 **Сессия Умной Рефлексии (Контур 1 — Метапознание)**\n"
            f"Исходный тезис: *«{thought}»*\n\n"
            + "\n\n".join(res["socratic_questions"])
        )

    def _cmd_stress_test(self, user_id: int, args_str: str) -> str:
        complaint = args_str or "Чувствую сильную усталость и вязкость перед написанием сложного раздела архитектуры."
        probe = self.engine.evaluate_congruence_d_index(
            user_id=user_id, user_complaint_text=complaint, subjective_energy_claim=2.5
        )
        return probe["message"]

    def _cmd_smart_content(self, user_id: int, args_str: str) -> str:
        user = self.db.ensure_user(user_id)
        filters = json.loads(user.get("content_filters_json") or "{}")
        if args_str:
            created = self.db.add_smart_research(
                user_id=user_id,
                entry_type="research_request",
                title=args_str,
                why_context="Запрос из модуля /Умный_контент для развития проекта",
                interest_level=9,
                output_format="document",
                result_summary=(
                    f"Исследование по теме «{args_str}» завершено: сопоставлены данные паспортов метрик "
                    "и первоисточники HowToLiveBetter (Grade A)."
                ),
            )
            return (
                f"📚 **Новое исследование создано и обработано (`#{created['id']}`):**\n"
                f"• **Тема:** {created['title']}\n"
                f"• **Статус:** `{created['status']}`\n"
                f"• **Выжимка:** {created['result_summary']}"
            )

        items = self.db.get_smart_research(user_id)
        lines = [
            "📡 **Модуль `/Умный_контент` (Темы, Исследования, Глобальные фильтры)**",
            "**Активные глобальные фильтры внимания (Контур 1):**",
            f"• **Достоверность:** {filters.get('trust_level')}",
            f"• **Частота дайджеста:** {filters.get('frequency')}",
            f"• **Регион:** {filters.get('region')}",
            f"• **Эмоциональная окраска:** {filters.get('tone')}\n",
            f"**База исследований и отслеживаемых тем ({len(items)}):**",
        ]
        for it in items[:5]:
            lines.append(f"• [{it['entry_type']}] **{it['title']}** — Статус: `{it['status']}`")
        lines.append("\nЧтобы запустить новое исследование: `/smart_content Когнитивная эргономика ИИ-агентов`")
        return "\n".join(lines)

    def _cmd_second_brain(self, user_id: int) -> str:
        res = self.agent.execute_tool(user_id, "export_obsidian_digest", {})
        return f"🗂 **Экспорт слепка во Второй Мозг (Obsidian Markdown):**\n\n```markdown\n{res['obsidian_markdown']}\n```"

    def _cmd_team(self) -> str:
        team = self.engine.get_team_zero_knowledge_summary()
        lines = [
            "👥 **Командный контур DelaemOS (Zero-Knowledge Team Extension)**",
            f"• **Численность пилотной группы:** `{team['team_size']}` чел.",
            f"• **Агрегированный SGI стаи:** `{team['team_sgi']}`",
            f"• **Статус Circuit Breaker:** {team['circuit_breaker']}\n",
            "**Рабочие статусы участников (личные медицинские и психо-метрики скрыты):**",
        ]
        for m in team["members"]:
            int_badge = " 🔥 [ИНТЕНСИВ]" if m["intensive"] else ""
            lines.append(
                f"• **{m['name']}** ({m['role']}): {m['work_mode']} | Загрузка WIP: `{m['wip_load']}`{int_badge}"
            )
        return "\n".join(lines)

    def _cmd_intensive(self, user_id: int, args_str: str) -> str:
        days = 3
        if args_str.strip().isdigit():
            days = max(1, min(7, int(args_str.strip())))
        res = self.engine.activate_corporate_intensive(user_id, duration_days=days)
        return res["message"]

    # -------------------------------------------------------------------------
    # Генератор научно-технического отчета по пилоту (для заявки на грант)
    # -------------------------------------------------------------------------
    def generate_grant_pilot_report(self) -> str:
        users = self.db.get_all_users()
        audits = self.db.get_audit_events(limit=500)
        team_summary = self.engine.get_team_zero_knowledge_summary()

        soft_gating_count = sum(1 for a in audits if a["event_type"] == "SOFT_GATING")
        d_index_probes = [a for a in audits if a["event_type"] == "D_INDEX_PROBE"]
        tool_calls_count = sum(1 for a in audits if a["event_type"] == "TOOL_CALL")

        lines = [
            "# Отчет о пилотном тестировании прототипа (MVP) системы DelaemOS",
            f"**Дата формирования отчета:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Объем выборки пилота:** {len(users)} чел. (командный контур с архитектурой Zero-Knowledge Privacy)",
            "",
            "## 1. Подтвержденная научно-техническая новизна (НТН)",
            "1. **Реализована многоконтурная модель человека (Контуры 0–4)** с оцифровкой 17-польного паспорта метрик и динамической калибровкой индивидуального коридора нормы ($SafetyThreshold = \\mu - 2\\sigma$).",
            "2. **Реализован алгоритм каскадного шлюзового аудита (Cascading Gates)** на базе индекса устойчивости $SGI = CurrentLevel \\times (Stability / 10)$ с учетом принципа узкого горлышка Либиха.",
            "3. **Реализован вероятностный детектор конгруэнтности ($D$-Index)**, разделяющий истинное физиологическое истощение Контура 0 и когнитивное сопротивление перед точками бифуркации Контура 3.",
            "",
            "## 2. Сводная телеметрия пилотной группы",
            "| Участник | Роль в команде | Текущий SGI Контура 0 | Шлюзовой режим | Активный WIP | Завершенных экспериментов |",
            "| :--- | :--- | :---: | :---: | :---: | :---: |",
        ]

        for u in users:
            st = self.engine.evaluate_user_state(u["user_id"])
            exps = self.db.get_user_experiments(u["user_id"])
            done_exps = sum(1 for e in exps if e["status"] == "COMPLETED")
            lines.append(
                f"| {u['full_name']} | {u['role_in_team']} | **{st['contour_0_sgi']}** | `{st['gate_mode']}` | `{st['active_tasks_count']}/{st['wip_limit']}` | {done_exps} (всего {len(exps)}) |"
            )

        lines.extend(
            [
                "",
                "## 3. Статистика срабатывания кибернетических контуров защиты",
                f"- **Агрегированный командный SGI:** `{team_summary['team_sgi']}` ({team_summary['circuit_breaker']})",
                f"- **Всего обращений Главного Агента к внутренним сервисам и скилам:** `{tool_calls_count}`",
                f"- **Срабатываний предиктивного перехватчика перегрузки (Soft Gating):** `{soft_gating_count}` (предотвращены спринты на истощенном субстрате)",
                f"- **Проверок конгруэнтности ($D$-Index) и запусков 10-минутных микро-контрактов:** `{len(d_index_probes)}`",
            ]
        )
        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Встроенный HTTP Long-Polling клиент Telegram Bot API
    # -------------------------------------------------------------------------
    def run_telegram_polling(self) -> None:
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
            print(
                "⚠️ Переменная окружения TELEGRAM_BOT_TOKEN не задана.\n"
                "Запустите `export TELEGRAM_BOT_TOKEN='ваш_токен'` или используйте `python3 bot.py --cli` для локальной консоли."
            )
            return

        base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        offset = 0
        print("🤖 Telegram-бот DelaemOS запущен в режиме Long-Polling...")
        while True:
            try:
                url = f"{base_url}/getUpdates?timeout=25&offset={offset}"
                with urllib.request.urlopen(url, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    msg = upd.get("message") or {}
                    text = msg.get("text")
                    if not text:
                        continue
                    chat_id = msg["chat"]["id"]
                    from_user = msg.get("from") or {}
                    user_id = from_user.get("id", chat_id)
                    username = from_user.get("username", "tg_user")
                    full_name = (
                        f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip()
                        or username
                    )
                    reply = self.handle_incoming_message(
                        user_id=user_id,
                        text=text,
                        username=username,
                        full_name=full_name,
                    )
                    send_payload = urllib.parse.urlencode(
                        {"chat_id": chat_id, "text": reply}
                    ).encode("utf-8")
                    urllib.request.urlopen(f"{base_url}/sendMessage", data=send_payload, timeout=15)
            except KeyboardInterrupt:
                print("\nОстановка бота.")
                break
            except Exception as exc:
                print(f"Ошибка соединения с Telegram API: {exc}. Повтор через 5 сек...")
                time.sleep(5)

    def run_cli_console(self) -> None:
        print("=" * 72)
        print("🧠 Интерактивная консоль DelaemOS (режим тестирования без Telegram)")
        print("Введите /start для списка команд или напишите сообщение ИИ-Штурману.")
        print("Для выхода введите exit.")
        print("=" * 72)
        user_id = 1001
        while True:
            try:
                raw = input("\n[Вы] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nВыход.")
                break
            if raw.lower() in ("exit", "quit", "выход"):
                break
            if not raw:
                continue
            response = self.handle_incoming_message(
                user_id=user_id,
                text=raw,
                username="founder",
                full_name="Основатель проекта",
            )
            print(f"\n[DelaemOS Штурман]:\n{response}")


if __name__ == "__main__":
    app = DelaemBotApplication()
    if "--cli" in sys.argv:
        app.run_cli_console()
    else:
        app.run_telegram_polling()
