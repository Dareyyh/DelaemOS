"""
knowledge_base.py — Доказательная база знаний HowToLiveBetter и Радар возможностей (Opportunity Radar).
Хранит:
1. Паспорта рекомендаций (9 полей шаблона спецификации: RecommendationID, ExpectedBenefit,
   EvidenceGrade, Applicability, Contraindications, SourceURL, Jurisdiction, Version_Data_source).
2. Поисковый движок интервенций по метрикам, контурам и ограничениям человека.
3. Каталог внешних возможностей (гранты, акселераторы, научные хабы) для модуля стратегирования по 6 капиталам.
"""

from typing import Any, Dict, List, Optional


RECOMMENDATIONS_CATALOG: List[Dict[str, Any]] = [
    {
        "recommendation_id": "REC_SLEEP_01",
        "target_metric_id": "sleep",
        "contour": 0,
        "title": "Протокол световой гигиены и охлаждения спальни (90-минутный буфер)",
        "expected_benefit": "Сокращение времени засыпания на 20–35%, рост глубокой фазы сна и повышение утреннего SGI на +1.2..1.8 балла за 7 дней (неопределенность: низкая).",
        "evidence_grade": "Grade A (Систематические обзоры и РКИ по хронобиологии и мелатониновому профилю)",
        "applicability": "При нарушении засыпания, работе за экранами после 21:00 и фрагментированном сне.",
        "contraindications": "Нет медицинских противопоказаний; при клинической бессоннице (более 3 месяцев) требуется консультация сомнолога.",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный / РФ",
        "version_data_source": "HowToLiveBetter v2026.1 (проверено 2026-10)",
        "protocol_action": "За 90 минут до сна приглушить верхний свет, перевести экраны в теплый спектр/убрать телефон и проветрить спальню до 18–20°C.",
        "cost_effort": "Низкая стоимость (0 ₽), требует дисциплины переключения вечером.",
    },
    {
        "recommendation_id": "REC_ACT_01",
        "target_metric_id": "energy_activity",
        "contour": 0,
        "title": "Утренняя световая инсоляция + 15 минут быстрой ходьбы после пробуждения",
        "expected_benefit": "Синхронизация кортизолового пика, устранение дневной сонливости к 14:00 и рост дневного тонуса на +25%.",
        "evidence_grade": "Grade A (Исследования циркадных осцилляторов и фоторецепторов ipRGC)",
        "applicability": "При утренней вялости, удаленной работе из дома и дефиците естественного света.",
        "contraindications": "Острые респираторные заболевания с высокой температурой (Hard Constraint Контура 0).",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный / РФ",
        "version_data_source": "HowToLiveBetter v2026.1",
        "protocol_action": "В течение первых 45 минут после подъема выйти на улицу на 15 минут быстрой ходьбы без солнцезащитных очков и без скроллинга телефона.",
        "cost_effort": "15 минут утром, 0 ₽.",
    },
    {
        "recommendation_id": "REC_ENV_01",
        "target_metric_id": "room_env",
        "contour": 0,
        "title": "Контроль CO2 ниже 800 ppm через цикл сквозного проветривания каждые 60 минут",
        "expected_benefit": "Сохранение скорости принятия сложных решений и предотвращение падения когнитивных тестов на 15–20% в закрытом помещении.",
        "evidence_grade": "Grade A (Экспериментальные исследования влияния концентрации CO2 на когнитивные функции)",
        "applicability": "При сидячей интеллектуальной работе в кабинете или домашнем офисе.",
        "contraindications": "При сильном уличном шуме или смоге использовать приточную вентиляцию / бризер.",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный / РФ",
        "version_data_source": "HowToLiveBetter v2026.1",
        "protocol_action": "Открывать окно на 5 минут перед каждым 50-минутным спринтом глубокой работы (DEEP_WORK).",
        "cost_effort": "Минимальная, 0 ₽.",
    },
    {
        "recommendation_id": "REC_META_01",
        "target_metric_id": "metacognition",
        "contour": 1,
        "title": "Протокол децентрации и вечерней калибровки гипотез (3 вопроса с позиции 3-го лица)",
        "expected_benefit": "Снижение влияния туннельного мышления и повышение точности планирования дня на ~30%.",
        "evidence_grade": "Grade B (Когнитивно-поведенческие исследования самодистанцирования / И. Гроссманн)",
        "applicability": "При застревании в операционной текучке и потере стратегического фокуса.",
        "contraindications": "Не заменяет психотерапию при острых тревожных расстройствах.",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный",
        "version_data_source": "HowToLiveBetter v2026.1",
        "protocol_action": "Вечером записать в бот 3 ответа: 1) Какое главное предположение дня подтвердилось/опроверглось? 2) Где я действовал по инерции? 3) Что посоветовал бы внешнему штурману в моей ситуации?",
        "cost_effort": "10 минут вечером.",
    },
    {
        "recommendation_id": "REC_EMO_01",
        "target_metric_id": "emotional_reg",
        "contour": 1,
        "title": "Протокол 10-минутного микро-контракта + физиологический вздох перед сложной задачей",
        "expected_benefit": "Преодоление стартового порога сопротивления в 75–80% случаев без выгорания и чувства вины.",
        "evidence_grade": "Grade A/B (Поведенческая активация и исследования вегетативной регуляции дыхания)",
        "applicability": "Когда физиологическая база в норме (SGI >= 6.0), но ощущается сильное сопротивление старту.",
        "contraindications": "При реальном физиологическом истощении Контура 0 (SGI < 3.5) применять запрещено — нужен полноценный сон.",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный",
        "version_data_source": "HowToLiveBetter v2026.1",
        "protocol_action": "Выполнить 3 двойных вдоха с долгим выдохом, запустить таймер на 10 минут и делать самый маленький черновой шаг задачи.",
        "cost_effort": "10 минут.",
    },
    {
        "recommendation_id": "REC_ATT_01",
        "target_metric_id": "attention_filter",
        "contour": 1,
        "title": "Утренний цифровой карантин (первые 60 минут дня без ленты и мессенджеров)",
        "expected_benefit": "Снижение фрагментации внимания и увеличение длительности первой глубокой фокус-сессии на +40 минут.",
        "evidence_grade": "Grade B (Исследования когнитивной стоимости переключения контекста / Г. Марк)",
        "applicability": "При привычке проверять Telegram и новости сразу после пробуждения.",
        "contraindications": "Дежурства с обязательным экстренным реагированием.",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный",
        "version_data_source": "HowToLiveBetter v2026.1",
        "protocol_action": "Не открывать новостные каналы и чаты до завершения первого 45-минутного блока ключевой задачи дня.",
        "cost_effort": "0 ₽, высокая отдача для Контура 1 и 3.",
    },
    {
        "recommendation_id": "REC_WIP_01",
        "target_metric_id": "wip_control",
        "contour": 3,
        "title": "Жесткое ограничение WIP (не более 1 задачи DEEP_WORK одновременно)",
        "expected_benefit": "Сокращение времени доведения задач до релиза (Lead Time) на 35–50% за счет устранения штрафа переключения.",
        "evidence_grade": "Grade A (Закон Литтла в теории очередей и когнитивная эргономика)",
        "applicability": "Для индивидуальной и командной разработки, написания грантов и исследований.",
        "contraindications": "Нет.",
        "source_url": "https://github.com/eternity4719/HowToLiveBetter",
        "jurisdiction": "Глобальный",
        "version_data_source": "HowToLiveBetter v2026.1",
        "protocol_action": "Держать в статусе ACTIVE не более 1 тяжелой когнитивной задачи; все новые входящие идеи складывать в бэклог Второго мозга.",
        "cost_effort": "0 ₽.",
    },
]

