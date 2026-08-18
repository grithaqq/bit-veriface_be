import logging

# from core.events import create_start_app_handler
import router
from core.config import settings
# from api.api_v1.api import api_router
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from core.deps import get_current_username

# Suppress specific warnings
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# warnings.filterwarnings("ignore", category=urllib3.exceptions.SecurityWarning)

# Adjust logging levels
log = logging.getLogger("uvicorn")
# log.setLevel(logging.INFO)


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=None,  # Disable default openapi.json
        docs_url=None,  # Disable default docs
        redoc_url=None  # Disable default redoc
    )

    @application.get("/docs", include_in_schema=False)
    async def get_documentation(username: str = Depends(get_current_username)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title=settings.PROJECT_NAME)

    @application.get("/openapi.json", include_in_schema=False)
    async def openapi():
        return get_openapi(title=settings.PROJECT_NAME, version="1.0.0", routes=application.routes)

    application.mount(
        "/upload_files",
        StaticFiles(directory=settings.UPLOAD_PATH),
        name="upload_files",
    )

    #Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        list_allowed_origins = settings.BACKEND_CORS_ORIGINS
        log.info(f"Allowed CORS origins: {list_allowed_origins}")
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list_allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # application.add_event_handler("startup", create_start_app_handler(application))
    application.include_router(router.api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    # init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
