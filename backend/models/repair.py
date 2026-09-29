from typing import List, Optional

from pydantic import BaseModel


class QuestionOption(BaseModel):
    value: str
    label: str
    sub: Optional[str] = None


class Question(BaseModel):
    key: str
    label: str
    options: List[QuestionOption]


class Repair(BaseModel):
    id: str
    name: str
    examples: str
    questions: List[Question]
