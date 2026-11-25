# Hozircha tayyor savollar bazasi mavjud bo‘lgan fanlar.
SUBJECT_RANGES = {
    "Matematika": (1, 11),
    "Ona tili": (1, 11),
    "Ingliz tili": (1, 11),
}

def subjects_for_grade(grade: int):
    return [name for name, (low, high) in SUBJECT_RANGES.items()
            if low <= grade <= high]
