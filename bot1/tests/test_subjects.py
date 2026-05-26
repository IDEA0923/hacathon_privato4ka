from services.users import (
    _build_subjects_code,
    append_subject_code,
    subject_codes_to_labels,
)


def test_build_subjects_code_uses_three_letter_codes() -> None:
    assert _build_subjects_code("math") == "mat"
    assert _build_subjects_code("Информатика") == "inf"
    assert _build_subjects_code("математика + физика") == "matphy"
    assert _build_subjects_code("math, ") == "mat"


def test_append_subject_keeps_existing_and_avoids_duplicates() -> None:
    assert append_subject_code("mat", "inf") == ("matinf", True)
    assert append_subject_code("matinf", "inf") == ("matinf", False)


def test_subject_labels_for_combined_storage() -> None:
    assert subject_codes_to_labels("matinfphy") == "Математика, Информатика, Физика"
