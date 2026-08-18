import shutil
# from shared.repository import RepositoryBase
from pathlib import Path
from typing import List
from uuid import UUID

from core.config import settings
from dbase import models
from sqlalchemy.orm import Session
from uploader import domain


class FileRepository(domain.FileIORepositoryBase):
    def __init__(self):
        self.base_path = Path(settings.UPLOAD_PATH)
        self.tmp_path = Path(settings.TMP_PATH)
        self._build_base_path()
        self._build_tmp_path()

    # @override
    def _build_tmp_path(self):
        if not self.tmp_path.exists():
            self.tmp_path.mkdir(exist_ok=True)

    def _tmp_build_path(self, filename, subpath=None) -> Path:
        path = self.tmp_path.joinpath(filename)
        if subpath:
            path = self.tmp_path.joinpath(subpath)
            path.mkdir(exist_ok=True)
            path = path.joinpath(filename)
        return path

    # @override
    def _build_base_path(self):
        if not self.base_path.exists():
            self.base_path.mkdir(exist_ok=True)

    def _build_path(self, filename, subpath=None) -> Path:
        path = self.base_path.joinpath(filename)
        if subpath:
            path = self.base_path.joinpath(subpath)
            path.mkdir(exist_ok=True)
            path = path.joinpath(filename)
        return path

    # @override
    def get_multi(self, subpath=None, skip=0, limit=100):
        pass

    # @override
    def get(self, subpath=None):
        pass

    def save(self, filename, data, subpath=None):
        file_location = self._build_path(filename, subpath)
        try:
            with file_location.open("wb") as buffer:
                shutil.copyfileobj(data, buffer)
        except Exception as e:
            raise Exception(e)

    def tmp_save(self, filename, data, subpath=None):
        file_location = self._tmp_build_path(filename, subpath)
        try:
            with file_location.open("wb") as buffer:
                shutil.copyfileobj(data, buffer)
        except Exception as e:
            raise Exception(e)

    def replace(self, old_filename, new_filename, data, subpath=None):
        old_file_location = self._build_path(old_filename, subpath)

        if old_file_location.exists():
            old_file_location.unlink()
            self.save(new_filename, data, subpath)

    def remove(self, filename, subpath=None):
        file_location = self._build_path(filename, subpath)
        print(file_location)
        if file_location.exists():
            file_location.unlink()

    def count(self) -> int:
        pass


class UploadedFileRepository(domain.UploadFileRepositoryBase):
    def __init__(self, session: Session):
        self.session = session

    def get(self, *, id: UUID) -> domain.UploadFile:
        db_obj = (
            self.session.query(models.UploadedFile)
            .filter(models.UploadedFile.id == id)
            .first()
        )
        return db_obj

    def get_multi_by_user_id(
        self, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[domain.UploadFile]:
        db_obj = (
            self.session.query(models.UploadedFile)
            .filter(models.UploadedFile.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        db_obj = [db.to_entity() for db in db_obj]
        return db_obj

    def remove(self, id: UUID) -> None:
        db_image: models.UploadedFile = (
            self.session.query(models.UploadedFile)
            .filter(models.UploadedFile.id == id)
            .first()
        )
        self.session.delete(db_image)
        self.session.commit()
        return db_image.to_entity()

    def create(self, *, obj_in: domain.UploadFile) -> domain.UploadFile:
        db_obj = models.UploadedFile(
            original_filename=obj_in.original_filename,
            saved_filename=obj_in.saved_filename,
            content_type=obj_in.content_type,
            user_id=obj_in.user_id,
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj.to_entity()

    def update(
        self, *, id: UUID, db_obj: models.UploadedFile, obj_in: domain.UploadFile
    ) -> domain.UploadFile:
        pass

    def count(self, user_id: UUID) -> int:
        total = (
            self.session.query(models.UploadedFile)
            .filter(models.UploadedFile.user_id == user_id)
            .count()
        )
        return total

    def get_file_download(self, user_id: UUID, img_id: UUID) -> domain.UploadFile:
        db_image = (
            self.session.query(models.UploadedFile)
            .filter(
                models.UploadedFile.user_id == user_id, models.UploadedFile.id == img_id
            )
            .first()
        )
        return db_image

    def search(self):
        pass


class MilvusRepository:
    pass