<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const BASE = import.meta.env.PROD ? '/mind-vault' : ''

type View = 'overview' | 'library' | 'categories' | 'search' | 'raw'

const view = ref<View>('overview')
const summaryLoading = ref(false)
const catLoading = ref(false)
const libLoading = ref(false)
const docLoading = ref(false)

const notes = ref<{ sections: any[], items: any[], raw: string }>({ sections: [], items: [], raw: '' })
const summary = ref<{ summary: string, topics: string[] } | null>(null)
const categories = ref<{ categories: any[] }>({ categories: [] })
const library = ref<{ docs: any[], total: number }>({ docs: [], total: 0 })
const activeDoc = ref<{ name: string, folder: string, content: string, summaryText?: string } | null>(null)
const docSummaryLoading = ref(false)

const searchQ = ref('')
const searchResults = ref<any[]>([])
const searchLoading = ref(false)

const summaryLoaded = ref(false)
const catLoaded = ref(false)
const libLoaded = ref(false)
const totalItems = computed(() => notes.value.items.length)

async function fetchNotes() {
  const r = await fetch(`${BASE}/api/notes`)
  notes.value = await r.json()
}

async function fetchSummary() {
  summaryLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/summary`)
    summary.value = await r.json()
    summaryLoaded.value = true
  } finally {
    summaryLoading.value = false
  }
}

async function fetchCategories() {
  if (catLoaded.value) return
  catLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/categorize`)
    categories.value = await r.json()
    catLoaded.value = true
  } finally {
    catLoading.value = false
  }
}

async function fetchLibrary() {
  if (libLoaded.value) return
  libLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/library`)
    library.value = await r.json()
    libLoaded.value = true
  } finally {
    libLoading.value = false
  }
}

async function openDoc(doc: any) {
  docLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/doc?folder=${doc.folder}&name=${doc.name}`)
    const data = await r.json()
    activeDoc.value = { ...data, summaryText: undefined }
  } finally {
    docLoading.value = false
  }
}

async function summarizeDoc() {
  if (!activeDoc.value) return
  docSummaryLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/doc-summary?folder=${activeDoc.value.folder}&name=${activeDoc.value.name}`)
    const data = await r.json()
    activeDoc.value = { ...activeDoc.value, summaryText: data.summary }
  } finally {
    docSummaryLoading.value = false
  }
}

async function doSearch() {
  if (!searchQ.value.trim()) return
  searchLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/search?q=${encodeURIComponent(searchQ.value)}`)
    const data = await r.json()
    searchResults.value = data.results
  } finally {
    searchLoading.value = false
  }
}

function setView(v: View) {
  view.value = v
  activeDoc.value = null
  if (v === 'overview' && !summaryLoaded.value) fetchSummary()
  if (v === 'categories' && !catLoaded.value) fetchCategories()
  if (v === 'library' && !libLoaded.value) fetchLibrary()
}

// folder label → emoji map
const folderEmoji: Record<string, string> = {
  root: '📋',
  articles: '📰',
  saves: '💾',
  conversations: '💬',
}

function renderMarkdown(md: string): string {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[hli])(.+)$/gm, '<p>$1</p>')
}

onMounted(() => {
  fetchNotes()
  fetchSummary()
})
</script>

