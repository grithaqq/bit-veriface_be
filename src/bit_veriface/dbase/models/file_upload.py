import uuid

from dbase.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uploader import domain


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    original_filename = Column(String, nullable=False)
    saved_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="uploaded_files")

    def to_entity(self) -> domain.UploadFile:
        return domain.UploadFile(
            id=uuid.UUID(str(self.id)),
            original_filename=self.original_filename,
            saved_filename=self.saved_filename,
            content_type=self.content_type,
            created_at=self.created_at,
            modified_at=self.updated_at,
            user_id=uuid.UUID(str(self.user_id)),
        )
