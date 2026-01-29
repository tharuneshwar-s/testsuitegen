import hashlib


def build_ir(
    source_type: str,
    source_name: str,
    source_payload: str,
    operations: list,
    types: list = None,
    version: str = "1.0",
    metadata: dict = None,
) -> dict:
    ir = {
        "ir_version": version,
        "source": {
            "type": source_type,
            "name": source_name,
            "hash": f"sha256:{_hash(source_payload)}",
        },
        "operations": operations,
        "types": types or [],
    }

    # Add metadata if provided
    if metadata:
        ir["metadata"] = metadata

    return ir


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()
