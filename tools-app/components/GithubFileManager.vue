<template>
  <b-modal :id="id">

    <template #modal-header="{ close }">
      <h5>File Selector</h5>
    </template>

    <template #default="{ hide }">
      
      <b-breadcrumb>
        <b-breadcrumb-item v-for="crumb, idx in breadCrumbs" :key="`crumb-${idx}`" v-html="crumb.text" @click="update(crumb.to)"></b-breadcrumb-item>
      </b-breadcrumb>

      <b-button-group v-if="dirs.length > 0" size="sm" class="dir">
        <b-button v-for="dir in dirs" :key="dir" pill @click="update(`${curPath}/${dir}`)">
          <fa :icon="faFolder" title="Folder"></fa>{{dir.split('/').pop()}}
        </b-button>
      </b-button-group>

      <ul class="file-list" v-if="showFiles && files.length > 0">
        <li class="file" v-for="file in files" :key="file.sha">
          <span v-html="file.name"></span>
          <fa class="trash-icon" :icon="faTrashCan" title="Delete file" @click="deleteFile(file)"></fa>
        </li>
      </ul>

      <b-modal :id="`${id}-new-folder-name`" title="Create Folder" hide-backdrop>
        <b-form-input v-model="newFolderName" placeholder="New Folder Name"></b-form-input>
      </b-modal>

    </template>

    <template #modal-footer="{ cancel }">
      <div class="w-100">
        <b-button class="float-left" size="sm" variant="primary" v-b-modal.new-folder-name>New Folder</b-button>
        <b-button class="float-right" size="sm" variant="primary" @click="select">Select</b-button>
        <b-button class="float-right" size="sm" style="margin-right:12px;" @click="cancel()">Cancel</b-button>
      </div>
    </template>

  </b-modal>
</template>

<script lang="ts">

import Vue from 'vue'
import { faFolder, faTrashCan }  from '@fortawesome/free-regular-svg-icons'

export default Vue.extend({
  name: 'GithubFileManager',
  props: {
    id: { type: String, default: 'github-file-manager' },
    showFiles: { type: Boolean, default: () => false }
  },
  data: () => ({
    dirList: <any[]>[],
    curPath: <string>'',
    newFolderName: ''
  }),
  computed: {
    acct(): string {return this.$store.state.acct},
    repo(): string {return this.$store.state.repo},
    path(): string {return this.$store.state.path},
    githubClient() {return this.$store.state.githubClient},
    dirs() {return this.dirList.filter(item => item.type === 'dir').map(item => item.name)},
    files() {return this.dirList.filter(item => item.type === 'file')},
    breadCrumbs(): any[] {
      console.log(`curPath=${this.curPath}`)
      let breadCrumbs = [{text: 'root', to: ``}]
      let pathElems = this.curPath.split('/').filter(pe => pe)
      for (let i = 0; i < pathElems.length; i++) {
        breadCrumbs.push({text: pathElems[i], to: `${pathElems.slice(0,i+1).join('/')}`})
      }
      console.log(breadCrumbs)
      return breadCrumbs
    },
    faFolder() { return faFolder },
    faTrashCan() { return faTrashCan }
  },
  async mounted() {
    this.$root.$on('bv::modal::show', this.onOpen)
    this.$root.$on('bv::modal::hide', this.onClose)
  },
  methods: {

    select() {
      (this as any).$bvModal.hide(this.id)
      this.$root.$emit('github-folder-changed', this.curPath)
    },

    onOpen(evt:any, modalId:string) {
      if (modalId === this.id) {
        this.curPath = this.path
        this.update(this.path)
      }
    },

    onClose(evt:any, modalId:string) {
      if (modalId === this.id) {
        console.log(`onClose: ${this.id}`)
        this.dirList = []
      } else if (modalId === `${this.id}-new-folder-name`) {
        this.createFolder()
      }
    },

    update(path:string) {
      this.curPath = path
      this.githubClient.dirlist(this.acct, this.repo, this.curPath).then((dirList:any[]) => this.dirList = dirList)
    },

    async createFolder() {
      if (this.newFolderName) {
        let path = [...this.curPath.split('/').filter(pe => pe), ...[this.newFolderName]].join('/')
        console.log(`createFolder: name=${this.newFolderName} path=${path}`)
        await this.githubClient.newFolder(this.acct, this.repo, path)
        this.githubClient.dirlist(this.acct, this.repo, this.curPath).then((dirList:any[]) => this.dirList = dirList)
      }
    },

    async deleteFile(toDelete:any) {
      let path = `${this.curPath}/${toDelete.name}`
      console.log(`deleteFile: path=${path} sha=${toDelete.sha}`)
      await this.githubClient.deleteFile(this.acct, this.repo, path, toDelete.sha)
      this.dirList = this.dirList.filter(file => file.name !== toDelete.name)
      if (this.files.length === 0) {
        this.curPath = this.curPath.split('/').slice(0,-1).join('/')
        this.githubClient.dirlist(this.acct, this.repo, this.curPath).then((dirList:any[]) => this.dirList = dirList)
      }
    }

  },

  watch: {}
})

</script>

<style scoped>
  .dir.btn-group {
    width: 100%;
  }
  .dir.btn-group .btn {
    color: black;
    background-color: white;
    margin: 0 0 .5rem .5rem;
    flex: none;
  }
  .dir svg {
    margin-right: 6px;
  }
  .breadcrumb-item {
    cursor: pointer;
  }

  [data-icon="trash-can"] {
    color: red;
    cursor: pointer;
  }

  ul.file-list {
    padding-left: 0;
    height: 40vh;
    overflow-y: scroll;
  }

  .file {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 0 12px;
    border: 1px solid transparent;
    border-radius: 3px;
  }

  .file .trash-icon {
    margin-left: auto;
  }

  .file:hover {
    background-color: #ddd;
    border: 1px solid #999;
    border-radius: 3px;
  }

</style>
