export type Language = 'en' | 'hi' | 'mr';

const messages = {
  en: { scan: 'Scan a plant', camera: 'Open camera', gallery: 'Choose existing photo', save: 'Save to health passport', retry: 'Try again' },
  hi: { scan: 'पौधे को स्कैन करें', camera: 'कैमरा खोलें', gallery: 'मौजूदा फोटो चुनें', save: 'हेल्थ पासपोर्ट में सहेजें', retry: 'फिर से कोशिश करें' },
  mr: { scan: 'झाडाचे स्कॅन करा', camera: 'कॅमेरा उघडा', gallery: 'विद्यमान फोटो निवडा', save: 'हेल्थ पासपोर्टमध्ये जतन करा', retry: 'पुन्हा प्रयत्न करा' },
} as const;

export function t(language: Language, key: keyof typeof messages.en): string { return messages[language][key]; }
