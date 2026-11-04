"""
engine.py — Математическое и кибернетическое ядро DelaemOS.
Реализует:
1. Расчет Solid Ground Index (SGI = CurrentLevel * Stability / 10) и принцип узкого горлышка Либиха.
2. Калибровку индивидуального коридора нормы (Baseline_personal и порог SafetyThreshold = mean - 2*sigma).
3. Шлюзовой перехватчик (Cascading Gate Interceptor): режимы LOCKED, RESTRICTED, UNLOCKED и Soft Gating.
4. Детектор конгруэнтности (D-Index / Divergence Engine) и генерацию «Сократических уколов».
5. Командный агрегатор с принципом Zero-Knowledge Privacy и поддержку режима Корпоративного интенсива.
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config import (
    CONTOURS,
    SGI_LOCKED_THRESHOLD,
    SGI_RESTRICTED_THRESHOLD,
    WIP_LIMITS_BY_GATE,
)
from database import DelaemDatabase


class CyberneticEngine:
    def __init__(self, db: DelaemDatabase) -> None:
        self.db = db

    # -------------------------------------------------------------------------
    # 1. Расчет SGI, личного Baseline и статуса шлюза (Cascading Gates)
    # -------------------------------------------------------------------------
    def compute_metric_baseline(
        self, user_id: int, metric_id: str
    ) -> Dict[str, float]:
        """
        Рассчитывает личную норму (среднее и стандартное отклонение) по истории наблюдений
        и плавающий порог безопасности SafetyThreshold = Baseline_personal - 2*sigma.
        """
        history = self.db.get_metric_history(user_id, metric_id, limit=30)
        values = [float(h["value"]) for h in history]
        if not values:
            return {"mean": 7.2, "sigma": 0.7, "personal_threshold": 5.8, "samples": 0}

        mean_val = sum(values) / len(values)
        if len(values) > 1:
            variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
            sigma = max(0.35, math.sqrt(variance))
        else:
            sigma = 0.7

        personal_threshold = round(max(2.5, min(6.5, mean_val - 2.0 * sigma)), 2)
        return {
            "mean": round(mean_val, 2),
            "sigma": round(sigma, 2),
            "personal_threshold": personal_threshold,
            "samples": len(values),
        }

    def evaluate_user_state(self, user_id: int) -> Dict[str, Any]:
        """
        Комплексный расчет состояния по всем 5 контурам с применением Закона Либиха
        (узкое горлышко базового контура определяет пропускную способность системы).
        """
        user = self.db.ensure_user(user_id)
        all_metrics = self.db.get_user_metrics(user_id)

        contour_summary: Dict[int, Dict[str, Any]] = {}
        for c_idx in CONTOURS.keys():
            c_metrics = [m for m in all_metrics if m["contour"] == c_idx]
            if c_metrics:
                sgis = [m["sgi"] for m in c_metrics]
                min_metric = min(c_metrics, key=lambda x: x["sgi"])
                avg_sgi = round(sum(sgis) / len(sgis), 2)
                bottleneck_sgi = min_metric["sgi"]
                # Эффективный SGI контура учитывает и среднее, и узкое горлышко Либиха (вес 60% у минимума)
                effective_sgi = round(0.6 * bottleneck_sgi + 0.4 * avg_sgi, 2)
            else:
                avg_sgi = 5.0
                bottleneck_sgi = 5.0
                effective_sgi = 5.0
                min_metric = None

            contour_summary[c_idx] = {
                "contour": c_idx,
                "name": CONTOURS[c_idx]["name"],
                "avg_sgi": avg_sgi,
                "bottleneck_sgi": bottleneck_sgi,
                "effective_sgi": effective_sgi,
                "bottleneck_metric": min_metric["name"] if min_metric else "Нет данных",
                "bottleneck_metric_id": min_metric["metric_id"] if min_metric else "",
                "metrics": c_metrics,
            }

        c0_sgi = contour_summary[0]["effective_sgi"]
        c1_sgi = contour_summary[1]["effective_sgi"]
        substrate_sgi = round(0.7 * c0_sgi + 0.3 * c1_sgi, 2)

        # Определение шлюзового режима (Cascading Gate)
        if c0_sgi < SGI_LOCKED_THRESHOLD:
            gate_mode = "LOCKED"
            conductance_pct = 20
        elif c0_sgi < SGI_RESTRICTED_THRESHOLD or substrate_sgi < 4.2:
            gate_mode = "RESTRICTED"
            conductance_pct = 60
        else:
            gate_mode = "UNLOCKED"
            conductance_pct = 100

        # Если включен режим Корпоративного интенсива — временно расширяем WIP на 1 слот,
        # если нет жесткого биологического вето (c0_sgi >= 2.8)
        wip_limit = WIP_LIMITS_BY_GATE[gate_mode]
        if user.get("intensive_mode") == 1 and c0_sgi >= 2.8:
            wip_limit += 1

        active_tasks = self.db.get_active_tasks(user_id)
        sleep_baseline = self.compute_metric_baseline(user_id, "sleep")

        return {
            "user": user,
            "contour_0_sgi": c0_sgi,
            "contour_1_sgi": c1_sgi,
            "substrate_sgi": substrate_sgi,
            "gate_mode": gate_mode,
            "conductance_pct": conductance_pct,
            "wip_limit": wip_limit,
            "active_tasks_count": len(active_tasks),
            "active_tasks": active_tasks,
            "contours": contour_summary,
            "sleep_baseline": sleep_baseline,
            "bottleneck": contour_summary[0]["bottleneck_metric"],
        }

    # -------------------------------------------------------------------------
    # 2. Шлюзовой перехватчик задач и Информированное согласие (Soft Gating)
    # -------------------------------------------------------------------------
    def check_task_gate(
        self,
        user_id: int,
        title: str,
        cognitive_type: str = "DEEP_WORK",
        estimated_minutes: int = 60,
        resistance_level: int = 5,
        force_override: bool = False,
    ) -> Dict[str, Any]:
        """
        Проверяет, можно ли взять задачу в работу при текущем состоянии Контура 0 и WIP-лимите.
        При пробое фундамента вычисляет мультипликаторов риска (Soft Gating).
        """
        state = self.evaluate_user_state(user_id)
        c0_sgi = state["contour_0_sgi"]
        gate_mode = state["gate_mode"]
        wip_limit = state["wip_limit"]
        current_wip = state["active_tasks_count"]

        # Расчет деградации относительно личной нормы
        sleep_metric = self.db.get_metric(user_id, "sleep")
        sleep_base = state["sleep_baseline"]["mean"]
        sleep_cur = sleep_metric["current_level"] if sleep_metric else 6.5
        depletion_pct = max(
            0, int(round((max(0.0, sleep_base - sleep_cur) / max(1.0, sleep_base)) * 100))
        )
        if depletion_pct == 0 and c0_sgi < SGI_RESTRICTED_THRESHOLD:
            depletion_pct = int(round((SGI_RESTRICTED_THRESHOLD - c0_sgi) / SGI_RESTRICTED_THRESHOLD * 100))

        # Расчет мультипликаторов риска при дефиците Контура 0
        deficit = max(0.0, SGI_RESTRICTED_THRESHOLD - c0_sgi)
        error_prob_increase = min(85, int(round(deficit * 28 + (15 if cognitive_type == "DEEP_WORK" else 5))))
        time_multiplier = round(1.0 + deficit * 0.35 + (0.2 if resistance_level >= 7 else 0.0), 1)
        recovery_rollback_days = max(1, int(round(1 + deficit * 1.8)))

        needs_soft_gating = (
            (gate_mode == "LOCKED" and cognitive_type in ("DEEP_WORK", "SYNC"))
            or (gate_mode == "RESTRICTED" and cognitive_type == "DEEP_WORK" and estimated_minutes > 45)
            or (current_wip >= wip_limit and cognitive_type != "RECOVERY")
        )

        if needs_soft_gating and not force_override:
            soft_gating_message = (
                f"⚠️ **Шлюзовой аудит (Soft Gating — режим {gate_mode})**\n"
                f"Твой фундамент Контура 0 сейчас на уровне **SGI = {c0_sgi}** "
                f"(узкое горлышко: *{state['bottleneck']}*, истощение ~{max(depletion_pct, 25)}% от нормы, "
                f"активных задач: {current_wip}/{wip_limit}).\n\n"
                f"Если ты возьмешь задачу **«{title}»** ({cognitive_type}) прямо сейчас:\n"
                f"• Вероятность когнитивной ошибки выше на **~{error_prob_increase}%**\n"
                f"• Время выполнения растянется в **{time_multiplier}x раза**\n"
                f"• Откат по базовому ресурсу займет **{recovery_rollback_days} дн.** вместо 1 дня.\n\n"
                f"Как поступим?\n"
                f"1️⃣ **[Снизить планку до Sandbox]** — записать задачу в щадящем режиме (25 мин чернового наброска без риска)\n"
                f"2️⃣ **[Взять под свою ответственность]** — форсировать выполнение с фиксацией в журнале рисков\n"
                f"3️⃣ **[Уйти на перезагрузку]** — активировать протокол восстановления Контура 0"
            )
            self.db.log_audit_event(
                user_id=user_id,
                event_type="SOFT_GATING",
                contour_0_sgi=c0_sgi,
                gate_mode=gate_mode,
                payload={
                    "task_title": title,
                    "cognitive_type": cognitive_type,
                    "error_prob_increase": error_prob_increase,
                    "time_multiplier": time_multiplier,
                    "recovery_rollback_days": recovery_rollback_days,
                },
            )
            return {
                "allowed": False,
                "status": "SOFT_GATING_REQUIRED",
                "gate_mode": gate_mode,
                "contour_0_sgi": c0_sgi,
                "risk_metrics": {
                    "error_prob_increase_pct": error_prob_increase,
                    "time_multiplier": time_multiplier,
                    "recovery_rollback_days": recovery_rollback_days,
                },
                "message": soft_gating_message,
            }

        # Если шлюз открыт или пользователь явно подтвердил ответственность
        task_status = "SANDBOXED" if (gate_mode != "UNLOCKED" and not force_override) else "ACTIVE"
        created_task = self.db.create_task(
            user_id=user_id,
            title=title,
            cognitive_type=cognitive_type,
            resistance_level=resistance_level,
            estimated_minutes=estimated_minutes,
            status=task_status,
            gate_mode_at_creation=gate_mode,
            forced_by_user=1 if force_override else 0,
        )
        self.db.log_audit_event(
            user_id=user_id,
            event_type="GATE_CHECK",
            contour_0_sgi=c0_sgi,
            gate_mode=gate_mode,
            payload={"task_id": created_task["id"], "forced": force_override},
        )
        return {
            "allowed": True,
            "status": "CREATED",
            "gate_mode": gate_mode,
            "contour_0_sgi": c0_sgi,
            "task": created_task,
            "message": (
                f"✅ Задача **«{title}»** добавлена в поток "
                f"(режим: `{task_status}`, когнитивный профиль: `{cognitive_type}`, SGI Контура 0: `{c0_sgi}`)."
            ),
        }

    # -------------------------------------------------------------------------
    # 3. Детектор конгруэнтности (D-Index) и «Сократический укол»
    # -------------------------------------------------------------------------
    def evaluate_congruence_d_index(
        self, user_id: int, user_complaint_text: str, subjective_energy_claim: float = 2.0
    ) -> Dict[str, Any]:
        """
        Вычисляет расхождение (D-Index от 0 до 10) между:
        - Потоком А: объективная/утренняя физиология Контура 0 (SGI сна и тела)
        - Потоком Б: наличие задач с высоким сопротивлением или точкой бифуркации («Шкура на кону»)
        - Потоком В: словами человека о полной усталости и неспособности работать.
        """
        state = self.evaluate_user_state(user_id)
        c0_sgi = state["contour_0_sgi"]
        active_tasks = state["active_tasks"]
        high_resistance_tasks = [t for t in active_tasks if t["resistance_level"] >= 7]

        # Переводим SGI в эквивалент шкалы бодрости (1..10) для сопоставления с субъективной жалобой
        physiological_readiness_10 = min(10.0, round(c0_sgi * 1.4, 2))
        raw_gap = max(0.0, physiological_readiness_10 - subjective_energy_claim)
        resistance_boost = 1.8 if high_resistance_tasks else 0.5
        d_index = round(min(10.0, raw_gap * 1.15 + resistance_boost), 2)

        # Вероятность того, что причина в когнитивном трении / избегании, а не в истощении тела
        avoidance_probability = min(92, max(15, int(round(d_index * 9.5))))

        if c0_sgi >= SGI_RESTRICTED_THRESHOLD and d_index >= 4.5:
            target_task = (
                high_resistance_tasks[0]["title"]
                if high_resistance_tasks
                else (active_tasks[0]["title"] if active_tasks else "ключевой задачей дня")
            )
            pattern_type = "HIGH_DIVERGENCE_AVOIDANCE_HYPOTHESIS"
            socratic_message = (
                f"🔍 **Детектор конгруэнтности (D-Index = {d_index}/10)**\n"
                f"• **Наблюдаемый факт:** твой базовый субстрат Контура 0 в норме (`SGI = {c0_sgi}`, шлюз `{state['gate_mode']}`), "
                f"однако субъективно ощущается вязкость и упадок сил.\n"
                f"• **Вероятностная гипотеза (~{avoidance_probability}%):** дело не в физическом истощении организма, "
                f"а в когнитивном сопротивлении или страхе оценки перед задачей **«{target_task}»**.\n"
                f"• **Проверка реальностью:** что именно в этом шаге вызывает наибольшее внутреннее трение — "
                f"неясность первого действия или высокая цена ошибки?\n\n"
                f"⚡ **Микро-контракт (Принцип 10-минутного стресс-теста):**\n"
                f"Давай заключим честную сделку: ровно **10 минут** работы по таймеру над самым неприятным узлом задачи "
                f"(без обязательства доделать до конца). Если через 10 минут вязкость не уйдет — мы официально закрываем "
                f"рабочий блок и включаем **Протокол конструктивного отдыха** (40 минут прогулки без телефона и соцсетей)."
            )
        else:
            pattern_type = "TRUE_SUBSTRATE_DEPLETION"
            socratic_message = (
                f"🛡 **Анализ состояния (D-Index = {d_index}/10 — данные конгруэнтны)**\n"
                f"• **Наблюдаемый факт:** твой Контур 0 действительно пробит (`SGI = {c0_sgi}`). "
                f"Жалоба на усталость полностью совпадает с физиологическим дефицитом.\n"
                f"• **Протокол восстановления (Enforced Hygiene):** никакой дофаминовой анестезии в YouTube/TikTok. "
                f"Закрываем рабочие чаты на 3–4 часа: 40 минут прогулки без наушников + горизонтальный отдых в тишине."
            )

        self.db.log_audit_event(
            user_id=user_id,
            event_type="D_INDEX_PROBE",
            contour_0_sgi=c0_sgi,
            gate_mode=state["gate_mode"],
            d_index=d_index,
            payload={
                "complaint": user_complaint_text,
                "avoidance_probability": avoidance_probability,
                "pattern_type": pattern_type,
            },
        )
        return {
            "d_index": d_index,
            "contour_0_sgi": c0_sgi,
            "avoidance_probability": avoidance_probability,
            "pattern_type": pattern_type,
            "message": socratic_message,
        }

    # -------------------------------------------------------------------------
    # 4. Командный контур (Zero-Knowledge Team Extension) и Интенсивы
    # -------------------------------------------------------------------------
    def get_team_zero_knowledge_summary(self) -> Dict[str, Any]:
        """
        Агрегирует готовность команды (2-3 человека) без раскрытия личных медицинских
        и психологических метрик участников (принцип Zero-Knowledge Privacy).
        """
        users = self.db.get_all_users()
        if not users:
            return {"team_size": 0, "team_sgi": 0.0, "status": "NO_DATA", "message": "Нет участников в команде."}

        member_states = []
        for u in users:
            st = self.evaluate_user_state(u["user_id"])
            # Наружу отдаем только рабочий статус и загрузку WIP, скрывая сырые личные метрики
            work_mode_label = {
                "UNLOCKED": "🟢 Deep Focus Ready",
                "RESTRICTED": "🟡 Sandbox / Routine Only",
                "LOCKED": "🔴 Recovery Protocol",
            }.get(st["gate_mode"], "🟡 Sandbox")
            member_states.append(
                {
                    "name": u["full_name"] or u["username"],
                    "role": u["role_in_team"],
                    "work_mode": work_mode_label,
                    "gate_mode": st["gate_mode"],
                    "wip_load": f"{st['active_tasks_count']}/{st['wip_limit']}",
                    "intensive": bool(u.get("intensive_mode")),
                    "_internal_sgi": st["contour_0_sgi"],
                }
            )

        avg_team_sgi = round(
            sum(m["_internal_sgi"] for m in member_states) / len(member_states), 2
        )
        locked_count = sum(1 for m in member_states if m["gate_mode"] == "LOCKED")
        restricted_count = sum(1 for m in member_states if m["gate_mode"] == "RESTRICTED")

        if locked_count > 0 or avg_team_sgi < SGI_LOCKED_THRESHOLD:
            circuit_breaker = "ACTIVE (Активирован Circuit Breaker: рекомендуется срезать скоуп спринта и убрать синхронные митинги)"
        elif restricted_count >= 2 or avg_team_sgi < SGI_RESTRICTED_THRESHOLD:
            circuit_breaker = "CAUTION (Команда в режиме частичной проводимости: фокус на закрытии текущих задач без новых рисков)"
        else:
            circuit_breaker = "NOMINAL (Высокая когнитивная пропускная способность: можно проводить штурмы и брать задачи «Шкура на кону»)"

        # Удаляем внутренний SGI из публичного словаря участников
        for m in member_states:
            m.pop("_internal_sgi", None)

        return {
            "team_size": len(member_states),
            "team_sgi": avg_team_sgi,
            "circuit_breaker": circuit_breaker,
            "members": member_states,
        }

    def activate_corporate_intensive(self, user_id: int, duration_days: int = 3) -> Dict[str, Any]:
        """
        Переводит участника или команду в режим «Корпоративный интенсив» (временная мобилизация Контура 3)
        с обязательным бронированием буфера восстановления после завершения.
        """
        state = self.evaluate_user_state(user_id)
        if state["contour_0_sgi"] < SGI_LOCKED_THRESHOLD:
            return {
                "activated": False,
                "message": (
                    "❌ Отказ шлюза безопасности: невозможно запустить режим Корпоративного интенсива при "
                    f"аварийном Контуре 0 (`SGI = {state['contour_0_sgi']}`). Сначала требуется базовое восстановление."
                ),
            }

        recovery_date = (datetime.utcnow() + timedelta(days=duration_days)).strftime("%Y-%m-%d")
        self.db.set_intensive_mode(user_id, True, recovery_date=recovery_date)
        # Автоматически создаем защищенное событие восстановления в Task Flow
        self.db.create_task(
            user_id=user_id,
            title=f"[ОБЯЗАТЕЛЬНЫЙ БУФЕР] Восстановление субстрата после интенсива ({recovery_date})",
            cognitive_type="RECOVERY",
            resistance_level=1,
            estimated_minutes=240,
            deadline_stiffness="Hard",
            status="ACTIVE",
            gate_mode_at_creation=state["gate_mode"],
        )
        return {
            "activated": True,
            "recovery_date": recovery_date,
            "message": (
                f"🔥 **Режим «Корпоративный интенсив» активирован на {duration_days} дн.**\n"
                f"• Лимит параллельных задач (WIP) временно увеличен на +1 слот.\n"
                f"• На дату **{recovery_date}** в расписание жестко забронирован обязательный буфер восстановления "
                f"Контура 0 (защита от пост-спринтового отката)."
            ),
        }
