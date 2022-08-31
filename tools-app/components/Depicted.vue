<template>
<b-container class="depicted">
  <div class="heading">
    <b>Depicted entities</b>&nbsp;<i>(People, places, objects, etc)</i>
  </div>
  <ul class="depicted:">
    <li :data-entity="item.id" v-for="item in depicted" :key="item.id">
      <span class="label">
        <a :href="`https://www.wikidata.org/entity/${item.id}`" v-html="item.label"></a>
      </span>
      <span class="description" v-html="item.description"></span>
      <span class="push" v-b-tooltip.hover title="Remove entity">
        <fa class="remove-icon" :icon="removeIcon" v-b-tooltip.hover title="Remove entity" @click="removeEntity(item)"></fa>
      </span>
    </li>
  </ul>
  <ve-wikidata-search @entity-selected="addEntity"></ve-wikidata-search>
</b-container>
</template>

<script lang="ts">

import Vue from 'vue'
import { faXmarkCircle }  from '@fortawesome/free-regular-svg-icons'

export default Vue.extend({
  name: 'Depicted',
  data: () => ({
    depicted: <any[]>[]
  }),
  computed: {
    removeIcon() { return faXmarkCircle }
  },
  methods: {
    
    addEntity(event:any) {
      this.depicted = [...this.depicted, event.detail]
    },

    removeEntity(toRemove:any) {
      this.depicted = this.depicted.filter(item => item.id !== toRemove.id)
    }

  }
})

</script>

<style scoped>

  .depicted {
    padding: 0;
  }

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    padding: 6px 12px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }

  .depicted .label {
    min-width: 25%;
  }
  .push {
    margin-left: auto;
  }
  .remove-icon {
    color: #999;
    cursor: pointer;
  }
  .remove-icon:hover {
    color: red;
    cursor: pointer;
  }

</style>
