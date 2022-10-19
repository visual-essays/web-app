<template>
  <div id="editor" ref="editor" @paste="paste" @drop="drop" @dragover.prevent @dragover="overDropzone=true" @dragleave="overDropzone=false" :class="{overDropzone}">

    <div class="controls">
      
      <content-path></content-path>

      <div class="buttons">
        <span @click="showHelp" v-b-tooltip.hover :title="isMobile ? '' : 'Show Help Documentation'"><fa :icon="helpIcon"></fa></span>
        <span v-if="isLoggedIn" @click="saveFile" v-b-tooltip.hover :title="isMobile ? '' : 'Save Essay'"><fa :icon="saveIcon"></fa></span>
        <span @click="copyLink" v-b-tooltip.hover :title="isMobile ? '' : 'Copy Essay Link'"><fa :icon="linkIcon"></fa></span>
        <span @click="copyText" v-b-tooltip.hover :title="isMobile ? '' : 'Copy Essay Text'"><fa :icon="copyIcon"></fa></span>
        <span @click="launch" v-b-tooltip.hover :title="isMobile ? '' : 'View Essay'"><fa :icon="launchIcon"></fa></span>
        <span @click="togglePreview" v-b-tooltip.hover :title="isMobile ? '' : 'Toggle Essay Preview'"><fa :icon="previewIcon"></fa></span>
      </div>
    </div>

    <b-toast id="essay-saved" title="" solid auto-hide-delay="1000" no-close-button><b>Essay save to Github: {{`${saveStatus ? 'success' : 'failed'}`}}</b></b-toast>
    <b-toast id="link-copied" title="" solid auto-hide-delay="1000" no-close-button><b>Link copied to clipboard:</b>&nbsp;{{link}}</b-toast>
    <b-toast id="text-copied" title="" solid auto-hide-delay="1000" no-close-button><b>Essay text copied to clipboard</b></b-toast>

    <textarea v-cloak ref="content" autocomplete="off"></textarea>

    <b-button pill class="fab" variant="primary" @click="togglePreview">+</b-button>

  </div>
</template>

<script lang="ts">

import Vue from 'vue'
import { BootstrapVue } from 'bootstrap-vue'
Vue.use(BootstrapVue)

import { faCircleQuestion, faCopy, faEye, faFloppyDisk, faFolderOpen }  from '@fortawesome/free-regular-svg-icons'
import { faArrowUpRightFromSquare, faLink }  from '@fortawesome/free-solid-svg-icons'

const SimpleMDE: any = (window as any).SimpleMDE

const apiEndpoint = process.env.isDev
  ? 'http://localhost:8000'
  : location.hostname === 'localhost'
    ? 'https://api.juncture-digital.org'
    : `https://api.${location.hostname.split('.').slice(1).join('.')}`
const wcDevEndpoint = 'http://localhost:3333/build'

const webappHost = process.env.isDev
  ? 'http://localhost:8080'
  : 'https://beta.juncture-digital.org'

const iiifEndpoint = process.env.isDev
  ? 'http://localhost:8088'
  : location.hostname === 'localhost'
    ? 'https://iiif.juncture-digital.org'
    : `https://iiif.${location.hostname.split('.').slice(1).join('.')}`

