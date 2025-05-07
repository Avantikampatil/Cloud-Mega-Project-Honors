const langdetect = require('langdetect');

// Sample text to detect language
const text = "¿Hola, cómo estás?";

// Detect language
const detectedLanguage = langdetect.detectOne(text);

console.log('Detected language:', detectedLanguage);
