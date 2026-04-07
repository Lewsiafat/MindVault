<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'

const BASE = import.meta.env.PROD ? '/mind-vault' : ''

type View = 'overview' | 'library' | 'categories' | 'search' | 'raw' | 'wiki'

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

const stats = ref<{ total_docs: number, total_words: number, notes_items: number, folder_counts: Record<string, number> } | null>(null)
const statsLoading = ref(false)

// Wiki
const wikiStatus = ref<{ wiki_exists: boolean, total_summaries: number, total_pages: number, pending_count: number, pending_ingest: any[] } | null>(null)
const wikiPages = ref<{ pages: any[] }>({ pages: [] })
const activeWikiPage = ref<{ slug: string, type: string, content: string } | null>(null)
const wikiLoading = ref(false)
const wikiIngestLoading = ref(false)
const wikiSynthLoading = ref(false)
const wikiSynthResult = ref<{ synthesized: number, total_concepts_found: number } | null>(null)
const wikiStatusLoaded = ref(false)

// Lint
const lintResult = ref<{ issues: any[], suggestions: any[], health_score: number, summary: string, stats: any } | null>(null)
const lintLoading = ref(false)
const fixingIssueIdx = ref<number | null>(null)

// Theme
const isDark = ref(localStorage.getItem('mv-theme') !== 'light')
function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('mv-theme', isDark.value ? 'dark' : 'light')
  document.documentElement.setAttribute('data-theme', isDark.value ? '' : 'light')
  if (!isDark.value) document.documentElement.setAttribute('data-theme', 'light')
  else document.documentElement.removeAttribute('data-theme')
}
// Apply saved theme on load
if (!isDark.value) document.documentElement.setAttribute('data-theme', 'light')

// Configure marked
marked.setOptions({ breaks: true, gfm: true })

function renderMd(md: string): string {
  return marked.parse(md) as string
}

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

async function fetchStats() {
  if (stats.value) return
  statsLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/stats`)
    stats.value = await r.json()
  } finally {
    statsLoading.value = false
  }
}

async function fetchWikiStatus() {
  const r = await fetch(`${BASE}/api/wiki/status`)
  wikiStatus.value = await r.json()
  wikiStatusLoaded.value = true
}

async function fetchWikiPages() {
  wikiLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/wiki/pages`)
    wikiPages.value = await r.json()
  } finally {
    wikiLoading.value = false
  }
}

async function openWikiPage(slug: string, type: string) {
  const r = await fetch(`${BASE}/api/wiki/page?slug=${encodeURIComponent(slug)}&type=${type}`)
  activeWikiPage.value = await r.json()
}

