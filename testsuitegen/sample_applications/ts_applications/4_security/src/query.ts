/**
 * Intents: HAPPY_PATH, SQL_INJECTION, XSS_INJECTION
 *
 * Query Builder Module
 * Demonstrates security scenarios (SQL Injection vulnerability).
 */

export class QueryBuilder {
  
  /**
   * ❌ VULNERABLE: Direct string concatenation
   */
  static buildUnsafeQuery(table: string, column: string, value: string): string {
    // LLM should detect this as insecure if analyzing for security
    return `SELECT * FROM ${table} WHERE ${column} = '${value}'`;
  }

  /**
   * ✅ SAFE: Uses Parameterized query placeholder
   */
  static buildSafeQuery(table: string, column: string, value: string): { sql: string; params: string[] } {
    // Validate table/column names against allowlist to prevent object injection
    const allowedTables = ["users", "products"];
    const allowedColumns = ["id", "name", "email", "status"];
    
    if (!allowedTables.includes(table)) {
      throw new Error("Invalid table name");
    }
    if (!allowedColumns.includes(column)) {
      throw new Error("Invalid column name");
    }

    return {
      sql: `SELECT * FROM ${table} WHERE ${column} = ?`,
      params: [value]
    };
  }
  
  /**
   * Sanitize HTML input to prevent XSS
   */
  static sanitizeInput(input: string): string {
    return input
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}
