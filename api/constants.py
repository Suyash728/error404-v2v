from enum import Enum


class Symptom(str, Enum):
    CRAMPS = "cramps"
    BLOATING = "bloating"
    HEADACHE = "headache"
    ACNE = "acne"
    FATIGUE = "fatigue"
    TENDER_BREASTS = "tender_breasts"
    BACK_PAIN = "back_pain"
    NAUSEA = "nausea"
    MOOD_SWINGS = "mood_swings"
    INSOMNIA = "insomnia"
    CRAVINGS = "cravings"
    SPOTTING = "spotting"
    DIARRHEA = "diarrhea"
    CONSTIPATION = "constipation"
