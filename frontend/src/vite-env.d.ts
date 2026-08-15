/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the Python API. Unset means read data.json instead. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
