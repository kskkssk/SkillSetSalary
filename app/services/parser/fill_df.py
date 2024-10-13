import pandas as pd
import json
import os


def init_df():
    df = pd.DataFrame(columns=[
     'area', 'schedule', 'experience',
     'professional_roles', 'skills',
     'employment_Проектная работа',
     'employment_Стажировка', 'employment_Частичная занятость',
     'experience^3', 'has_experience'
    ])
    return df


def emp_operations(emp):
    emp_dict = {'employment_Проектная работа': 0,
                'employment_Стажировка': 0,
                'employment_Частичная занятость': 0}

    for key in emp_dict:
        if isinstance(emp, str):
            if key[11:].lower() == emp.lower():
                emp_dict[key] = 1
    return emp_dict


def open_dict(json_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, json_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    return d


def make_row(df, skills, city, schedule, experience, specializations, emp_dict):
    dict_schedule = open_dict('dict_schedule.json')
    dict_area = open_dict('dict_area.json')
    dict_prof = open_dict('dict_prof.json')
    ski = None
    if skills:
        ski = ','.join([skill.lower() for skill in skills])
    new_data = {
     'area': dict_area.get(city),
     'schedule': dict_schedule.get(schedule),
     'experience': experience,
     'professional_roles': dict_prof.get(specializations),
     'skills': ski if ski else '',
     'employment_Проектная работа': emp_dict['employment_Проектная работа'],
     'employment_Стажировка': emp_dict['employment_Стажировка'],
     'employment_Частичная занятость': emp_dict['employment_Частичная занятость'],
     'experience^3': experience ** 3 if experience else 0,
     'has_experience': 1 if experience else 0
    }

    new_row = pd.DataFrame([new_data])
    df = pd.concat([df, new_row], ignore_index=True)
    return df


def load_skills_from_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'skills_list.json')

    with open(file_path, 'r', encoding='utf-8') as file:
        skills_list = json.load(file)

    return skills_list


def ecd_skills(df, skills):
    df['skills'] = df['skills'].fillna('')
    df['skills'] = df['skills'].apply(lambda x: [skill.strip() for skill in x.split(',')])
    for skill_name in skills:
        df[skill_name] = df['skills'].apply(lambda x: 1 if skill_name in x else 0)
    return df
