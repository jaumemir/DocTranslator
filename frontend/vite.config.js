import { defineConfig,loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import path from 'path'
const resolve = (dir) => path.resolve(process.cwd(), dir)

// https://vitejs.dev/config/
export default defineConfig({
    base: './', // Ensure this is not set to '/'
    plugins: [vue(),createSvgIconsPlugin({
      // Specify the icon folders to be cached
      iconDirs: [resolve('src/icons/svg')],
      // iconDirs: [path.resolve(process.cwd(), 'src/assets/icons')],
      // Specify the symbolId format
      symbolId: 'icon-[dir]-[name]'
    })],
    server: {
      proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
}     
  }
},
    resolve: {
        alias: {
          '@': path.resolve(__dirname, './src'),
          '@assets': path.resolve(__dirname, './src/assets'),
        },
        base: './',
        build:{
            assetsDir:"static",
        }
    }
})
