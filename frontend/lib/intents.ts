// Intent definitions matching testsuitegen core module

// Intent definitions matching testsuitegen core module

export const OPENAPI_INTENTS = [
  // General
  { id: "HAPPY_PATH", label: "Happy Path", category: "general", description: "Valid request with expected response", example: '{ "status": 200, "body": { "id": 123, "name": "Test Item" } }' },

  // Field Validation
  { id: "REQUIRED_FIELD_MISSING", label: "Required Field Missing", category: "field", description: "Test missing required fields", example: '{ "error": "Missing required field: username" }' },
  { id: "NULL_NOT_ALLOWED", label: "Null Not Allowed", category: "field", description: "Test null values on non-nullable fields", example: '{ "age": null } // Error: age cannot be null' },
  { id: "TYPE_VIOLATION", label: "Type Violation", category: "field", description: "Test incorrect data types", example: '{ "age": "twenty" } // Error: expected integer' },
  { id: "UNION_NO_MATCH", label: "Union No Match", category: "field", description: "Value doesn't match any schema in union", example: '{ "type": "unknown_variant" }' },
  
  // Path & Header
  { id: "RESOURCE_NOT_FOUND", label: "Resource Not Found", category: "path", description: "Valid format but non-existent resource", example: 'GET /users/999999 -> 404 Not Found' },
  { id: "FORMAT_INVALID_PATH_PARAM", label: "Invalid Path Param", category: "path", description: "Invalid path parameter format", example: 'GET /users/abc (expected uuid)' },
  { id: "HEADER_MISSING", label: "Header Missing", category: "field", description: "Missing required header", example: 'Missing "X-API-Key" header' },
  { id: "HEADER_ENUM_MISMATCH", label: "Header Enum Mismatch", category: "string", description: "Header value not in allowed list", example: 'X-Environment: "STAGING" (allowed: PROD, DEV)' },
  
  // String Constraints
  { id: "ENUM_MISMATCH", label: "Enum Mismatch", category: "string", description: "Value not in allowed enum list", example: '{ "color": "purple" } // Allowed: red, green, blue' },
  { id: "STRING_TOO_SHORT", label: "String Too Short", category: "string", description: "Below minimum length", example: '{ "password": "123" } // Min length: 8' },
  { id: "STRING_TOO_LONG", label: "String Too Long", category: "string", description: "Exceeds maximum length", example: '{ "username": "a".repeat(100) } // Max length: 50' },
  { id: "PATTERN_MISMATCH", label: "Pattern Mismatch", category: "string", description: "Doesn't match regex pattern", example: '{ "phone": "123-abc" } // Expected: \\d{3}-\\d{3}-\\d{4}' },
  { id: "FORMAT_INVALID", label: "Format Invalid", category: "string", description: "Doesn't match format (email, uuid, etc)", example: '{ "email": "not-an-email" }' },
  
  // Numeric Constraints
  { id: "NUMBER_TOO_SMALL", label: "Number Too Small", category: "numeric", description: "Below minimum value", example: '{ "age": 17 } // Min: 18' },
  { id: "NUMBER_TOO_LARGE", label: "Number Too Large", category: "numeric", description: "Exceeds maximum value", example: '{ "rating": 6 } // Max: 5' },
  { id: "NOT_MULTIPLE_OF", label: "Not Multiple Of", category: "numeric", description: "Value is not a multiple of step", example: '{ "time": 15 } // Step: 10' },
  
  // Boundaries
  { id: "BOUNDARY_MIN_MINUS_ONE", label: "Boundary Min-1", category: "boundary", description: "One below minimum boundary", example: '{ "quantity": 0 } // Min: 1' },
  { id: "BOUNDARY_MAX_PLUS_ONE", label: "Boundary Max+1", category: "boundary", description: "One above maximum boundary", example: '{ "quantity": 101 } // Max: 100' },
  { id: "BOUNDARY_MIN_LENGTH_MINUS_ONE", label: "Length Min-1", category: "boundary", description: "Length one below minimum", example: '"pass" (len:4) // Min: 5' },
  { id: "BOUNDARY_MAX_LENGTH_PLUS_ONE", label: "Length Max+1", category: "boundary", description: "Length one above maximum", example: '"title..." (len:256) // Max: 255' },
  { id: "BOUNDARY_MIN_ITEMS_MINUS_ONE", label: "Items Min-1", category: "boundary", description: "Count on below minimum", example: '[] (options: 0) // MinItems: 1' },
  { id: "BOUNDARY_MAX_ITEMS_PLUS_ONE", label: "Items Max+1", category: "boundary", description: "Count one above maximum", example: '[1, 2, 3, 4] // MaxItems: 3' },

  // Array Constraints
  { id: "ARRAY_TOO_SHORT", label: "Array Too Short", category: "array", description: "Below minimum items", example: '[] // Expected at least 1 item' },
  { id: "ARRAY_TOO_LONG", label: "Array Too Long", category: "array", description: "Exceeds maximum items", example: '[1..100] // Expected at most 50 items' },
  { id: "ARRAY_NOT_UNIQUE", label: "Items Not Unique", category: "array", description: "Duplicate items in unique array", example: '[1, 2, 2, 3] // UniqueItems: true' },
  { id: "ARRAY_ITEM_TYPE_VIOLATION", label: "Item Type Error", category: "array", description: "Incorrect type for array items", example: '["a", 1, "c"] // Expected all strings' },
  { id: "ARRAY_SHAPE_VIOLATION", label: "Array Shape Error", category: "array", description: "Incorrect array structure", example: '{ "tags": "not-an-array" }' },
  { id: "NESTED_ARRAY_ITEM_TYPE_VIOLATION", label: "Nested Item Error", category: "array", description: "Type error in nested array", example: '[[1], ["a"]] // Expected list of list of ints' },
  { id: "ARRAY_ITEM_OBJECT_VALUE_TYPE_VIOLATION", label: "Item Object Error", category: "array", description: "Type error in object within array", example: '[{ "id": "wrong" }] // Expected id as int' },

  // Object Structure
  { id: "ADDITIONAL_PROPERTY_NOT_ALLOWED", label: "Extra Property", category: "structural", description: "Property not allowed by schema", example: '{ "valid": 1, "extra": "forbidden" }' },
  { id: "OBJECT_VALUE_TYPE_VIOLATION", label: "Object Value Error", category: "structural", description: "Incorrect type for object value", example: '{ "settings": 123 } // Expected object' },
  { id: "OBJECT_TOO_FEW_PROPERTIES", label: "Too Few Props", category: "structural", description: "Below minProperties count", example: '{ "x": 1 } // MinProps: 2' },
  { id: "OBJECT_TOO_MANY_PROPERTIES", label: "Too Many Props", category: "structural", description: "Exceeds maxProperties count", example: '{ "a":1, "b":2, "c":3 } // MaxProps: 2' },
  { id: "DISCRIMINATOR_VIOLATION", label: "Discriminator Error", category: "structural", description: "Invalid polymorphism discriminator", example: '{ "type": "dog", "flight_speed": 10 } // Dog cannot fly' },
  { id: "DEPENDENCY_VIOLATION", label: "Dependency Error", category: "structural", description: "Missing dependent field", example: '{ "credit_card": "...", "cvv": null }' },
  { id: "CONDITIONAL_REQUIRED_MISSING", label: "Conditional Missing", category: "structural", description: "Missing conditionally required field", example: 'If "country" is "US", "state" is required' },

  // Edge Cases
  { id: "EMPTY_STRING", label: "Empty String", category: "edge", description: "Empty string test", example: '{ "name": "" }' },
  { id: "WHITESPACE_ONLY", label: "Whitespace Only", category: "edge", description: "Only whitespace characters", example: '{ "name": "   " }' },
  
  // Security
  { id: "SQL_INJECTION", label: "SQL Injection", category: "security", description: "SQL injection attempt", example: "' OR '1'='1" },
  { id: "XSS_INJECTION", label: "XSS Injection", category: "security", description: "Cross-site scripting attempt", example: "<script>alert(1)</script>" },
  { id: "COMMAND_INJECTION", label: "Command Injection", category: "security", description: "OS Command injection attempt", example: "; rm -rf /" },
  { id: "HEADER_INJECTION", label: "Header Injection", category: "security", description: "CRLF / Header injection attempt", example: "Check%0d%0aCookie: malicious=value" },
];

