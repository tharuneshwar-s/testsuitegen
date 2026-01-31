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
  // ===== BUG VERSION (uncomment to show bug) =====
  return Number.isInteger(age) && age >= 18 && age <= 120;  // BUG: Returns false instead of throwing
  // ===============================================
  
  // ===== FIXED VERSION =====
  if (!Number.isInteger(age)) {
    throw new Error("Age must be an integer");
  }
  if (age < 18) {
    throw new Error("Age must be at least 18");
  }
  if (age > 120) {
    throw new Error("Age cannot exceed 120");
  }
  return true;
  // =========================
}

export function validateUsername(username: string): boolean {
  // ===== BUG VERSION (uncomment to show bug) =====
  // const regex = /^[a-zA-Z0-9_]{3,20}$/;
  // return regex.test(username);  // BUG: Returns false instead of throwing
  // ===============================================
  
  // ===== FIXED VERSION =====
  if (typeof username !== 'string') {
    throw new Error("Username must be a string");
  }
  const regex = /^[a-zA-Z0-9_]{3,20}$/;
  if (!regex.test(username)) {
    throw new Error("Username must be 3-20 alphanumeric characters or underscores");
  }
  return true;
  // =========================
}

export function validateEmail(email: string): boolean {
  // ===== BUG VERSION (uncomment to show bug) =====
  // const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  // return regex.test(email);  // BUG: Returns false instead of throwing
  // ===============================================
  
  // ===== FIXED VERSION =====
  if (typeof email !== 'string') {
    throw new Error("Email must be a string");
  }
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!regex.test(email)) {
    throw new Error("Invalid email format");
  }
  return true;
  // =========================
}

export function registerUser(user: UserProfile): string {
  // ===== BUG VERSION (uncomment to show bug) =====
  // Missing required field validation and type checks
  // ===============================================
  
  // ===== FIXED VERSION =====
  // Check required fields
  if (!user.username) {
    throw new Error("Username is required");
  }
  if (user.age === undefined || user.age === null) {
    throw new Error("Age is required");
  }
  if (!user.email) {
    throw new Error("Email is required");
  }
  
  // Type validation
  if (user.bio !== undefined && typeof user.bio !== 'string') {
    throw new Error("Bio must be a string");
  }
  
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
  // =========================
}
