from fastapi import APIRouter

from app.db.client import get_supabase

router = APIRouter(prefix="/api")


@router.get("/subjects")
async def list_subjects():
    result = (
        get_supabase()
        .table("materia")
        .select("id_materia, nombre, codigo, area_disciplinar")
        .order("nombre")
        .execute()
    )
    return {"subjects": result.data}