export const PYTHON_INTENTS = [
  // General & Structure
  { id: "HAPPY_PATH", label: "Happy Path", category: "general", description: "Valid arguments with expected return", example: 'add_user(name="Alice", age=30)' },
  { id: "REQUIRED_ARG_MISSING", label: "Required Arg Missing", category: "structural", description: "Missing required arguments", example: 'add_user(name="Alice") // Missing age' },
  { id: "UNEXPECTED_ARGUMENT", label: "Unexpected Argument", category: "structural", description: "Extra unexpected arguments", example: 'add_user(unknown="value")' },
  { id: "TOO_MANY_POS_ARGS", label: "Too Many Args", category: "structural", description: "Too many positional arguments", example: 'add_user("Alice", 30, "Extra")' },
  { id: "OBJECT_MISSING_FIELD", label: "Object Missing Field", category: "structural", description: "Missing field in object/dict", example: 'process_data({"id": 1}) // Missing "value"' },
  { id: "OBJECT_EXTRA_FIELD", label: "Object Extra Field", category: "structural", description: "Extra field in object/dict", example: 'process_data({"id": 1, "extra": 2})' },

  // Type System
  { id: "TYPE_VIOLATION", label: "Type Violation", category: "type", description: "Incorrect argument types", example: 'add_user(age="thirty")' },
  { id: "NULL_NOT_ALLOWED", label: "Null Not Allowed", category: "type", description: "Null where not allowed", example: 'add_user(name=None)' },
  { id: "ARRAY_ITEM_TYPE_VIOLATION", label: "List Item Type Error", category: "type", description: "Incorrect type in list items", example: 'process_ids([1, "2", 3])' },
  { id: "DICT_KEY_TYPE_VIOLATION", label: "Dict Key Type Error", category: "type", description: "Incorrect type for dict keys", example: 'config = { 1: "value" } // Expected string keys' },
  { id: "DICT_VALUE_TYPE_VIOLATION", label: "Dict Value Type Error", category: "type", description: "Incorrect type for dict values", example: 'config = { "timeout": "10s" } // Expected int' },
  { id: "UNION_NO_MATCH", label: "Union No Match", category: "type", description: "Value doesn't match Union types", example: 'process(val=SystemObject()) // Expected int|str' },

  // Constraints
  { id: "BOUNDARY_MIN_MINUS_ONE", label: "Boundary Min-1", category: "boundary", description: "One below minimum", example: 'set_score(-1) // Min: 0' },
  { id: "BOUNDARY_MAX_PLUS_ONE", label: "Boundary Max+1", category: "boundary", description: "One above maximum", example: 'set_score(101) // Max: 100' },
  { id: "STRING_TOO_SHORT", label: "String Too Short", category: "string", description: "Below minimum length", example: 'set_password("123")' },
  { id: "STRING_TOO_LONG", label: "String Too Long", category: "string", description: "Exceeds maximum length", example: 'set_title("A" * 1000)' },
  { id: "PATTERN_MISMATCH", label: "Pattern Mismatch", category: "string", description: "Doesn't match regex", example: 'set_sku("abc") // Expected ^[A-Z]{3}-\\d{3}$' },
  { id: "ENUM_MISMATCH", label: "Enum Mismatch", category: "string", description: "Not in enum list", example: 'set_color("purple") // Allowed: red, green' },
  { id: "NOT_MULTIPLE_OF", label: "Not Multiple Of", category: "numeric", description: "Not a multiple of step", example: 'set_time(15) // Step: 10' },

  // Edge Cases
  { id: "EMPTY_STRING", label: "Empty String", category: "edge", description: "Empty string", example: 'set_name("")' },
  { id: "WHITESPACE_ONLY", label: "Whitespace Only", category: "edge", description: "Only whitespace", example: 'set_name("   ")' },
  { id: "ZERO_VALUE", label: "Zero Value", category: "edge", description: "Zero numeric value", example: 'pay_amount(0)' },
  { id: "NEGATIVE_VALUE", label: "Negative Value", category: "edge", description: "Negative numbers", example: 'pay_amount(-100)' },
  { id: "EMPTY_COLLECTION", label: "Empty Collection", category: "edge", description: "Empty array/list", example: 'process_items([])' },

  // Security
  { id: "SQL_INJECTION", label: "SQL Injection", category: "security", description: "SQL injection attempt", example: "run_query(\"'; DROP TABLE users --\")" },
  { id: "XSS_INJECTION", label: "XSS Injection", category: "security", description: "XSS attempt", example: 'render_comment("<script>alert(1)</script>")' },
  { id: "COMMAND_INJECTION", label: "Command Injection", category: "security", description: "Command injection attempt", example: 'system_call("; rm -rf /")' },
  { id: "PATH_TRAVERSAL", label: "Path Traversal", category: "security", description: "Path traversal attempt", example: 'read_file("../../etc/passwd")' },

  // Runtime
  { id: "MUTABLE_DEFAULT_TRAP", label: "Mutable Default", category: "structural", description: "Mutable default argument trap", example: 'def foo(l=[]): l.append(1)' },
];

