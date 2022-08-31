function isMobile() {
  return ('ontouchstart' in document.documentElement && /mobi/i.test(navigator.userAgent) )
}

export default async ({ app }, inject) => {
  app.store.commit('setIsMobile', isMobile() )
}