export default Vue.extend({
  name: 'Editor',
  data: () => ({
    content: '',
    saveStatus: false,
    simplemde: <any>{},
    isPreviewActive: false,
    loadedDependencies: <any[]>[],
    overDropzone: false,
    externalWindow: <any>null
  }),
  computed: {
    acct(): string {return this.$store.state.essaysAcct},
    repo(): string {return this.$store.state.essaysRepo},
    ref(): string {return this.$store.state.essaysRef},
    path(): string {return this.$store.state.essaysPath},
    contentPath(): string {return this.$store.state.essaysContentPath},
    authToken(): string {return this.$store.state.authToken},
    isLoggedIn() {return this.$store.state.authToken !== ''},
    isMobile(): string {return this.$store.state.isMobile},
    link(): string {return `${webappHost}/${this.acct}/${this.repo}/${this.path}${this.ref ? '?ref='+this.ref : ''}`},
    githubClient() {return this.$store.state.githubClient},
    
    launchIcon() { return faArrowUpRightFromSquare },
    helpIcon() { return faCircleQuestion },
    copyIcon() { return faCopy },
    previewIcon() { return faEye },
    saveIcon() { return faFloppyDisk },
    folderIcon() { return faFolderOpen },
    linkIcon() { return faLink }
  },
  created() { console.log(`${this.$options.name}.created`)},
  async mounted() {
    if (this.acct && this.repo) {
      console.log(`Editor.mounted: essaysAcct=${this.acct} essaysRepo=${this.repo} essaysContentPath=${this.contentPath}`)
      // let path = ['essays', this.acct, this.repo, ...this.contentPath.replace(/\/README\.md$/,'').replace(/\.md$/,'').split('/')].filter(pe => pe).join('/')
      //window.history.replaceState({}, '', `/${path}`)
    }
    this.initEditor()
  },
  methods: {

    initEditor() {
      this.simplemde = new SimpleMDE({
        previewRender: this.previewRender,
        // initialValue,
        autosave: {
          enabled: false,
          delay: 10000,
          // uniqueId: this.userHash
          uniqueId: 'aaaa'
        },
        hideIcons: ['side-by-side', 'fullscreen', 'preview', 'guide'],
        tabSize: 4
      })
      this.simplemde.codemirror.on('drop', (_:any, evt:MouseEvent) => evt.preventDefault())
      this.simplemde.codemirror.on('paste', (_:any, evt:MouseEvent) => evt.preventDefault())
    },

    previewRender(markdown:string, preview:HTMLElement) {
      if (this.isPreviewActive) {
        this.loadedDependencies.forEach(el => el.parentElement.removeChild(el))
        this.loadedDependencies = []
      } else {
        let body = {'prefix': `${this.acct}/${this.repo}`, 'markdown': markdown}
        fetch(`${apiEndpoint}/html/?inline=true`, {method: 'POST', body: JSON.stringify(body)})
          .then(resp => resp.text())
          .then(html => {
            let htmlEls = new DOMParser().parseFromString(html, 'text/html').children[0].children
            let head = (htmlEls[0] as HTMLElement)
            let body = (htmlEls[1] as HTMLElement)
            Array.from(body.querySelectorAll('ve-image')).forEach((veImg:any) => veImg.setAttribute('auth-token', this.authToken))
            preview.innerHTML = body.innerHTML
            this.loadDependencies(head.querySelectorAll('link[rel="stylesheet"]'), 0, () => this.loadDependencies(head.querySelectorAll('style'), 0, null))
            this.loadDependencies(body.querySelectorAll('script'), 0, null)
          })
        return ''
      }
    },

    drop(e: DragEvent) {
      let cursorPos = this.simplemde.codemirror.coordsChar({left:e.pageX, top:e.pageY})
      let inputText = ''
      if (e.dataTransfer) inputText = decodeURI(e.dataTransfer.getData('Text') || e.dataTransfer.getData('text/plain') || e.dataTransfer.getData('text/uri-list'))
      if (inputText && isURL(inputText)) {
        let url = inputText
        let parsed = new URL(url)
        let manifestUrl = parsed.searchParams.get('manifest')
        if (manifestUrl) {
          let imageId = manifestUrl.indexOf(iiifEndpoint) > 0 && manifestUrl.indexOf('manifest.json') > 0
            ? manifestUrl.split('/').slice(-2,-1).pop() as string
            : manifestUrl as string
            this.insertAtCursor(cursorPos, `.ve-image ${decodeURIComponent(imageId)}\n`)
        } else {
          this.getManifestUrl(url).then((manifestUrl:string) => {
            let imageId = manifestUrl.split('/').slice(3,-1).join('/')
            if (cursorPos.line === 0) {
              this.insertAtCursor(cursorPos, `.ve-header "File Title" ${imageId}\n`)
            } else {
              this.insertAtCursor(cursorPos, `.ve-image ${imageId}\n`)
            }
          })
        }
      }
    },

    paste(e: ClipboardEvent) {
      let pastedText = e.clipboardData?.getData('Text') || ''
      console.log('paste', pastedText)
      if (isURL(pastedText)) {
        let manifestUrl = (new URL(pastedText)).searchParams.get('manifest')
        if (manifestUrl) {
          let imageId = manifestUrl.indexOf(iiifEndpoint) > 0 && manifestUrl.indexOf('manifest.json') > 0
            ? manifestUrl.split('/').slice(-2,-1).pop() as string
            : manifestUrl as string
          this.simplemde.codemirror.replaceSelection(`\n.ve-image ${decodeURIComponent(imageId)}\n`)
        } else {
          this.getManifestUrl(pastedText).then((manifestUrl:string) => {
            manifestUrl = manifestUrl.indexOf(iiifEndpoint) === 0
              ? decodeURIComponent(manifestUrl.split('/').slice(3,-1).join('/'))
              : manifestUrl
            let viewer = manifestUrl.indexOf('youtube.com') > 0 ? 'video' : 'image'
            this.simplemde.codemirror.replaceSelection(`\n.ve-${viewer} ${manifestUrl}\n`)
          })
        }
      } else {
        this.simplemde.codemirror.replaceSelection(pastedText)
      }
    },

    async getManifestUrl(imageUrl: string) {
      imageUrl = imageUrl.split('#')[0]
      let resp = await fetch(`${process.env.isDev ? 'http://localhost:8088' : iiifEndpoint}/?url=${encodeURIComponent(imageUrl)}`)
      return await resp.text()
    },

    insertAtCursor(pos:any, text:string) {
      let priorLine = this.simplemde.codemirror.getRange({line:pos.line-2, char:0}, pos).trim().split(/\s/)
      if (priorLine.length > 0 && priorLine[0] === '.ve-image') {
        let merged = '.ve-image\n'
        merged += `    - ${priorLine.slice(1).join(' ')}\n`
        merged += `    - ${text.split(/\s/).slice(1).join(' ')}\n`
        this.simplemde.codemirror.setSelection({line:pos.line-1,ch:0}, {line:pos.line})
        this.simplemde.codemirror.replaceSelection(merged)
      } else {
        pos.ch = 0
        this.simplemde.codemirror.setSelection(pos, pos)
        this.simplemde.codemirror.replaceSelection(text)
      }
    },

    togglePreview() {
      SimpleMDE.togglePreview(this.simplemde)
      this.isPreviewActive = !this.isPreviewActive
    },
    
    showHelp() {
      this.openWindow(`${webappHost}/a3b5125/help/`, `toolbar=no,location=no,left=0,top=0,width=800,height=800,scrollbars=no,status=no`)
    },
  
    async saveFile() {
      console.log('saveFile', this.contentPath)
      if (this.isLoggedIn) {
        let markdown = this.simplemde.value()
        this.saveStatus = await this.githubClient.putFile(this.acct, this.repo, this.contentPath, markdown, this.ref)
        ;(this as any).$bvToast.show('essay-saved')
      }
    },
  
    copyLink() {
      navigator.clipboard.writeText(this.link)
      ;(this as any).$bvToast.show('link-copied')
    },
  
    copyText() {
      navigator.clipboard.writeText(this.simplemde.value())
      ;(this as any).$bvToast.show('text-copied')
    },
  
    launch() {
      window.open(this.link, '_blank')
    },
  
    openWindow(url:string, options:any) {
      if (this.externalWindow) { this.externalWindow.close() }
      if (options === undefined) options = 'toolbar=yes,location=yes,left=0,top=0,width=1000,height=1200,scrollbars=yes,status=yes'
      this.externalWindow = window.open(url, '_blank', options)
    },
    
    loadDependencies(dependencies:any, i:number, callback:any) {
      if (dependencies.length > 0) {
        this.load(dependencies.item(i), () => {
          if (i < dependencies.length-1) this.loadDependencies(dependencies, i+1, callback) 
          else if (callback) callback()
        })
      }
    },

    load(srcEl:HTMLElement, callback:any) {
      let e
      if (srcEl.localName  === 'link') {
        e = document.createElement('link')
        e.href = process.env.isDev
          ? (srcEl as HTMLLinkElement).href.replace(/https:\/\/unpkg\.com\/visual-essays\/dist\/visual-essays/, wcDevEndpoint)
          : (srcEl as HTMLLinkElement).href
        e.rel = (srcEl as HTMLLinkElement).rel
        e.type = 'text/css'
        e.addEventListener('load', callback)
        this.loadedDependencies.push(e)
        document.getElementsByTagName('head')[0].appendChild(e)
      } else if (srcEl.localName  === 'style') {
        e = document.createElement('style')
        e.textContent = srcEl.textContent
        e.addEventListener('load', callback)
        this.loadedDependencies.push(e)
        document.getElementsByTagName('head')[0].appendChild(e)
      } else if (srcEl.localName  === 'script') {
        e = document.createElement('script')
        if ((srcEl as HTMLScriptElement).src) {
          e.src = process.env.isDev
            ? (srcEl as HTMLScriptElement).src.replace(/https:\/\/unpkg\.com\/visual-essays\/dist\/visual-essays/, wcDevEndpoint)
            : (srcEl as HTMLScriptElement).src
          if ((srcEl as HTMLScriptElement).type) e.type = (srcEl as HTMLScriptElement).type
          e.addEventListener('load', callback)
        } else {
          if ((srcEl as HTMLScriptElement).type) e.type = (srcEl as HTMLScriptElement).type
          e.text = (srcEl as HTMLScriptElement).text
        }
        this.loadedDependencies.push(e)
        document.getElementsByTagName('body')[0].appendChild(e)
        if (!e.src) callback()
      }
    },

  },
  watch: {

    contentPath: {
      async handler (contentPath) {
        console.log(`${this.$options.name}.watch.contentPath`, contentPath)
        let path = ['essays', this.acct, this.repo, ...this.contentPath.replace(/\/?README\.md$/,'').replace(/\.md$/,'').split('/')].filter(pe => pe).join('/')
        window.history.replaceState({}, '', `/${path}${this.ref ? '?ref='+this.ref : ''}`)
        let resp = await this.githubClient.getFile(this.acct, this.repo, contentPath, this.ref)
        this.content = resp.content
      },
      immediate: true
    },

    ref: {
      async handler (ref, prior) {
        console.log(`${this.$options.name}.watch.ref=${ref} prior=${prior}`)
        if (prior !== undefined) {
          let path = ['essays', this.acct, this.repo, ...this.contentPath.replace(/\/?README\.md$/,'').replace(/\.md$/,'').split('/')].filter(pe => pe).join('/')
          window.history.replaceState({}, '', `/${path}`)
          this.content = await this.githubClient.getFile(this.acct, this.repo, this.contentPath, ref)
        }
      },
      immediate: true
    },

    content(markdown) {
      this.simplemde.value(markdown)
    },

    isPreviewActive(isActive) {
      if (isActive) (document.getElementById('__layout') as HTMLElement)?.classList.add('preview')
      else (document.getElementById('__layout') as HTMLElement)?.classList.remove('preview')
    }

}
})

