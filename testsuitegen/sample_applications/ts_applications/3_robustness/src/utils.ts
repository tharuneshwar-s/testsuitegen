/**
 * Intents: HAPPY_PATH, NULL_NOT_ALLOWED, EMPTY_STRING, NEGATIVE_VALUE
 *
 * String Utilities Module
 * Demonstrates robustness against edge cases and invalid inputs.
 */

export function truncateString(str: string | null | undefined, maxLength: number): string {
  if (str === null || str === undefined) {
    return "";
  }
  if (maxLength < 0) {
    return str; // or throw error? Robustness decision: be safe
  }
  if (str.length <= maxLength) {
    return str;
  }
  return str.slice(0, maxLength) + "...";
}

export function parseTags(input: string): string[] {
  // Edge case: empty string, null (if strict null checks off), special chars
  if (!input || input.trim() === "") {
    return [];
  }
  return input.split(",").map(tag => tag.trim()).filter(tag => tag.length > 0);
}

export function safeJsonParse(jsonString: string): any | null {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    return null; // Return null instead of crashing
  }
}

export function urlify(text: string): string {
    if (!text) return "";
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')           // Replace spaces with -
        .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
        .replace(/\-\-+/g, '-');        // Replace multiple - with single -
}
