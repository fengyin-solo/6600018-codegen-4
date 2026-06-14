from pydantic import BaseModel
from typing import List, Optional


class OCRResult(BaseModel):
    id: str
    text: str
    bbox: List[float]
    confidence: float
    corrected: Optional[str] = None
    variant_refs: Optional[List[str]] = None


class Document(BaseModel):
    id: str
    name: str
    image_url: str
    results: List[OCRResult]
    created_at: str


class Annotation(BaseModel):
    id: str
    type: str
    bbox: List[float]
    label: str
    content: str


class VariantEntry(BaseModel):
    id: Optional[str] = None
    ancient: str
    modern: str
    definition: str = ""
    pinyin: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[str] = None


class VariantEntryCreate(BaseModel):
    ancient: str
    modern: str
    definition: str = ""
    pinyin: Optional[str] = None
    source: Optional[str] = None


class VariantEntryUpdate(BaseModel):
    ancient: Optional[str] = None
    modern: Optional[str] = None
    definition: Optional[str] = None
    pinyin: Optional[str] = None
    source: Optional[str] = None
