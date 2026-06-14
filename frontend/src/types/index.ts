export interface OCRResult {
  id: string
  text: string
  bbox: [number, number, number, number]
  confidence: number
  corrected?: string
  variant_refs?: string[]
}

export interface Document {
  id: string
  name: string
  imageUrl: string
  results: OCRResult[]
  annotations: Annotation[]
  createdAt: string
}

export interface Annotation {
  id: string
  type: 'region' | 'character' | 'note'
  bbox: [number, number, number, number]
  label: string
  content: string
}

export interface VariantChar {
  ancient: string
  modern: string
  frequency: number
}

export interface VariantEntry {
  id?: string
  ancient: string
  modern: string
  definition: string
  pinyin?: string
  source?: string
  createdAt?: string
}

export interface VariantEntryCreate {
  ancient: string
  modern: string
  definition?: string
  pinyin?: string
  source?: string
}

export interface VariantEntryUpdate {
  ancient?: string
  modern?: string
  definition?: string
  pinyin?: string
  source?: string
}