async function ingestDoc(folder: string, name: string) {
  wikiIngestLoading.value = true
  try {
    await fetch(`${BASE}/api/wiki/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder, name })
    })
    await fetchWikiStatus()
    await fetchWikiPages()
  } finally {
    wikiIngestLoading.value = false
  }
}

async function ingestAll() {
  wikiIngestLoading.value = true
  try {
    await fetch(`${BASE}/api/wiki/ingest-all`, { method: 'POST' })
    await fetchWikiStatus()
    await fetchWikiPages()
  } finally {
    wikiIngestLoading.value = false
  }
}

async function synthesizeConcepts(force = false) {
  wikiSynthLoading.value = true
  wikiSynthResult.value = null
  try {
    const r = await fetch(`${BASE}/api/wiki/synthesize?force=${force}`, { method: 'POST' })
    const data = await r.json()
    wikiSynthResult.value = data
    await fetchWikiStatus()
    await fetchWikiPages()
  } finally {
    wikiSynthLoading.value = false
  }
}

async function runLint() {
  lintLoading.value = true
  lintResult.value = null
  try {
    const r = await fetch(`${BASE}/api/wiki/lint`)
    lintResult.value = await r.json()
  } finally {
    lintLoading.value = false
  }
}

async function fixIssue(issue: any, idx: number) {
  fixingIssueIdx.value = idx
  try {
    await fetch(`${BASE}/api/wiki/fix`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ issue_type: issue.type, affected: issue.affected || [] })
    })
    // Re-run lint to show updated state
    await runLint()
    await fetchWikiStatus()
    await fetchWikiPages()
  } finally {
    fixingIssueIdx.value = null
  }
}

async function openDoc(folder: string, name: string) {
  docLoading.value = true
  try {
    const r = await fetch(`${BASE}/api/doc?folder=${folder}&name=${name}`)
    const data = await r.json()
    activeDoc.value = { ...data, summaryText: undefined }
    // switch to library view so back button works
    if (view.value !== 'library') {
      view.value = 'library'
      libLoaded.value = true // don't re-fetch
    }
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

const recentDocs = computed(() => {
  return [...library.value.docs]
    .sort((a, b) => (b.mtime ?? 0) - (a.mtime ?? 0))
    .slice(0, 8)
})

function formatDate(ts: number): string {
  if (!ts) return ''
  const d = new Date(ts * 1000)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - d.getTime()) / 86400000)
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays} 天前`
  return d.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' })
}

function setView(v: View) {
  view.value = v
  activeDoc.value = null
  activeWikiPage.value = null
  if (v === 'overview') {
    if (!summaryLoaded.value) fetchSummary()
    fetchStats()
    if (!libLoaded.value) fetchLibrary()
  }
  if (v === 'categories' && !catLoaded.value) fetchCategories()
  if (v === 'library' && !libLoaded.value) fetchLibrary()
  if (v === 'wiki' && !wikiStatusLoaded.value) {
    fetchWikiStatus()
    fetchWikiPages()
  }
}

const folderEmoji: Record<string, string> = {
  root: '📋', articles: '📰', saves: '💾', conversations: '💬',
}
const folderLabel: Record<string, string> = {
  root: '個人筆記', articles: '文章', saves: '儲存', conversations: '對話記錄',
}

onMounted(() => {
  fetchNotes()
  fetchSummary()
  fetchStats()
  fetchLibrary()
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
        <button :class="['nav-item', view === 'wiki' && 'active']" @click="setView('wiki')">
          <span>📖</span> Wiki
        </button>
      </nav>
      <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切換淺色主題' : '切換深色主題'">
        {{ isDark ? '☀️' : '🌙' }}
      </button>

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
        <div class="card">
          <div class="card-header">
            <span>✨</span>
            <span class="card-title">AI 知識庫摘要</span>
            <button class="refresh-btn" @click="() => { summaryLoaded = false; fetchSummary() }" :disabled="summaryLoading">
              {{ summaryLoading ? '生成中...' : '重新生成' }}
            </button>
          </div>
          <div v-if="summaryLoading" class="loading-dots"><span></span><span></span><span></span></div>
          <div v-else-if="summary">
            <p class="summary-text">{{ summary.summary }}</p>
            <div class="topics">
              <span class="topic-tag" v-for="t in summary.topics" :key="t">{{ t }}</span>
            </div>
          </div>
        </div>
        <!-- Stats dashboard -->
        <div class="stats-dashboard" v-if="stats">
          <div class="stat-card">
            <div class="stat-card-num">{{ stats.total_docs }}</div>
            <div class="stat-card-label">📄 文件總數</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-num">{{ stats.total_words.toLocaleString() }}</div>
            <div class="stat-card-label">📝 總字數</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-num">{{ stats.notes_items }}</div>
            <div class="stat-card-label">📌 筆記條目</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-num">{{ Object.keys(stats.folder_counts).length }}</div>
            <div class="stat-card-label">🗂️ 分類數量</div>
          </div>
        </div>
        <div class="stats-folder-row" v-if="stats">
          <span class="folder-stat" v-for="(count, label) in stats.folder_counts" :key="label">
            {{ label }} <strong>{{ count }}</strong>
          </span>
        </div>

        <!-- Recent docs -->
        <h2 class="section-subtitle">最近更新</h2>
        <div v-if="libLoading && !library.docs.length" class="loading-dots" style="justify-content:flex-start;gap:0.4rem;margin-bottom:1rem;">
          <span></span><span></span><span></span>
        </div>
        <div class="recent-docs" v-else>
          <div class="recent-doc-card" v-for="doc in recentDocs" :key="doc.folder + doc.name"
            @click="openDoc(doc.folder, doc.name)">
            <div class="recent-doc-top">
              <span class="recent-doc-label">{{ doc.label }}</span>
              <span class="recent-doc-time">{{ formatDate(doc.mtime) }}</span>
            </div>
            <div class="recent-doc-title">{{ doc.title || doc.name }}</div>
            <p class="recent-doc-preview">{{ doc.preview }}</p>
          </div>
        </div>
      </section>

      <!-- ── LIBRARY ── -->
      <section v-if="view === 'library'" class="section">
        <!-- Doc reader -->
        <div v-if="activeDoc" class="doc-reader">
          <div class="doc-reader-header">
            <button class="back-btn" @click="activeDoc = null">← 返回</button>
            <span class="doc-reader-title">{{ activeDoc.name }}</span>
            <button class="refresh-btn" @click="summarizeDoc" :disabled="docSummaryLoading">
              {{ docSummaryLoading ? 'AI 摘要中...' : '✨ AI 摘要' }}
            </button>
          </div>
          <div v-if="activeDoc.summaryText" class="doc-summary-box">
            <strong>AI 摘要：</strong> {{ activeDoc.summaryText }}
          </div>
          <!-- Rendered markdown -->
          <div class="md-body" v-html="renderMd(activeDoc.content)"></div>
        </div>

        <template v-else>
          <h1 class="page-title">文件庫 <span class="title-count">{{ library.total }}</span></h1>
          <div v-if="libLoading" class="loading-state">
            <div class="loading-dots"><span></span><span></span><span></span></div>
            <p>載入文件中...</p>
          </div>
          <div v-else>
            <div v-for="folder in ['root','articles','saves','conversations']" :key="folder">
              <div v-if="library.docs.filter(d => d.folder === folder).length" class="folder-group">
                <h2 class="folder-title">{{ folderEmoji[folder] }} {{ folderLabel[folder] }}</h2>
                <div class="doc-grid">
                  <div class="doc-card" v-for="doc in library.docs.filter(d => d.folder === folder)" :key="doc.name"
                    @click="openDoc(doc.folder, doc.name)">
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
          <p>AI 正在分析所有筆記和文件...</p>
        </div>
        <div v-else>
          <div class="categories-grid">
            <div class="cat-card" v-for="cat in categories.categories" :key="cat.name">
              <div class="cat-header">
                <span class="cat-emoji">{{ cat.emoji }}</span>
                <span class="cat-name">{{ cat.name }}</span>
                <span class="cat-count">{{ cat.items?.length || 0 }}</span>
              </div>
              <ul class="cat-items">
                <li v-for="item in cat.items" :key="item.text || item"
                  :class="['cat-item', (item.type === 'doc' && item.folder) ? 'cat-item-doc' : '']"
                  @click="item.type === 'doc' && item.folder ? openDoc(item.folder, item.name) : null">
                  <span class="cat-item-icon" v-if="item.type === 'doc'">📄</span>
                  {{ item.text || item }}
                  <span class="cat-item-arrow" v-if="item.type === 'doc' && item.folder">→</span>
                </li>
              </ul>
            </div>
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
          <div class="result-item"
            :class="r.type === 'document' ? 'result-item-doc' : ''"
            v-for="(r, i) in searchResults" :key="i"
            @click="r.type === 'document' ? openDoc(r.folder || 'root', r.source) : null"
            :style="r.type === 'document' ? 'cursor:pointer' : ''">
            <div class="result-header">
              <span class="result-badge">{{ r.category }}</span>
              <span v-if="r.type === 'document'" class="result-type-badge">📄 文件</span>
              <span class="result-source">{{ r.source }}</span>
            </div>
            <p class="result-text">{{ r.text }}</p>
          </div>
        </div>
        <div v-else-if="searchQ && !searchLoading" class="empty-state">
          沒有找到符合「{{ searchQ }}」的結果
        </div>
      </section>

      <!-- ── WIKI ── -->
      <section v-if="view === 'wiki'" class="section">
        <!-- Page reader -->
        <div v-if="activeWikiPage" class="doc-reader">
          <div class="doc-reader-header">
            <button class="back-btn" @click="activeWikiPage = null">← 返回 Wiki</button>
            <span class="doc-reader-title">{{ activeWikiPage.slug }}</span>
            <span class="result-type-badge">{{ activeWikiPage.type === 'summary' ? '📝 摘要' : '💡 概念' }}</span>
          </div>
          <div class="md-body" v-html="renderMd(activeWikiPage.content)"></div>
        </div>

        <template v-else>
          <h1 class="page-title">
            Wiki
            <span class="title-count" v-if="wikiStatus">{{ wikiStatus.total_summaries + wikiStatus.total_pages }} 頁</span>
          </h1>

          <!-- Status card -->
          <div class="card">
            <div class="card-header">
              <span>⚙️</span>
              <span class="card-title">Wiki 狀態</span>
              <button class="refresh-btn" @click="fetchWikiStatus()">重新整理</button>
            </div>
            <div v-if="wikiStatus">
              <div class="stats-dashboard" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 0.75rem">
                <div class="stat-card">
                  <div class="stat-card-num">{{ wikiStatus.total_summaries }}</div>
                  <div class="stat-card-label">📝 摘要頁</div>
                </div>
                <div class="stat-card">
                  <div class="stat-card-num">{{ wikiStatus.total_pages }}</div>
                  <div class="stat-card-label">💡 概念頁</div>
                </div>
                <div class="stat-card">
                  <div class="stat-card-num">{{ wikiStatus.pending_count }}</div>
                  <div class="stat-card-label">⏳ 待匯入</div>
                </div>
              </div>
              <div v-if="wikiStatus.pending_count > 0" class="wiki-pending">
                <div class="wiki-pending-header">
                  <span class="section-subtitle" style="margin:0">待匯入文件</span>
                  <button class="search-btn" @click="ingestAll" :disabled="wikiIngestLoading" style="padding: 0.35rem 0.9rem; font-size: 0.82rem">
                    {{ wikiIngestLoading ? '匯入中...' : `全部匯入 (${wikiStatus.pending_count})` }}
                  </button>
                </div>
                <div class="wiki-pending-list">
                  <button v-for="p in wikiStatus.pending_ingest" :key="p.slug"
                    class="wiki-pending-btn" @click="ingestDoc(p.folder, p.name)" :disabled="wikiIngestLoading">
                    {{ p.name }}
                  </button>
                </div>
              </div>
              <div v-else class="wiki-all-done">✅ 所有文件已匯入 Wiki</div>
            </div>
          </div>

          <!-- Synthesis card -->
          <div class="card" v-if="wikiStatus && wikiStatus.total_summaries > 0">
            <div class="card-header">
              <span>💡</span>
              <span class="card-title">概念合成</span>
              <button class="search-btn" @click="synthesizeConcepts()" :disabled="wikiSynthLoading"
                style="padding: 0.35rem 0.9rem; font-size: 0.82rem">
                {{ wikiSynthLoading ? '合成中...' : '合成概念頁' }}
              </button>
            </div>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 0 0 0.5rem">
              從所有摘要頁中提取共同概念，自動生成跨文件的概念綜合頁面。
            </p>
            <div v-if="wikiSynthResult" class="wiki-synth-result">
              <span>✨ 合成完成：找到 <strong>{{ wikiSynthResult.total_concepts_found }}</strong> 個概念，生成 <strong>{{ wikiSynthResult.synthesized }}</strong> 頁</span>
            </div>
            <div v-if="wikiStatus.total_pages > 0" class="wiki-all-done" style="margin-top: 0.5rem">
              目前有 {{ wikiStatus.total_pages }} 個概念頁 —
              <span class="wiki-resynth-link" @click="synthesizeConcepts(true)">重新合成</span>
            </div>
          </div>

          <!-- Lint card -->
          <div class="card" v-if="wikiStatus && wikiStatus.total_summaries > 0">
            <div class="card-header">
              <span>🔍</span>
              <span class="card-title">Wiki 健康檢查</span>
              <button class="search-btn" @click="runLint" :disabled="lintLoading"
                style="padding: 0.35rem 0.9rem; font-size: 0.82rem">
                {{ lintLoading ? '檢查中...' : '執行 Lint' }}
              </button>
            </div>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 0">
              分析矛盾、孤兒頁、缺失連結，並提出改善建議。
            </p>
            <div v-if="lintResult" class="lint-report">
              <div class="lint-score-row">
                <div class="lint-score" :class="lintResult.health_score >= 80 ? 'score-good' : lintResult.health_score >= 50 ? 'score-mid' : 'score-bad'">
                  {{ lintResult.health_score }}
                </div>
                <div class="lint-summary">{{ lintResult.summary }}</div>
              </div>
              <div v-if="lintResult.issues?.length" class="lint-section">
                <div class="lint-section-title">⚠️ 發現問題 ({{ lintResult.issues.length }})</div>
                <div class="lint-issue" v-for="(issue, i) in lintResult.issues" :key="i"
                  :class="`issue-${issue.severity}`">
                  <span class="issue-badge">{{ issue.type }}</span>
                  <span class="issue-desc">{{ issue.description }}</span>
                  <div class="issue-actions">
                    <span v-for="slug in (issue.affected || []).slice(0, 2)" :key="slug"
                      class="issue-slug-link"
                      @click="openWikiPage(slug, 'summary')">
                      {{ slug }}
                    </span>
                    <button class="issue-fix-btn"
                      :disabled="fixingIssueIdx !== null"
                      @click="fixIssue(issue, i)">
                      {{ fixingIssueIdx === i ? '修復中...' : '→ 修復' }}
                    </button>
                  </div>
                </div>
              </div>
              <div v-if="lintResult.suggestions?.length" class="lint-section">
                <div class="lint-section-title">💡 改善建議</div>
                <div class="lint-suggestion" v-for="(s, i) in lintResult.suggestions" :key="i">
                  <strong>{{ s.action }}</strong> — {{ s.reason }}
                </div>
              </div>
            </div>
          </div>

          <!-- Wiki pages -->
          <div v-if="wikiLoading" class="loading-state">
            <div class="loading-dots"><span></span><span></span><span></span></div>
          </div>
          <div v-else>
            <template v-if="wikiPages.pages?.filter((p:any) => p.type === 'summary').length">
              <h2 class="section-subtitle">📝 摘要頁</h2>
              <div class="doc-grid">
                <div class="doc-card" v-for="p in wikiPages.pages?.filter((p:any) => p.type === 'summary')" :key="p.slug"
                  @click="openWikiPage(p.slug, p.type)">
                  <div class="doc-name">{{ p.title }}</div>
                  <div class="doc-filename wiki-source-tag">📝 摘要</div>
                  <div class="doc-size">{{ p.updated }}</div>
                </div>
              </div>
            </template>

            <template v-if="wikiPages.pages?.filter((p:any) => p.type === 'concept').length">
              <h2 class="section-subtitle" style="margin-top: 1.5rem">💡 概念頁</h2>
              <div class="doc-grid">
                <div class="doc-card" v-for="p in wikiPages.pages?.filter((p:any) => p.type === 'concept')" :key="p.slug"
                  @click="openWikiPage(p.slug, p.type)">
                  <div class="doc-name">{{ p.title }}</div>
                  <div class="doc-filename wiki-source-tag">💡 概念</div>
                  <div class="doc-size">{{ p.updated }}</div>
                </div>
              </div>
            </template>

            <div v-if="!wikiPages.pages?.length" class="empty-state" style="padding: 2rem 0">
              尚無 Wiki 頁面。點擊「全部匯入」開始從文件生成摘要。
            </div>
          </div>
        </template>
      </section>

      <!-- ── RAW ── -->
      <section v-if="view === 'raw'" class="section">
        <h1 class="page-title">原始筆記</h1>
        <!-- Rendered markdown view with toggle -->
        <div class="raw-toggle">
          <span style="font-size:0.85rem;color:var(--muted)">notes.md</span>
        </div>
        <div class="md-body notes-md-body" v-html="renderMd(notes.raw)"></div>
      </section>

    </main>
  </div>
</template>

<style scoped>
.layout { display: flex; min-height: 100vh; }

/* sidebar */
.sidebar { width: 220px; min-height: 100vh; background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 1.5rem 1rem; position: sticky; top: 0; flex-shrink: 0; }
.logo { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 2rem; }
.logo-icon { font-size: 1.5rem; }
.logo-text { font-size: 1.1rem; font-weight: 700; color: var(--accent); letter-spacing: -0.02em; }
.nav { display: flex; flex-direction: column; gap: 0.3rem; }
.nav-item { display: flex; align-items: center; gap: 0.6rem; padding: 0.55rem 0.8rem; border-radius: 8px; background: transparent; color: var(--muted); font-size: 0.9rem; text-align: left; width: 100%; }
.nav-item:hover { background: var(--surface2); color: var(--text); }
.nav-item.active { background: var(--accent); color: #fff; }
.sidebar-stats { margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border); display: flex; gap: 1rem; flex-wrap: wrap; }
.stat { display: flex; flex-direction: column; }
.stat-num { font-size: 1.3rem; font-weight: 700; color: var(--accent2); }
.stat-label { font-size: 0.72rem; color: var(--muted); }

/* main */
.main { flex: 1; padding: 2rem; overflow-y: auto; max-width: 960px; }
.page-title { font-size: 1.6rem; font-weight: 700; margin-bottom: 1.5rem; }
.title-count { font-size: 1rem; color: var(--muted); font-weight: 400; margin-left: 0.4rem; }

/* card */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; }
.card-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; }
.card-title { font-weight: 600; font-size: 1rem; flex: 1; }
.refresh-btn { background: var(--surface2); color: var(--muted); border: 1px solid var(--border); border-radius: 6px; padding: 0.3rem 0.7rem; font-size: 0.8rem; }
.refresh-btn:hover:not(:disabled) { color: var(--text); }
.refresh-btn:disabled { opacity: 0.5; cursor: default; }
.summary-text { line-height: 1.7; margin-bottom: 1rem; }
.topics { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.topic-tag { background: var(--surface2); border: 1px solid var(--border); color: var(--accent2); padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.8rem; }

/* stats dashboard */
.stats-dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 0.75rem; }
@media (max-width: 700px) { .stats-dashboard { grid-template-columns: repeat(2, 1fr); } }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; text-align: center; }
.stat-card-num { font-size: 1.8rem; font-weight: 700; color: var(--accent2); line-height: 1; margin-bottom: 0.35rem; }
.stat-card-label { font-size: 0.78rem; color: var(--muted); }
.stats-folder-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.75rem; }
.folder-stat { background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; padding: 0.2rem 0.75rem; font-size: 0.78rem; color: var(--muted); }
.folder-stat strong { color: var(--accent); margin-left: 0.25rem; }
.section-subtitle { font-size: 1rem; font-weight: 600; color: var(--muted); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; }

