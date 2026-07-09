// @ts-check
import { defineConfig } from 'astro/config';

// Served at the root custom domain ff.patrickflower.com, so base is '/'.
// Committed static assets (CNAME, favicon) live in ./static; the build output
// goes to ./public, which is gitignored (see .gitignore + README repo layout).
export default defineConfig({
  site: 'https://ff.patrickflower.com',
  base: '/',
  publicDir: './static',
  outDir: './public',
  build: { format: 'directory' },
});
