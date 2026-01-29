import { validateAge } from "./src/validator";

// Mocking & Setup
jest.mock('../src/ageValidator', () => ({
  validateAge: jest.fn().mockImplementation((age: number): Promise<number> => {
    if (age < 18) {
      throw new Error('Age must be at least 18');
    }
    return Promise.resolve(200);
  }),
}));

describe("validateAge", () => {
  it.each(testCases)("intent: %s", async (testCase) => {
    const { intent, args, expectedStatus } = testCase;

    if (expectedStatus >= 400) {
      await expect(async () => {
        return await (validateAge)(args);
      }).rejects.toThrow();
    } else {
      const result = await (validateAge)(args);
      expect(result).toBe(expectedStatus);
    }
  });
});