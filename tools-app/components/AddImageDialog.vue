<template>
  <b-modal id="add-image">

    <template #modal-header="{ close }">
      <h5>Add Image</h5>
    </template>

    <template #default="{ hide }">
    <b-overlay :show="busy" rounded="sm">

      <div :style="`height:${imageUrl ? 150 : 0}px;`">
        <img ref="img" style="padding-left:16px; height:100%;" :src="imageUrl">
      </div>

      <b-container v-if="file.name" fluid="sm" class="image-data">
        <b-row>
          <b-col sm="3" class="label"><label for="folder">Folder:</label></b-col>
          <b-col sm="9" class="value">
            <b-form-input type="text" plaintext ref="folder" id="folder" name="folder" :value="folder"></b-form-input>
            <b-button size="sm" variant="outline-primary" v-b-modal.github-folder-selector>Change</b-button>
          </b-col>
        </b-row>
        <b-row>
          <b-col sm="3" class="label"><label for="fname">Name</label></b-col>
          <b-col sm="9" class="value">
            <b-form-input 
              ref="fname"
              id="fname"
              name="fname"
              type="text"
              :state="fileName.trim().length > 0"
              placeholder="Image name (required)"
              v-model="fileName"
            ></b-form-input>
          </b-col>
        </b-row>
        <b-row>
          <b-col sm="3" class="label"><label for="summary">Summary</label></b-col>
          <b-col sm="9" class="value">
            <b-form-input
              ref="summary"
              id="summary"
              name="summary"
              type="text" 
              placeholder="Short description (optional)"
              v-model="summary"
            ></b-form-input>
          </b-col>
        </b-row>
        <b-row v-for="value, key in exifData" :key="key" style="flex-wrap:nowrap;">
          <b-col sm="3" class="label" v-html="key" style="width:unset;"></b-col>
          <b-col sm="9" class="value" v-html="value"></b-col>
        </b-row>
        <b-row>
          <b-col sm="12" style="padding-left:0;">
            <depicted></depicted>
          </b-col>
        </b-row>
      </b-container>

      <input v-else ref="filePicker" type="file" accept="image/x-png,image/jpeg,image/gif" @change="fileSelected"/>
    </b-overlay>
    </template>

    <template #modal-footer="{ cancel }">
      <b-button :disabled="busy || !fileName" size="sm" variant="primary" @click="addImage">Add</b-button>
      <b-button size="sm" @click="cancel()">Cancel</b-button>
    </template>

  </b-modal>
</template>

<script lang="ts">

import Vue from 'vue'
import EXIF from 'exif-js'
import { faFolder }  from '@fortawesome/free-regular-svg-icons'
import GithubFileSelector from './GithubFileManager.vue'
const yaml = require('js-yaml')

