/**
 * API Service - Centralized API client for MediVault
 *
 * Features:
 * - Axios-based HTTP client
 * - JWT token management
 * - Request/response interceptors
 * - Error handling
 * - TypeScript interfaces
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Types
interface User {
  id: string;
  email: string;
  full_name: string;
  user_type: 'patient' | 'doctor';
  profile_picture_url?: string;
  age?: number;
  gender?: string;
  date_of_birth?: string;
  license_number?: string;
  specialization?: string;
  hospital_affiliation?: string;
}

interface AuthResponse {
  success: boolean;
  user: User;
  token: string;
}

interface MedicalRecord {
  id: string;
  record_id: string;
  patient_id: string;
  file_name: string;
  file_path: string;
  file_type: string;
  document_type?: string;
  document_date?: string;
  clinical_summary?: string;
  overall_severity: number;
  has_critical_alerts: boolean;
  processing_status: string;
  created_at: string;
}

interface Biomarker {
  id: string;
  biomarker_type: string;
  value: number;
  unit: string;
  normal_min?: number;
  normal_max?: number;
  is_abnormal: boolean;
  measurement_date: string;
}

interface Anomaly {
  id: string;
  anomaly_type: string;
  severity: number;
  is_critical: boolean;
  title: string;
  message: string;
  recommendation?: string;
  acknowledged: boolean;
  detection_date: string;
}

// ============================================================================
// API CLIENT CLASS
// ============================================================================

class APIService {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    // Create axios instance
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.setAuthToken(null);
          window.dispatchEvent(new CustomEvent('auth:logout'));
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  // ============================================================================
  // AUTH ENDPOINTS
  // ============================================================================

  auth = {
    /**
     * Login with email and password
     */
    login: async (email: string, password: string): Promise<AuthResponse> => {
      const response = await this.client.post('/auth/login', { email, password });
      return response.data;
    },

    /**
     * Login with Google OAuth
     */
    loginWithGoogle: async (googleData: any): Promise<AuthResponse> => {
      const response = await this.client.post('/auth/google-oauth', googleData);
      return response.data;
    },

    /**
     * Sign up as patient
     */
    signupPatient: async (data: any): Promise<AuthResponse> => {
      const response = await this.client.post('/auth/signup/patient', data);
      return response.data;
    },

    /**
     * Sign up as doctor
     */
    signupDoctor: async (data: any): Promise<AuthResponse> => {
      const response = await this.client.post('/auth/signup/doctor', data);
      return response.data;
    },

    /**
     * Get current session
     */
    getSession: async (): Promise<{ success: boolean; user: User }> => {
      const response = await this.client.get('/auth/session');
      return response.data;
    },

    /**
     * Refresh token
     */
    refreshToken: async (): Promise<{ success: boolean; token: string }> => {
      const response = await this.client.post('/auth/refresh');
      return response.data;
    },

    /**
     * Logout
     */
    logout: async (): Promise<{ success: boolean }> => {
      const response = await this.client.post('/auth/logout');
      return response.data;
    },

    /**
     * Update profile
     */
    updateProfile: async (updates: any): Promise<{ success: boolean; user: User }> => {
      const response = await this.client.put('/auth/profile', updates);
      return response.data;
    },

    /**
     * Change password
     */
    changePassword: async (currentPassword: string, newPassword: string): Promise<{ success: boolean }> => {
      const response = await this.client.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      return response.data;
    }
  };

  // ============================================================================
  // RECORDS ENDPOINTS
  // ============================================================================

  records = {
    /**
     * Upload medical record
     */
    upload: async (file: File, metadata?: any): Promise<any> => {
      const formData = new FormData();
      formData.append('file', file);

      if (metadata) {
        Object.keys(metadata).forEach(key => {
          formData.append(key, metadata[key]);
        });
      }

      const response = await this.client.post('/records/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    },

    /**
     * Get all records with pagination
     */
    getAll: async (params?: { limit?: number; offset?: number; order_by?: string }): Promise<{
      success: boolean;
      records: MedicalRecord[];
      total: number;
    }> => {
      const response = await this.client.get('/records/all', { params });
      return response.data;
    },

    /**
     * Get specific record by ID
     */
    getById: async (recordId: string): Promise<{
      success: boolean;
      record: MedicalRecord;
      biomarkers: Biomarker[];
      medications: any[];
      diseases: any[];
      anomalies: Anomaly[];
    }> => {
      const response = await this.client.get(`/records/${recordId}`);
      return response.data;
    },

    /**
     * Download record file
     */
    download: async (recordId: string): Promise<Blob> => {
      const response = await this.client.get(`/records/download/${recordId}`, {
        responseType: 'blob'
      });
      return response.data;
    },

    /**
     * Search records
     */
    search: async (params: {
      query: string;
      search_type?: 'semantic' | 'keyword' | 'hybrid';
      generate_summary?: boolean;
      n_results?: number;
    }): Promise<{
      success: boolean;
      total_results: number;
      results: any[];
      ai_summary?: string;
      tokens_used: number;
    }> => {
      const response = await this.client.post('/records/search', params);
      return response.data;
    },

    /**
     * Ask question about medical history
     */
    ask: async (question: string): Promise<{
      success: boolean;
      answer: string;
      question: string;
      tokens_used: number;
    }> => {
      const response = await this.client.post('/records/ask', { question });
      return response.data;
    },

    /**
     * Get anomalies
     */
    getAnomalies: async (params?: {
      critical_only?: boolean;
      unacknowledged_only?: boolean;
    }): Promise<{
      success: boolean;
      anomalies: Anomaly[];
    }> => {
      const response = await this.client.get('/records/anomalies/all', { params });
      return response.data;
    },

    /**
     * Get biomarkers
     */
    getBiomarkers: async (params?: {
      type?: string;
      limit?: number;
    }): Promise<{
      success: boolean;
      biomarkers: Biomarker[];
    }> => {
      const response = await this.client.get('/records/biomarkers', { params });
      return response.data;
    },

    /**
     * Get biomarker trend
     */
    getBiomarkerTrend: async (biomarkerType: string, days?: number): Promise<{
      success: boolean;
      biomarker_type: string;
      data: Biomarker[];
    }> => {
      const response = await this.client.get(`/records/biomarkers/trend/${biomarkerType}`, {
        params: { days }
      });
      return response.data;
    },

    /**
     * Get patient summary
     */
    getSummary: async (): Promise<{
      success: boolean;
      summary: {
        total_records: number;
        critical_records: number;
        unacknowledged_anomalies: number;
        last_upload: string;
      };
    }> => {
      const response = await this.client.get('/records/summary');
      return response.data;
    }
  };

  // ============================================================================
  // DOCTOR ENDPOINTS
  // ============================================================================

  doctor = {
    /**
     * Get accessible patients
     */
    getPatients: async (): Promise<{
      success: boolean;
      patients: any[];
    }> => {
      const response = await this.client.get('/doctor/patients');
      return response.data;
    },

    /**
     * Get patient details
     */
    getPatientDetails: async (patientId: string): Promise<{
      success: boolean;
      patient: any;
      recent_records: MedicalRecord[];
      critical_anomalies: Anomaly[];
      summary: any;
    }> => {
      const response = await this.client.get(`/doctor/patient/${patientId}`);
      return response.data;
    },

    /**
     * Get patient records
     */
    getPatientRecords: async (patientId: string, params?: {
      limit?: number;
      offset?: number;
    }): Promise<{
      success: boolean;
      records: MedicalRecord[];
    }> => {
      const response = await this.client.get(`/doctor/patient/${patientId}/records`, { params });
      return response.data;
    },

    /**
     * Get patient biomarker trend
     */
    getPatientBiomarkerTrend: async (patientId: string, biomarkerType: string, days?: number): Promise<{
      success: boolean;
      biomarker_type: string;
      data: Biomarker[];
    }> => {
      const response = await this.client.get(`/doctor/patient/${patientId}/biomarkers/${biomarkerType}`, {
        params: { days }
      });
      return response.data;
    },

    /**
     * Get patient notes
     */
    getPatientNotes: async (patientId: string): Promise<{
      success: boolean;
      notes: any[];
    }> => {
      const response = await this.client.get(`/doctor/patient/${patientId}/notes`);
      return response.data;
    },

    /**
     * Add patient note
     */
    addPatientNote: async (patientId: string, note: {
      note_text: string;
      note_type?: string;
      visit_date?: string;
      is_private?: boolean;
      record_id?: string;
    }): Promise<{
      success: boolean;
      note: any;
    }> => {
      const response = await this.client.post(`/doctor/patient/${patientId}/notes`, note);
      return response.data;
    },

    /**
     * Acknowledge anomaly
     */
    acknowledgeAnomaly: async (anomalyId: string): Promise<{
      success: boolean;
      anomaly: Anomaly;
    }> => {
      const response = await this.client.post(`/doctor/anomaly/${anomalyId}/acknowledge`);
      return response.data;
    },

    /**
     * Get patient anomalies
     */
    getPatientAnomalies: async (patientId: string, params?: {
      critical_only?: boolean;
      unacknowledged_only?: boolean;
    }): Promise<{
      success: boolean;
      anomalies: Anomaly[];
    }> => {
      const response = await this.client.get(`/doctor/patient/${patientId}/anomalies`, { params });
      return response.data;
    },

    /**
     * Request patient access
     */
    requestAccess: async (patientEmail: string, message?: string): Promise<{
      success: boolean;
      message: string;
      patient_id: string;
    }> => {
      const response = await this.client.post('/doctor/request-access', {
        patient_email: patientEmail,
        message
      });
      return response.data;
    },

    /**
     * Search patients
     */
    searchPatients: async (query: string): Promise<{
      success: boolean;
      patients: any[];
    }> => {
      const response = await this.client.post('/doctor/search-patients', { query });
      return response.data;
    },

    /**
     * Get dashboard statistics
     */
    getDashboard: async (): Promise<{
      success: boolean;
      stats: {
        total_patients: number;
        critical_alerts: number;
        patients_with_alerts: any[];
      };
    }> => {
      const response = await this.client.get('/doctor/dashboard');
      return response.data;
    }
  };
}

// ============================================================================
// EXPORT SINGLETON
// ============================================================================

export const apiService = new APIService();
export default apiService;
