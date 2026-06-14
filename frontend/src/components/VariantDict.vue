<template>
  <div class="flex flex-col h-full gap-3">
    <div class="flex items-center justify-between">
      <h3 class="text-amber-300 font-bold text-sm">异体字词典</h3>
      <button @click="openCreate"
        class="bg-amber-600 hover:bg-amber-500 text-black text-xs px-3 py-1 rounded font-medium">
        + 新增词条
      </button>
    </div>

    <input v-model="store.variantSearchQuery" placeholder="搜索异体字、对照字或释义..."
      class="w-full bg-gray-800 rounded px-3 py-2 text-sm" />

    <div class="flex-1 overflow-y-auto space-y-2">
      <div v-if="store.variantLoading" class="text-gray-500 text-xs text-center py-4">加载中...</div>
      <div v-else-if="!store.filteredVariantEntries.length" class="text-gray-500 text-xs text-center py-4">
        暂无词条，请先添加词条
      </div>
      <div v-for="entry in store.filteredVariantEntries" :key="entry.id"
        class="bg-gray-800 rounded p-2 text-sm cursor-pointer hover:bg-gray-750"
        @click="selectedEntry = entry">
        <div class="flex justify-between items-start">
          <div>
            <span class="text-amber-400 font-bold text-lg">{{ entry.ancient }}</span>
            <span class="text-gray-400 mx-2">→</span>
            <span class="text-white font-medium">{{ entry.modern }}</span>
          </div>
          <div class="flex gap-1">
            <button @click.stop="editEntry(entry)"
              class="text-blue-400 text-xs hover:underline">编辑</button>
            <button @click.stop="doDelete(entry.id!)"
              class="text-red-400 text-xs hover:underline">删除</button>
          </div>
        </div>
        <div v-if="entry.definition" class="text-gray-400 text-xs mt-1">
          {{ entry.definition }}
        </div>
        <div class="flex gap-3 mt-1 text-xs text-gray-500">
          <span v-if="entry.pinyin">拼音: {{ entry.pinyin }}</span>
          <span v-if="entry.source">出处: {{ entry.source }}</span>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeForm">
      <div class="bg-gray-900 rounded-lg p-5 w-96 max-w-[90vw]">
        <h3 class="text-amber-300 font-bold mb-4">
          {{ editingId ? '编辑词条' : '新增词条' }}
        </h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs text-gray-400 mb-1">异体字 (古字)</label>
            <input v-model="form.ancient"
              class="w-full bg-gray-800 rounded px-3 py-2 text-sm"
              placeholder="例如：學" />
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">对照字 (今字)</label>
            <input v-model="form.modern"
              class="w-full bg-gray-800 rounded px-3 py-2 text-sm"
              placeholder="例如：学" />
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">释义</label>
            <textarea v-model="form.definition" rows="3"
              class="w-full bg-gray-800 rounded px-3 py-2 text-sm resize-none"
              placeholder="字义解释..."></textarea>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-400 mb-1">拼音</label>
              <input v-model="form.pinyin"
                class="w-full bg-gray-800 rounded px-3 py-2 text-sm"
                placeholder="xué" />
            </div>
            <div>
              <label class="block text-xs text-gray-400 mb-1">出处</label>
              <input v-model="form.source"
                class="w-full bg-gray-800 rounded px-3 py-2 text-sm"
                placeholder="论语·学而" />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button @click="closeForm"
            class="px-4 py-2 text-sm bg-gray-700 rounded hover:bg-gray-600">取消</button>
          <button @click="submitForm"
            class="px-4 py-2 text-sm bg-amber-500 text-black rounded hover:bg-amber-400 font-medium">
            {{ editingId ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="selectedEntry" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="selectedEntry = null">
      <div class="bg-gray-900 rounded-lg p-5 w-96 max-w-[90vw]">
        <div class="flex justify-between items-start mb-3">
          <div>
            <span class="text-amber-400 font-bold text-3xl">{{ selectedEntry.ancient }}</span>
            <span class="text-gray-400 mx-2">→</span>
            <span class="text-white text-xl">{{ selectedEntry.modern }}</span>
          </div>
          <button @click="selectedEntry = null" class="text-gray-500 hover:text-white">×</button>
        </div>
        <div class="space-y-2 text-sm">
          <div v-if="selectedEntry.pinyin" class="text-gray-400">
            拼音：<span class="text-white">{{ selectedEntry.pinyin }}</span>
          </div>
          <div v-if="selectedEntry.definition">
            <div class="text-gray-400 text-xs mb-1">释义</div>
            <div class="text-white bg-gray-800 rounded p-2">{{ selectedEntry.definition }}</div>
          </div>
          <div v-if="selectedEntry.source" class="text-gray-400 text-xs">
            出处：{{ selectedEntry.source }}
          </div>
          <div v-if="selectedEntry.createdAt" class="text-gray-600 text-xs">
            创建时间：{{ selectedEntry.createdAt }}
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-4">
          <button @click="editEntry(selectedEntry); selectedEntry = null"
            class="px-3 py-1.5 text-sm bg-blue-600 rounded hover:bg-blue-500">编辑</button>
          <button @click="selectedEntry = null"
            class="px-3 py-1.5 text-sm bg-gray-700 rounded hover:bg-gray-600">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useOcrStore } from '../store/ocr'
import type { VariantEntry, VariantEntryCreate } from '../types'

const store = useOcrStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const selectedEntry = ref<VariantEntry | null>(null)

const form = reactive<VariantEntryCreate>({
  ancient: '',
  modern: '',
  definition: '',
  pinyin: '',
  source: '',
})

onMounted(() => {
  store.fetchVariantEntries()
})

function openCreate() {
  editingId.value = null
  form.ancient = ''
  form.modern = ''
  form.definition = ''
  form.pinyin = ''
  form.source = ''
  showForm.value = true
}

function editEntry(entry: VariantEntry) {
  editingId.value = entry.id || null
  form.ancient = entry.ancient
  form.modern = entry.modern
  form.definition = entry.definition
  form.pinyin = entry.pinyin || ''
  form.source = entry.source || ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
}

async function submitForm() {
  if (!form.ancient || !form.modern) {
    alert('请填写异体字和对照字')
    return
  }
  const data: VariantEntryCreate = {
    ancient: form.ancient,
    modern: form.modern,
    definition: form.definition,
    pinyin: form.pinyin || undefined,
    source: form.source || undefined,
  }
  if (editingId.value) {
    await store.updateVariantEntry(editingId.value, data)
  } else {
    await store.createVariantEntry(data)
  }
  closeForm()
}

async function doDelete(id: string) {
  if (!confirm('确定要删除这个词条吗？')) return
  await store.deleteVariantEntry(id)
}
</script>