export const TYPESCRIPT_INTENTS = [
  // General
  { id: "HAPPY_PATH", label: "Happy Path", category: "general", description: "Valid arguments with expected return", example: 'greetUser("Alice")' },

  // Structure
  { id: "REQUIRED_ARG_MISSING", label: "Required Arg Missing", category: "structural", description: "Missing required parameter", example: 'createUser() // Missing name param' },
  { id: "UNEXPECTED_ARGUMENT", label: "Unexpected Argument", category: "structural", description: "Extra unexpected arguments", example: 'greet({name: "A", extra: true})' },
  { id: "OBJECT_MISSING_FIELD", label: "Object Missing Field", category: "structural", description: "Missing field in object", example: 'createUser({name: "A"}) // Missing email' },
  { id: "OBJECT_EXTRA_FIELD", label: "Object Extra Field", category: "structural", description: "Extra field in strict object", example: 'createUser({name: "A", extra: true})' },

  // Type System
  { id: "TYPE_VIOLATION", label: "Type Violation", category: "type", description: "Incorrect argument types", example: 'addUser(123) // Expected string' },
  { id: "NULL_NOT_ALLOWED", label: "Null Not Allowed", category: "type", description: "Null where not allowed", example: 'greet(null)' },
  { id: "ARRAY_ITEM_TYPE_VIOLATION", label: "Array Item Type Error", category: "type", description: "Incorrect type in array items", example: 'processIds([1, "2", 3])' },
  { id: "UNION_NO_MATCH", label: "Union No Match", category: "type", description: "Value doesn't match union type", example: 'process(InvalidType)' },
  { id: "GENERIC_TYPE_VIOLATION", label: "Generic Type Error", category: "type", description: "Value violates generic constraint", example: 'Container<number>(["string"])' },
  { id: "INTERFACE_MISSING_PROPERTY", label: "Interface Property Missing", category: "type", description: "Missing required interface property", example: 'const user: User = {name: "A"}' },

  // Constraints
  { id: "BOUNDARY_MIN_MINUS_ONE", label: "Boundary Min-1", category: "boundary", description: "One below minimum", example: 'setScore(-1) // Min: 0' },
  { id: "BOUNDARY_MAX_PLUS_ONE", label: "Boundary Max+1", category: "boundary", description: "One above maximum", example: 'setScore(101) // Max: 100' },
  { id: "STRING_TOO_SHORT", label: "String Too Short", category: "string", description: "Below minimum length", example: 'setPassword("12")' },
  { id: "STRING_TOO_LONG", label: "String Too Long", category: "string", description: "Exceeds maximum length", example: 'setTitle("A".repeat(1000))' },
  { id: "PATTERN_MISMATCH", label: "Pattern Mismatch", category: "string", description: "Doesn't match regex pattern", example: 'setSku("abc")' },
  { id: "ENUM_MISMATCH", label: "Enum Mismatch", category: "string", description: "Not in enum list", example: 'setColor("purple" as Color)' },

  // Edge Cases
  { id: "EMPTY_STRING", label: "Empty String", category: "edge", description: "Empty string", example: 'setName("")' },
  { id: "WHITESPACE_ONLY", label: "Whitespace Only", category: "edge", description: "Only whitespace", example: 'setName("   ")' },
  { id: "ZERO_VALUE", label: "Zero Value", category: "edge", description: "Zero numeric value", example: 'pay(0)' },
  { id: "NEGATIVE_VALUE", label: "Negative Value", category: "edge", description: "Negative numbers", example: 'pay(-100)' },
  { id: "EMPTY_COLLECTION", label: "Empty Collection", category: "edge", description: "Empty array", example: 'processItems([])' },

  // Security
  { id: "SQL_INJECTION", label: "SQL Injection", category: "security", description: "SQL injection attempt", example: `query("'; DROP TABLE users --")` },
  { id: "XSS_INJECTION", label: "XSS Injection", category: "security", description: "XSS attempt", example: `render("<script>alert(1)</script>")` },
  { id: "PATH_TRAVERSAL", label: "Path Traversal", category: "security", description: "Path traversal attempt", example: `readFile("../../etc/passwd")` },
  { id: "COMMAND_INJECTION", label: "Command Injection", category: "security", description: "Command injection attempt", example: `exec("; rm -rf /")` },
];

export const INTENT_CATEGORIES = {
  general: { label: "General", color: "emerald" },
  field: { label: "Field Validation", color: "blue" },
  path: { label: "Path Parameters", color: "purple" },
  string: { label: "String Constraints", color: "cyan" },
  numeric: { label: "Numeric Constraints", color: "amber" },
  boundary: { label: "Boundary Tests", color: "orange" },
  edge: { label: "Edge Cases", color: "slate" },
  security: { label: "Security", color: "red" },
  type: { label: "Type System", color: "indigo" },
  structural: { label: "Structure", color: "violet" },
  array: { label: "Array Constraints", color: "teal" },
};

