/**
 * Offline Story Cache using IndexedDB
 * Stores full narrative data for offline reading
 */

const DB_NAME = 'sv_offline_stories';
const DB_VERSION = 1;
const STORE_NAME = 'narratives';

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('student_id', 'student_id', { unique: false });
        store.createIndex('saved_date', 'saved_date', { unique: false });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function saveStoryOffline(narrative) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const record = {
      ...narrative,
      saved_date: new Date().toISOString(),
      offline: true,
    };
    const req = store.put(record);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

export async function getOfflineStories(studentId = null) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    let req;
    if (studentId) {
      const idx = store.index('student_id');
      req = idx.getAll(studentId);
    } else {
      req = store.getAll();
    }
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

export async function getOfflineStory(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const req = tx.objectStore(STORE_NAME).get(id);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => reject(req.error);
  });
}

export async function removeOfflineStory(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const req = tx.objectStore(STORE_NAME).delete(id);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

export async function isStorySaved(id) {
  const story = await getOfflineStory(id);
  return !!story;
}

export async function getOfflineStorageInfo() {
  const stories = await getOfflineStories();
  const totalSize = stories.reduce((acc, s) => {
    return acc + new Blob([JSON.stringify(s)]).size;
  }, 0);
  return {
    count: stories.length,
    sizeBytes: totalSize,
    sizeMB: (totalSize / (1024 * 1024)).toFixed(2),
  };
}

export function isOnline() {
  return navigator.onLine;
}
