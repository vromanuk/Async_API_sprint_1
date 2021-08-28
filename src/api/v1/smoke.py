from fastapi import APIRouter

router = APIRouter(
    prefix="/smoke",
)


@router.get(
    "/",
    summary="Минимальный healthcheck сервера",
    response_description="200 OK, если сервер принимает и обрабатывает сообщения",
    tags=["smoke"],
)
def smoke():
    return {"message": "OK"}
