import { apiClient } from './client';
import type { 
  GenerateRecommendationRequest, 
  GenerateRecommendationResponse 
} from '@/types/recommendation';

export const recommendationsApi = {
  generate: async (request: GenerateRecommendationRequest) => {
    const response = await apiClient.post<GenerateRecommendationResponse>(
      '/recommendations/generate',
      request
    );
    return response.data;
  },

  getUserRecommendations: async (userId: string) => {
    const response = await apiClient.get<GenerateRecommendationResponse[]>(
      `/recommendations/${userId}`
    );
    return response.data;
  },
};

export default recommendationsApi;
