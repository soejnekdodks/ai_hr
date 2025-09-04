from fastapi import APIRouter


router = APIRouter()


@router.post("/api/v1/cvs/")
async def root(cv_id: str):
    pass


@router.get("/api/v1/questions/")
async def get_questions(cv_id: str):
    pass


@router.post("/api/v1/answers/")
async def post_quentions(data: dict):
    pass
