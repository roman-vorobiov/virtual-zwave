from enum import Enum


class SecurityLevel(Enum):
    NONE = "NONE"
    GRANTED = "HIGHEST_GRANTED"
    SUPPORTED = "HIGHEST_SUPPORTED"
