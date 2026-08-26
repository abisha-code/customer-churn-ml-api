from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionInput(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "Tenure Months": 12,
                "Monthly Charges": 75.50,
                "Total Charges": 906.00,
                "Gender": "Female",
                "Senior Citizen": "No",
                "Partner": "Yes",
                "Dependents": "No",
                "Phone Service": "Yes",
                "Multiple Lines": "No",
                "Internet Service": "Fiber optic",
                "Online Security": "No",
                "Online Backup": "No",
                "Device Protection": "No",
                "Tech Support": "No",
                "Streaming TV": "Yes",
                "Streaming Movies": "Yes",
                "Contract": "Month-to-month",
                "Paperless Billing": "Yes",
                "Payment Method": "Electronic check",
            }
        },
    )

    tenure_months: int = Field(
        ..., ge=0, le=100, alias="Tenure Months",
        description="Number of months the customer has stayed with the company"
    )
    monthly_charges: float = Field(
        ..., gt=0, alias="Monthly Charges",
        description="Current monthly bill amount, must be positive"
    )
    total_charges: float = Field(
        ..., ge=0, alias="Total Charges",
        description="Total amount charged to the customer so far"
    )

    gender: Literal["Male", "Female"] = Field(..., alias="Gender")
    senior_citizen: Literal["Yes", "No"] = Field(..., alias="Senior Citizen")
    partner: Literal["Yes", "No"] = Field(..., alias="Partner")
    dependents: Literal["Yes", "No"] = Field(..., alias="Dependents")
    phone_service: Literal["Yes", "No"] = Field(..., alias="Phone Service")
    multiple_lines: Literal["Yes", "No", "No phone service"] = Field(
        ..., alias="Multiple Lines"
    )
    internet_service: Literal["DSL", "Fiber optic", "No"] = Field(
        ..., alias="Internet Service"
    )
    online_security: Literal["Yes", "No", "No internet service"] = Field(
        ..., alias="Online Security"
    )
    online_backup: Literal["Yes", "No", "No internet service"] = Field(
        ..., alias="Online Backup"
    )
    device_protection: Literal["Yes", "No", "No internet service"] = Field(
        ..., alias="Device Protection"
    )
    tech_support: Literal["Yes", "No", "No internet service"] = Field(
        ..., alias="Tech Support"
    )
    streaming_tv: Literal["Yes", "No", "No internet service"] = Field(
        ..., alias="Streaming TV"
    )
    streaming_movies: Literal["Yes", "No", "No internet service"] = Field(
        ..., alias="Streaming Movies"
    )
    contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        ..., alias="Contract"
    )
    paperless_billing: Literal["Yes", "No"] = Field(..., alias="Paperless Billing")
    payment_method: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ] = Field(..., alias="Payment Method")