/* recent docs */
.recent-docs { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.75rem; }
.recent-doc-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; cursor: pointer; transition: border-color 0.2s, transform 0.15s; }
.recent-doc-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.recent-doc-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; }
.recent-doc-label { font-size: 0.72rem; color: var(--accent2); background: var(--surface2); padding: 0.1rem 0.5rem; border-radius: 10px; }
.recent-doc-time { font-size: 0.72rem; color: var(--muted); }
.recent-doc-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.35rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-doc-preview { font-size: 0.78rem; color: var(--muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0; }

/* library */
.folder-group { margin-bottom: 2rem; }
.folder-title { font-size: 0.85rem; font-weight: 600; color: var(--muted); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; }
.doc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.doc-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; cursor: pointer; transition: border-color 0.2s, transform 0.15s; }
.doc-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.doc-name { font-weight: 600; margin-bottom: 0.15rem; font-size: 0.95rem; }
.doc-filename { font-size: 0.72rem; color: var(--muted); margin-bottom: 0.5rem; font-family: monospace; }
.doc-preview { font-size: 0.8rem; color: var(--muted); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.5rem; }
.doc-size { font-size: 0.72rem; color: var(--border); text-align: right; }

/* doc reader */
.doc-reader { display: flex; flex-direction: column; gap: 1rem; }
.doc-reader-header { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.back-btn { background: var(--surface2); color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 0.4rem 0.8rem; font-size: 0.85rem; }
.back-btn:hover { border-color: var(--accent); }
.doc-reader-title { font-weight: 600; flex: 1; font-size: 0.95rem; color: var(--muted); }
.doc-summary-box { background: var(--surface2); border: 1px solid var(--accent); border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.9rem; line-height: 1.6; }
.raw-toggle { margin-bottom: 0.5rem; }

/* categories */
.categories-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.cat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; }
.cat-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
.cat-emoji { font-size: 1.2rem; }
.cat-name { font-weight: 600; flex: 1; }
.cat-count { background: var(--surface2); color: var(--accent2); font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 20px; }
.cat-items { list-style: none; padding: 0; }
.cat-item { font-size: 0.82rem; color: var(--muted); padding: 0.25rem 0.4rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 0.3rem; border-radius: 4px; }
.cat-item:last-child { border-bottom: none; }
.cat-item-doc { cursor: pointer; }
.cat-item-doc:hover { background: var(--surface2); color: var(--text); }
.cat-item-icon { font-size: 0.75rem; flex-shrink: 0; }
.cat-item-arrow { margin-left: auto; color: var(--accent); font-size: 0.8rem; flex-shrink: 0; }

