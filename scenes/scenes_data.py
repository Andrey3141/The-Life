"""
Полная система сцен (36 сцен + 12 концовок)
Все переходы ведут на существующие сцены
"""

from core.models import Scene, Choice, Subject

SCENES_DATA = []

# =============== КОРПОРАТИВНЫЙ ПУТЬ (12 сцен) ===============

SCENES_DATA.append(Scene(
    scene_id="start",
    title="Начало карьеры",
    description="Вы стоите перед выбором своей первой работы. Только что закончили колледж и теперь решаете, как строить свою карьеру.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Устроиться в крупную корпорацию",
            next_scene_id="corporate_entry",
            effects={"management": 10, "finance": 5, "money": 30000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 0)
        ),
        Choice(
            text="Работать в небольшом стартапе",
            next_scene_id="startup_entry",
            effects={"marketing": 10, "economics": 5, "money": 20000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 0)
        ),
        Choice(
            text="Пойти на государственную службу",
            next_scene_id="government_entry",
            effects={"reputation": 10, "management": 5, "money": 25000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 0)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_entry",
    title="Первый день в корпорации",
    description="Вы приходите в офис крупной IT-компании. Все новое и немного пугающее.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Усердно работать над первым проектом",
            next_scene_id="corporate_project_success",
            effects={"management": 15, "reputation": 10, "money": 5000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 5)
        ),
        Choice(
            text="Знакомиться с коллегами и начальством",
            next_scene_id="corporate_networking",
            effects={"reputation": 15, "happiness": 10, "health": -5},
            money_cost=10000,
            required_skill=(Subject.REPUTATION, 0)
        ),
        Choice(
            text="Изучать внутренние процессы компании",
            next_scene_id="corporate_study",
            effects={"finance": 10, "economics": 15, "happiness": -5},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 0)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_project_success",
    title="Успешный проект",
    description="Ваш первый проект завершился успешно. Руководство заметило ваши старания.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Попросить повышение зарплаты",
            next_scene_id="corporate_raise",
            effects={"money": 20000, "reputation": 10, "happiness": 15},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 15)
        ),
        Choice(
            text="Попросить более интересный проект",
            next_scene_id="corporate_challenge",
            effects={"management": 20, "happiness": 10, "health": -10},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 10)
        ),
        Choice(
            text="Предложить оптимизацию процессов",
            next_scene_id="corporate_optimization",
            effects={"economics": 25, "reputation": 15, "money": 10000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 10)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_raise",
    title="Повышение зарплаты",
    description="Вы получили повышение зарплаты на 30%! Теперь у вас больше возможностей.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Инвестировать в образование",
            next_scene_id="corporate_education",
            effects={"economics": 30, "finance": 20, "money": -50000},
            money_cost=50000,
            required_skill=(Subject.FINANCE, 15)
        ),
        Choice(
            text="Купить квартиру в ипотеку",
            next_scene_id="corporate_mortgage",
            effects={"money": -20000, "happiness": 25, "health": 10},
            money_cost=20000,
            required_skill=(Subject.FINANCE, 20)
        ),
        Choice(
            text="Откладывать деньги на будущее",
            next_scene_id="corporate_savings",
            effects={"money": 40000, "finance": 25, "happiness": 10},
            money_cost=0,
            required_skill=(Subject.FINANCE, 10)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_education",
    title="Инвестиции в образование",
    description="Вы поступили на курс MBA. Знания бесценны, но учеба отнимает много времени.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Сосредоточиться на учебе",
            next_scene_id="corporate_mba_focus",
            effects={"economics": 40, "finance": 35, "health": -20},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 30)
        ),
        Choice(
            text="Совмещать учебу и работу",
            next_scene_id="corporate_mba_balance",
            effects={"management": 25, "economics": 20, "health": -30},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_mba_focus",
    title="Завершение MBA",
    description="Вы успешно закончили MBA с отличием. Новые знания открывают новые возможности.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Стать консультантом",
            next_scene_id="consultant_career",
            effects={"reputation": 40, "money": 150000, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 30)
        ),
        Choice(
            text="Вернуться в корпорацию на высокую должность",
            next_scene_id="corporate_executive",
            effects={"management": 45, "money": 200000, "health": -25},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_mba_balance",
    title="Баланс работы и учебы",
    description="Вы совмещали работу и учебу. Это было тяжело, но вы справились.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Искать новую работу с дипломом",
            next_scene_id="job_search_mba",
            effects={"money": 120000, "reputation": 30, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 25)
        ),
        Choice(
            text="Остаться в текущей компании",
            next_scene_id="corporate_stay",
            effects={"management": 35, "money": 80000, "happiness": 15},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_executive",
    title="Должность вице-президента",
    description="Вы стали вице-президентом компании. Большая власть, большая ответственность.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Стремиться к позиции CEO",
            next_scene_id="ceo_aspiration",
            effects={"management": 50, "money": 300000, "health": -40},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 45)
        ),
        Choice(
            text="Уделять время семье",
            next_scene_id="executive_family_balance",
            effects={"happiness": 40, "health": 30, "money": 150000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="ceo_aspiration",
    title="Путь к CEO",
    description="Вы решили бороться за должность генерального директора. Это потребует всех сил.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Бороться внутри компании",
            next_scene_id="internal_ceo_fight",
            effects={"management": 55, "reputation": 40, "health": -50},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 50)
        ),
        Choice(
            text="Перейти в другую компанию как CEO",
            next_scene_id="external_ceo_offer",
            effects={"money": 500000, "reputation": 45, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_networking",
    title="Нетворкинг в корпорации",
    description="Вы активно знакомитесь с коллегами. Это помогает в карьере.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать строить связи",
            next_scene_id="corporate_project_success",
            effects={"reputation": 20, "money": 15000, "happiness": 15},
            money_cost=5000,
            required_skill=(Subject.REPUTATION, 10)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_study",
    title="Изучение процессов компании",
    description="Вы глубоко изучили работу компании. Это дает преимущество.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Использовать знания для карьеры",
            next_scene_id="corporate_optimization",
            effects={"economics": 30, "money": 20000, "reputation": 15},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_mortgage",
    title="Ипотека",
    description="Вы купили квартиру. Ежемесячные платежи, но свой дом.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Искать дополнительный доход",
            next_scene_id="finance_investment",
            effects={"money": 25000, "finance": 20, "health": -10},
            money_cost=0,
            required_skill=(Subject.FINANCE, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_savings",
    title="Накопления",
    description="Вы откладываете деньги. Финансовая подушка безопасности растет.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Инвестировать накопления",
            next_scene_id="finance_investment",
            effects={"money": 30000, "finance": 25, "happiness": 15},
            money_cost=0,
            required_skill=(Subject.FINANCE, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_challenge",
    title="Сложный проект",
    description="Вам поручили важный международный проект. Это шанс проявить себя.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Принять вызов",
            next_scene_id="corporate_executive",
            effects={"management": 35, "reputation": 30, "health": -20},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_optimization",
    title="Оптимизация процессов",
    description="Ваша оптимизация повысила эффективность отдела на 40%.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Получить повышение",
            next_scene_id="corporate_executive",
            effects={"management": 40, "money": 50000, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 30)
        )
    ]
))

