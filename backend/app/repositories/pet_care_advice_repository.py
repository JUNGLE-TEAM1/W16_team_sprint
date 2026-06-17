from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.pet_care_advice import (
    PET_CARE_ADVICE_STATUS_COMPLETED,
    PET_CARE_ADVICE_STATUS_STALE,
    PetCareAdvice,
)
from backend.app.schemas.ai import PetCareAdviceResponse


class PetCareAdviceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_post_id(self, post_id: int) -> PetCareAdvice | None:
        statement = select(PetCareAdvice).where(PetCareAdvice.post_id == post_id)
        return self.db.execute(statement).scalar_one_or_none()

    def upsert_completed(self, post_id: int, response: PetCareAdviceResponse) -> PetCareAdvice:
        advice = self.get_by_post_id(post_id)
        source_payload = [source.model_dump() for source in response.sources]
        now = datetime.utcnow()
        if advice is None:
            advice = PetCareAdvice(post_id=post_id)
            self.db.add(advice)

        advice.answer = response.answer
        advice.action_plan = response.action_plan
        advice.safety_note = response.safety_note
        advice.sources = source_payload
        advice.hospital_candidates = [
            hospital.model_dump() for hospital in response.hospital_candidates
        ]
        advice.status = PET_CARE_ADVICE_STATUS_COMPLETED
        advice.generated_at = now
        self.db.flush()
        self.db.refresh(advice)
        return advice

    def mark_stale(self, post_id: int) -> None:
        advice = self.get_by_post_id(post_id)
        if advice is None:
            return
        advice.status = PET_CARE_ADVICE_STATUS_STALE
        self.db.flush()
