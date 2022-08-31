import { defineCustomElements } from 'visual-essays/loader'

if (process.client)
defineCustomElements(window)