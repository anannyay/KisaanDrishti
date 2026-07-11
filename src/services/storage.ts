import AsyncStorage from '@react-native-async-storage/async-storage';
import type { Intervention, SavedObservation } from '../types';

const OBSERVATIONS = 'croppulse:observations:v1';
const INTERVENTIONS = 'croppulse:interventions:v1';

async function readList<T>(key: string): Promise<T[]> {
  const value = await AsyncStorage.getItem(key);
  if (!value) return [];
  try { return JSON.parse(value) as T[]; } catch { return []; }
}

export const getObservations = () => readList<SavedObservation>(OBSERVATIONS);
export const getInterventions = () => readList<Intervention>(INTERVENTIONS);

export async function saveObservation(observation: SavedObservation): Promise<void> {
  const current = await getObservations();
  await AsyncStorage.setItem(OBSERVATIONS, JSON.stringify([observation, ...current].slice(0, 100)));
}

export async function saveIntervention(intervention: Intervention): Promise<void> {
  const current = await getInterventions();
  await AsyncStorage.setItem(INTERVENTIONS, JSON.stringify([intervention, ...current].slice(0, 100)));
}
