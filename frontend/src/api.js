import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// Request Interceptor: Add API Key
api.interceptors.request.use(config => {
  const apiKey = localStorage.getItem('api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Response Interceptor: Handle 401
api.interceptors.response.use(response => response, async error => {
  if (error.response && error.response.status === 401) {
    const apiKey = window.prompt("Authentication Required. Please enter the API Key (found in server logs or data/secrets.json):");
    if (apiKey) {
      localStorage.setItem('api_key', apiKey);
      // Retry the original request with the new key
      error.config.headers['X-API-Key'] = apiKey;
      return api(error.config);
    }
  }
  return Promise.reject(error);
});

export const getUserStats = () => api.get('/user').then(res => res.data);
export const getCurriculum = () => api.get('/curriculum').then(res => res.data);
export const getStudyItems = () => api.get('/study').then(res => res.data);
export const confirmStudyItem = (word) => api.post('/study/confirm', { word });
export const getQuizQuestion = () => api.get('/quiz/vocab').then(res => res.data);
export const submitQuizAnswer = (questionId, answer) => api.post('/quiz/answer', { question_id: questionId, answer }).then(res => res.data);
export const searchDictionary = (q) => api.get('/dictionary/search', { params: { q } }).then(res => res.data);
export const addToDictionary = (word, kana, meanings) => api.post('/dictionary/add', { word, kana, meanings });
export const getShopItems = () => api.get('/shop').then(res => res.data);
export const buyShopItem = (itemId) => api.post('/shop/buy', { item_id: itemId });
export const getSettings = () => api.get('/settings').then(res => res.data);
export const updateSettings = (track, theme, displayMode, showRomaji) => api.post('/settings', {
    track,
    theme,
    display_mode: displayMode,
    show_romaji: showRomaji
});

export const getWordOfTheDay = () => api.get('/word_of_the_day').then(res => res.data);

export default api;
