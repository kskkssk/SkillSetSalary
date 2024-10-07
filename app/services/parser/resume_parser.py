import re

global_target_mean = 136153.294


def extract_skills(text):
    skills_list = []
    skills_start = re.search(r'Навыки', text, re.IGNORECASE)
    if skills_start:
        start_idx = skills_start.end()
        skills_text = text[start_idx:].strip()

        skills_start_two = re.search(r'Навыки', skills_text, re.IGNORECASE)
        if skills_start_two:
            start_idx = skills_start_two.end()
            skills_text = skills_text[start_idx:].strip()

        end_of_skills = re.search(
            r'(Дополнительная информация|Личные качества|Обо мне|Образование|Опыт работы|Желаемая должность и зарплата)',
            skills_text, re.IGNORECASE)
        if end_of_skills:
            skills_text = skills_text[:end_of_skills.start()].strip()

        skills_text = re.sub(r'\s{2,}', ', ', skills_text)  # Убираем лишние пробелы
        skills_text = skills_text.replace('- ', '')  # Убираем тире
        skills_text = skills_text.replace('\n', ', ')  # Заменяем переносы строк на запятые
        skills_list = skills_text.split(', ')  # Превращаем текст в список

        reg = re.compile('[^a-zA-Zа-яА-Я ]')
        skills_list = [reg.sub('', skill).strip() for skill in skills_list]

    return skills_list if skills_list is not None else ''


def extract_exp(text):
    exp_start = re.search(r'Опыт работы', text, re.IGNORECASE)
    if exp_start:
        start_idx = exp_start.end()
        exp_text = text[start_idx:].strip()
        end_of_exp = re.search(r'(года|год|лет)', exp_text, re.IGNORECASE)
        if end_of_exp:
            exp_text = exp_text[:end_of_exp.start()].strip()
        number = re.findall(r'\d+', exp_text)
        if number:
            for n in number:
                return int(n)


def check_experience(exp):
    return 0 if exp == 0 or exp is None else exp


def extract_emp(text):
    emp_start = re.search(r'Занятость', text, re.IGNORECASE)
    emp_text = None  # Initialize emp_text to None
    if emp_start:
        start_idx = emp_start.end()
        emp_text = text[start_idx:].strip()
        end_of_emp = re.search(r'(занятость|стажировка|работа)', emp_text, re.IGNORECASE)
        if end_of_emp:
            emp_text = emp_text[:end_of_emp.end()].strip()
        emp_text = emp_text.replace(': ', '')

    return emp_text if emp_text else 0


def extract_sch(text):
    schedule_start = re.search(r'График работы', text, re.IGNORECASE)
    schedule_text = None  # Initialize schedule_text to None
    if schedule_start:
        start_idx = schedule_start.end()
        schedule_text = text[start_idx:].strip()
        end_of_schedule = re.search(r'(работа|день|график|метод)', schedule_text, re.IGNORECASE)
        if end_of_schedule:
            schedule_text = schedule_text[:end_of_schedule.end()].strip()
        schedule_text = schedule_text.replace(': ', '')

    return schedule_text if schedule_text else global_target_mean


def extract_area(text):
    city = None
    exp_start = re.search(r'(Проживает|Город проживания)', text, re.IGNORECASE)
    if exp_start:
        start_idx = exp_start.end()
        exp_text = text[start_idx:].strip()
        city_match = re.search(r'\b\w+', exp_text)
        if city_match:
            city = city_match.group(0)

    return city if city else global_target_mean


def extract_specializations(text):
    specializations = None
    specializations_start = re.search(r'Специализации:', text, re.IGNORECASE)

    if specializations_start:
        start_idx = specializations_start.end()
        specializations_section = text[start_idx:].strip()
        lines = re.findall(r'—\s*(.*)', specializations_section)
        if lines:
            specializations = lines[0].strip()

    if specializations is None:
        specializations_start = re.search(r'Должность:', text, re.IGNORECASE)
        if specializations_start:
            start_idx = specializations_start.end()
            specializations_section = text[start_idx:].strip()
            line_match = re.search(r'([^\n]+)', specializations_section)
            if line_match:
                specializations = line_match.group(1).strip()

    return specializations if specializations else global_target_mean

