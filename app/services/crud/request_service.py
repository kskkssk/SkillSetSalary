from catboost import CatBoostRegressor
import shap
import gc
import pandas as pd
from services.parser.upload_cv import upload
from services.parser.resume_parser import extract_specializations, extract_skills, check_experience
from services.parser.resume_parser import extract_exp, extract_sch, extract_area, extract_emp
from services.parser.fill_df import init_df, emp_operations, make_row, load_skills_from_json, ecd_skills
from services.parser.interpret_df import inter


class RequestService:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def validate(pdf_path: str):
        try:
            pdf_path.endswith('.pdf')
            return pdf_path
        except ValueError:
            raise ValueError('Expected file in format: .pdf')

    @staticmethod
    def load_model() -> CatBoostRegressor:
        model_path = 'cb_super'
        model = CatBoostRegressor()
        model.load_model(model_path)
        return model

    @staticmethod
    def interpretate(model, df):
        explainer = shap.Explainer(model)
        shap_dict = {}

        batch_size = 100
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i + batch_size]
            shap_values = explainer(batch_df)
            shap_values_df = pd.DataFrame(shap_values.values, columns=batch_df.columns)

            for col in batch_df.columns:
                if col not in shap_dict:
                    shap_dict[col] = []
                shap_dict[col].extend(shap_values_df[col].tolist())

        return shap_dict

    def process(self, pdf_path: str):
        pdf_path = self.validate(pdf_path)  # check if file is .pdf
        data = upload(pdf_path)  # get text from .pdf

        # parse data from text
        specializations = extract_specializations(data)
        skills = extract_skills(data)
        experience = extract_exp(data)
        experience = check_experience(experience)
        emp = extract_emp(data)
        city = extract_area(data)
        schedule = extract_sch(data)

        # create df
        df = init_df()
        # process the data
        emp_dict = emp_operations(emp)
        df = make_row(df, skills, city, schedule, experience, specializations, emp_dict)
        skills_list = load_skills_from_json()
        ecd_skills(df, skills_list)
        final_df = df.drop('skills', axis=1)
        del df
        gc.collect()
        return final_df

    def predict(self, pdf_path: str):
        final_df = self.process(pdf_path)
        model = self.load_model()
        salary = model.predict(final_df)
        salary = float(salary[0])
        return salary

    def interpretate_pred(self, pdf_path: str):
        final_df = self.process(pdf_path)
        model = self.load_model()
        shap_dict = self.interpretate(model, final_df)
        skills_improve, skills_advice = inter(final_df, shap_dict)
        del final_df
        del model
        gc.collect()
        return skills_improve, skills_advice
