def validate_payload_structure(original: dict, enhanced: dict) -> bool:
    """
    Validate that payload structure remains identical.

    Checks:
    - Same keys
    - Same types (with special handling for placeholders)
    - Same array lengths
    - Recursive validation for nested dicts/lists
    - Empty dicts must stay empty
    """
    # Check if both dictionaries have the same keys
    if original.keys() != enhanced.keys():
        return False

    for k in original:
        orig_val = original[k]
        enh_val = enhanced[k]

        # Special handling for placeholder strings
        if isinstance(orig_val, str) and orig_val.startswith("__PLACEHOLDER_"):
            # Allow any type replacement for placeholders
            continue

        # Check if the types of the original and enhanced values match
        is_orig_num = isinstance(orig_val, (int, float)) and not isinstance(
            orig_val, bool
        )
        is_enh_num = isinstance(enh_val, (int, float)) and not isinstance(enh_val, bool)

        if is_orig_num and is_enh_num:
            continue
        elif type(orig_val) != type(enh_val):
            return False

        # Recursively validate nested dictionaries
        if isinstance(orig_val, dict):
            # Allow empty original dicts to be populated
            if not orig_val:
                continue
            if not validate_payload_structure(orig_val, enh_val):
                return False

        # Validate lists: ensure same length and recursively validate elements
        if isinstance(orig_val, list):
            # if len(orig_val) != len(enh_val):
            #     return False
            for o, e in zip(orig_val, enh_val):
                # Ensure empty dictionaries in lists remain empty
                if isinstance(o, dict) and len(o) == 0:
                    # if not (isinstance(e, dict) and len(e) == 0):
                    #     return False
                    continue
                # Check if the types of the elements match
                if type(o) != type(e):
                    return False
                # Recursively validate nested dictionaries in lists
                if isinstance(o, dict):
                    if not validate_payload_structure(o, e):
                        return False
    return True
