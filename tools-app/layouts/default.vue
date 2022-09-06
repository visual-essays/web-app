<template>
  <div class="wrapper">
    <!-- <app-header></app-header> -->

    <b-navbar id="top-navbar" align="right" fixed="top" type="dark" variant="primary">
      <b-navbar-brand href="/">Juncture</b-navbar-brand>
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

    <github-file-selector id="essays-file-selector"></github-file-selector>
    <github-file-selector id="media-file-selector" folders-only></github-file-selector>
    <repository-selector id="media-repository-selector"></repository-selector>
    <repository-selector id="essays-repository-selector"></repository-selector>

  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'DefaultLayout',
  data: () => ({}),
  computed: {
    acct() {return this.$store.state.acct},
    repo() {return this.$store.state.repo},
    isLoggedIn() {return this.$store.state.authToken !== ''},
    isMobile(): string {return this.$store.state.isMobile}
  },
  created() {
    if ((new URL(location.href)).searchParams.get('code')) window.history.replaceState({}, '', '/')
  },  
  methods: {

    login() { window.location.href = `https://github.com/login/oauth/authorize?client_id=f30ce4168a0bb95ecaa3&scope=repo&state=some_state&redirect_uri=${location.href}` },
    logout() { this.$store.commit('clearAuthToken') }

  }
})
</script>

<style scoped>
  .wrapper {
    padding: 56px 0;
  }
  .navbar-toggler {
    margin-left: auto;
  }
  #bottom-navbar .navbar-nav {
    flex-direction: row;
    gap: 24px;
  }

  .preview .navbar {
    display: none;
  }
  .preview .wrapper {
    padding: 0;
  }
</style>