<template>
  <div class="layout">
    <!-- sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">🧠</span>
        <span class="logo-text">MindVault</span>
      </div>

      <nav class="nav">
        <button :class="['nav-item', view === 'overview' && 'active']" @click="setView('overview')">
          <span>✨</span> 概覽
        </button>
        <button :class="['nav-item', view === 'library' && 'active']" @click="setView('library')">
          <span>📚</span> 文件庫
        </button>
        <button :class="['nav-item', view === 'categories' && 'active']" @click="setView('categories')">
          <span>🗂️</span> 分類
        </button>
        <button :class="['nav-item', view === 'search' && 'active']" @click="setView('search')">
          <span>🔍</span> 搜尋
        </button>
        <button :class="['nav-item', view === 'raw' && 'active']" @click="setView('raw')">
          <span>📄</span> 原始筆記
        </button>
      </nav>

      <div class="sidebar-stats" v-if="notes.items.length">
        <div class="stat">
          <span class="stat-num">{{ notes.sections.length }}</span>
          <span class="stat-label">筆記區塊</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ library.total || '…' }}</span>
          <span class="stat-label">文件</span>
        </div>
      </div>
    </aside>

    <!-- main -->
    <main class="main">

      <!-- ── OVERVIEW ── -->
      <section v-if="view === 'overview'" class="section">
        <h1 class="page-title">概覽</h1>

        <div class="card summary-card">
          <div class="card-header">
            <span class="card-icon">✨</span>
            <span class="card-title">AI 知識庫摘要</span>
            <button class="refresh-btn" @click="() => { summaryLoaded = false; fetchSummary() }" :disabled="summaryLoading">
              {{ summaryLoading ? '生成中...' : '重新生成' }}
            </button>
          </div>
          <div v-if="summaryLoading" class="loading-dots"><span></span><span></span><span></span></div>
          <div v-else-if="summary">
            <p class="summary-text">{{ summary.summary }}</p>
            <div class="topics" v-if="summary.topics?.length">
              <span class="topic-tag" v-for="t in summary.topics" :key="t">{{ t }}</span>
            </div>
          </div>
        </div>

        <div class="sections-grid">
          <div class="section-card" v-for="sec in notes.sections" :key="sec.title">
            <div class="section-title">{{ sec.title }}</div>
            <div class="section-count">{{ sec.items.length }} 項</div>
            <ul class="section-items">
              <li v-for="item in sec.items.slice(0, 4)" :key="item">{{ item }}</li>
              <li v-if="sec.items.length > 4" class="more">+{{ sec.items.length - 4 }} 更多</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ── LIBRARY ── -->
      <section v-if="view === 'library'" class="section">
        <!-- Doc reader -->
        <div v-if="activeDoc" class="doc-reader">
          <div class="doc-reader-header">
            <button class="back-btn" @click="activeDoc = null">← 返回文件庫</button>
            <span class="doc-reader-title">{{ activeDoc.name }}</span>
            <button class="refresh-btn" @click="summarizeDoc" :disabled="docSummaryLoading">
              {{ docSummaryLoading ? 'AI 摘要中...' : '✨ AI 摘要' }}
            </button>
          </div>
          <div v-if="activeDoc.summaryText" class="doc-summary-box">
            <strong>AI 摘要：</strong> {{ activeDoc.summaryText }}
          </div>
          <pre class="raw-content doc-raw">{{ activeDoc.content }}</pre>
        </div>

        <template v-else>
          <h1 class="page-title">文件庫 <span class="title-count">{{ library.total }}</span></h1>

          <div v-if="libLoading" class="loading-state">
            <div class="loading-dots"><span></span><span></span><span></span></div>
            <p>載入文件中...</p>
          </div>

          <div v-else>
            <!-- Group by folder -->
            <div v-for="folder in ['root','articles','saves','conversations']" :key="folder">
              <div v-if="library.docs.filter(d => d.folder === folder).length" class="folder-group">
                <h2 class="folder-title">{{ folderEmoji[folder] }} {{ SUBFOLDERS_LABEL[folder] }}</h2>
                <div class="doc-grid">
                  <div
                    class="doc-card"
                    v-for="doc in library.docs.filter(d => d.folder === folder)"
                    :key="doc.name"
                    @click="openDoc(doc)"
                  >
                    <div class="doc-name">{{ doc.title || doc.name }}</div>
                    <div class="doc-filename">{{ doc.name }}</div>
                    <p class="doc-preview">{{ doc.preview }}</p>
                    <div class="doc-size">{{ Math.round(doc.size / 1024 * 10) / 10 }} KB</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </section>

      <!-- ── CATEGORIES ── -->
      <section v-if="view === 'categories'" class="section">
        <h1 class="page-title">AI 智能分類</h1>
        <div v-if="catLoading" class="loading-state">
          <div class="loading-dots"><span></span><span></span><span></span></div>
          <p>AI 正在分析筆記...</p>
        </div>
        <div v-else class="categories-grid">
          <div class="cat-card" v-for="cat in categories.categories" :key="cat.name">
            <div class="cat-header">
              <span class="cat-emoji">{{ cat.emoji }}</span>
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count">{{ cat.items?.length || 0 }}</span>
            </div>
            <ul class="cat-items">
              <li v-for="item in cat.items" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ── SEARCH ── -->
      <section v-if="view === 'search'" class="section">
        <h1 class="page-title">搜尋</h1>
        <div class="search-box">
          <input v-model="searchQ" placeholder="搜尋筆記和文件..." class="search-input" @keyup.enter="doSearch" />
          <button class="search-btn" @click="doSearch" :disabled="searchLoading">
            {{ searchLoading ? '搜尋中...' : '搜尋' }}
          </button>
        </div>
        <div v-if="searchResults.length" class="search-results">
          <div class="result-item" v-for="(r, i) in searchResults" :key="i">
            <div class="result-header">
              <span class="result-badge">{{ r.category }}</span>
              <span v-if="r.type === 'document'" class="result-type-badge">文件</span>
              <span class="result-source">{{ r.source }}</span>
            </div>
            <p class="result-text">{{ r.text }}</p>
          </div>
        </div>
        <div v-else-if="searchQ && !searchLoading" class="empty-state">
          沒有找到符合「{{ searchQ }}」的結果
        </div>
      </section>

      <!-- ── RAW ── -->
      <section v-if="view === 'raw'" class="section">
        <h1 class="page-title">原始筆記</h1>
        <pre class="raw-content">{{ notes.raw }}</pre>
      </section>

    </main>
  </div>
