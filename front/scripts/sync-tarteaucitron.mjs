import { cpSync, existsSync, rmSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const rootDir = dirname(dirname(fileURLToPath(import.meta.url)))
const src = join(rootDir, "node_modules", "tarteaucitronjs")
const dest = join(rootDir, "public", "tarteaucitron")

if (!existsSync(src)) {
  console.error("tarteaucitronjs is not installed, run npm install first")
  process.exit(1)
}

if (existsSync(dest)) {
  rmSync(dest, { recursive: true })
}

cpSync(src, dest, {
  recursive: true,
  filter: (path) => !/\.(md|txt)$|package\.json$|LICENSE$|\.github/.test(path)
})
