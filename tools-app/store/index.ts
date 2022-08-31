import { GithubClient } from '../gh-utils'

export const state = () => ({
  mediaAcct: localStorage.getItem('gh-media-acct') || '',
  mediaRepo: localStorage.getItem('gh-media-repo') || '',
  mediaRef: localStorage.getItem('gh-media-ref') || '',
  mediaPath: localStorage.getItem('gh-media-path') || '',
  mediaContentPath: localStorage.getItem('gh-media-content-path') || '',
  mediaDirList: <any[]>[],

  essaysAcct: localStorage.getItem('gh-essays-acct') || '',
  essaysRepo: localStorage.getItem('gh-essays-repo') || '',
  essaysRef: localStorage.getItem('gh-essays-ref') || '',
  essaysPath: localStorage.getItem('gh-essays-path') || '',
  essaysContentPath: localStorage.getItem('gh-essays-content-path') || '',
  essaysDirList: <any[]>[],

  fileSelectorPath: '',
  
  unscopedToken: localStorage.getItem('gh-unscoped-token') || '',
  authToken: localStorage.getItem('gh-auth-token') || '',
  githubClient: GithubClient,
  
  isMobile: false
})
  
export const mutations = {
  
  setMediaAcct (state: any, acct: string) {
    state.mediaAcct = acct
    if (acct) localStorage.setItem('gh-media-acct', acct)
    else localStorage.removeItem('gh-media-acct')
  },
  setMediaRepo (state: any, repo: string) {
    state.mediaRepo = repo
    if (repo) localStorage.setItem('gh-media-repo', repo)
    else localStorage.removeItem('gh-media-repo')
  },
  setMediaRef (state: any, ref: string) {
    state.mediaRef = ref
    if (ref) localStorage.setItem('gh-media-ref', ref)
    else localStorage.removeItem('gh-media-ref')
  },
  setMediaPath (state: any, path: string) {
    state.mediaPath = path
    if (path) localStorage.setItem('gh-media-path', path)
    else localStorage.removeItem('gh-media-path')
  },
  setMediaContentPath (state: any, path: string) {
    state.mediaContentPath = path
    console.log(`setMediaContentPath`, path)
    if (path) localStorage.setItem('gh-media-content-path', path)
    else localStorage.removeItem('gh-media-content-path')
  },
  setMediaDirList (state: any, dirList: any[]) {
    state.mediaDirList = dirList
  },

  setEssaysAcct (state: any, acct: string) {
    state.essaysAcct = acct
    if (acct) localStorage.setItem('gh-essays-acct', acct)
    else localStorage.removeItem('gh-essays-acct')
  },
  setEssaysRepo (state: any, repo: string) {
    state.essaysRepo = repo
    if (repo) localStorage.setItem('gh-essays-repo', repo)
    else localStorage.removeItem('gh-essays-repo')
  },
  setEssaysRef (state: any, ref: string) {
    state.essaysRef = ref
    if (ref) localStorage.setItem('gh-essays-ref', ref)
    else localStorage.removeItem('gh-essays-ref')
  },
  setEssaysPath (state: any, path: string) {
    state.essaysPath = path
    if (path) localStorage.setItem('gh-essays-path', path)
    else localStorage.removeItem('gh-essays-path')
  },
  setEssaysContentPath (state: any, path: string) {
    state.essaysContentPath = path
    if (path) localStorage.setItem('gh-essays-content-path', path)
    else localStorage.removeItem('gh-essays-content-path')
  },
  setEssaysDirList (state: any, dirList: any[]) {
    state.essaysDirList = dirList
  },

  setFileSelectorPath (state: any, path: string) { state.fileSelectorPath = path },

  setUnscopedToken (state: any, token: string) {
    state.unscopedToken = token
    if (token) {
      localStorage.setItem('gh-unscoped-token', token)
      state.githubClient = new GithubClient(state.authToken || state.unscopedToken)
    } else {
      localStorage.removeItem('gh-unscoped-token')
      state.githubClient = state.authToken ? new GithubClient(state.authToken) : null
    }
  },

  setAuthToken (state: any, token: string) {
    state.authToken = token
    if (token) {
      localStorage.setItem('gh-auth-token', token)
      state.githubClient = new GithubClient(state.authToken)
    } else {
      localStorage.removeItem('gh-auth-token')
      state.githubClient = state.unscopedToken ? new GithubClient(state.unscopedToken) : null
    }
  },
  clearAuthToken (state: any) {
    state.authToken = ''
    localStorage.removeItem('gh-auth-token')
    if (state.unscopedToken) state.githubClient = new GithubClient(state.unscopedToken)
  },

  setGithubClient (state: any) {
    let token = state.authToken || state.unscopedToken
    state.githubClient = token ? new GithubClient(token) : null
  },

  setIsMobile (state: any, isMobile: boolean) { state.isMobile = isMobile }

}
  