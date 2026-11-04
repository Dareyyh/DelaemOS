"""
agent.py — Главный Агент (Мета-Оркестратор) системы DelaemOS.
Реализует:
1. Реестр инструментов, сервисов и скилов (12 типизированных инструментов в формате OpenAI Function Calling).
2. Диспетчеризацию запросов: агент сам решает, когда обратиться к сервису расчета SGI,
   базе знаний HowToLiveBetter, детектору конгруэнтности D-Index, модулю стратегии или командному статусу.
3. Перехватчик шлюзов (Cascading Gate Interceptor) перед выполнением ресурсоемких действий.
4. Двойной контур исполнения:
   - Внешняя LLM (OpenAI / DeepSeek / совместимый endpoint) при наличии LLM_API_KEY.
   - Автономный кибернетический диспетчер (Built-in Socratic Orchestrator), позволяющий тестировать
     весь цикл инструментов и сократических ответов из коробки без платных ключей.
"""

import json
import urllib.request
from typing import Any, Callable, Dict, List, Optional

from config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    SIX_CAPITALS,
    SYSTEM_PROMPT_ORCHESTRATOR,
)
from database import DelaemDatabase
from engine import CyberneticEngine
from knowledge_base import KnowledgeService


class MainOrchestratorAgent:
    def __init__(
        self,
        db: DelaemDatabase,
        engine: CyberneticEngine,
        kb: KnowledgeService,
    ) -> None:
        self.db = db
        self.engine = engine
        self.kb = kb
        self.tools_schema = self._build_tools_schema()
        self.tool_handlers: Dict[str, Callable[..., Dict[str, Any]]] = {
            "get_current_state": self._tool_get_current_state,
            "update_metric_passport": self._tool_update_metric_passport,
            "check_and_create_task": self._tool_check_and_create_task,
            "run_congruence_d_index_probe": self._tool_run_congruence_d_index_probe,
            "search_howtolivebetter": self._tool_search_howtolivebetter,
            "start_personal_experiment": self._tool_start_personal_experiment,
            "skill_smart_reflection": self._tool_skill_smart_reflection,
            "skill_strategy_6_capitals": self._tool_skill_strategy_6_capitals,
            "scan_opportunity_radar": self._tool_scan_opportunity_radar,
            "manage_smart_content": self._tool_manage_smart_content,
            "get_team_status": self._tool_get_team_status,
            "export_obsidian_digest": self._tool_export_obsidian_digest,
        }

    # -------------------------------------------------------------------------
    # Схема инструментов (OpenAI / MCP Function Calling Format)
    # -------------------------------------------------------------------------
    def _build_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_current_state",
                    "description": "Возвращает состояние 5 контуров человека, индекс SGI, режим шлюза (LOCKED/RESTRICTED/UNLOCKED) и лимит WIP.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_metric_passport",
                    "description": "Обновляет уровень и стабильность метрики в паспорте (например, sleep, energy_activity, room_env, emotional_reg).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric_id": {"type": "string", "description": "ID метрики (sleep, energy_activity, room_env, metacognition, emotional_reg, attention_filter, second_brain, wip_control, skin_in_the_game, macro_alignment)"},
                            "current_level": {"type": "number", "description": "Оценка от 1 до 10"},
                            "stability": {"type": "number", "description": "Устойчивость от 1 до 10 (опционально)"},
                            "note": {"type": "string", "description": "Контекст наблюдения"},
                        },
                        "required": ["metric_id", "current_level"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "check_and_create_task",
                    "description": "Пропускает задачу через шлюзовой аудит (Cascading Gate) и добавляет в адаптивный Task Flow.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Название задачи"},
                            "cognitive_type": {"type": "string", "enum": ["DEEP_WORK", "SYNC", "ROUTINE", "RECOVERY"]},
                            "estimated_minutes": {"type": "integer", "description": "Оценка времени в минутах"},
                            "resistance_level": {"type": "integer", "description": "Уровень сопротивления (1..10)"},
                            "force_override": {"type": "boolean", "description": "Взять под свою ответственность при Soft Gating"},
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "run_congruence_d_index_probe",
                    "description": "Запускает детектор конгруэнтности (D-Index) при жалобах на усталость, вязкость или прокрастинацию.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "complaint_text": {"type": "string", "description": "Жалоба пользователя"},
                            "subjective_energy": {"type": "number", "description": "Субъективная оценка сил от 1 до 10"},
                        },
                        "required": ["complaint_text"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_howtolivebetter",
                    "description": "Ищет доказательные рекомендации в базе HowToLiveBetter с паспортом доказательности и противопоказаний.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric_id": {"type": "string", "description": "Целевая метрика (например, sleep, energy_activity)"},
                            "query": {"type": "string", "description": "Поисковый запрос"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "start_personal_experiment",
                    "description": "Запускает личный эксперимент из базы рекомендаций для проверки гипотезы на 7 дней.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric_id": {"type": "string"},
                            "recommendation_id": {"type": "string"},
                            "duration_days": {"type": "integer"},
                        },
                        "required": ["metric_id", "recommendation_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "skill_smart_reflection",
                    "description": "Генерирует сократическую сессию умной рефлексии и метапознания (Контур 1).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_thought": {"type": "string", "description": "Текущая мысль, дилемма или вопрос пользователя"},
                        },
                        "required": ["user_thought"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "skill_strategy_6_capitals",
                    "description": "Анализирует или добавляет элемент стратегии по 6 человеческим капиталам (Образ будущего, Чекпоинт, Гипотеза).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["view", "add"]},
                            "element_type": {"type": "string", "enum": ["future_vision", "checkpoint", "hypothesis", "risk_diagnosis"]},
                            "capital_type": {"type": "string", "enum": list(SIX_CAPITALS.keys())},
                            "title": {"type": "string"},
                            "target_state": {"type": "string"},
                        },
                        "required": ["action"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "scan_opportunity_radar",
                    "description": "Сканирует внешние возможности (гранты, конкурсы, научные хабы) под дефицитный капитал стратегии.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "capital_filter": {"type": "string", "description": "Капитал (economic, administrative, social, symbolic, cultural)"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_smart_content",
                    "description": "Управляет темами умного контента и запросами на исследование (/Умный_контент).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "enum": ["list", "add_topic", "new_research"]},
                            "title": {"type": "string"},
                            "why_context": {"type": "string"},
                            "interest_level": {"type": "integer"},
                        },
                        "required": ["mode"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_team_status",
                    "description": "Возвращает командную сводку (Zero-Knowledge Team Extension) и статус Circuit Breaker.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "export_obsidian_digest",
                    "description": "Формирует структурированную заметку для Второго мозга (Obsidian Markdown с YAML-паспортом).",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]

    # -------------------------------------------------------------------------
    # Реализация инструментов (Tool Implementations)
    # -------------------------------------------------------------------------
    def _tool_get_current_state(self, user_id: int, **kwargs: Any) -> Dict[str, Any]:
        return self.engine.evaluate_user_state(user_id)

    def _tool_update_metric_passport(
        self,
        user_id: int,
        metric_id: str,
        current_level: float,
        stability: Optional[float] = None,
        note: str = "Обновлено через диалог с агентом",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        updated = self.db.update_metric_value(
            user_id=user_id,
            metric_id=metric_id,
            current_level=current_level,
            stability=stability,
            source="agent_dialogue",
            note=note,
        )
        state = self.engine.evaluate_user_state(user_id)
        return {"updated_metric": updated, "new_contour_0_sgi": state["contour_0_sgi"], "gate_mode": state["gate_mode"]}

    def _tool_check_and_create_task(
        self,
        user_id: int,
        title: str,
        cognitive_type: str = "DEEP_WORK",
        estimated_minutes: int = 60,
        resistance_level: int = 5,
        force_override: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.engine.check_task_gate(
            user_id=user_id,
            title=title,
            cognitive_type=cognitive_type,
            estimated_minutes=estimated_minutes,
            resistance_level=resistance_level,
            force_override=force_override,
        )

    def _tool_run_congruence_d_index_probe(
        self,
        user_id: int,
        complaint_text: str,
        subjective_energy: float = 2.5,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.engine.evaluate_congruence_d_index(
            user_id=user_id,
            user_complaint_text=complaint_text,
            subjective_energy_claim=subjective_energy,
        )

    def _tool_search_howtolivebetter(
        self,
        user_id: int,
        metric_id: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        recs = self.kb.find_recommendations(metric_id=metric_id, query=query)
        return {"recommendations": recs}

    def _tool_start_personal_experiment(
        self,
        user_id: int,
        metric_id: str,
        recommendation_id: str,
        duration_days: int = 7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        recs = self.kb.find_recommendations(metric_id=metric_id)
        rec = next((r for r in recs if r["recommendation_id"] == recommendation_id), recs[0] if recs else None)
        hypothesis = rec["expected_benefit"] if rec else "Повышение уровня и стабильности метрики"
        protocol = rec["protocol_action"] if rec else "Ежедневное выполнение атомарного действия"
        exp = self.db.start_experiment(
            user_id=user_id,
            metric_id=metric_id,
            recommendation_id=recommendation_id,
            hypothesis=hypothesis,
            protocol_action=protocol,
            duration_days=duration_days,
        )
        return {"experiment": exp}

    def _tool_skill_smart_reflection(
        self, user_id: int, user_thought: str, **kwargs: Any
    ) -> Dict[str, Any]:
        state = self.engine.evaluate_user_state(user_id)
        questions = [
            f"1. **Эпистемическая проверка (Контур 1):** Какое неявное убеждение стоит за мыслью «{user_thought[:80]}...» — и какой наблюдаемый факт мог бы его опровергнуть?",
            "2. **Взгляд с 3-й стороны (Децентрация):** Если бы к тебе пришел коллега с точно такой же дилеммой при текущем ресурсе, какой один минимальный шаг ты бы ему предложил?",
            f"3. **Связь с субстратом (SGI = {state['contour_0_sgi']}):** Не продиктована ли эта оценка накопленным утомлением или страхом точки бифуркации («Шкура на кону»)?",
        ]
        return {
            "reflection_mode": "SOCRATIC_METACOGNITION",
            "contour_0_sgi": state["contour_0_sgi"],
            "socratic_questions": questions,
        }

    def _tool_skill_strategy_6_capitals(
        self,
        user_id: int,
        action: str = "view",
        element_type: str = "checkpoint",
        capital_type: str = "administrative",
        title: str = "",
        target_state: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if action == "add" and title:
            added = self.db.add_strategy_element(
                user_id=user_id,
                element_type=element_type,
                capital_type=capital_type,
                title=title,
                current_state="Зафиксировано в диалоге со штурманом",
                target_state=target_state or "Целевое состояние контрольной точки",
                metric_criteria="Устойчивый SGI >= 7.0 по связанным метрикам",
                resources_needed="Фокусные слоты DEEP_WORK",
                risks_and_mitigation="Контроль перегрузки через шлюз Контура 0",
            )
            return {"status": "ADDED", "element": added}
        elements = self.db.get_strategy_elements(user_id)
        return {"status": "VIEW", "elements": elements, "capitals_ontology": SIX_CAPITALS}

    def _tool_scan_opportunity_radar(
        self, user_id: int, capital_filter: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        opps = self.kb.scan_opportunities(capital_filter=capital_filter)
        return {"opportunities": opps}

    def _tool_manage_smart_content(
        self,
        user_id: int,
        mode: str = "list",
        title: str = "",
        why_context: str = "",
        interest_level: int = 8,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if mode in ("add_topic", "new_research") and title:
            entry_type = "topic" if mode == "add_topic" else "research_request"
            summary = (
                f"Аналитическая сводка по теме «{title}»: выделены первоисточники Grade A/B из базы HowToLiveBetter и смежных обзоров."
                if entry_type == "research_request"
                else ""
            )
            created = self.db.add_smart_research(
                user_id=user_id,
                entry_type=entry_type,
                title=title,
                why_context=why_context or "Для усиления проекта и 6 капиталов стратегии",
                interest_level=interest_level,
                result_summary=summary,
            )
            return {"created": created}
        items = self.db.get_smart_research(user_id)
        return {"items": items}

    def _tool_get_team_status(self, user_id: int, **kwargs: Any) -> Dict[str, Any]:
        return self.engine.get_team_zero_knowledge_summary()

    def _tool_export_obsidian_digest(self, user_id: int, **kwargs: Any) -> Dict[str, Any]:
        state = self.engine.evaluate_user_state(user_id)
        tasks = state["active_tasks"]
        exps = self.db.get_user_experiments(user_id)
        md_lines = [
            "---",
            f"system: DelaemOS_SecondBrain",
            f"user_id: {user_id}",
            f"contour_0_sgi: {state['contour_0_sgi']}",
            f"gate_mode: {state['gate_mode']}",
            "tags: [delaem_os, cybernetic_log, second_brain]",
            "---",
            f"# Цифровой слепок состояния ({state['user']['full_name']})",
            f"- **Режим шлюза:** `{state['gate_mode']}` (Проводимость: {state['conductance_pct']}%)",
            f"- **Узкое горлышко Контура 0 (по Либиху):** {state['bottleneck']} (`SGI = {state['contour_0_sgi']}`)",
            "",
            "## Активные задачи (Task Flow)",
        ]
        for t in tasks:
            md_lines.append(f"- [{t['cognitive_type']}] **{t['title']}** (Статус: `{t['status']}`)")
        md_lines.append("\n## Активные личные эксперименты")
        for e in exps[:3]:
            md_lines.append(
                f"- `{e['recommendation_id']}` по метрике `{e['metric_id']}`: старт с `{e['baseline_before']}` -> гипотеза: {e['hypothesis']}"
            )
        return {"obsidian_markdown": "\n".join(md_lines)}

    # -------------------------------------------------------------------------
    # Выполнение инструмента с записью в журнал аудита
    # -------------------------------------------------------------------------
    def execute_tool(
        self, user_id: int, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        handler = self.tool_handlers.get(tool_name)
        if not handler:
            return {"error": f"Инструмент {tool_name} не найден в реестре"}
        result = handler(user_id=user_id, **arguments)
        state = self.engine.evaluate_user_state(user_id)
        self.db.log_audit_event(
            user_id=user_id,
            event_type="TOOL_CALL",
            contour_0_sgi=state["contour_0_sgi"],
            gate_mode=state["gate_mode"],
            payload={"tool_name": tool_name, "arguments": arguments},
        )
        return result

    # -------------------------------------------------------------------------
    # Главная точка входа диалога (/chat и свободные сообщения)
    # -------------------------------------------------------------------------
    def process_message(self, user_id: int, text: str) -> Dict[str, Any]:
        """
        Обрабатывает сообщение пользователя:
        1. Если настроен внешний LLM_API_KEY — выполняет цикл Function Calling к LLM.
        2. Если ключа нет или нужен мгновенный локальный ответ — использует встроенный
           кибернетический диспетчер намерений (Intent & Gate Dispatcher), который
           автоматически вызывает нужные сервисы, скилы и базу знаний.
        """
        self.db.ensure_user(user_id)
        if LLM_API_KEY and LLM_API_KEY != "YOUR_OPENAI_OR_DEEPSEEK_KEY":
            try:
                return self._process_with_external_llm(user_id, text)
            except Exception as exc:
                # Безопасный откат на встроенный кибернетический оркестратор при ошибке сети
                fallback = self._process_with_builtin_orchestrator(user_id, text)
                fallback["note"] = f"Сработал автономный контур оркестратора ({exc})"
                return fallback
        return self._process_with_builtin_orchestrator(user_id, text)

    def _process_with_builtin_orchestrator(
        self, user_id: int, text: str
    ) -> Dict[str, Any]:
        """
        Автономный кибернетический диспетчер: распознает намерение пользователя,
        автоматически вызывает сервисы/скилы/базу знаний и строит ответ по формуле:
        [Наблюдаемый факт] -> [Вероятностная гипотеза] -> [Проверочный вопрос / Действие].
        """
        lower = text.lower()
        invoked_tools: List[str] = []

        # Сценарий 1: Пользователь жалуется на усталость, ступор, нежелание работать или прокрастинацию
        if any(
            w in lower
            for w in [
                "устал",
                "нет сил",
                "не могу начать",
                "вязкость",
                "тяжело",
                "лень",
                "ступор",
                "прокрастин",
                "выгорел",
                "отдохнуть",
            ]
        ):
            probe = self.execute_tool(
                user_id,
                "run_congruence_d_index_probe",
                {"complaint_text": text, "subjective_energy": 2.5},
            )
            invoked_tools.append("run_congruence_d_index_probe")
            return {
                "reply": probe["message"],
                "invoked_tools": invoked_tools,
                "data": probe,
            }

        # Сценарий 2: Пользователь сообщает о сне или самочувствии («спал 5 часов», «сон на 4»)
        if any(w in lower for w in ["спал", "сон", "выспался", "недосып", "бодрость"]):
            # Извлекаем числовую оценку если есть
            nums = [int(s) for s in lower.replace(",", " ").split() if s.isdigit()]
            val = float(nums[0]) if nums and 1 <= nums[0] <= 10 else (4.0 if "недосып" in lower or "плохо" in lower else 7.5)
            upd = self.execute_tool(
                user_id,
                "update_metric_passport",
                {"metric_id": "sleep", "current_level": val, "note": text},
            )
            invoked_tools.append("update_metric_passport")
            recs = self.execute_tool(
                user_id, "search_howtolivebetter", {"metric_id": "sleep"}
            )
            invoked_tools.append("search_howtolivebetter")
            top_rec = recs["recommendations"][0]
            reply = (
                f"📊 **Паспорт метрики «Сон» обновлен:** уровень `{val}/10`.\n"
                f"• **Текущий SGI Контура 0:** `{upd['new_contour_0_sgi']}` (Режим шлюза: **{upd['gate_mode']}**).\n"
                f"• **Рекомендация из базы HowToLiveBetter (`{top_rec['recommendation_id']}`, {top_rec['evidence_grade']}):**\n"
                f"  *{top_rec['title']}* — {top_rec['protocol_action']}\n"
                f"• Хочешь запустить 7-дневный эксперимент по этому протоколу командой `/experiment`?"
            )
            return {"reply": reply, "invoked_tools": invoked_tools, "data": upd}

        # Сценарий 3: Постановка задачи («задача: ...», «нужно сделать ...», «запланируй ...»)
        if any(w in lower for w in ["задача", "сделать", "запланируй", "написать", "разработать", "дописать"]):
            force = "ответственность" in lower or "форсировать" in lower
            cog_type = "ROUTINE" if "рутин" in lower or "мелк" in lower else "DEEP_WORK"
            res = self.execute_tool(
                user_id,
                "check_and_create_task",
                {
                    "title": text[:90],
                    "cognitive_type": cog_type,
                    "estimated_minutes": 90,
                    "resistance_level": 7 if cog_type == "DEEP_WORK" else 3,
                    "force_override": force,
                },
            )
            invoked_tools.append("check_and_create_task")
            return {"reply": res["message"], "invoked_tools": invoked_tools, "data": res}

        # Сценарий 4: Запрос про гранты, возможности, стратегию или 6 капиталов
        if any(w in lower for w in ["грант", "стратег", "капитал", "возможност", "радар"]):
            strat = self.execute_tool(user_id, "skill_strategy_6_capitals", {"action": "view"})
            opps = self.execute_tool(user_id, "scan_opportunity_radar", {"capital_filter": "economic"})
            invoked_tools.extend(["skill_strategy_6_capitals", "scan_opportunity_radar"])
            top_opp = opps["opportunities"][0]
            reply = (
                f"🧭 **Стратегический навигатор (6 капиталов + Opportunity Radar)**\n"
                f"• В твоей стратегии активно **{len(strat['elements'])}** ключевых элементов.\n"
                f"• **Найденная возможность высокого рычага:** *{top_opp['title']}*\n"
                f"  — Ценность: {top_opp['funding_or_value']}\n"
                f"  — Требование: {top_opp['requirements']}\n"
                f"  — Следующий шаг: {top_opp['action_step']}"
            )
            return {"reply": reply, "invoked_tools": invoked_tools, "data": {"strategy": strat, "opportunities": opps}}

        # Сценарий 5: Запрос про команду или интенсив
        if any(w in lower for w in ["команд", "статус команды", "интенсив"]):
            team = self.execute_tool(user_id, "get_team_status", {})
            invoked_tools.append("get_team_status")
            lines = [
                f"👥 **Командный статус (Zero-Knowledge Privacy):** SGI стаи = `{team['team_sgi']}`",
                f"• **Статус Circuit Breaker:** {team['circuit_breaker']}",
            ]
            for m in team["members"]:
                lines.append(f"  — **{m['name']}** ({m['role']}): {m['work_mode']} | WIP: `{m['wip_load']}`")
            return {"reply": "\n".join(lines), "invoked_tools": invoked_tools, "data": team}

        # Сценарий по умолчанию: Диагностика состояния + Умная рефлексия + База знаний
        state = self.execute_tool(user_id, "get_current_state", {})
        refl = self.execute_tool(user_id, "skill_smart_reflection", {"user_thought": text})
        invoked_tools.extend(["get_current_state", "skill_smart_reflection"])
        reply = (
            f"🧠 **Отклик ИИ-Штурмана DelaemOS**\n"
            f"• **Наблюдаемый контекст:** Контур 0 SGI = `{state['contour_0_sgi']}` (режим `{state['gate_mode']}`, "
            f"узкое горлышко: *{state['bottleneck']}*, активных задач: `{state['active_tasks_count']}/{state['wip_limit']}`).\n"
            f"• **Вероятностная гипотеза:** твой запрос касается согласования текущих действий с долгосрочным вектором.\n\n"
            f"**Вопросы для самокалибровки:**\n" + "\n".join(refl["socratic_questions"])
        )
        return {"reply": reply, "invoked_tools": invoked_tools, "data": state}

    def _process_with_external_llm(self, user_id: int, text: str) -> Dict[str, Any]:
        """
        Полноценный цикл OpenAI-совместимого Function Calling (поддерживает OpenAI, DeepSeek, OpenRouter, vLLM).
        """
        state = self.engine.evaluate_user_state(user_id)
        context_header = (
            f"Текущая телеметрия пользователя: Contour_0_SGI={state['contour_0_sgi']}, "
            f"Gate={state['gate_mode']}, Bottleneck={state['bottleneck']}, "
            f"WIP={state['active_tasks_count']}/{state['wip_limit']}."
        )
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT_ORCHESTRATOR + "\n" + context_header},
            {"role": "user", "content": text},
        ]
        payload = {
            "model": LLM_MODEL,
            "messages": messages,
            "tools": self.tools_schema,
            "tool_choice": "auto",
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LLM_API_KEY}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        choice = result["choices"][0]["message"]
        invoked_tools: List[str] = []

        if choice.get("tool_calls"):
            messages.append(choice)
            for tc in choice["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"].get("arguments") or "{}")
                tool_out = self.execute_tool(user_id, fn_name, fn_args)
                invoked_tools.append(fn_name)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fn_name,
                        "content": json.dumps(tool_out, ensure_ascii=False),
                    }
                )
            second_payload = {
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": 0.3,
            }
            req2 = urllib.request.Request(
                f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
                data=json.dumps(second_payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LLM_API_KEY}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req2, timeout=25) as resp2:
                final_res = json.loads(resp2.read().decode("utf-8"))
            reply_text = final_res["choices"][0]["message"]["content"]
        else:
            reply_text = choice.get("content") or ""

        return {"reply": reply_text, "invoked_tools": invoked_tools}
