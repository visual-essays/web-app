<template>
  <div>

    <content-path tool="media"></content-path>

    <b-button-group size="sm">
      <b-button v-for="dir in dirs" :key="dir" v-html="dir.split('/').pop()" :to="dir" pill></b-button>
    </b-button-group>
  
    <ve-image-grid as-cards >
      <ul>
        <li v-for="manifest, idx in manifests" :key="`grid-${idx}`" v-html="manifest"></li>
      </ul>
    </ve-image-grid>

    <b-button v-if="isLoggedIn" pill class="fab" variant="primary" v-b-modal.add-image>+</b-button>
    <add-image-dialog></add-image-dialog>

  </div>
</template>

<script lang="ts">

import Vue from 'vue'

const iiifServer = 'https://iiif.juncture-digital.org'

const fileExtensions = new Set(['yaml','jpg','jpeg','jp2','png','tif','tiff'])
const ignore = new Set(['iiif-props.yaml', 'iiif-props.template.yaml'])

export default Vue.extend({
  name: 'Media',
  data: () => ({}),
  computed: {
    dirList(): any[] {return this.$store.state.mediaDirList},
    acct(): string {return this.$store.state.mediaAcct},
    repo(): string {return this.$store.state.mediaRepo},
    path(): string {return this.$store.state.mediaPath},
    root(): string {return [this.acct, this.repo, ...this.path.split('/')].filter(pe => pe).join('/') },
    manifests(): string[] {return Array.from(new Set((this.dirList || [])
      .filter((item:any) => item.type === 'file')
      .filter((item:any) => !ignore.has(item.name))
      .filter((item:any) => fileExtensions.has(item.name.split('.').pop().toLowerCase()))
      .map((item:any) => `${iiifServer}/gh:${this.root}/${encodeURIComponent(item.name.split('.').slice(0,-1).join('.'))}/manifest.json`)))
    },
    dirs(): string[] {return (this.dirList || []) 
          .filter((item:any) => item.type === 'dir')
          .map((item:any) => `/media/${this.root}/${item.name}`)
    },
    isLoggedIn() {return this.$store.state.authToken !== ''}
    ,
  },
  created() {},
  async mounted() {
    console.log(`${this.$options.name}.mounted`, this.dirList)
  },
  methods: {},
  watch: {}
})

</script>

<style scoped>
  [v-cloak] {
    display: none
  }
  
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 12px;
    font-family: Roboto, sans-serif;
  }
  
  .dir.btn-group {
    width: 100%;
    background-color: #e9ecef;
  }
  .dir.btn-group .btn {
    color: black;
    background-color: white;
    margin: 0 0 .5rem .5rem;
    flex: none;
  }

  .fab {
    position: fixed;
    right: 10px;
    bottom: 70px;
    font-weight: bold;
    font-size: 1.2rem;
  }

</style>
