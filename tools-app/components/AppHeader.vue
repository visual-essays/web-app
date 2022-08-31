<template>
<div>
  <b-navbar ref="navbar" fixed="top" toggleable="lg" type="dark" variant="primary">
    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-navbar-brand to="/">Juncture Tools</b-navbar-brand>
    
    <b-collapse id="nav-collapse" is-nav>
      <!-- Inline nav items -->
      <b-navbar-nav>
        <b-nav-item to="/media">Media</b-nav-item>
        <b-nav-item to="/essays">Essays</b-nav-item>
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-item v-if="isLoggedIn" @click="logout">Logout</b-nav-item>
        <b-nav-item v-else  @click="login">Login</b-nav-item>
      </b-navbar-nav>

    </b-collapse>
  </b-navbar>
  <div style="height:56px;"></div>

  <repository-selector id="media-repository-selector"></repository-selector>
  <repository-selector id="essays-repository-selector"></repository-selector>

</div>
</template>

<script lang="ts">

import Vue from 'vue'

export default Vue.extend({
  name: 'AppHeader',
  data: () => ({}),
  computed: {
    acct() {return this.$store.state.acct},
    repo() {return this.$store.state.repo},
    isLoggedIn() {return this.$store.state.authToken !== ''},
    isMobile(): string {return this.$store.state.isMobile}
  },
  created() {
    console.log(this.$route)
  },
  methods: {

    login() { window.location.href = `https://github.com/login/oauth/authorize?client_id=f30ce4168a0bb95ecaa3&scope=repo&state=some_state&redirect_uri=${location.href}` },
    logout() { this.$store.commit('clearAuthToken') }

  },
  watch: {}
})

</script>

<style scoped>
   .navbar-toggler {
    padding: 0.25rem 0;
   }

  .repo-selector {
    cursor: pointer;
    color: white;
  }
  .repo-selector:hover {
    text-decoration: underline;
  }
  .repo-selector span {
    font-size: 1.2rem;
  }

</style>
