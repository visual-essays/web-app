<template>
  <div>

    <b-navbar id="top-navbar" align="right" fixed="top"type="dark" variant="primary">
      <b-navbar-brand to="/">Juncture Tools</b-navbar-brand>
    </b-navbar>

    <b-navbar id="bottom-navbar" align="right" fixed="bottom" toggleable="lg" type="dark" variant="primary">

      <b-navbar-nav>
        <b-nav-item to="/media">Media</b-nav-item>
        <b-nav-item to="/essays">Essays</b-nav-item>
      </b-navbar-nav>

      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav class="ml-auto">
          <b-nav-item v-if="isLoggedIn" @click="logout">Logout</b-nav-item>
          <b-nav-item v-else  @click="login">Login</b-nav-item>
        </b-navbar-nav>
      </b-collapse>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
    </b-navbar>

    <Nuxt />

  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'PWALayout',
  created() {
    if ((new URL(location.href)).searchParams.get('code')) window.history.replaceState({}, '', '/')
  }
})
</script>

<style scoped>
  .navbar-toggler {
    margin-left: auto;
  }
  #bottom-navbar .navbar-nav {
    flex-direction: row;
    gap: 24px;
  }
</style>