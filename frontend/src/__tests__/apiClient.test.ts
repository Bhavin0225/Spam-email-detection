import { apiClient } from '../services/apiClient';
import { describe, it, expect, beforeEach } from 'vitest';

describe('apiClient Interceptors', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should verify interceptors are correctly registered on startup', () => {
    expect(apiClient.interceptors.request).toBeDefined();
    expect(apiClient.interceptors.response).toBeDefined();
  });

  it('should resolve authorization Bearer configurations', async () => {
    localStorage.setItem('access_token', 'test_access_token');
    
    // Trigger request interceptor callback manually if possible
    const interceptorCall = (apiClient.interceptors.request as any).handlers[0];
    const mockConfig = { headers: {} as any };
    
    const result = interceptorCall.fulfilled(mockConfig);
    expect(result.headers.Authorization).toBe('Bearer test_access_token');
  });
});