</template>

<script lang="ts">
// Folder display labels (accessible in template)
export const SUBFOLDERS_LABEL: Record<string, string> = {
  root: '個人筆記',
  articles: '文章',
  saves: '儲存',
  conversations: '對話記錄',
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }

/* sidebar */
.sidebar {
  width: 220px; min-height: 100vh;
  background: var(--surface); border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 1.5rem 1rem; position: sticky; top: 0; flex-shrink: 0;
}
.logo { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 2rem; }
.logo-icon { font-size: 1.5rem; }
.logo-text { font-size: 1.1rem; font-weight: 700; color: var(--accent); letter-spacing: -0.02em; }

.nav { display: flex; flex-direction: column; gap: 0.3rem; }
.nav-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.55rem 0.8rem; border-radius: 8px;
  background: transparent; color: var(--muted); font-size: 0.9rem;
  text-align: left; width: 100%;
}
.nav-item:hover { background: var(--surface2); color: var(--text); }
.nav-item.active { background: var(--accent); color: #fff; }

.sidebar-stats { margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border); display: flex; gap: 1rem; flex-wrap: wrap; }
.stat { display: flex; flex-direction: column; }
.stat-num { font-size: 1.3rem; font-weight: 700; color: var(--accent2); }
.stat-label { font-size: 0.72rem; color: var(--muted); }

/* main */
.main { flex: 1; padding: 2rem; overflow-y: auto; }
.page-title { font-size: 1.6rem; font-weight: 700; margin-bottom: 1.5rem; }
.title-count { font-size: 1rem; color: var(--muted); font-weight: 400; margin-left: 0.4rem; }

/* cards */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem; }
.card-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; }
.card-icon { font-size: 1.1rem; }
.card-title { font-weight: 600; font-size: 1rem; flex: 1; }
.refresh-btn {
  background: var(--surface2); color: var(--muted);
  border: 1px solid var(--border); border-radius: 6px;
  padding: 0.3rem 0.7rem; font-size: 0.8rem;
}
.refresh-btn:hover:not(:disabled) { color: var(--text); }
.refresh-btn:disabled { opacity: 0.5; cursor: default; }