/* search */
.search-box { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
.search-input { flex: 1; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.7rem 1rem; color: var(--text); font-size: 0.95rem; font-family: inherit; outline: none; }
.search-input:focus { border-color: var(--accent); }
.search-btn { background: var(--accent); color: #fff; border-radius: 8px; padding: 0.7rem 1.2rem; font-size: 0.9rem; }
.search-btn:disabled { opacity: 0.5; }
.search-results { display: flex; flex-direction: column; gap: 0.75rem; }
.result-item { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem; }
.result-item-doc:hover { border-color: var(--accent); }
.result-header { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem; flex-wrap: wrap; }
.result-badge { background: var(--accent); color: #fff; font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 4px; }
.result-type-badge { background: var(--surface2); color: var(--accent2); font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 4px; border: 1px solid var(--border); }
.result-source { font-size: 0.75rem; color: var(--muted); margin-left: auto; }
.result-text { font-size: 0.9rem; }

/* wiki */
.wiki-pending { background: var(--surface2); border-radius: 8px; padding: 0.75rem 1rem; }
.wiki-pending-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.6rem; }
.wiki-pending-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.wiki-pending-btn { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0.25rem 0.65rem; font-size: 0.78rem; color: var(--muted); cursor: pointer; }
.wiki-pending-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--text); }
.wiki-pending-btn:disabled { opacity: 0.5; cursor: default; }
.wiki-all-done { text-align: center; color: var(--accent2); font-size: 0.9rem; padding: 0.5rem; }
.wiki-source-tag { font-size: 0.72rem; color: var(--muted); margin-bottom: 0.5rem; font-family: monospace; }
.wiki-synth-result { background: var(--surface2); border: 1px solid var(--accent); border-radius: 8px; padding: 0.5rem 0.75rem; font-size: 0.85rem; color: var(--text); }
.wiki-resynth-link { color: var(--accent); cursor: pointer; text-decoration: underline; font-size: 0.85rem; }

