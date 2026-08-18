import uuid
# from src.shared.paginator import Pagination, paginate_data
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import UUID

from core import deps
from core.config import settings
from dbase import models
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from shared import schemas as shr_schemas
from sqlalchemy.orm import Session
from uploader import domain, repository, schemas, usecase

router = APIRouter()


def uploader_usecase(session: Session = Depends(deps.get_db)):
    dbase_repo = repository.UploadedFileRepository(session)
    file_repo = repository.FileRepository()
    ucase = usecase.UploadFileUsecase(file_repo, dbase_repo)
    return ucase


@router.get("/file/{file_id}")
async def read_file(
    file_id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UploadFileUsecase = Depends(uploader_usecase),
) -> Any:
    file = ucase.get(id=file_id, subpath="")
    data = schemas.UploadedFileBase(**asdict(file))
    file_schema = schemas.UploadedFileGetResponse(
        status=201, message="File retrieved successfully!", data=data
    )
    return file_schema


@router.get("/files")
async def read_files(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UploadFileUsecase = Depends(uploader_usecase),
) -> Any:
    upload_files = ucase.get_multi_by_user_id(
        user_id=current_user.id, skip=skip, limit=limit, subpath=""
    )
    return schemas.UploadedFileListResponse(**asdict(upload_files))


@router.post("/upload")
async def create_upload_file(
    file: UploadFile,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UploadFileUsecase = Depends(uploader_usecase),
) -> Any:
    if not file:
        raise HTTPException(status_code=404, detail=f"'data_input' argument invalid!")

    if not (file.content_type == "image/jpeg" or file.content_type == "image/png"):
        raise HTTPException(
            status_code=404,
            detail=f"'content_type' is not accepted, send only jpg or png image!",
        )
    ori_ext = Path(file.filename).suffix
    input_data = {
        "original_filename": str(file.filename),
        "saved_filename": str(uuid.uuid4()) + ori_ext,
        "content_type": str(file.content_type),
        "user_id": str(current_user.id),
    }

    upfile = domain.UploadFile(**input_data)
    uploader = ucase.save(upfile=upfile, data=file.file, subpath=str(current_user.id))
    data = schemas.UploadedFileBase(
        original_filename=uploader.original_filename,
        saved_filename=uploader.saved_filename,
        content_type=uploader.content_type,
        user_id=uploader.user_id,
        created_at=uploader.created_at,
        updated_at=uploader.modified_at,
    )
    return shr_schemas.BaseResponse(
        status=200, message="File uploaded successfully!", data=data
    )


@router.delete("/file/{file_id}")
async def remove_file(
    file_id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UploadFileUsecase = Depends(uploader_usecase),
):
    u = ucase.remove(id=file_id, subpath=str(current_user.id))
    return schemas.UploadedFileDelete(
        status=200, message="Successfully deleted!", data=u.original_filename
    )


@router.get("/file/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    ucase: usecase.UploadFileUsecase = Depends(uploader_usecase),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
):
    u = ucase.get_file_download(user_id=current_user.id, img_id=file_id)
    return FileResponse(
        path=u[1], media_type=u[0].content_type, filename=u[0].saved_filename
    )


@router.post("/search")
def search_image(
    file: UploadFile,
    ucase: usecase.UploadFileUsecase = Depends(uploader_usecase),
    skip: int = 0,
    limit: int = 100,
    max_distance: float = 70,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
):
    if not file:
        raise HTTPException(status_code=404, detail=f"'data_input' argument invalid!")
    if not (file.content_type == "image/jpeg" or file.content_type == "image/png"):
        raise HTTPException(
            status_code=404,
            detail=f"'content_type' is not accepted, send only jpg or png image!",
        )
    ori_ext = Path(file.filename).suffix

    ori_ext = Path(file.filename).suffix
    input_data = {
        "original_filename": str(file.filename),
        "saved_filename": str(uuid.uuid4()) + ori_ext,
        "content_type": str(file.content_type),
        "user_id": str(current_user.id),
    }
    upfile = domain.UploadFile(**input_data)
    uploader = ucase.search(
        upfile=upfile,
        data=file.file,
        subpath=str(current_user.id),
        skip=skip,
        limit=limit,
    )
    
    sorted_array = sorted(uploader["data"], key=lambda x: x['distance'], reverse=False)
    data = [
        {
            "img_path": f"{settings.SERVER_NAME}/{u['entity']['img_path']}",
            "img_id": UUID(u["entity"]["img_id"]),
            "user_id": UUID(u["entity"]["user_id"]),
            "distance": u["distance"],
        }

        for u in sorted_array if u['distance'] <= max_distance]
    pagination = {
        "total_item": uploader["pagination"].total_item,
        "total_page": uploader["pagination"].total_page,
        "page_size": uploader["pagination"].page_size,
        "curr_page": uploader["pagination"].curr_page,
        "prev_page": uploader["pagination"].prev_page,
        "next_page": uploader["pagination"].next_page,
        "has_prev": uploader["pagination"].has_prev,
        "has_next": uploader["pagination"].has_next,
    }
    return schemas.ListUploadedFileInMilvus(
        status=200, message="Image search successful!", data=data, pagination=pagination
    )
