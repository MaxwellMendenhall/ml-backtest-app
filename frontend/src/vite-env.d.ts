/// <reference types="vite/client" />
interface ImportMetaEnv {
    readonly VITE_API_URL: string
    readonly VITE_ANOTHER_VARIABLE: string
    // add more environment variables here...
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}