/* lint */
.lint-report { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
.lint-score-row { display: flex; align-items: center; gap: 1rem; }
.lint-score { width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; font-weight: 700; flex-shrink: 0; }
.score-good { background: color-mix(in srgb, var(--success) 15%, transparent); color: var(--success); border: 2px solid var(--success); }
.score-mid { background: color-mix(in srgb, #f59e0b 15%, transparent); color: #f59e0b; border: 2px solid #f59e0b; }
.score-bad { background: color-mix(in srgb, var(--danger) 15%, transparent); color: var(--danger); border: 2px solid var(--danger); }
.lint-summary { font-size: 0.9rem; color: var(--text); line-height: 1.5; }
.lint-section { display: flex; flex-direction: column; gap: 0.4rem; }
.lint-section-title { font-size: 0.8rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
.lint-issue { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.83rem; }
.issue-high { background: color-mix(in srgb, var(--danger) 10%, transparent); border-left: 3px solid var(--danger); }
.issue-medium { background: color-mix(in srgb, #f59e0b 10%, transparent); border-left: 3px solid #f59e0b; }
.issue-low { background: var(--surface2); border-left: 3px solid var(--border); }
.issue-badge { background: var(--surface2); color: var(--accent); font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-family: monospace; }
.issue-desc { color: var(--text); flex: 1; }
.issue-actions { display: flex; align-items: center; gap: 0.4rem; flex-shrink: 0; flex-wrap: wrap; justify-content: flex-end; }
.issue-slug-link { font-size: 0.7rem; color: var(--accent2); font-family: monospace; cursor: pointer; text-decoration: underline; white-space: nowrap; }
.issue-slug-link:hover { color: var(--accent); }
.issue-fix-btn { background: var(--accent); color: #fff; border-radius: 5px; padding: 0.2rem 0.55rem; font-size: 0.75rem; white-space: nowrap; flex-shrink: 0; }
.issue-fix-btn:disabled { opacity: 0.5; cursor: default; }
.issue-fix-btn:hover:not(:disabled) { opacity: 0.85; }
.lint-suggestion { font-size: 0.83rem; color: var(--muted); padding: 0.3rem 0; border-bottom: 1px solid var(--border); }
.lint-suggestion:last-child { border-bottom: none; }

/* theme toggle */
.theme-toggle { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 0.4rem 0.6rem; font-size: 1rem; margin-bottom: 0.75rem; width: 100%; text-align: left; color: var(--muted); }
.theme-toggle:hover { border-color: var(--accent); }

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

<!-- Global styles for rendered markdown -->
<style>
.md-body {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.75rem 2rem;
  color: var(--text);
  line-height: 1.8;
  font-size: 0.92rem;
  overflow-y: auto;
}
.notes-md-body { max-height: 80vh; }
.doc-reader .md-body { max-height: 75vh; }

.md-body h1 { font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 0.75rem; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }
.md-body h2 { font-size: 1.2rem; font-weight: 600; margin: 1.25rem 0 0.6rem; color: var(--text); }
.md-body h3 { font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem; color: var(--accent2); }
.md-body h4 { font-size: 0.9rem; font-weight: 600; margin: 0.75rem 0 0.4rem; color: var(--muted); }
.md-body p { margin: 0.5rem 0; }
.md-body ul, .md-body ol { padding-left: 1.5rem; margin: 0.5rem 0; }
.md-body li { margin: 0.25rem 0; color: var(--muted); }
.md-body strong { color: var(--text); font-weight: 600; }
.md-body em { color: var(--accent2); font-style: italic; }
.md-body code { background: var(--surface2); color: var(--accent2); padding: 0.15rem 0.4rem; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }
.md-body pre { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; overflow-x: auto; margin: 0.75rem 0; }
.md-body pre code { background: none; padding: 0; color: var(--text); font-size: 0.82rem; }
.md-body blockquote { border-left: 3px solid var(--accent); padding-left: 1rem; color: var(--muted); margin: 0.75rem 0; font-style: italic; }
.md-body table { width: 100%; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.85rem; }
.md-body th { background: var(--surface2); padding: 0.5rem 0.75rem; text-align: left; font-weight: 600; border: 1px solid var(--border); }
.md-body td { padding: 0.4rem 0.75rem; border: 1px solid var(--border); color: var(--muted); }
.md-body hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
.md-body a { color: var(--accent); }
</style>
