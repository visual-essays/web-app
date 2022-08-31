<template>
  <div class="content-path">

    <div class="repo-selector" v-if="acct" 
      @click="selectRepository"
      v-b-tooltip.hover :title="isMobile ? '' : 'Select Repository'">
      <span v-html="acct"></span>:
      <span v-html="repo"></span>
      <span v-if="ref"> ({{ref}})</span>
    </div>
    <div v-else>
      <div class="repo-selector" @click="selectRepository">Select Repository</div>
    </div>

    <b-breadcrumb v-if="acct">
      <b-breadcrumb-item v-for="item, idx in breadCrumbs" :key="`bc-${idx}`" 
        @click="selectFile(item, idx)"
        :html="item.text"
      ></b-breadcrumb-item>
    </b-breadcrumb>

  </div>
</template>

<script lang="ts">

import Vue from 'vue'

export default Vue.extend({
  name: 'ContentPath',
  props: {
    tool: { type: String, default: 'essays' }
  },
  data: () => ({}),
  computed: {
    baseRoute(): string {return (this.$route.name || '').replace(/-all$/,'').split('/').filter(pe => pe).join('/')},
    toolTitleCase(): string {return this.tool.charAt(0).toUpperCase() + this.tool.slice(1).toLowerCase()},
    acct(): string {return this.$store.state[`${this.tool}Acct`]},
    repo(): string {return this.$store.state[`${this.tool}Repo`]},
    ref(): string {return this.$store.state[`${this.tool}Ref`]},
    root(): string {return this.acct && this.repo ? `${this.acct}/${this.repo}` : ''},
    path(): string {return this.$store.state[`${this.tool}Path`]},
    dirList(): string {return this.$store.state[`${this.tool}DirList`]},
    contentPath(): string {return this.$store.state[`${this.tool}ContentPath`]},
    githubClient(): any {return this.$store.state.githubClient},
    isMobile(): boolean {return this.$store.state.isMobile},
    breadCrumbs(): any[] {
      let breadCrumbs = this.tool === 'essays' ? [] : [{text: 'root', to: ''}]
      let pathElems = this.contentPath.split('/').filter(pe => pe)
      for (let i = 0; i < pathElems.length; i++) {
        breadCrumbs.push({text: pathElems[i], to: `/${pathElems.slice(0,i+1).join('/')}`})
      }
      return breadCrumbs
    }
  },
  created() {
    console.log(this.$route)
  },
  mounted() {
    console.log('contentPath.mounted')
    this.$root.$on('github-path-changed', (path: string) => {
      console.log(`github-path-changed: tool=${this.tool} path=${path}`)
      this.$store.commit(`set${this.toolTitleCase}ContentPath`, path)
      this.$store.commit(`set${this.toolTitleCase}Path`, path.replace(/^\//,'').replace(/\/?README\.md$/,'').replace(/\.md$/,''))
      //this.$router.push({path: `/${this.baseRoute}/${this.acct}/${this.repo}/${path}`, query: this.ref ? {ref: this.ref} : {} })
    })
    
    let pathElems = (this.$route.params?.pathMatch || '').split('/').filter(pe => pe)
    this.$store.commit(`set${this.toolTitleCase}Path`, pathElems.length > 2 ? pathElems.slice(2).join('/') : this.path)
    if (pathElems.length > 0) this.$store.commit(`set${this.toolTitleCase}Acct`, pathElems[0])
    if (pathElems.length > 1) this.$store.commit(`set${this.toolTitleCase}Repo`, pathElems[1])
    
    console.log(`tool=${this.tool} ref=${this.$route.query.ref}`)
    if (this.$route.query.ref) this.$store.commit(`set${this.toolTitleCase}Ref`, this.$route.query.ref)

    this.$store.commit(`set${this.toolTitleCase}DirList`, [])

    this.githubClient.fullPath(this.acct, this.repo, this.path, this.ref, this.tool === 'media')
      .then((contentPath:string) => {
        this.$store.commit(`set${this.toolTitleCase}ContentPath`, contentPath)
        return contentPath
      })
      .then((contentPath:string) => {
        this.githubClient.dirlist(this.acct, this.repo, contentPath, this.ref)
        .then((dirList:any[]) => this.$store.commit(`set${this.toolTitleCase}DirList`, dirList))
      })

    let browserPath = `/${this.tool}/${this.root}${this.path ? '/'+this.path : ''}`
    if (this.ref) browserPath += `?ref=${this.ref}`
    window.history.replaceState({}, '', browserPath)
    console.log(`browserPath=${browserPath}`)

    console.log(`${this.$options.name}.mounted acct=${this.acct} repo=${this.repo} ref=${this.ref} path=${this.path} contentPath=${this.contentPath}`)

  },
  methods: {

    selectFile(item:any, idx:number) {
      console.log('selectFile', this.tool, item)
      if (this.tool === 'media') {
        this.$router.push({path: `/${this.tool}/${this.root}${item.to}`})
        this.$store.commit(`set${this.toolTitleCase}Path`, item.to)
      } else {
        this.$store.commit('setFileSelectorPath', item.to)
        ;(this as any).$bvModal.show(`${this.tool}-file-selector`)
      }
    },

    selectRepository() {
      (this as any).$bvModal.show(`${this.tool}-repository-selector`)
    }

  },
  watch: {
  
    root: {
      async handler(root) {
        console.log(`${this.$options.name}.watch.root: root=${this.root}`)
        this.$store.commit(`set${this.toolTitleCase}Path`, '')
        this.$router.push({path: `/${this.baseRoute}/${root}`, query: this.ref ? {ref:this.ref} : {} })
      },
      immediate: false
    },

    path: {
      async handler(repo) {
        console.log(`${this.$options.name}.watch.path: path=${this.path}`)
        if (repo) this.$store.commit(`set${this.toolTitleCase}ContentPath`, await this.githubClient.fullPath(this.acct, this.repo, this.path, this.ref, this.tool === 'media')) 
      },
      immediate: false
    },

    contentPath: {
      async handler() {
        console.log(`${this.$options.name}.watch.root: contentPath=${this.contentPath}`)
        //let dirList = await this.githubClient.dirlist(this.acct, this.repo, this.contentPath, this.ref)
        //this.dirs = dirList.filter((item:any) => item.type === 'dir')
        //.map((item:any) => `/${this.tool}/${this.acct}/${this.repo}/${this.contentPath}/${item.name}`)  
        
        this.$store.commit(`set${this.toolTitleCase}DirList`, await this.githubClient.dirlist(this.acct, this.repo, this.contentPath, this.ref))
        console.log('dirList', this.dirList)
        //let path = ['media', this.acct, this.repo, ...this.contentPath.split('/')].filter(pe => pe).join('/')
        //window.history.replaceState({}, '', `/${path}`)
      },
      immediate: false
    },

    ref: {
      async handler(ref) {
        console.log(`${this.$options.name}.watch.ref: ref=${this.ref}`)
        this.$router.push({path: `/${this.baseRoute}/${this.root}`, query: ref ? {ref} : {}})
      },
      immediate: false
    }

  }
})

</script>

<style scoped>

  .content-path {
    display: flex;
    align-items: center;
    width: 100%;
    background-color: white;
    padding: 0px 6px;
    z-index: 10;
  }

  .repo-selector {
    cursor: pointer;
    background-color: #ddd;
    padding: 6px;
  }
  .repo-selector:hover {
    text-decoration: underline;
  }
  .repo-selector span {
    font-size: 1rem;
  }

  .breadcrumb {
    margin: 0;
    padding: 0 0 0 12px;
    background-color: white;
  }

  /* Mobile Devices */
  @media (max-width: 480px) {

    /*
    .path, .breadcrumb {
      flex-direction: column;
      align-items: unset;
      padding: 0;
    }
    */

  }

  /* Larger Devices */
  @media (min-width: 481px) {
  }


</style>
