const storage = {
  get: (key, defaultValue = null) => {
    try {
      const val = localStorage.getItem(key);
      if (val === null) return defaultValue;
      return JSON.parse(val);
    } catch {
      return defaultValue;
    }
  },
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.error('Storage set error:', e);
    }
  },
  remove: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.error('Storage remove error:', e);
    }
  }
};

export const KEYS = {
  WEIXIN_ID: 'weixin_id',
  LLM_PROVIDER: 'llm_provider',
  CURRENT_PAGE: 'current_page',
  THEME: 'theme',
  LLM_API_KEY: 'llm_api_key',
  LLM_MODEL: 'llm_model',
  WHISPER_API_KEY: 'whisper_api_key',
  WHISPER_LANGUAGE: 'whisper_language',
  DEFAULT_FPS: 'default_fps',
  STORAGE_PATH: 'storage_path',
  AUTO_START: 'auto_start'
};

export default storage;
