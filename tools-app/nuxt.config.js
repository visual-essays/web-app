export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // Target: https://go.nuxtjs.dev/config-target
  target: 'static',
  env: {
    isDev: process.env.NODE_ENV === 'DEV'
  },

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: 'Juncture Tools',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' },
      { name: 'apple-apple-mobile-web-app-capable', content: 'yes' },
      { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
      { name: 'theme-color', content: '#5A162E' },
    ],
    link: [
      { rel: 'icon', type: 'image/svg+xml', href: 'https://visual-essays.github.io/web-app/static/images/favicon.svg' },
      { rel: 'icon', type: 'image/x-icon', href: 'https://visual-essays.github.io/web-app/static/images/favicon.ico' },
      // { rel: 'stylesheet', href: 'https://unpkg.com/visual-essays@0.2.53/dist/visual-essays/visual-essays.css' }
      { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css' }
    ],
    script: [
      {src: `${process.env.NODE_ENV === 'DEV' ? 'http://localhost:3333/build' : 'https://unpkg.com/visual-essays/dist/visual-essays'}/visual-essays.esm.js`, type: 'module'},
      {src: 'https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js'}
    ]
  },

  vue: {
    config: {
      productionTip: false,
      devtools: true
    }
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    // { src: '@/plugins/wc-plugin.js', ssr: false },
    { src: '@/plugins/env.js', ssr: false },
    { src: '@/plugins/auth-token.js', ssr: false },
    { src: '@/plugins/bootstrap.js', ssr: false }

  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    '@nuxt/typescript-build',
    '@nuxtjs/fontawesome'
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/bootstrap
    'bootstrap-vue/nuxt',
    // https://go.nuxtjs.dev/pwa
    '@nuxtjs/pwa'
  ],

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    manifest: {
      lang: 'en',
      start_url: 'https://beta.juncture-digital.org/tools?standalone=true',
      theme_color: '#5A162E'
    },
    icon: {
      source: 'static/icon.jpg',
      // targetDir: '../static/icons',
      // cacheDir: '../static/icons'
    }
  },

  fontawesome: {
    component: 'fa',
    icons: {
    }
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
  },

  generate: {
    fallback: true
  }
}