# =============== СТАРТАП ПУТЬ (12 сцен) ===============

SCENES_DATA.append(Scene(
    scene_id="startup_entry",
    title="Начало в стартапе",
    description="Вы в маленьком офисе с 5 сотрудниками. Нет строгих правил, но и нет стабильности.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Взять на себя несколько проектов",
            next_scene_id="startup_multitask",
            effects={"management": 20, "health": -15, "money": 3000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 5)
        ),
        Choice(
            text="Сосредоточиться на одном проекте",
            next_scene_id="startup_focus",
            effects={"finance": 15, "reputation": 10, "happiness": 5},
            money_cost=0,
            required_skill=(Subject.FINANCE, 0)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_multitask",
    title="Многозадачность",
    description="Вы работаете над несколькими проектами одновременно. Это сложно, но вы учитесь.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать в том же темпе",
            next_scene_id="startup_burnout_risk",
            effects={"management": 25, "health": -30, "money": 10000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 20)
        ),
        Choice(
            text="Нанять помощника",
            next_scene_id="startup_hire",
            effects={"money": -20000, "management": 15, "happiness": 20},
            money_cost=20000,
            required_skill=(Subject.FINANCE, 15)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_focus",
    title="Фокус на одном проекте",
    description="Вы сосредоточились на одном ключевом проекте. Результаты впечатляют.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Искать инвесторов",
            next_scene_id="startup_investors",
            effects={"marketing": 20, "money": 100000, "happiness": 15},
            money_cost=5000,
            required_skill=(Subject.MARKETING, 10)
        ),
        Choice(
            text="Развивать проект самостоятельно",
            next_scene_id="startup_bootstrapped",
            effects={"finance": 25, "money": 30000, "happiness": 10},
            money_cost=0,
            required_skill=(Subject.FINANCE, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_investors",
    title="Поиск инвесторов",
    description="Вы нашли инвесторов! Теперь у вас есть деньги для развития, но и обязательства.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Быстро расти и масштабироваться",
            next_scene_id="startup_scale",
            effects={"money": 500000, "management": 35, "health": -25},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 30)
        ),
        Choice(
            text="Расти постепенно",
            next_scene_id="startup_steady",
            effects={"money": 200000, "happiness": 30, "health": 15},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_scale",
    title="Быстрый рост",
    description="Ваш стартап быстро растет. Вы нанимаете новых сотрудников, открываете новые офисы.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Готовиться к IPO",
            next_scene_id="startup_ipo",
            effects={"finance": 40, "money": 1000000, "health": -35},
            money_cost=0,
            required_skill=(Subject.FINANCE, 35)
        ),
        Choice(
            text="Продать компанию",
            next_scene_id="startup_exit",
            effects={"money": 5000000, "happiness": 40, "health": 20},
            money_cost=0,
            required_skill=(Subject.FINANCE, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_steady",
    title="Стабильный рост",
    description="Ваш стартап растет стабильно и надежно. Меньше стресса, больше контроля.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать стабильный рост",
            next_scene_id="startup_profitable",
            effects={"money": 300000, "happiness": 35, "health": 25},
            money_cost=0,
            required_skill=(Subject.FINANCE, 25)
        ),
        Choice(
            text="Принять предложение о покупке",
            next_scene_id="startup_exit",
            effects={"money": 3000000, "happiness": 45, "health": 30},
            money_cost=0,
            required_skill=(Subject.FINANCE, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_bootstrapped",
    title="Самостоятельное развитие",
    description="Вы развиваете проект на собственные средства. Медленно, но уверенно.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Добиться прибыльности",
            next_scene_id="startup_profitable",
            effects={"finance": 30, "money": 150000, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.FINANCE, 25)
        ),
        Choice(
            text="Искать инвесторов позже",
            next_scene_id="startup_investors",
            effects={"marketing": 25, "money": 50000, "happiness": 15},
            money_cost=0,
            required_skill=(Subject.MARKETING, 15)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_burnout_risk",
    title="Риск выгорания",
    description="Вы работаете на износ. Риск выгорания высок.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать в том же духе",
            next_scene_id="burnout_failure",
            effects={"health": -50, "money": 50000, "happiness": -40},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        ),
        Choice(
            text="Взять перерыв",
            next_scene_id="startup_focus",
            effects={"health": 20, "happiness": 25, "money": -10000},
            money_cost=10000,
            required_skill=(Subject.MANAGEMENT, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_hire",
    title="Нанять помощника",
    description="Вы наняли помощника. Работать стало легче.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать развитие",
            next_scene_id="startup_focus",
            effects={"management": 20, "money": 30000, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 15)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_profitable",
    title="Прибыльный стартап",
    description="Ваш стартап стал прибыльным! Вы создали устойчивый бизнес.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Расширяться дальше",
            next_scene_id="startup_scale",
            effects={"money": 400000, "management": 40, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 35)
        ),
        Choice(
            text="Наслаждаться успехом",
            next_scene_id="startup_exit",
            effects={"money": 2000000, "happiness": 50, "health": 40},
            money_cost=0,
            required_skill=(Subject.FINANCE, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_ipo",
    title="Подготовка к IPO",
    description="Вы готовите компанию к публичному размещению акций. Это исторический момент!",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Успешно провести IPO",
            next_scene_id="startup_exit_success",
            effects={"money": 10000000, "finance": 50, "reputation": 50},
            money_cost=0,
            required_skill=(Subject.FINANCE, 40)
        ),
        Choice(
            text="Сорвать IPO из-за проблем",
            next_scene_id="startup_failure",
            effects={"money": -500000, "reputation": -30, "happiness": -40},
            money_cost=0,
            required_skill=(Subject.FINANCE, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_failure",
    title="Провал стартапа",
    description="Стартап не смог выжить на рынке. Конкуренция оказалась слишком сильной.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Начать новый проект",
            next_scene_id="startup_entry",
            effects={"management": 15, "money": -100000, "happiness": -20},
            money_cost=100000,
            required_skill=(Subject.MANAGEMENT, 20)
        ),
        Choice(
            text="Устроиться в корпорацию",
            next_scene_id="corporate_entry",
            effects={"money": 100000, "reputation": 10, "happiness": 10},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 15)
        )
    ]
))

# =============== ГОСУДАРСТВЕННЫЙ ПУТЬ (12 сцен) ===============

SCENES_DATA.append(Scene(
    scene_id="government_entry",
    title="Первые дни на госслужбе",
    description="Большой кабинет, строгий дресс-код и много бумажной работы.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Строго следовать инструкциям",
            next_scene_id="government_rules",
            effects={"reputation": 15, "management": 10, "happiness": -10},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 5)
        ),
        Choice(
            text="Предложить оптимизацию процессов",
            next_scene_id="government_optimize",
            effects={"economics": 20, "reputation": 5, "money": 5000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 10)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_rules",
    title="Следование правилам",
    description="Вы строго следуете всем инструкциям. Начальство довольное, но скучно.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать в том же духе",
            next_scene_id="government_stagnation",
            effects={"reputation": 10, "happiness": -15, "money": 20000},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 20)
        ),
        Choice(
            text="Проявить инициативу",
            next_scene_id="government_initiative",
            effects={"reputation": 25, "management": 20, "happiness": 10},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 15)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_optimize",
    title="Оптимизация процессов",
    description="Ваше предложение по оптимизации было принято. Вы улучшаете работу отдела.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать улучшения",
            next_scene_id="government_reformer",
            effects={"economics": 30, "reputation": 25, "money": 30000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 25)
        ),
        Choice(
            text="Заняться карьерным ростом",
            next_scene_id="government_promotion",
            effects={"management": 30, "reputation": 20, "money": 40000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_reformer",
    title="Реформатор",
    description="Вы стали известны как реформатор. Ваши идеи меняют работу министерства.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Бороться за должность замминистра",
            next_scene_id="government_deputy",
            effects={"reputation": 40, "money": 150000, "health": -20},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 35)
        ),
        Choice(
            text="Перейти в международную организацию",
            next_scene_id="government_international",
            effects={"reputation": 45, "money": 200000, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_stagnation",
    title="Карьерный застой",
    description="Вы слишком долго оставались на одной должности. Карьера не двигается.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Смириться с положением",
            next_scene_id="stagnation_failure",
            effects={"happiness": -30, "money": 50000, "reputation": -10},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 10)
        ),
        Choice(
            text="Активизироваться",
            next_scene_id="government_initiative",
            effects={"management": 25, "reputation": 20, "happiness": 15},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_initiative",
    title="Проявление инициативы",
    description="Вы проявили инициативу. Начальство это оценило.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Получить повышение",
            next_scene_id="government_promotion",
            effects={"reputation": 30, "money": 60000, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 25)
        ),
        Choice(
            text="Взяться за новый проект",
            next_scene_id="government_reformer",
            effects={"economics": 35, "reputation": 25, "money": 40000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_promotion",
    title="Повышение на госслужбе",
    description="Вы получили повышение! Теперь у вас больше ответственности и власти.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Использовать власть для реформ",
            next_scene_id="government_reformer",
            effects={"economics": 40, "reputation": 35, "money": 80000},
            money_cost=0,
            required_skill=(Subject.ECONOMICS, 35)
        ),
        Choice(
            text="Использовать власть для обогащения",
            next_scene_id="government_corruption",
            effects={"money": 300000, "reputation": -20, "happiness": -15},
            money_cost=0,
            required_skill=(Subject.FINANCE, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_deputy",
    title="Заместитель министра",
    description="Вы стали заместителем министра! Огромная власть и влияние.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Проводить важные реформы",
            next_scene_id="government_minister",
            effects={"reputation": 50, "money": 250000, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 40)
        ),
        Choice(
            text="Заботиться о своем благосостоянии",
            next_scene_id="government_corruption",
            effects={"money": 500000, "reputation": -30, "happiness": -20},
            money_cost=0,
            required_skill=(Subject.FINANCE, 35)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_international",
    title="Международная организация",
    description="Вы перешли работать в международную организацию. Глобальное влияние.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Бороться с глобальными проблемами",
            next_scene_id="government_minister",
            effects={"reputation": 55, "money": 300000, "happiness": 35},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 45)
        ),
        Choice(
            text="Использовать положение для бизнеса",
            next_scene_id="government_business",
            effects={"money": 700000, "reputation": 40, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.FINANCE, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_corruption",
    title="Коррупционные схемы",
    description="Вы вовлеклись в коррупционные схемы. Деньги текут рекой, но это опасно.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать обогащаться",
            next_scene_id="corruption_failure",
            effects={"money": 1000000, "reputation": -50, "happiness": -30},
            money_cost=0,
            required_skill=(Subject.FINANCE, 40)
        ),
        Choice(
            text="Остановиться и уйти",
            next_scene_id="government_exit",
            effects={"money": 200000, "reputation": -10, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.FINANCE, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_business",
    title="Бизнес на связях",
    description="Вы используете свои связи для бизнеса. Деньги есть, но это серая зона.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Легализовать бизнес",
            next_scene_id="investor_success",
            effects={"money": 2000000, "reputation": 35, "happiness": 40},
            money_cost=0,
            required_skill=(Subject.FINANCE, 40)
        ),
        Choice(
            text="Продолжать в том же духе",
            next_scene_id="corruption_failure",
            effects={"money": 3000000, "reputation": -40, "happiness": -25},
            money_cost=0,
            required_skill=(Subject.FINANCE, 45)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="government_exit",
    title="Уход с госслужбы",
    description="Вы ушли с госслужбы. Пора начинать новую жизнь.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Открыть свой бизнес",
            next_scene_id="startup_entry",
            effects={"money": 300000, "management": 30, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        ),
        Choice(
            text="Стать консультантом",
            next_scene_id="consultant_success",
            effects={"reputation": 45, "money": 400000, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 40)
        )
    ]
))

# =============== ОБЩИЕ СЦЕНЫ (финансы, здоровье, карьера) ===============

SCENES_DATA.append(Scene(
    scene_id="finance_investment",
    title="Инвестиционные решения",
    description="У вас есть свободные деньги. Куда инвестировать?",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Недвижимость",
            next_scene_id="real_estate_investment",
            effects={"money": 50000, "finance": 20, "happiness": 15},
            money_cost=100000,
            required_skill=(Subject.FINANCE, 20)
        ),
        Choice(
            text="Акции",
            next_scene_id="stock_investment",
            effects={"money": 80000, "finance": 25, "happiness": 10},
            money_cost=50000,
            required_skill=(Subject.FINANCE, 25)
        ),
        Choice(
            text="Стартапы",
            next_scene_id="startup_investment",
            effects={"money": 200000, "finance": 30, "happiness": 5},
            money_cost=200000,
            required_skill=(Subject.FINANCE, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="real_estate_investment",
    title="Инвестиции в недвижимость",
    description="Вы купили недвижимость. Цены растут, доход стабильный.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать инвестировать",
            next_scene_id="investor_success",
            effects={"money": 300000, "finance": 35, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.FINANCE, 30)
        ),
        Choice(
            text="Продать и выйти",
            next_scene_id="finance_investment",
            effects={"money": 400000, "finance": 25, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.FINANCE, 25)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="stock_investment",
    title="Инвестиции в акции",
    description="Вы играете на бирже. Рынок волатилен, но прибыль может быть огромной.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать торговать",
            next_scene_id="investor_success",
            effects={"money": 500000, "finance": 40, "happiness": 15},
            money_cost=0,
            required_skill=(Subject.FINANCE, 35)
        ),
        Choice(
            text="Потерять деньги",
            next_scene_id="bankruptcy_failure",
            effects={"money": -300000, "finance": 20, "happiness": -30},
            money_cost=0,
            required_skill=(Subject.FINANCE, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="startup_investment",
    title="Инвестиции в стартапы",
    description="Вы инвестируете в перспективные стартапы. Высокий риск, высокая доходность.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Попасть в успешный стартап",
            next_scene_id="investor_success",
            effects={"money": 2000000, "finance": 45, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.FINANCE, 40)
        ),
        Choice(
            text="Потерять инвестиции",
            next_scene_id="bankruptcy_failure",
            effects={"money": -500000, "finance": 15, "happiness": -40},
            money_cost=0,
            required_skill=(Subject.FINANCE, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="health_crisis",
    title="Проблемы со здоровьем",
    description="Постоянный стресс сказался на здоровье. Нужно принимать меры.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Взять длительный отпуск",
            next_scene_id="health_recovery",
            effects={"health": 40, "happiness": 30, "money": -50000},
            money_cost=50000,
            required_skill=None
        ),
        Choice(
            text="Продолжать работать",
            next_scene_id="health_deterioration",
            effects={"health": -30, "money": 50000, "happiness": -25},
            money_cost=0,
            required_skill=None
        ),
        Choice(
            text="Найти баланс",
            next_scene_id="work_life_balance",
            effects={"health": 20, "happiness": 25, "management": 15},
            money_cost=20000,
            required_skill=(Subject.MANAGEMENT, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="health_recovery",
    title="Восстановление здоровья",
    description="Вы взяли отпуск и восстановили силы. Здоровье улучшилось.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Вернуться к работе с новыми силами",
            next_scene_id="career_crossroads",
            effects={"health": 50, "happiness": 40, "money": 30000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 25)
        ),
        Choice(
            text="Изменить образ жизни",
            next_scene_id="balance_success",
            effects={"health": 60, "happiness": 50, "money": 50000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 20)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="health_deterioration",
    title="Ухудшение здоровья",
    description="Игнорирование проблем привело к ухудшению здоровья.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать игнорировать",
            next_scene_id="health_failure",
            effects={"health": -60, "money": 100000, "happiness": -50},
            money_cost=0,
            required_skill=None
        ),
        Choice(
            text="Срочно лечиться",
            next_scene_id="health_recovery",
            effects={"health": 30, "money": -100000, "happiness": 20},
            money_cost=100000,
            required_skill=None
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="work_life_balance",
    title="Баланс работы и жизни",
    description="Вы нашли баланс. Работа и личная жизнь в гармонии.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать в том же духе",
            next_scene_id="balance_success",
            effects={"happiness": 60, "health": 50, "money": 100000},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 30)
        ),
        Choice(
            text="Снова погрузиться в работу",
            next_scene_id="career_crossroads",
            effects={"management": 40, "money": 200000, "health": -20},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 35)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="career_crossroads",
    title="Перекресток карьеры",
    description="Вы достигли определенного уровня. Пора решать, куда двигаться дальше.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Стремиться к топ-менеджменту",
            next_scene_id="executive_path",
            effects={"management": 40, "money": 50000, "health": -25},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 35)
        ),
        Choice(
            text="Основать свой бизнес",
            next_scene_id="entrepreneur_path",
            effects={"economics": 35, "money": -100000, "happiness": 20},
            money_cost=100000,
            required_skill=(Subject.ECONOMICS, 30)
        ),
        Choice(
            text="Стать экспертом-консультантом",
            next_scene_id="consultant_path",
            effects={"reputation": 40, "money": 80000, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="executive_path",
    title="Путь топ-менеджера",
    description="Вы выбрали путь топ-менеджера. Впереди борьба за высшие должности.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Бороться за CEO",
            next_scene_id="internal_ceo_fight",
            effects={"management": 50, "money": 300000, "health": -40},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 45)
        ),
        Choice(
            text="Остаться на текущем уровне",
            next_scene_id="balance_success",
            effects={"happiness": 45, "money": 150000, "health": 30},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="entrepreneur_path",
    title="Путь предпринимателя",
    description="Вы решили основать свой бизнес. Свобода, но и огромные риски.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Открыть бизнес",
            next_scene_id="startup_entry",
            effects={"management": 35, "money": -200000, "happiness": 25},
            money_cost=200000,
            required_skill=(Subject.MANAGEMENT, 30)
        ),
        Choice(
            text="Купить готовый бизнес",
            next_scene_id="startup_profitable",
            effects={"money": -500000, "management": 30, "happiness": 20},
            money_cost=500000,
            required_skill=(Subject.FINANCE, 35)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="consultant_path",
    title="Путь консультанта",
    description="Вы стали независимым консультантом. Свободный график, высокая оплата.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Создать консалтинговую компанию",
            next_scene_id="consultant_success",
            effects={"reputation": 50, "money": 500000, "happiness": 35},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 40)
        ),
        Choice(
            text="Работать независимо",
            next_scene_id="balance_success",
            effects={"reputation": 45, "money": 300000, "happiness": 40},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 35)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="consultant_career",
    title="Карьера консультанта",
    description="Вы стали консультантом. Помогаете компаниям решать сложные проблемы.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Создать свою фирму",
            next_scene_id="consultant_success",
            effects={"reputation": 55, "money": 600000, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 45)
        ),
        Choice(
            text="Работать в международной компании",
            next_scene_id="balance_success",
            effects={"reputation": 50, "money": 400000, "happiness": 35},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 40)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="job_search_mba",
    title="Поиск работы с MBA",
    description="С дипломом MBA вы можете претендовать на высокие должности.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Найти работу в корпорации",
            next_scene_id="corporate_executive",
            effects={"money": 300000, "reputation": 35, "happiness": 25},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 30)
        ),
        Choice(
            text="Найти работу в консалтинге",
            next_scene_id="consultant_career",
            effects={"reputation": 40, "money": 250000, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 35)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="corporate_stay",
    title="Остаться в компании",
    description="Вы решили остаться в текущей компании. Стабильность и предсказуемость.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Добиваться повышения",
            next_scene_id="corporate_executive",
            effects={"management": 40, "money": 150000, "happiness": 20},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 35)
        ),
        Choice(
            text="Наслаждаться стабильностью",
            next_scene_id="balance_success",
            effects={"happiness": 50, "money": 100000, "health": 40},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 30)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="executive_family_balance",
    title="Баланс карьеры и семьи",
    description="Вы нашли баланс между высокой должностью и семейной жизнью.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Продолжать в том же духе",
            next_scene_id="balance_success",
            effects={"happiness": 60, "money": 200000, "health": 45},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 35)
        ),
        Choice(
            text="Снова погрузиться в карьеру",
            next_scene_id="ceo_aspiration",
            effects={"management": 55, "money": 400000, "health": -30},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 45)
        )
    ]
))

