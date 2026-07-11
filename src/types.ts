export type AnalysisResult = {
  version: string;
  quality: { acceptable: boolean; blur_score: number; brightness: number; warnings: string[] };
  metrics: {
    canopy_coverage_pct: number;
    green_pct: number;
    yellowing_pct: number;
    browning_pct: number;
    visual_health_score: number;
    confidence: number;
  };
  evidence: string[];
  disclaimer: string;
};

export type SavedObservation = {
  id: string;
  plantId: string;
  createdAt: string;
  imageUri: string;
  analysis: AnalysisResult;
  synced: boolean;
};

export type Intervention = {
  id: string;
  plantId: string;
  type: 'irrigation' | 'nutrition' | 'other';
  note: string;
  createdAt: string;
};
