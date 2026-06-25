/// <reference types="vitest" />

import { type ConfigEnv, type UserConfigExport, loadEnv } from "vite"
import path, { resolve } from "path"
import vue from "@vitejs/plugin-vue"
import vueJsx from "@vitejs/plugin-vue-jsx"
import { createSvgIconsPlugin } from "vite-plugin-svg-icons"
import svgLoader from "vite-svg-loader"
import UnoCSS from "unocss/vite"

/** Configuration documentation: https://cn.vitejs.dev/config */
export default ({ mode }: ConfigEnv): UserConfigExport => {
  const viteEnv = loadEnv(mode, process.cwd()) as ImportMetaEnv
  const { VITE_PUBLIC_PATH } = viteEnv
  return {
    /** Modify base according to actual situation during build */
    base: VITE_PUBLIC_PATH,
    resolve: {
      alias: {
        /** @ symbol points to src directory */
        "@": resolve(__dirname, "./src")
      }
    },
    server: {
      /** Set host: true to use Network mode and access project via IP */
      host: true, // host: "0.0.0.0"
      /** Port number */
      port: 3333,
      /** Whether to automatically open browser */
      open: false,
      /** Allow CORS */
      cors: true,
      /** Whether to exit directly when port is occupied */
      strictPort: false,
      /** API proxy */
      // proxy: {
      //   "/api": {
      //     target: "http://127.0.0.1:5000",
      //     ws: true,
      //     rewrite: (path) => path.replace(/^\/api/, ""),
      //     /** Whether to allow cross-origin */
      //     changeOrigin: true
      //   }
      // },
      /** Warm up commonly used files to improve initial page load speed */
      warmup: {
        clientFiles: ["./src/layouts/**/*.vue"]
      }
    },
    build: {
      /** Warn when a single chunk file exceeds 2048KB */
      chunkSizeWarningLimit: 2048,
      /** Disable gzip compressed size reporting */
      reportCompressedSize: false,
      /** Static assets directory after build */
      assetsDir: "static",
      rollupOptions: {
        output: {
          /**
           * Chunking strategy
           * 1. Note that these package names must exist, otherwise the build will fail
           * 2. If you don't want to customize chunk splitting strategy, you can remove this configuration
           */
          manualChunks: {
            vue: ["vue", "vue-router", "pinia"],
            element: ["element-plus", "@element-plus/icons-vue"],
            vxe: ["vxe-table", "vxe-table-plugin-element", "xe-utils"]
          }
        }
      }
    },
    /** Minifier */
    esbuild:
      mode === "development"
        ? undefined
        : {
            /** Remove console.log during build */
            pure: ["console.log"],
            /** Remove debugger during build */
            drop: ["debugger"],
            /** Remove all comments during build */
            legalComments: "none"
          },
    /** Vite plugins */
    plugins: [
      vue(),
      vueJsx(),
      /** Convert SVG static images to Vue components */
      svgLoader({ defaultImport: "url" }),
      /** SVG */
      createSvgIconsPlugin({
        iconDirs: [path.resolve(process.cwd(), "src/icons/svg")],
        symbolId: "icon-[dir]-[name]"
      }),
      /** UnoCSS */
      UnoCSS()
    ]
    /** Vitest unit test configuration: https://cn.vitest.dev/config */
    // test: {
    //   include: ["tests/**/*.test.ts"],
    //   environment: "jsdom"
    // }
  }
}