# =============== КОНЦОВКИ (12 концовок) ===============

# Успешные концовки
SCENES_DATA.append(Scene(
    scene_id="ceo_success",
    title="Генеральный директор",
    description="Вы стали генеральным директором международной корпорации!\n\nДоход: 5 млн ₽ в год.\nПерсональный водитель, частный самолет, виллы по всему миру.\n\nИтог: карьерный триумф!",
    is_ending=True,
    game_over=False,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="startup_exit_success",
    title="Успешный выход из стартапа",
    description="Вы продали свой стартап за 50 млн ₽!\n\nФинансовая независимость в 35 лет.\nМожете заниматься чем угодно: новые проекты, инвестиции, путешествия.\n\nИтог: финансовая свобода!",
    is_ending=True,
    game_over=False,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="government_minister",
    title="Министр",
    description="Вы стали министром! Ваши реформы меняют страну к лучшему.\n\nВласть, влияние, историческое наследие.\nУважение миллионов людей.\n\nИтог: служение обществу на высшем уровне!",
    is_ending=True,
    game_over=False,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="balance_success",
    title="Гармоничная жизнь",
    description="Вы нашли идеальный баланс между работой, семьей и личной жизнью.\n\nДоход 500 тыс ₽ в месяц, любящая семья, здоровье, хобби.\nРабота 40 часов в неделю, 2 месяца отпуска в год.\n\nИтог: гармония и счастье!",
    is_ending=True,
    game_over=False,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="consultant_success",
    title="Эксперт-консультант",
    description="Вы стали востребованным консультантом с доходом 3 млн ₽ в год.\n\nСвободный график, работа из любой точки мира.\nПомогаете компаниям расти и развиваться.\n\nИтог: свобода и высокий доход!",
    is_ending=True,
    game_over=False,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="investor_success",
    title="Успешный инвестор",
    description="Ваши инвестиции принесли миллионы!\n\nПассивный доход 200 тыс ₽ в месяц.\nНе нужно работать, деньги работают на вас.\n\nИтог: финансовая независимость!",
    is_ending=True,
    game_over=False,
    choices=[]
))

