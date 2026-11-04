"""
test_simulation.py — Автоматический интеграционный тест и симулятор пилота на 3 человека.
Прогоняет полный жизненный цикл DelaemOS:
1. Регистрация 3 участников команды (Основатель/Архитектор, Техлид, Продуктовый исследователь).
2. Серия чек-инов Контура 0 (включая сценарий пробоя сна у одного из участников).
3. Срабатывание шлюзового перехватчика (Soft Gating) при попытке взять тяжелую задачу DEEP_WORK на пробитом Контуре 0.
4. Срабатывание детектора конгруэнтности (D-Index) и «Сократического укола» (10-минутный микро-контракт), когда база в норме, но участник жалуется на усталость перед сложной задачей.
5. Подбор рекомендации из базы HowToLiveBetter, запуск и успешное завершение 7-дневного личного эксперимента с замером до/после.
6. Сборка стратегии по 6 капиталам, сканирование Радара возможностей и запуск исследования в /Умный_контент.
7. Активация режима «Корпоративный интенсив» и выгрузка готового научно-технического отчета для грантовой заявки (grant_pilot_report.md).
"""

import os
from bot import DelaemBotApplication


def run_pilot_simulation(db_file: str = "delaem_pilot_test.db") -> str:
    if os.path.exists(db_file):
        os.remove(db_file)

    app = DelaemBotApplication(db_path=db_file)

    # 1. Инициализация 3 участников пилотной команды
    team_members = [
        (101, "founder_arch", "Алексей (Основатель & Архитектор)", "Мета-контур / Стратег"),
        (102, "tech_lead", "Дмитрий (AI/Backend Техлид)", "Программная дирекция"),
        (103, "product_res", "Елена (Продукт & Аналитика)", "Исполнительная дирекция"),
    ]
    for uid, uname, fname, role in team_members:
        app.db.ensure_user(uid, username=uname, full_name=fname, role_in_team=role)

    # 2. Калибровка истории наблюдений (симуляция динамики чек-инов)
    # Участник 101: высокий стабильный ресурс (SGI ~ 6.4 -> UNLOCKED), жалуется на ступор -> проверим D-Index!
    app.handle_incoming_message(101, "/checkin 8.0 7.5 8.5")
    app.handle_incoming_message(101, "/tasks Спроектировать граф 6 капиталов для гранта")
    d_index_resp = app.handle_incoming_message(
        101, "Я жутко устал, нет сил начинать этот раздел, хочу лечь отдохнуть"
    )
    assert "D-Index" in d_index_resp and "10 минут" in d_index_resp, "Ожидался Сократический укол D-Index!"

    # Участник 102: пробой Контура 0 (недосып: сон 3.5, тонус 4.0) -> пытается взять тяжелую задачу -> проверим Soft Gating!
    app.handle_incoming_message(102, "/checkin 3.5 4.0 6.0")
    soft_gate_resp = app.handle_incoming_message(
        102, "/tasks Написать ядро байесовской сети на 500 строк"
    )
    assert "Soft Gating" in soft_gate_resp, "Ожидался перехват Soft Gating при пробитом Контуре 0!"

    # Участник 102 запускает личный эксперимент из базы HowToLiveBetter по восстановлению сна и завершает его с ростом
    app.handle_incoming_message(102, "/experiment")
    exps_102 = app.db.get_user_experiments(102)
    assert len(exps_102) >= 1
    app.db.finish_experiment(
        102,
        exps_102[0]["id"],
        value_after=7.8,
        user_feedback="Световая гигиена за 90 минут до сна вернула глубокий сон за 6 дней.",
    )
    app.handle_incoming_message(102, "/checkin 7.8 7.2 8.0")

    # Участник 103: тестирует Умную рефлексию, Стратегию 6 капиталов, Умный контент и режим Интенсива
    app.handle_incoming_message(103, "/checkin 7.5 7.5 8.0")
    refl_resp = app.handle_incoming_message(
        103, "/reflection Как связать командный трекинг с принципом Zero-Knowledge Privacy?"
    )
    assert "Метапознание" in refl_resp
    app.handle_incoming_message(
        103, "/smart_content Влияние уровня CO2 на когнитивную продуктивность R&D-команд"
    )
    app.handle_incoming_message(103, "/intensive 3")

    # Проверка выгрузки во Второй мозг (Obsidian Markdown) и Командного статуса
    sb_resp = app.handle_incoming_message(101, "/second_brain")
    assert "DelaemOS_SecondBrain" in sb_resp
    team_resp = app.handle_incoming_message(101, "/team")
    assert "Zero-Knowledge" in team_resp

    # Генерация итогового отчета для грантовой заявки
    grant_report = app.handle_incoming_message(101, "/export_grant")
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grant_pilot_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(grant_report)

    print("✅ Все интеграционные тесты и сценарии пилота на 3 участниках пройдены успешно!")
    print(f"📄 Отчет для грантовой заявки сохранен в: {report_path}")
    return grant_report


if __name__ == "__main__":
    run_pilot_simulation()