.summary-text { color: var(--text); line-height: 1.7; margin-bottom: 1rem; }
.topics { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.topic-tag { background: var(--surface2); border: 1px solid var(--border); color: var(--accent2); padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.8rem; }

/* sections grid */
.sections-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }
.section-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; transition: border-color 0.2s; }
.section-card:hover { border-color: var(--accent); }
.section-title { font-weight: 600; margin-bottom: 0.3rem; }
.section-count { font-size: 0.8rem; color: var(--accent2); margin-bottom: 0.6rem; }
.section-items { list-style: none; padding: 0; }
.section-items li { font-size: 0.82rem; color: var(--muted); padding: 0.15rem 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.section-items li::before { content: '• '; color: var(--accent); }
.more { color: var(--accent) !important; font-style: italic; }

/* library */
.folder-group { margin-bottom: 2rem; }
.folder-title { font-size: 1rem; font-weight: 600; color: var(--muted); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.85rem; }
.doc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.doc-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; cursor: pointer; transition: border-color 0.2s, transform 0.15s; }
.doc-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.doc-name { font-weight: 600; margin-bottom: 0.15rem; font-size: 0.95rem; }
.doc-filename { font-size: 0.72rem; color: var(--muted); margin-bottom: 0.5rem; font-family: monospace; }
.doc-preview { font-size: 0.8rem; color: var(--muted); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.5rem; }
.doc-size { font-size: 0.72rem; color: var(--border); text-align: right; }

/* doc reader */
.doc-reader { display: flex; flex-direction: column; gap: 1rem; }
.doc-reader-header { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.back-btn { background: var(--surface2); color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 0.4rem 0.8rem; font-size: 0.85rem; }
.back-btn:hover { border-color: var(--accent); }
.doc-reader-title { font-weight: 600; flex: 1; }
.doc-summary-box { background: var(--surface2); border: 1px solid var(--accent); border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.9rem; color: var(--text); line-height: 1.6; }
.doc-raw { font-size: 0.8rem; max-height: 70vh; overflow-y: auto; }

/* categories */
.categories-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.cat-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; }
.cat-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
.cat-emoji { font-size: 1.2rem; }
.cat-name { font-weight: 600; flex: 1; }
.cat-count { background: var(--surface2); color: var(--accent2); font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 20px; }
.cat-items { list-style: none; padding: 0; }
.cat-items li { font-size: 0.82rem; color: var(--muted); padding: 0.2rem 0; border-bottom: 1px solid var(--border); }
.cat-items li:last-child { border-bottom: none; }

/* search */
.search-box { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
.search-input { flex: 1; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.7rem 1rem; color: var(--text); font-size: 0.95rem; font-family: inherit; outline: none; }
.search-input:focus { border-color: var(--accent); }
.search-btn { background: var(--accent); color: #fff; border-radius: 8px; padding: 0.7rem 1.2rem; font-size: 0.9rem; }
.search-btn:disabled { opacity: 0.5; }

.search-results { display: flex; flex-direction: column; gap: 0.75rem; }
.result-item { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem; }
.result-header { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem; flex-wrap: wrap; }
.result-badge { background: var(--accent); color: #fff; font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 4px; }
.result-type-badge { background: var(--surface2); color: var(--accent2); font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 4px; border: 1px solid var(--border); }
.result-source { font-size: 0.75rem; color: var(--muted); margin-left: auto; }
.result-text { font-size: 0.9rem; }

/* raw */
.raw-content { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; line-height: 1.7; color: var(--muted); white-space: pre-wrap; word-break: break-word; }

/* loading */
.loading-state { text-align: center; padding: 3rem; color: var(--muted); }
.loading-state p { margin-top: 1rem; font-size: 0.9rem; }
.loading-dots { display: flex; justify-content: center; gap: 0.4rem; }
.loading-dots span { width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: bounce 1.2s infinite; }
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }

.empty-state { text-align: center; color: var(--muted); padding: 2rem; }
</style>
