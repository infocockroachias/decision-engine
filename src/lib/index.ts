// Laya Analysis Engine - Singleton export
import { LayaAnalysisEngine } from './laya-engine';

let engineInstance: LayaAnalysisEngine | null = null;

export function getLayaEngine(): LayaAnalysisEngine {
  if (!engineInstance) {
    engineInstance = new LayaAnalysisEngine();
  }
  return engineInstance;
}

export { LayaAnalysisEngine } from './laya-engine';