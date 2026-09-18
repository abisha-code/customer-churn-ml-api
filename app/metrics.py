from prometheus_client import Counter

prediction_counter = Counter(
    "churn_predictions_total",
    "Total number of successful churn predictions made, labeled by predicted class",
    ["predicted_class"],
)
