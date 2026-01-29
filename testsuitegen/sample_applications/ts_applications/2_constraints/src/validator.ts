/**
 * Intents: HAPPY_PATH, BOUNDARY_MIN_MINUS_ONE, PATTERN_MISMATCH, STRING_TOO_LONG
 *
 * User Validation Module
 * Demonstrates input constraints and validation logic.
 */

export interface UserProfile {
  username: string;
  age: number;
  email: string;
  bio?: string;
}

export function validateAge(age: number): boolean {
  return Number.isInteger(age) && age >= 18 && age <= 120;
}

export function validateUsername(username: string): boolean {
  // Username must be 3-20 chars, alphanumeric or underscore
  const regex = /^[a-zA-Z0-9_]{3,20}$/;
  return regex.test(username);
}

export function validateEmail(email: string): boolean {
  // Basic email regex
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

export function registerUser(user: UserProfile): string {
  if (!validateUsername(user.username)) {
    throw new Error("Invalid username");
  }
  if (!validateAge(user.age)) {
    throw new Error("Invalid age: Must be 18-120");
  }
  if (!validateEmail(user.email)) {
    throw new Error("Invalid email format");
  }
  if (user.bio && user.bio.length > 500) {
    throw new Error("Bio too long");
  }
  
  return `User ${user.username} registered successfully`;
}
