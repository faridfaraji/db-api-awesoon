import enum


class DocType(enum.Enum):
    PRODUCT = "PRODUCT"
    CATEGORY = "CATEGORY"
    ORDER = "ORDER"
    POLICY = "POLICY"
    PAGE = "PAGE"
    BLOG = "BLOG"


class ScanStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class TriggerType(enum.Enum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    WEBHOOK = "WEBHOOK"


class MessageType(enum.Enum):
    AI = "AI"
    USER = "USER"
