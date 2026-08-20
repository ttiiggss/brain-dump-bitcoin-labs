"""
Hash Generation Module — Practical Examples

SHA-256 hash generation for documents with error handling and testing.
"""

import hashlib
import os
import tempfile
from typing import Optional

def hash_document(file_path: str, chunk_size: int = 65536) -> str:
    """
    Compute SHA-256 hash of a document file.

    Reads file in binary chunks to handle large files efficiently.

    Args:
        file_path: Path to the document file
        chunk_size: Number of bytes to read per chunk (default: 64KB)

    Returns:
        SHA-256 hash as hexadecimal string (64 characters)

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
    """
    sha256_hash = hashlib.sha256()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {file_path}")

    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(chunk_size), b''):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def hash_bytes(data: bytes) -> str:
    """
    Compute SHA-256 hash of raw bytes (for API uploads).

    Args:
        data: Raw bytes to hash

    Returns:
        SHA-256 hash as hexadecimal string
    """
    return hashlib.sha256(data).hexdigest()


def verify_hash(file_path: str, expected_hash: str) -> dict:
    """
    Verify that a document matches the expected hash.

    Args:
        file_path: Path to the document file
        expected_hash: Expected SHA-256 hash (case-insensitive)

    Returns:
        Dict with 'valid' (bool) and 'actual_hash' (str) keys
    """
    try:
        actual_hash = hash_document(file_path)
        is_valid = actual_hash.lower() == expected_hash.lower()

        return {
            'valid': is_valid,
            'actual_hash': actual_hash,
            'expected_hash': expected_hash,
            'match': is_valid
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'match': False
        }


def hash_from_upload(file_content: bytes, filename: Optional[str] = None) -> dict:
    """
    Hash a document from an upload (binary content).

    Args:
        file_content: Binary content of the file
        filename: Optional filename for logging

    Returns:
        Dict with hash and metadata
    """
    document_hash = hash_bytes(file_content)
    file_size = len(file_content)

    result = {
        'hash': document_hash,
        'algorithm': 'sha256',
        'size_bytes': file_size,
        'filename': filename or 'unknown'
    }

    return result


def demonstrate_hash_collisions():
    """
    Demonstrate that identical files produce identical hashes,
    and that changing a single bit changes the hash completely.
    """
    print("=== SHA-256 Hash Demonstration ===\n")

    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f1:
        f1.write("Hello, World!")
        file1_path = f1.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f2:
        f2.write("Hello, World!")
        file2_path = f2.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f3:
        f3.write("Hello, World")  # Missing exclamation mark
        file3_path = f3.name

    try:
        # Hash identical files
        hash1 = hash_document(file1_path)
        hash2 = hash_document(file2_path)
        hash3 = hash_document(file3_path)

        print(f"File 1 hash: {hash1}")
        print(f"File 2 hash: {hash2}")
        print(f"Identical? {hash1 == hash2}")

        print(f"\nFile 3 hash (changed content): {hash3}")
        print(f"Same as file 1? {hash1 == hash3}")

        # Demonstrate avalanche effect: single bit change → completely different hash
        print("\n=== Avalanche Effect ===")
        print("Changing just one character changes the entire hash:")
        print(f"Length of hash: {len(hash1)} characters")
        print(f"Matching characters (file1 vs file3): {sum(1 for a, b in zip(hash1, hash3) if a == b)}")

    finally:
        # Clean up
        os.unlink(file1_path)
        os.unlink(file2_path)
        os.unlink(file3_path)


if __name__ == '__main__':
    # Run demonstration
    demonstrate_hash_collisions()

    # Test hash verification
    print("\n=== Hash Verification Test ===")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test document")
        test_file = f.name

    try:
        test_hash = hash_document(test_file)
        print(f"Document hash: {test_hash}")

        # Verify correct hash
        result = verify_hash(test_file, test_hash)
        print(f"\nVerify with correct hash:")
        print(f"  Valid: {result['valid']}")
        print(f"  Match: {result['match']}")

        # Verify incorrect hash
        result = verify_hash(test_file, "wrong" * 16)
        print(f"\nVerify with incorrect hash:")
        print(f"  Valid: {result['valid']}")
        print(f"  Match: {result['match']}")

        # Test upload hashing
        print("\n=== Upload Hashing Test ===")
        content = b"This is a test document uploaded via API."
        result = hash_from_upload(content, "test.txt")
        print(f"Hash from upload: {result['hash']}")
        print(f"File size: {result['size_bytes']} bytes")

    finally:
        os.unlink(test_file)