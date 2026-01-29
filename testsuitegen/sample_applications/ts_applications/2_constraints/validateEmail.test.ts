import { validateEmail } from "./src/validator";
import * as fs from "fs";
import * as path from "path";

// Mocking & Setup
jest.mock("../src/emailValidator", () => ({
  isValidEmail: jest.fn().mockImplementation((email: string): boolean => {
    // Simulate email validation logic
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }),
}));

describe("validateEmail", () => {
  it.each(testCases)("intent: %s", async (testCase) => {
    const { intent, args, expectedStatus } = testCase;

    if (expectedStatus >= 400) {
      await expect(async () => {
        return await (validateEmail)(args);
      }).rejects.toThrow();
    } else {
      const result = await (validateEmail)(args);
      expect(result).toBeDefined();
    }
  });
});