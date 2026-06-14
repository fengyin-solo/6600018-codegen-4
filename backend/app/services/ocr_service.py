"""OCR service using mock data (replace with PaddleOCR for production)."""
import io
import random
import uuid
import time
from typing import List, Dict, Any, Optional
from app.models.schemas import VariantEntry, VariantEntryCreate, VariantEntryUpdate

# Variant character mapping (traditional/ancient → simplified)
VARIANT_DICT: Dict[str, str] = {
    '説': '说', '學': '学', '習': '习', '遠': '远', '樂': '乐',
    '書': '书', '國': '国', '東': '东', '長': '长', '門': '门',
}

VARIANT_ENTRIES: Dict[str, VariantEntry] = {}


def _init_default_entries():
    defaults = [
        VariantEntry(ancient='説', modern='说', definition='同"说"，喜悦、高兴', pinyin='yuè', source='论语·学而'),
        VariantEntry(ancient='學', modern='学', definition='学习，效法', pinyin='xué', source='论语·学而'),
        VariantEntry(ancient='習', modern='习', definition='温习，练习', pinyin='xí', source='论语·学而'),
        VariantEntry(ancient='遠', modern='远', definition='距离长，久远', pinyin='yuǎn', source='论语·学而'),
        VariantEntry(ancient='樂', modern='乐', definition='快乐，喜悦', pinyin='lè', source='论语·学而'),
        VariantEntry(ancient='書', modern='书', definition='书籍，书写', pinyin='shū'),
        VariantEntry(ancient='國', modern='国', definition='国家，邦国', pinyin='guó'),
        VariantEntry(ancient='東', modern='东', definition='东方，东部', pinyin='dōng'),
        VariantEntry(ancient='長', modern='长', definition='长久，年长', pinyin='cháng/zhǎng'),
        VariantEntry(ancient='門', modern='门', definition='门户，门径', pinyin='mén'),
    ]
    for e in defaults:
        e.id = str(uuid.uuid4())
        e.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        VARIANT_ENTRIES[e.id] = e


_init_default_entries()


def rebuild_variant_dict():
    global VARIANT_DICT
    VARIANT_DICT = {e.ancient: e.modern for e in VARIANT_ENTRIES.values()}


def list_variant_entries(ancient: Optional[str] = None, modern: Optional[str] = None) -> List[VariantEntry]:
    results = list(VARIANT_ENTRIES.values())
    if ancient:
        results = [e for e in results if ancient in e.ancient]
    if modern:
        results = [e for e in results if modern in e.modern]
    results.sort(key=lambda e: e.created_at or '', reverse=True)
    return results


def get_variant_entry(entry_id: str) -> Optional[VariantEntry]:
    return VARIANT_ENTRIES.get(entry_id)


def create_variant_entry(data: VariantEntryCreate) -> VariantEntry:
    entry = VariantEntry(
        id=str(uuid.uuid4()),
        ancient=data.ancient,
        modern=data.modern,
        definition=data.definition,
        pinyin=data.pinyin,
        source=data.source,
        created_at=time.strftime('%Y-%m-%d %H:%M:%S'),
    )
    VARIANT_ENTRIES[entry.id] = entry
    rebuild_variant_dict()
    return entry


def update_variant_entry(entry_id: str, data: VariantEntryUpdate) -> Optional[VariantEntry]:
    entry = VARIANT_ENTRIES.get(entry_id)
    if not entry:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)
    rebuild_variant_dict()
    return entry


def delete_variant_entry(entry_id: str) -> bool:
    if entry_id in VARIANT_ENTRIES:
        del VARIANT_ENTRIES[entry_id]
        rebuild_variant_dict()
        return True
    return False


def find_matching_entries(text: str) -> List[VariantEntry]:
    matched = []
    chars = set(text)
    for entry in VARIANT_ENTRIES.values():
        if entry.ancient in chars:
            matched.append(entry)
    return matched


# Mock OCR results for demonstration
MOCK_RESULTS: List[Dict[str, Any]] = [
    {"id": "r1", "text": "子曰", "bbox": [50, 30, 80, 40], "confidence": 0.95},
    {"id": "r2", "text": "學而時習之", "bbox": [50, 80, 200, 40], "confidence": 0.88},
    {"id": "r3", "text": "不亦説乎", "bbox": [50, 130, 160, 40], "confidence": 0.91},
    {"id": "r4", "text": "有朋自遠方來", "bbox": [50, 180, 240, 40], "confidence": 0.87},
    {"id": "r5", "text": "不亦樂乎", "bbox": [50, 230, 160, 40], "confidence": 0.93},
]


def run_ocr(image_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Run OCR on an image.
    In production, replace with:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        result = ocr.ocr(image_path, cls=True)
    """
    results = []
    for i, mock in enumerate(MOCK_RESULTS):
        matched = find_matching_entries(mock["text"])
        results.append({
            "id": f"ocr_{i}",
            "text": mock["text"],
            "bbox": mock["bbox"],
            "confidence": mock["confidence"] + random.uniform(-0.05, 0.05),
            "variant_refs": [e.id for e in matched if e.id],
            "corrected": convert_variants(mock["text"]),
        })
    return results


def convert_variants(text: str) -> str:
    """Convert ancient/variant characters to modern simplified."""
    return "".join(VARIANT_DICT.get(c, c) for c in text)
