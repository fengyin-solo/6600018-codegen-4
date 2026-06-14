import uuid
import time
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.ocr_service import (
    run_ocr,
    list_variant_entries,
    get_variant_entry,
    create_variant_entry,
    update_variant_entry,
    delete_variant_entry,
    find_matching_entries,
)
from app.models.schemas import VariantEntryCreate, VariantEntryUpdate

router = APIRouter()


@router.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    """Upload an image and run OCR."""
    content = await file.read()
    results = run_ocr(content, file.filename or "unknown")
    return {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "results": results,
        "timestamp": time.time(),
    }


@router.get("/ocr/variants")
def get_variants():
    """Get variant character dictionary."""
    from app.services.ocr_service import VARIANT_DICT
    return VARIANT_DICT


@router.get("/variants")
def list_variants(
    ancient: Optional[str] = Query(None, description="按异体字搜索"),
    modern: Optional[str] = Query(None, description="按对照字搜索"),
):
    """列出异体字词条，支持搜索。"""
    return list_variant_entries(ancient=ancient, modern=modern)


@router.get("/variants/{entry_id}")
def get_variant(entry_id: str):
    """获取单个异体字词条详情。"""
    entry = get_variant_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="词条不存在")
    return entry


@router.post("/variants", status_code=201)
def create_variant(data: VariantEntryCreate):
    """创建新的异体字词条。"""
    return create_variant_entry(data)


@router.put("/variants/{entry_id}")
def update_variant(entry_id: str, data: VariantEntryUpdate):
    """更新异体字词条。"""
    entry = update_variant_entry(entry_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="词条不存在")
    return entry


@router.delete("/variants/{entry_id}", status_code=204)
def delete_variant(entry_id: str):
    """删除异体字词条。"""
    if not delete_variant_entry(entry_id):
        raise HTTPException(status_code=404, detail="词条不存在")
    return None


@router.get("/variants/match/{text}")
def match_variants(text: str):
    """在文本中匹配已有的异体字词条。"""
    return find_matching_entries(text)


@router.post("/ocr/search")
def search_text(query: str):
    """Search across all OCR results."""
    return {"query": query, "results": []}
