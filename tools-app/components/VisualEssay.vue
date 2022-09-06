<template>
  <div ref="app" id="app" v-html="html"></div>
</template>

<script type="module">
  
import Vue from 'vue'

const apiEndpoint = 'https://api.juncture-digital.org'

export default Vue.extend({
  name: 'VisualEssay',
  props: {
    acct: { type: String, default: '' },
    repo: { type: String, default: '' },
    branch: { type: String, default: '' },
    root: { type: String, default: '' },
    path: { type: String, default: '' }
  },
  data: () => ({
    _acct: '',
    _repo: '',
    _ref: '',
    _path: '',
    _prefix: '',
    _base: '',
    _baseQarg: '',
    html: null
  }),
  created() {
    console.log(this.$route)
    let pathOffset = this.$route.name.replace(/-all$/,'').replace(/^all$/,'').split('/').filter(pe => pe).length
    console.log(this.acct, this.repo, this.branch, this.basePath, pathOffset)
    let _pathElems = this.$route.path.split('/').filter(pe => pe)
    console.log(_pathElems)
    this._acct = this.acct || (_pathElems.length > 0 ? _pathElems[0] : 'visual-essays')
    this._repo = this.repo || (_pathElems.length > 1 ? _pathElems[1] : 'content')
    this._ref = this.branch || (this.$route.query.branch || this.$route.query.ref || '')
    this._path = this.path || [...this.root.split('/'), ..._pathElems.slice(this.acct ? 0+pathOffset : 2)].filter(pe => pe).join('/')
    this._prefix = [this._acct, this._repo].filter(elem => elem).join('/')
    this._base = _pathElems.length > 0 ? `/${_pathElems.join('/')}/` : '/'
    let _basePathElems = this._base.split('/').filter(elem => elem)
    this._baseQarg = _basePathElems.length > 0 ? `/${_basePathElems.join('/')}/` : '/'

    let baseEl = document.head.querySelector('base')
    if (!baseEl) {
      baseEl = document.createElement('base')
      document.head.prepend(baseEl)
    }
    baseEl.href = this._base
    console.log(`acct=${this._acct} repo=${this._repo} ref=${this._ref} path=${this._path} prefix=${this._prefix} base=${this._base}}`)
  },
  mounted() {
    document.body.style.visibility = 'hidden'
    this.loadPage()
  },
  methods: {

    loadPage() {
      let url = `${apiEndpoint}/html/${this._prefix}/${this._path}${this._path === '' ? '' : '/'}?base=${this._baseQarg}&prefix=${this._prefix}&inline=true`
      if (this._ref) url += `&ref=${this._ref}`
      console.log(url)
      fetch(url).then(resp => resp.text())
      .then(html => {
        let [head, body] = new DOMParser().parseFromString(html, 'text/html').children[0].children
        this.html = (body.querySelector(':scope > #app') || body).innerHTML
        // Loads stylesheets and scripts used by loaded page
        this.loadDependencies(head.querySelectorAll('link[rel="stylesheet"]'), 0, () => this.loadDependencies(head.querySelectorAll('style'), 0))
        this.loadDependencies(body.querySelectorAll('script'), 0)
      })
    },
    
    loadDependencies(dependencies, i, callback) {
      if (dependencies.length > 0) {
        this.load(dependencies.item(i), () => {
          if (i < dependencies.length-1) this.loadDependencies(dependencies, i+1, callback) 
          else if (callback) callback()
        })
      }
    },

    load(srcEl, callback) {
      let e
      if (srcEl.localName  === 'link') {
        e = document.createElement('link')
        e.href = srcEl.href
        e.rel = srcEl.rel
        e.type = 'text/css'
        e.addEventListener('load', callback)
        document.getElementsByTagName('head')[0].appendChild(e)
      } else if (srcEl.localName  === 'style') {
        e = document.createElement('style')
        e.textContent = srcEl.textContent
        e.addEventListener('load', callback)
        document.getElementsByTagName('head')[0].appendChild(e)
      } else if (srcEl.localName  === 'script') {
        e = document.createElement('script')
        if (srcEl.src) {
          e.src = srcEl.src
          if (srcEl.type) e.type = srcEl.type
          e.addEventListener('load', callback)
        } else {
          if (srcEl.type) e.type = srcEl.type
          e.text = srcEl.text
        }
        document.getElementsByTagName('body')[0].appendChild(e)
        if (!e.src) callback()
      }
    }
  },
  watch: {
    
  }
})

</script>

<style scoped>
  .visible { visibility: visible; opacity: 1; transition: opacity .5s linear; }
  .hidden { visibility: hidden; opacity: 0; transition: visibility 0s .5s, opacity .5s linear; }
</style>
