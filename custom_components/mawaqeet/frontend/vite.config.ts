import { resolve } from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    emptyOutDir: true,
    outDir: resolve(__dirname, "../www"),
    lib: {
      entry: resolve(__dirname, "src/mawaqeet-prayer-card.ts"),
      formats: ["es"],
      fileName: () => "mawaqeet-prayer-card.js",
    },
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
    minify: true,
    sourcemap: false,
  },
});
