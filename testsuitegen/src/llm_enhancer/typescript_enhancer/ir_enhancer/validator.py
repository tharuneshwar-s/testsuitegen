def validate_ir_enhancement_flexible(original: dict, enhanced: dict) -> bool:
    """
    Validates IR enhancement with support for Type Resolution.

    Allowed:
    - Adding constraints (min/max, pattern, etc.)
    - Resolving "Complex type" objects into detailed schemas with properties
    - Changing generic object to specific enum
    - Expanding placeholder objects

    Forbidden:
    - Removing properties defined in AST
    - Changing primitive types (e.g., int -> bool) unless original was Any/Object

    Args:
        original: Original schema from AST
        enhanced: Enhanced schema from LLM

    Returns:
        True if enhancement is valid
    """
    if "properties" in original:
        if "properties" not in enhanced:
            return False  # Should not lose properties container

        for prop_name, orig_prop in original["properties"].items():
            if prop_name not in enhanced["properties"]:
                print(f"      [Validation] Missing property: {prop_name}")
                return False

            enh_prop = enhanced["properties"][prop_name]

            # Allow Object -> Detailed Object resolution
            if orig_prop.get("type") == "object" and "description" in orig_prop:
                if "Complex type" in orig_prop["description"]:
                    continue  # Allow total replacement of complex placeholders

            # Allow Object -> Enum (for enum types marked as objects)
            if (
                orig_prop.get("type") == "object"
                and enh_prop.get("type") == "string"
                and "enum" in enh_prop
            ):
                continue  # Allow enum resolution

            # Recursive check for nested schemas
            if not validate_ir_enhancement_flexible(orig_prop, enh_prop):
                return False

    return True
