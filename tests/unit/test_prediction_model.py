from app.db.base import Base
from app.db.models.prediction import Prediction


def test_prediction_model_registers_expected_schema() -> None:
    table = Prediction.__table__

    assert table.metadata is Base.metadata
    assert set(table.columns.keys()) == {
        "id",
        "message_ciphertext",
        "label",
        "spam_probability",
        "threshold",
        "message_length",
        "created_at",
    }
    assert all(not column.nullable for column in table.columns)
    assert table.c.created_at.server_default is not None
    assert {
        constraint.name
        for constraint in table.constraints
        if constraint.name is not None
    } == {
        "ck_predictions_label",
        "ck_predictions_message_length",
        "ck_predictions_spam_probability",
        "ck_predictions_threshold",
    }