function isURL(str:string) { return /^https*:\/\//.test(str) }
</script>

<style>

  .CodeMirror {
    height: calc(100vh - 200px);
  }

  main {
    /* padding: 0 !important; */
  }

  .preview .CodeMirror {
    height: 100vh;
  }
  .preview .editor-toolbar,
  .preview .editor-statusbar {
    display: none;
  }

  .preview .editor-preview {
    padding: 0;
  }

  /* Mobile Devices */
  @media (max-width: 480px) {

    .CodeMirror {
      height: calc(100vh - 280px);
    }
  }

</style>

<style scoped>

  [v-cloak] {
    display: none
  }
  
  * {
    box-sizing: border-box;
  }
  
  #editor {
    position: relative;
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  #editor.preview {
    height: unset;
  }

  .editor-toolbar {
    display: none;
  }
  .preview .controls {
    display: none;
  }

  body {
    margin: 12px;
    font-family: Roboto, sans-serif;
  }

  .content {
    padding: 12px;
  }

  .controls {
    display: flex;
    flex-direction: column;
    width: 100%;
    background-color: white;
    padding-top: 6px;
    /* align-items: center; */
  }

  .buttons {
    padding: 6px 12px;
    display: flex;
    gap: 15px;
    margin-left: auto;
    font-size: 22px;
  }
  .buttons span {
    cursor: pointer;
  }

  .fab {
    display: none;
    position: fixed;
    right: 10px;
    bottom: 70px;
    z-index: 10;
    width: 30px;
		height: 30px;
		border-radius: 15px;
		font-size: 20px;
    font-weight: bold;
		text-align: center;
    padding: 0;
  }

  .preview .fab {
    display: inline-block;
  }

  /* Mobile Devices */
  @media (max-width: 480px) {

  }

  /* Larger Devices */
  @media (min-width: 481px) {
  }

</style>
