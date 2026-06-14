import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Document, OCRResult, Annotation, VariantEntry, VariantEntryCreate, VariantEntryUpdate } from '../types'

const API_BASE = '/api'

export const useOcrStore = defineStore('ocr', () => {
  const documents = ref<Document[]>([])
  const currentDoc = ref<Document | null>(null)
  const isLoading = ref(false)
  const searchQuery = ref('')
  const searchResults = ref<OCRResult[]>([])

  const variantEntries = ref<VariantEntry[]>([])
  const variantLoading = ref(false)
  const variantSearchQuery = ref('')

  // Mock data
  const MOCK_DOC: Document = {
    id: '1',
    name: '论语·学而篇',
    imageUrl: '',
    results: [
      { id: 'r1', text: '子曰', bbox: [50, 30, 80, 40], confidence: 0.95 },
      { id: 'r2', text: '学而', bbox: [50, 80, 80, 40], confidence: 0.88 },
      { id: 'r3', text: '时习之', bbox: [50, 130, 120, 40], confidence: 0.91 },
      { id: 'r4', text: '不亦说乎', bbox: [50, 180, 160, 40], confidence: 0.87 },
      { id: 'r5', text: '有朋', bbox: [200, 30, 80, 40], confidence: 0.93 },
      { id: 'r6', text: '自远方来', bbox: [200, 80, 160, 40], confidence: 0.85 },
      { id: 'r7', text: '不亦乐乎', bbox: [200, 130, 160, 40], confidence: 0.92 },
    ],
    annotations: [],
    createdAt: '2025-01-15'
  }

  const variantDict = computed(() => {
    const dict: Record<string, string> = {}
    for (const e of variantEntries.value) {
      dict[e.ancient] = e.modern
    }
    return dict
  })

  const filteredVariantEntries = computed(() => {
    const q = variantSearchQuery.value.trim()
    if (!q) return variantEntries.value
    return variantEntries.value.filter(e =>
      e.ancient.includes(q) || e.modern.includes(q) || e.definition.includes(q)
    )
  })

  function getVariantEntryById(id: string): VariantEntry | undefined {
    return variantEntries.value.find(e => e.id === id)
  }

  async function fetchVariantEntries(ancient?: string, modern?: string) {
    variantLoading.value = true
    try {
      const params = new URLSearchParams()
      if (ancient) params.set('ancient', ancient)
      if (modern) params.set('modern', modern)
      const resp = await fetch(`${API_BASE}/variants?${params.toString()}`)
      if (resp.ok) {
        variantEntries.value = await resp.json()
      }
    } catch {
      console.error('Failed to fetch variant entries')
    } finally {
      variantLoading.value = false
    }
  }

  async function createVariantEntry(data: VariantEntryCreate) {
    try {
      const resp = await fetch(`${API_BASE}/variants`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (resp.ok) {
        const entry = await resp.json()
        variantEntries.value.unshift(entry)
        return entry
      }
    } catch {
      console.error('Failed to create variant entry')
    }
    return null
  }

  async function updateVariantEntry(id: string, data: VariantEntryUpdate) {
    try {
      const resp = await fetch(`${API_BASE}/variants/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (resp.ok) {
        const updated = await resp.json()
        const idx = variantEntries.value.findIndex(e => e.id === id)
        if (idx !== -1) {
          variantEntries.value[idx] = updated
        }
        return updated
      }
    } catch {
      console.error('Failed to update variant entry')
    }
    return null
  }

  async function deleteVariantEntry(id: string) {
    try {
      const resp = await fetch(`${API_BASE}/variants/${id}`, { method: 'DELETE' })
      if (resp.ok) {
        variantEntries.value = variantEntries.value.filter(e => e.id !== id)
        return true
      }
    } catch {
      console.error('Failed to delete variant entry')
    }
    return false
  }

  function loadMockDocument() {
    documents.value = [MOCK_DOC]
    currentDoc.value = MOCK_DOC
  }

  async function uploadAndOCR(file: File) {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await fetch('/api/ocr', { method: 'POST', body: formData })
      if (resp.ok) {
        const data = await resp.json()
        const doc: Document = {
          id: Date.now().toString(),
          name: file.name,
          imageUrl: URL.createObjectURL(file),
          results: data.results || [],
          annotations: [],
          createdAt: new Date().toISOString()
        }
        documents.value.push(doc)
        currentDoc.value = doc
      }
    } catch {
      // Use mock data as fallback
      loadMockDocument()
    } finally {
      isLoading.value = false
    }
  }

  function addAnnotation(type: Annotation['type'], bbox: [number, number, number, number], label: string, content: string) {
    if (!currentDoc.value) return
    currentDoc.value.annotations.push({
      id: Date.now().toString(),
      type, bbox, label, content
    })
  }

  function removeAnnotation(id: string) {
    if (!currentDoc.value) return
    currentDoc.value.annotations = currentDoc.value.annotations.filter(a => a.id !== id)
  }

  function convertVariant(text: string): string {
    return text.split('').map(c => variantDict.value[c] || c).join('')
  }

  function searchInDocuments(query: string) {
    const q = query.toLowerCase()
    searchResults.value = documents.value.flatMap(d =>
      d.results.filter(r => r.text.includes(q) || (r.corrected || '').includes(q))
    )
  }

  function exportTEI(): string {
    if (!currentDoc.value) return ''
    let tei = '<?xml version="1.0" encoding="UTF-8"?>\n'
    tei += '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
    tei += `  <teiHeader><fileDesc><titleStmt><title>${currentDoc.value.name}</title></titleStmt></fileDesc></teiHeader>\n`
    tei += '  <text><body>\n'
    for (const r of currentDoc.value.results) {
      tei += `    <seg type="line" xml:id="${r.id}" cert="${r.confidence}">${r.corrected || r.text}</seg>\n`
    }
    tei += '  </body></text>\n</TEI>'
    return tei
  }

  return {
    documents, currentDoc, isLoading, searchQuery, searchResults,
    variantEntries, variantLoading, variantSearchQuery, variantDict, filteredVariantEntries,
    loadMockDocument, uploadAndOCR, addAnnotation, removeAnnotation,
    convertVariant, searchInDocuments, exportTEI,
    fetchVariantEntries, createVariantEntry, updateVariantEntry, deleteVariantEntry, getVariantEntryById,
  }
})
