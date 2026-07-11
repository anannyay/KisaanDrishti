import type { AnalysisResult } from '../types';

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000';

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('Could not read the selected image.'));
    reader.onload = () => resolve(String(reader.result).split(',', 2)[1]);
    reader.readAsDataURL(blob);
  });
}

export async function analyzeImage(uri: string): Promise<AnalysisResult> {
  const imageResponse = await fetch(uri);
  const base64 = await blobToBase64(await imageResponse.blob());
  const response = await fetch(`${API_URL}/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_base64: base64 }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail ?? 'Image analysis failed.');
  return payload as AnalysisResult;
}
