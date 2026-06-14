<template>
  <div class="flex h-screen">
    <!-- Left: Document list -->
    <div class="w-64 bg-gray-900 p-4 flex flex-col gap-3 border-r border-gray-800">
      <h1 class="text-lg font-bold text-amber-400">古籍 OCR 标注平台</h1>

      <div>
        <label class="block bg-amber-500 text-black text-center py-2 rounded cursor-pointer hover:bg-amber-400 text-sm font-medium">
          上传古籍图片
          <input type="file" accept="image/*" @change="onUpload" class="hidden" />
        </label>
      </div>

      <button @click="store.loadMockDocument()" class="bg-gray-800 py-2 rounded text-sm hover:bg-gray-700">
        加载示例文档
      </button>

      <!-- Search -->
      <div>
        <input v-model="store.searchQuery" @input="store.searchInDocuments(store.searchQuery)"
          placeholder="全文检索..." class="w-full bg-gray-800 rounded px-3 py-2 text-sm" />
        <div v-if="store.searchResults.length" class="mt-1 space-y-1">
          <div v-for="r in store.searchResults" :key="r.id" class="bg-gray-800 rounded p-1 text-xs">
            {{ r.text }} <span class="text-gray-500">{{ (r.confidence * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>

      <!-- Document list -->
      <div class="flex-1 overflow-y-auto space-y-1">
        <div v-for="d in store.documents" :key="d.id" @click="store.currentDoc = d"
          class="bg-gray-800 rounded p-2 cursor-pointer text-sm"
          :class="store.currentDoc?.id === d.id ? 'ring-1 ring-amber-500' : ''">
          {{ d.name }}
          <div class="text-xs text-gray-500">{{ d.results.length }} 行识别</div>
        </div>
      </div>

      <!-- Export -->
      <button @click="doExport" class="bg-green-700 py-2 rounded text-sm hover:bg-green-600">
        导出 TEI/XML
      </button>
    </div>

    <!-- Center: Image + OCR overlay -->
    <div class="flex-1 relative bg-gray-950 overflow-hidden">
      <ImageCanvas v-if="store.currentDoc" />
      <div v-else class="flex items-center justify-center h-full text-gray-600">
        请上传古籍图片或加载示例文档
      </div>
    </div>

    <!-- Right panel with tabs -->
    <div class="w-80 bg-gray-900 flex flex-col border-l border-gray-800">
      <div class="flex border-b border-gray-800">
        <button @click="activeTab = 'results'"
          class="flex-1 py-2 text-sm font-medium transition-colors"
          :class="activeTab === 'results' ? 'text-amber-400 border-b-2 border-amber-400' : 'text-gray-400 hover:text-gray-300'">
          识别结果
        </button>
        <button @click="activeTab = 'dict'"
          class="flex-1 py-2 text-sm font-medium transition-colors"
          :class="activeTab === 'dict' ? 'text-amber-400 border-b-2 border-amber-400' : 'text-gray-400 hover:text-gray-300'">
          异体字词典
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-4">
        <div v-show="activeTab === 'results'" class="space-y-3">
          <h3 class="text-amber-300 font-bold text-sm">OCR 识别结果</h3>
          <div v-if="store.currentDoc" class="space-y-2">
            <div v-for="r in store.currentDoc.results" :key="r.id"
              class="bg-gray-800 rounded p-2 text-sm">
              <div class="flex justify-between">
                <span class="text-white font-medium">{{ r.text }}</span>
                <span class="text-xs px-2 py-0.5 rounded"
                  :class="r.confidence > 0.9 ? 'bg-green-900 text-green-400' : 'bg-yellow-900 text-yellow-400'">
                  {{ (r.confidence * 100).toFixed(0) }}%
                </span>
              </div>
              <div class="text-xs text-gray-400 mt-1">
                简体: <span class="text-amber-300">{{ store.convertVariant(r.text) }}</span>
              </div>

              <div v-if="r.variant_refs?.length" class="mt-2">
                <div class="text-xs text-gray-500 mb-1">引用异体字:</div>
                <div class="flex flex-wrap gap-1">
                  <button v-for="refId in r.variant_refs" :key="refId"
                    @click="showVariantDetail(refId)"
                    class="text-xs bg-amber-900/40 text-amber-300 px-2 py-0.5 rounded hover:bg-amber-900/60">
                    {{ store.getVariantEntryById(refId)?.ancient || '?' }}
                    → {{ store.getVariantEntryById(refId)?.modern || '?' }}
                  </button>
                </div>
              </div>

              <input v-model="r.corrected" placeholder="人工校正..."
                class="w-full bg-gray-700 rounded px-2 py-1 text-xs mt-2" />
            </div>
          </div>

          <h3 class="text-amber-300 font-bold text-sm mt-4">标注列表</h3>
          <div v-if="store.currentDoc" class="space-y-1">
            <div v-for="a in store.currentDoc.annotations" :key="a.id"
              class="bg-gray-800 rounded p-2 text-xs flex justify-between">
              <span>[{{ a.type }}] {{ a.label }}: {{ a.content }}</span>
              <button @click="store.removeAnnotation(a.id)" class="text-red-400 hover:underline">删除</button>
            </div>
            <div v-if="!store.currentDoc.annotations.length" class="text-gray-600 text-xs">
              在图片上拖拽框选区域添加标注
            </div>
          </div>
        </div>

        <div v-show="activeTab === 'dict'" class="h-full">
          <VariantDict />
        </div>
      </div>
    </div>

    <div v-if="variantDetail" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="variantDetail = null">
      <div class="bg-gray-900 rounded-lg p-5 w-96 max-w-[90vw]">
        <div class="flex justify-between items-start mb-3">
          <div>
            <span class="text-amber-400 font-bold text-3xl">{{ variantDetail.ancient }}</span>
            <span class="text-gray-400 mx-2">→</span>
            <span class="text-white text-xl">{{ variantDetail.modern }}</span>
          </div>
          <button @click="variantDetail = null" class="text-gray-500 hover:text-white text-xl">×</button>
        </div>
        <div class="space-y-2 text-sm">
          <div v-if="variantDetail.pinyin" class="text-gray-400">
            拼音：<span class="text-white">{{ variantDetail.pinyin }}</span>
          </div>
          <div v-if="variantDetail.definition">
            <div class="text-gray-400 text-xs mb-1">释义</div>
            <div class="text-white bg-gray-800 rounded p-2">{{ variantDetail.definition }}</div>
          </div>
          <div v-if="variantDetail.source" class="text-gray-400 text-xs">
            出处：{{ variantDetail.source }}
          </div>
          <div v-if="variantDetail.createdAt" class="text-gray-600 text-xs">
            创建时间：{{ variantDetail.createdAt }}
          </div>
        </div>
        <div class="flex justify-end mt-4">
          <button @click="variantDetail = null; activeTab = 'dict'"
            class="px-4 py-2 text-sm bg-amber-500 text-black rounded hover:bg-amber-400 font-medium">
            在词典中查看
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useOcrStore } from './store/ocr'
import ImageCanvas from './components/ImageCanvas.vue'
import VariantDict from './components/VariantDict.vue'
import type { VariantEntry } from './types'

const store = useOcrStore()
const activeTab = ref<'results' | 'dict'>('results')
const variantDetail = ref<VariantEntry | null>(null)

onMounted(() => {
  store.fetchVariantEntries()
})

function onUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) store.uploadAndOCR(file)
}

function doExport() {
  const tei = store.exportTEI()
  if (!tei) return
  const blob = new Blob([tei], { type: 'application/xml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${store.currentDoc?.name || 'export'}.xml`
  a.click()
  URL.revokeObjectURL(url)
}

function showVariantDetail(id: string) {
  const entry = store.getVariantEntryById(id)
  if (entry) {
    variantDetail.value = entry
  }
}
</script>