# Неудачные концовки
SCENES_DATA.append(Scene(
    scene_id="burnout_failure",
    title="Профессиональное выгорание",
    description="Постоянные переработки привели к полному выгоранию.\n\nНет энергии, мотивации, здоровья.\nПришлось уйти с работы, начинать все заново.\n\nИтог: цена успеха оказалась слишком высокой.",
    is_ending=True,
    game_over=True,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="bankruptcy_failure",
    title="Банкротство",
    description="Неудачные инвестиции привели к банкротству.\n\nДолги, продажа имущества, кредитная история испорчена.\nНачинать все с нуля в 40 лет тяжело.\n\nИтог: финансовый крах.",
    is_ending=True,
    game_over=True,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="health_failure",
    title="Потеря здоровья",
    description="Пренебрежение здоровьем привело к серьезной болезни.\n\nИнфаркт в 42 года, долгое восстановление.\nДеньги есть, но нет здоровья, чтобы ими пользоваться.\n\nИтог: здоровье важнее денег.",
    is_ending=True,
    game_over=True,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="corruption_failure",
    title="Коррупционный скандал",
    description="Вас уличили в коррупционных схемах.\n\nУголовное дело, потеря репутации, тюрьма.\nВсе накопления конфискованы.\n\nИтог: краткосрочная выгода, долгосрочные проблемы.",
    is_ending=True,
    game_over=True,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="family_failure",
    title="Потеря семьи",
    description="Карьера стоила вам семьи.\n\nРазвод, дети живут с бывшей супругой.\nБольшой дом, но пустой и тихий.\n\nИтог: успех в работе, провал в личной жизни.",
    is_ending=True,
    game_over=True,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="stagnation_failure",
    title="Карьерный застой",
    description="Вы слишком долго оставались на одном месте.\n\nМолодые коллеги обогнали вас.\nНет продвижения, зарплата не растет.\n\nИтог: упущенные возможности.",
    is_ending=True,
    game_over=True,
    choices=[]
))

