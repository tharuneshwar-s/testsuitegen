/**
 * Intents: HAPPY_PATH, ZERO_VALUE, EMPTY_COLLECTION
 *
 * Basic Calculator Module
 * Demonstrates functional logic and simple error handling.
 */

export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

export function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
}

export function calculateStats(numbers: number[]): { sum: number; average: number } {
  if (numbers.length === 0) {
    return { sum: 0, average: 0 };
  }
  const sum = numbers.reduce((acc, curr) => acc + curr, 0);
  return {
    sum,
    average: sum / numbers.length,
  };
}
