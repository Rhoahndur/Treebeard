import { apiClient } from './client';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export const authApi = {
  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    // Backend expects form data for OAuth2PasswordRequestForm
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store the token
    apiClient.setToken(response.data.access_token);

    return response.data;
  },

  /**
   * Logout (clear token)
   */
  logout() {
    apiClient.clearToken();
  },

  /**
   * Get current user from stored token
   */
  getCurrentUser() {
    const token = apiClient.getToken();
    if (!token) return null;

    try {
      // Decode JWT token to get user info
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: payload.sub,
        is_admin: payload.is_admin || false,
      };
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  },
};
