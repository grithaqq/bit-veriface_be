from typing import List
from uuid import UUID

from core.config import settings
from dbase.milvus.connection import client
from deepface import DeepFace
from shared import paginator
from uploader import domain

import logging
log = logging.getLogger("uvicorn")

class UploadFileUsecase:
    def __init__(
        self,
        file_repo: domain.FileIORepositoryBase,
        dbase_repo: domain.UploadFileRepositoryBase,
    ):
        self.file_repo = file_repo
        self.dbase_repo = dbase_repo

    def get_all_files_by_superuser_id(self):
        pass

    def get_file_download(self, user_id, img_id) -> domain.UploadFile:
        image = self.dbase_repo.get_file_download(user_id, img_id)
        base_path = str(self.file_repo.base_path)
        save_filename = image.saved_filename
        path = base_path + "/" + str(user_id) + "/" + save_filename
        return [image, path]

    def get_multi_by_user_id(
        self, user_id: UUID, subpath: str, skip: int = 0, limit: int = 100
    ) -> List[domain.ListUploadedFile]:
        total = self.dbase_repo.count(user_id=user_id)
        files = self.dbase_repo.get_multi_by_user_id(
            user_id=user_id, skip=skip, limit=limit
        )
        pagination = paginator.paginate_data(total=total, skip=skip, limit=limit)
        return domain.ListUploadedFile(
            status=200,
            message="Get files successfully",
            data=files,
            pagination=pagination,
        )

    def get(self, id: UUID, subpath: str) -> domain.UploadFile:
        db_obj = self.dbase_repo.get(id=id)
        return db_obj.to_entity()

    def save(
        self, upfile: domain.UploadFile, data: bytes, subpath: str
    ) -> domain.UploadFile:
        self.file_repo.save(upfile.saved_filename, data, subpath)
        result = self.dbase_repo.create(obj_in=upfile)
        path = self.file_repo.base_path.joinpath(subpath).joinpath(
            upfile.saved_filename
        )
        embedding = DeepFace.represent(img_path=path, model_name="Facenet")
        dt = {
            "vector": embedding[0]["embedding"],
            "img_path": str(path),
            "img_id": str(result.id),
            "user_id": str(subpath),
        }
        client.load_collection("deepface_collection")
        client.insert(collection_name=settings.MILVUS_FIRST_COLLECTION, data=[dt])
        return result

    def replace(
        self, old_filename: str, new_filename: str, data: bytes, subpath: str
    ) -> domain.UploadFile:
        self.file_repo.replace(old_filename, new_filename, data, subpath)
        return self.dbase_repo.update(old_filename, new_filename, subpath)

    def remove(self, subpath: str, id: UUID) -> domain.UploadFile:
        upload_file = self.dbase_repo.get(id=id)
        self.file_repo.remove(filename=upload_file.saved_filename, subpath=subpath)
        client.delete(collection_name="deepface_collection", filter=f"img_id == '{id}'")
        return self.dbase_repo.remove(id=id)

    def update(self, id: UUID, obj_in: domain.UploadFile) -> domain.UploadFile:
        upload_file = self.dbase_repo.get(id=id)
        return self.dbase_repo.update(id=id, db_obj=upload_file, obj_in=obj_in)

    def search(
        self,
        upfile: domain.UploadFile,
        data: bytes,
        subpath: str,
        skip: int = 0,
        limit: int = 100,
    ):
        path = self.file_repo.tmp_path.joinpath(subpath).joinpath(upfile.saved_filename)
        self.file_repo.tmp_save(upfile.saved_filename, data, subpath)
        embedding = DeepFace.represent(img_path=str(path), model_name="Facenet")
        query_image = embedding[0]["embedding"]
        client.load_collection("deepface_collection")
        results = client.search(
            "deepface_collection",
            data=[query_image],
            output_fields=["img_path", "user_id", "img_id"],
        )
        # log.info(results)

        paginate = paginator.paginate_data(
            total=len(results[0]), skip=skip, limit=limit
        )
        data = {
            "status": 200,
            "message": "Successfully searched!",
            "data": results[0],
            "pagination": paginate,
        }
        return data
