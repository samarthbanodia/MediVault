/**
 * Cache Service - IndexedDB-based caching for offline support
 *
 * Features:
 * - IndexedDB for persistent offline storage
 * - Automatic cache invalidation
 * - TTL (Time To Live) support
 * - Batch operations
 * - Type-safe interfaces
 */

// Types
interface CacheEntry<T> {
  key: string;
  data: T;
  timestamp: number;
  expiresAt?: number;
}

interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
}

// ============================================================================
// INDEXEDDB SETUP
// ============================================================================

const DB_NAME = 'MediVaultCache';
const DB_VERSION = 1;
const STORES = {
  RECORDS: 'records',
  BIOMARKERS: 'biomarkers',
  ANOMALIES: 'anomalies',
  SEARCH_RESULTS: 'search_results',
  USER_DATA: 'user_data'
};

class CacheService {
  private db: IDBDatabase | null = null;
  private initPromise: Promise<void> | null = null;

  constructor() {
    this.initPromise = this.init();
  }

  /**
   * Initialize IndexedDB
   */
  private async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) {
        console.warn('IndexedDB not supported');
        reject(new Error('IndexedDB not supported'));
        return;
      }

      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('IndexedDB open failed:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('✓ IndexedDB cache initialized');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object stores
        Object.values(STORES).forEach(storeName => {
          if (!db.objectStoreNames.contains(storeName)) {
            db.createObjectStore(storeName, { keyPath: 'key' });
          }
        });
      };
    });
  }

  /**
   * Ensure database is initialized
   */
  private async ensureInitialized(): Promise<void> {
    if (this.db) return;
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  /**
   * Check if a cache entry is expired
   */
  private isExpired(entry: CacheEntry<any>): boolean {
    if (!entry.expiresAt) return false;
    return Date.now() > entry.expiresAt;
  }

  /**
   * Get value from cache
   */
  async get<T>(storeName: string, key: string): Promise<T | null> {
    try {
      await this.ensureInitialized();
      if (!this.db) return null;

      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.get(key);

        request.onsuccess = () => {
          const entry: CacheEntry<T> | undefined = request.result;

          if (!entry) {
            resolve(null);
            return;
          }

          // Check if expired
          if (this.isExpired(entry)) {
            // Delete expired entry
            this.delete(storeName, key);
            resolve(null);
            return;
          }

          resolve(entry.data);
        };

        request.onerror = () => {
          console.error('Cache get failed:', request.error);
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }

  /**
   * Set value in cache
   */
  async set<T>(storeName: string, key: string, data: T, options?: CacheOptions): Promise<void> {
    try {
      await this.ensureInitialized();
      if (!this.db) return;

      const entry: CacheEntry<T> = {
        key,
        data,
        timestamp: Date.now(),
        expiresAt: options?.ttl ? Date.now() + options.ttl : undefined
      };

      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.put(entry);

        request.onsuccess = () => resolve();
        request.onerror = () => {
          console.error('Cache set failed:', request.error);
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }

  /**
   * Delete value from cache
   */
  async delete(storeName: string, key: string): Promise<void> {
    try {
      await this.ensureInitialized();
      if (!this.db) return;

      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.delete(key);

        request.onsuccess = () => resolve();
        request.onerror = () => {
          console.error('Cache delete failed:', request.error);
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }

  /**
   * Clear entire store
   */
  async clear(storeName: string): Promise<void> {
    try {
      await this.ensureInitialized();
      if (!this.db) return;

      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.clear();

        request.onsuccess = () => resolve();
        request.onerror = () => {
          console.error('Cache clear failed:', request.error);
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Cache clear error:', error);
    }
  }

  /**
   * Get all values from a store
   */
  async getAll<T>(storeName: string): Promise<T[]> {
    try {
      await this.ensureInitialized();
      if (!this.db) return [];

      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.getAll();

        request.onsuccess = () => {
          const entries: CacheEntry<T>[] = request.result || [];

          // Filter out expired entries
          const validEntries = entries.filter(entry => !this.isExpired(entry));

          resolve(validEntries.map(entry => entry.data));
        };

        request.onerror = () => {
          console.error('Cache getAll failed:', request.error);
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Cache getAll error:', error);
      return [];
    }
  }

  // ============================================================================
  // CONVENIENCE METHODS FOR SPECIFIC DATA TYPES
  // ============================================================================

  /**
   * Cache medical records
   */
  async cacheRecords(records: any[], ttl = 5 * 60 * 1000): Promise<void> {
    await this.set(STORES.RECORDS, 'all_records', records, { ttl });
  }

  /**
   * Get cached records
   */
  async getCachedRecords(): Promise<any[] | null> {
    return await this.get(STORES.RECORDS, 'all_records');
  }

  /**
   * Cache specific record
   */
  async cacheRecord(recordId: string, record: any, ttl = 30 * 60 * 1000): Promise<void> {
    await this.set(STORES.RECORDS, `record_${recordId}`, record, { ttl });
  }

  /**
   * Get cached record
   */
  async getCachedRecord(recordId: string): Promise<any | null> {
    return await this.get(STORES.RECORDS, `record_${recordId}`);
  }

  /**
   * Cache biomarkers
   */
  async cacheBiomarkers(biomarkers: any[], ttl = 10 * 60 * 1000): Promise<void> {
    await this.set(STORES.BIOMARKERS, 'all_biomarkers', biomarkers, { ttl });
  }

  /**
   * Get cached biomarkers
   */
  async getCachedBiomarkers(): Promise<any[] | null> {
    return await this.get(STORES.BIOMARKERS, 'all_biomarkers');
  }

  /**
   * Cache biomarker trend
   */
  async cacheBiomarkerTrend(biomarkerType: string, data: any[], ttl = 30 * 60 * 1000): Promise<void> {
    await this.set(STORES.BIOMARKERS, `trend_${biomarkerType}`, data, { ttl });
  }

  /**
   * Get cached biomarker trend
   */
  async getCachedBiomarkerTrend(biomarkerType: string): Promise<any[] | null> {
    return await this.get(STORES.BIOMARKERS, `trend_${biomarkerType}`);
  }

  /**
   * Cache anomalies
   */
  async cacheAnomalies(anomalies: any[], ttl = 5 * 60 * 1000): Promise<void> {
    await this.set(STORES.ANOMALIES, 'all_anomalies', anomalies, { ttl });
  }

  /**
   * Get cached anomalies
   */
  async getCachedAnomalies(): Promise<any[] | null> {
    return await this.get(STORES.ANOMALIES, 'all_anomalies');
  }

  /**
   * Cache search results
   */
  async cacheSearchResults(query: string, results: any, ttl = 10 * 60 * 1000): Promise<void> {
    const key = `search_${query.toLowerCase().replace(/\s+/g, '_')}`;
    await this.set(STORES.SEARCH_RESULTS, key, results, { ttl });
  }

  /**
   * Get cached search results
   */
  async getCachedSearchResults(query: string): Promise<any | null> {
    const key = `search_${query.toLowerCase().replace(/\s+/g, '_')}`;
    return await this.get(STORES.SEARCH_RESULTS, key);
  }

  /**
   * Cache user data
   */
  async cacheUserData(key: string, data: any, ttl = 60 * 60 * 1000): Promise<void> {
    await this.set(STORES.USER_DATA, key, data, { ttl });
  }

  /**
   * Get cached user data
   */
  async getCachedUserData(key: string): Promise<any | null> {
    return await this.get(STORES.USER_DATA, key);
  }

  /**
   * Clear user data by key
   */
  async clearUserData(key: string): Promise<void> {
    await this.delete(STORES.USER_DATA, key);
  }

  /**
   * Clear all records cache
   */
  async clearRecords(): Promise<void> {
    await this.clear(STORES.RECORDS);
  }

  /**
   * Clear all anomalies cache
   */
  async clearAnomalies(): Promise<void> {
    await this.clear(STORES.ANOMALIES);
  }

  /**
   * Clear all biomarkers cache
   */
  async clearBiomarkers(): Promise<void> {
    await this.clear(STORES.BIOMARKERS);
  }

  /**
   * Invalidate all caches
   */
  async invalidateAll(): Promise<void> {
    await Promise.all(
      Object.values(STORES).map(storeName => this.clear(storeName))
    );
  }

  /**
   * Invalidate patient-specific caches
   */
  async invalidatePatientCache(): Promise<void> {
    await Promise.all([
      this.clear(STORES.RECORDS),
      this.clear(STORES.BIOMARKERS),
      this.clear(STORES.ANOMALIES),
      this.clear(STORES.SEARCH_RESULTS)
    ]);
  }

  /**
   * Get cache size (approximate)
   */
  async getCacheSize(): Promise<number> {
    try {
      if (!navigator.storage || !navigator.storage.estimate) {
        return 0;
      }

      const estimate = await navigator.storage.estimate();
      return estimate.usage || 0;
    } catch (error) {
      console.error('Failed to get cache size:', error);
      return 0;
    }
  }

  /**
   * Clean up expired entries
   */
  async cleanupExpired(): Promise<void> {
    try {
      await this.ensureInitialized();
      if (!this.db) return;

      for (const storeName of Object.values(STORES)) {
        const transaction = this.db.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.openCursor();

        request.onsuccess = (event) => {
          const cursor = (event.target as IDBRequest).result;

          if (cursor) {
            const entry: CacheEntry<any> = cursor.value;

            if (this.isExpired(entry)) {
              cursor.delete();
            }

            cursor.continue();
          }
        };
      }
    } catch (error) {
      console.error('Cleanup failed:', error);
    }
  }
}

// ============================================================================
// EXPORT SINGLETON
// ============================================================================

export const cacheService = new CacheService();
export default cacheService;

// Auto-cleanup expired entries every 10 minutes
if (typeof window !== 'undefined') {
  setInterval(() => {
    cacheService.cleanupExpired();
  }, 10 * 60 * 1000);
}
