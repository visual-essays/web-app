export default async ({ app }, inject) => {
  // get unscoped token for reading public data
  if (!app.store.state.unscopedToken) {
    let unscopedToken = await fetch(`https://api.juncture-digital.org/gh-token`).then(resp => resp.text())
    app.store.commit('setUnscopedToken', unscopedToken)
  }
  let code = (new URL(location.href)).searchParams.get('code')
  if (code) {
    window.history.replaceState({}, '', '/')
    let authToken = await fetch(`https://api.juncture-digital.org/gh-token?code=${code}`).then(resp => resp.text())
    app.store.commit('setAuthToken', authToken)
  }
  app.store.commit('setGithubClient')
}