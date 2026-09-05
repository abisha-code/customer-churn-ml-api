import pandas as pd


def run_prediction(model, customer):
    input_df = pd.DataFrame([customer.model_dump(by_alias=True)])
    prediction = model.predict(input_df)[0]
    probability = float(model.predict_proba(input_df)[0][1])
    return prediction, probability