SCENES_DATA.append(Scene(
    scene_id="startup_exit",
    title="Выход из стартапа",
    description="Вы успешно продали свой стартап.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Начать новый проект",
            next_scene_id="startup_entry",
            effects={"money": 1000000, "management": 40, "happiness": 45},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 35)
        ),
        Choice(
            text="Уйти на пенсию",
            next_scene_id="balance_success",
            effects={"money": 5000000, "happiness": 60, "health": 50},
            money_cost=0,
            required_skill=(Subject.FINANCE, 40)
        )
    ]
))

# =============== ВСПОМОГАТЕЛЬНЫЕ ПЕРЕХОДЫ ===============

SCENES_DATA.append(Scene(
    scene_id="internal_ceo_fight",
    title="Борьба за CEO",
    description="Вы боретесь за должность генерального директора внутри компании.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Победить в борьбе",
            next_scene_id="ceo_success",
            effects={"management": 60, "money": 1000000, "health": -60},
            money_cost=0,
            required_skill=(Subject.MANAGEMENT, 55)
        ),
        Choice(
            text="Проиграть и уйти",
            next_scene_id="consultant_success",
            effects={"reputation": 50, "money": 500000, "happiness": 30},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 45)
        )
    ]
))

SCENES_DATA.append(Scene(
    scene_id="external_ceo_offer",
    title="Предложение CEO",
    description="Другая компания предлагает вам должность генерального директора.",
    is_ending=False,
    game_over=False,
    choices=[
        Choice(
            text="Принять предложение",
            next_scene_id="ceo_success",
            effects={"money": 800000, "reputation": 50, "health": -40},
            money_cost=0,
            required_skill=(Subject.REPUTATION, 45)
        )
    ]
))
