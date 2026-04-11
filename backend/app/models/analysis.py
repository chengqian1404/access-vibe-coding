from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.recording import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    speech_style = Column(Text, nullable=True)
    key_topics = Column(Text, nullable=True)
    total_qa_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    recording = relationship("Recording", back_populates="analyses")
    qa_pairs = relationship("QAPair", back_populates="analysis", cascade="all, delete-orphan")
    key_points = relationship("KeyPoint", back_populates="analysis", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "summary": self.summary,
            "speech_style": self.speech_style,
            "key_topics": self.key_topics,
            "total_qa_count": self.total_qa_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "qa_pairs": [qa.to_dict() for qa in self.qa_pairs] if self.qa_pairs else [],
            "key_points": [kp.to_dict() for kp in self.key_points] if self.key_points else [],
        }


class QAPair(Base):
    __tablename__ = "qa_pairs"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False, default="")
    answer = Column(Text, nullable=True)
    timestamp = Column(Float, nullable=True)
    category = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=True)

    analysis = relationship("Analysis", back_populates="qa_pairs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "question": self.question,
            "answer": self.answer,
            "timestamp": self.timestamp,
            "category": self.category,
            "confidence": self.confidence,
        }


class KeyPoint(Base):
    __tablename__ = "key_points"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False, default="")
    timestamp = Column(Float, nullable=True)
    importance = Column(Integer, nullable=False, default=3)  # 1-5
    category = Column(String(64), nullable=True)

    analysis = relationship("Analysis", back_populates="key_points")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "category": self.category,
        }
