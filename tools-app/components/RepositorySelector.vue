<template>
  <b-modal :id="id">
    <template #modal-header="{ close }">
      <h5>Github Repository Selector</h5>
    </template>

    <template #default="{ hide }">
      <div v-if="isLoggedIn">
        <b-form-checkbox
          id="mode-cb"
          v-model="mode"
          name="mode"
          value="memberOf"
          unchecked-value="any"
        >
        My Github account and organizations
        </b-form-checkbox><br>
      </div>

      <b-input-group>

      <b-form-select
          v-if="mode === 'memberOf'"
          v-model="selectedAcct"
          :options="accounts"
          value-field="login"
          text-field="login"
          :select-size="accounts.length"
        ></b-form-select>
        
        <b-form-input v-else
          id="acctInput"
          autocapitalize="off"
          placeholder="Enter user or account"
          @keyup="acctInputHandler"
          :value="selectedAcct || acct"
        ></b-form-input>

        <b-form-select
          v-if="selectedAcct"
          v-model="selectedRepo"
          :options="repositories"
          value-field="name"
          text-field="name"
          :select-size="Math.max(10,accounts.length)"
        ></b-form-select>`

        <b-form-select
          v-if="selectedRepo"
          v-model="selectedBranch"
          :options="branches"
          value-field="name"
          text-field="name"
          :select-size="Math.max(10,accounts.length)"
        ></b-form-select>`
        
      </b-input-group>
    </template>

    <template #modal-footer="{ cancel }">
      <!-- Emulate built in modal footer ok and cancel button actions -->
      <b-button size="sm" variant="primary" @click="submit">
        Select
      </b-button>
      <b-button size="sm" @click="cancel()">
        Cancel
      </b-button>
    </template>
  </b-modal>

</template>

<script lang="ts">

import Vue from 'vue'
import _ from 'lodash'

const defaultsForRole: any = {
  'media': new Set(['images']),
  'essays': new Set(['essays'])
}

export default Vue.extend({
  name: 'RepositorySelector',
  props: {
    id: { type: String, default: 'essays-repository-selector' }
  },
  data: () => ({
    mode: <string>'memberOf',
    selectedAcct: <string>'',
    selectedRepo: <string>'',
    defaultBranch: <string>'',
    selectedBranch: <string>'',
    accounts: <any[]>[],
    repositories: <any[]>[],
    branches: <string[]>[],
    root: <string>''
  }),
  computed: {
    role(): string {return this.id.split('-')[0]},
    acct(): string {return this.$store.state[`${this.role}Acct`]},
    repo(): string {return this.$store.state[`${this.role}Repo`]},
    isLoggedIn() {return this.$store.state.authToken !== ''},
    githubClient() {return this.$store.state.githubClient}
  },
  created() {
    this.acctInputHandler = <any>_.debounce(this.acctInputHandler, 500)
    this.root = (this.$route.name || '').replace(/-all$/,'').split('/').filter(pe => pe).join('/')
  },
  async mounted() {
    this.$root.$on('bv::modal::show', this.onOpen)
  },
  methods: {
    
    onOpen(evt:any, modalId:string) {
      if (this.id === modalId) {
        console.log(`onOpen: ${this.id} acct=${this.acct} repo=${this.repo} selectedAcct=${this.selectedAcct} selectedRepo=${this.selectedRepo}`)
        if (this.isLoggedIn) this.getMyRepositories()
      }
    },

    async getAccounts(): Promise<string[]> {
      return await Promise.all([this.githubClient.user(), this.githubClient.organizations()])
      .then(responses => responses.flat())
    },
    
    async getRepositories(acct:string): Promise<string[]> {
      console.log(`getRepositories: acct=${acct}`)
      return this.githubClient.repos(acct)
    },
    
    async acctInputHandler() {
      this.selectedAcct = (document.getElementById('acctInput') as HTMLInputElement).value
      this.repositories = this.selectedAcct
        ? await this.getRepositories(this.selectedAcct)
        : []
      this.selectedRepo = this.repositories.length
        ? (this.repositories.find((repo:any) => defaultsForRole[this.role].has(repo.name.toLowerCase())) || this.repositories[0]).name
        : []
    },

    async getMyRepositories() {
      if (this.isLoggedIn) {
        this.accounts = await this.getAccounts()
        this.selectedAcct = this.selectedAcct || this.acct || this.accounts[0].login
        this.repositories = await this.getRepositories(this.selectedAcct)
      }
    },

    submit() {
      (this as any).$bvModal.hide(this.id)
      this.$store.commit(`set${this.toTitleCase(this.role)}Acct`, this.selectedAcct)
      this.$store.commit(`set${this.toTitleCase(this.role)}Repo`, this.selectedRepo)
      console.log(`submit: role=${this.role} selectedBranch=${this.selectedBranch} defaultBranch=${this.defaultBranch}`)
      this.$store.commit(`set${this.toTitleCase(this.role)}Ref`, this.selectedBranch === this.defaultBranch ? '' : this.selectedBranch)
      this.$store.commit(`set${this.toTitleCase(this.role)}Path`, '')
      // let path = `/${[this.root,this.acct,this.repo].filter(pe => pe).join('/')}`
      // this.$router.push({path})
    },

    toTitleCase(s:string) {
      return (s.charAt(0).toUpperCase() + s.slice(1).toLowerCase())
    }
  },

  watch: {
    
    mode(mode) {
      if (mode === 'memberOf') this.getMyRepositories()
    },

    isLoggedIn: {
      async handler(isLoggedIn) {
        this.mode = isLoggedIn ? 'memberOf' : 'any'
        // if (isLoggedIn) this.getMyRepositories()
      },
      immediate: true
    },
    
    acct: {
      async handler() {
        this.selectedAcct = this.acct
      },
      immediate: false
    },

    selectedAcct: {
      async handler () {
        if (this.selectedAcct)
          this.repositories = await this.getRepositories(this.selectedAcct)
      },
      immediate: false
    },
  
    repositories() {
      console.log(this.repositories)
      this.selectedRepo = this.repositories.length
        ? this.selectedAcct === this.acct
          ? this.repo
          : (this.repositories.find((repo:any) => defaultsForRole[this.role].has(repo.name.toLowerCase())) || this.repositories[0]).name
        : ''
    },

    selectedRepo() {
      this.defaultBranch = this.repositories.find((repo:any) => repo.name === this.selectedRepo).default_branch
      this.githubClient.branches(this.selectedAcct, this.selectedRepo)
        .then((branches:any[]) => this.branches = branches.map((item:any) => item.name))
    },

    branches() {
      this.selectedBranch = this.branches.length
        ? this.branches.find((branch:string) => branch === this.defaultBranch) || this.branches[0]
        : ''
    },

  }
})

</script>

<style scoped>
</style>
