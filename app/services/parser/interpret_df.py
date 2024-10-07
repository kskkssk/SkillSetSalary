def inter(df, shap_dict):

    skills_advice = {}
    skills_improve = {}

    for col in df.columns[9:]:
        if col in shap_dict:
            if (df.loc[:, col] == 0).any() and shap_dict[col][0] < 0:
                skills_advice[col] = shap_dict[col]
            elif (df.loc[:, col] == 1).any() and shap_dict[col][0] > 0:
                skills_improve[col] = shap_dict[col]
    top_skills_advice = dict(sorted(skills_advice.items(), key=lambda item: item[1], reverse=True)[:10])
    top_skills_improve = dict(sorted(skills_improve.items(), key=lambda item: item[1], reverse=True)[:10])

    skills_advice = f'\n• '.join(top_skills_advice.keys())
    skills_advice = '• ' + skills_advice
    skills_improve = f'\n• '.join(top_skills_improve.keys())
    skills_improve = '• ' + skills_improve

    return skills_improve, skills_advice