# Встроенный каталог внешних возможностей для Opportunity Radar (при стратегировании по 6 капиталам)
OPPORTUNITY_RADAR_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "OPP_GRANT_FSI_START",
        "title": "Конкурс «Старт-1» / «Старт-ИИ» (Фонд содействия инновациям)",
        "target_capitals": ["economic", "administrative", "symbolic"],
        "funding_or_value": "До 4–5 млн ₽ на НИОКР и разработку прототипа ИИ-системы",
        "requirements": "Наличие научно-технической новизны (математическая модель SGI / D-Index), описание архитектуры и результаты первичного пилота.",
        "action_step": "Выгрузить отчет 14-дневного пилота DelaemOS через команду /export_grant и приложить к разделу НТН.",
    },
    {
        "id": "OPP_GRANT_STUDENT_STARTUP",
        "title": "Грант «Студенческий стартап» (ФСИ)",
        "target_capitals": ["economic", "symbolic"],
        "funding_or_value": "1 млн ₽ на создание MVP и регистрацию юрлица",
        "requirements": "Работающий прототип в Telegram, подтверждение востребованности на первых тестировщиках.",
        "action_step": "Провести 2-недельный замер на 3 участниках команды и зафиксировать динамику метрик.",
    },
    {
        "id": "OPP_HUB_AI_COMMUNITY",
        "title": "Профильные AI & Cybernetics исследовательские семинары и хакатоны",
        "target_capitals": ["social", "cultural", "symbolic"],
        "funding_or_value": "Привлечение со-исследователей, рецензентов и первых B2B-клиентов на командные интенсивы",
        "requirements": "Открытая демонстрация концепции 5 контуров и связки с базой HowToLiveBetter.",
        "action_step": "Опубликовать кейс пилотного тестирования с графиками шлюзового аудита SGI.",
    },
]


class KnowledgeService:
    def find_recommendations(
        self, metric_id: Optional[str] = None, query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = RECOMMENDATIONS_CATALOG
        if metric_id:
            filtered = [r for r in results if r["target_metric_id"] == metric_id]
            if filtered:
                return filtered
        if query:
            q = query.lower()
            filtered = [
                r
                for r in results
                if q in r["title"].lower()
                or q in r["expected_benefit"].lower()
                or q in r["protocol_action"].lower()
                or q in r["target_metric_id"].lower()
            ]
            if filtered:
                return filtered
        return results[:3]

    def scan_opportunities(
        self, capital_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not capital_filter:
            return OPPORTUNITY_RADAR_CATALOG
        c = capital_filter.lower()
        matched = [
            o for o in OPPORTUNITY_RADAR_CATALOG if c in o["target_capitals"]
        ]
        return matched if matched else OPPORTUNITY_RADAR_CATALOG