export default Vue.extend({
  components: { GithubFileSelector },
  name: 'AddImage',
  data: () => ({
    busy: false,
    dirList: <any[]>[],
    folder: <string>'',
    file: <File>{},
    fileName: <string>'',
    fileExtension: <string>'',
    summary: <string>'',
    imageUrl: '',
    exifData: <any>{}
  }),
  computed: {
    acct(): string {return this.$store.state.mediaAcct},
    repo(): string {return this.$store.state.mediaRepo},
    ref(): string {return this.$store.state.mediaRef},
    path(): string {return this.$store.state.mediaPath},
    isLoggedIn() {return this.$store.state.authToken !== ''},
    githubClient() {return this.$store.state.githubClient},
    dirs() {return this.dirList.filter(item => item.type === 'dir').map(item => item.name)},
    files() {return this.dirList.filter(item => item.type === 'dir').map(item => item.name)},
    faFolder() { return faFolder }
  },
  async mounted() {
    this.$root.$on('bv::modal::show', this.onOpen)
    this.$root.$on('bv::modal::hide', this.onClose)
    this.$root.$on('github-folder-changed', (path: string) => this.folder = path)
  },
  methods: {

    fileSelected() {
      let filePicker = this.$refs.filePicker as HTMLInputElement
      if (filePicker && filePicker.files && filePicker.files.length > 0) {
        this.file = filePicker.files[0]
        let parts: string[] = this.file.name.split('.')
        this.fileExtension = parts.slice(-1)[0].toLowerCase()
        let urlCreator = window.URL || window.webkitURL
        let imageEl = this.$refs.img as HTMLImageElement
        imageEl.onload = () => {
          this.getExifTags().then(data => this.exifData = data)
        }
        this.imageUrl = urlCreator.createObjectURL(this.file)
        
      }
    },

    onOpen(evt:any, modalId:string) {
      if (modalId === 'add-image') {
        this.folder = this.path
        this.githubClient.dirlist(this.acct, this.repo, this.path, this.ref).then((dirList:any[]) => this.dirList = dirList)
      }
    },

    onClose(evt:any, modalId:string) {
      this.busy = false
      if (modalId === 'add-image') {
        this.file = ({} as File)
        this.imageUrl = ''
        this.folder = ''
        this.summary = ''
        this.fileName = ''
        this.fileExtension = ''
      }
    },

    async addImage() {
      this.busy = true
      let metadata = await this.getMetadata()
      const reader = new FileReader()
      reader.onloadend = async () => {
        const base64data = reader.result 
        let fileName = this.fileName.replace(/ /g, '_')
        let path = [...this.folder.split('/').filter(pe => pe), ...[fileName]].join('/')
        await this.githubClient.putFile(this.acct, this.repo, `${path}.${this.fileExtension}`, base64data, this.ref)
        if (Object.keys(metadata))
          await this.githubClient.putFile(this.acct, this.repo, `${path}.yaml`, yaml.dump(metadata), this.ref);
        ;(this as any).$bvModal.hide('add-image')
      }
      reader.readAsBinaryString(this.file)
    },

    async getMetadata() {
      let metadata: any = {}
      if (this.summary) metadata.summary = this.summary
      let depicted = (Array.from(document.querySelectorAll('.depicted [data-entity]')) as HTMLElement[])
        .map(el => el.dataset.entity)
      if (depicted.length > 0) metadata.depicts = depicted
      let exifTags: any = await this.getExifTags()
      if (exifTags) metadata = {...metadata, ...exifTags}
      return metadata
    },

    async getExifTags() {
      function gpsCoords (coords:any, ref:any) {
        let decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
        if (ref === 'S' || ref === 'W') {
          decimal_degrees = -decimal_degrees
        }
        return decimal_degrees.toFixed(8)
      }

      return new Promise((resolve, reject) => {
        let img: any = this.$refs.img
        let data:any        
        EXIF.getData(img, () => {
          let tags = EXIF.getAllTags(img)
          if (tags) {
            data = {}
            if (tags.GPSLatitude) {
              let lat = gpsCoords(tags.GPSLatitude, tags.GPSLatitudeRef)
              let lon = gpsCoords(tags.GPSLongitude, tags.GPSLongitudeRef)
              data.location = `${lat},${lon}`
            }
            if (tags.DateTime) data.created = tags.DateTime
            if (tags.Orientation) data.orientation = tags.Orientation
            
            // if (tags.PixelXDimension) data.width = tags.PixelXDimension
            // if (tags.PixelYDimension) data.height = tags.PixelYDimension
            // if (tags.Model) data.model = tags.Model
          }
          resolve(data)
        })
      })
    }

  },

  watch: {}
})

</script>

<style scoped>
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
  .dir svg {
    margin-right: 6px;
  }

  .row {
    margin-top: 12px;
    align-items: center;
  }
  .image-data {
    margin-top: 12px;
  }
  .image-data .label {
    font-weight: bold;
    padding-left: 0;
  }
  .image-data .label::after {
    font-weight: bold; 
    content: ":";
  }
  .image-data .value {
    display: flex;
    padding-left: 0;
  }
  .image-data .value .btn {
    height: calc(1.5em + 0.75rem + 4px);
  }
</style>
