import re
import base64
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("shellguard.parser.anti_evasion")

class AntiEvasionEngine:
    """
    De-obfuscation and anti-evasion detection engine.
    Identifies attempts to hide destructive commands via quotes, string concatenation,
    base64 encoding, hex strings, or dynamic variable aliases.
    """

    # Regex patterns for common evasion techniques
    BASE64_EXEC_PATTERN = re.compile(
        r'(?:echo|printf)\s+[\'"]?([A-Za-z0-9+/=]{8,})[\'"]?\s*\|\s*(?:base64\s+-d|openssl\s+base64\s+-d)\s*\|\s*(?:bash|sh|zsh|eval)',
        re.IGNORECASE
    )
    HEX_DECODE_PATTERN = re.compile(r'\\x[0-9a-fA-F]{2}')
    QUOTED_OBFUSCATION_PATTERN = re.compile(r'([a-zA-Z0-9_\-\.]+)([\'"]+[\'"])+([a-zA-Z0-9_\-\.]+)')

    def inspect_and_clean(self, command: str) -> Tuple[str, bool, Optional[str]]:
        """
        Inspects command string for obfuscation patterns.
        Returns: (cleaned_command, is_obfuscated, evasion_type)
        """
        is_obfuscated = False
        evasion_type = None
        cleaned = command.strip()

        # 1. Base64 Payload Execution Detection
        b64_match = self.BASE64_EXEC_PATTERN.search(cleaned)
        if b64_match:
            try:
                encoded_str = b64_match.group(1)
                decoded_bytes = base64.b64decode(encoded_str)
                decoded_cmd = decoded_bytes.decode('utf-8', errors='ignore')
                logger.warning(f"Detected Base64 Obfuscation payload: '{encoded_str}' -> '{decoded_cmd}'")
                return decoded_cmd.strip(), True, "Base64 Execution Payload"
            except Exception as e:
                logger.error(f"Error decoding base64 payload: {e}")
                is_obfuscated = True
                evasion_type = "Malformed Base64 Payload"

        # 2. String Concatenation Quote Removal (e.g. r''m -r""f / -> rm -rf /)
        if "''" in cleaned or '""' in cleaned or self.QUOTED_OBFUSCATION_PATTERN.search(cleaned):
            dequoted = re.sub(r'[\'"]', '', cleaned)
            if dequoted != cleaned:
                logger.warning(f"Detected Quoted Concatenation Obfuscation: '{cleaned}' -> '{dequoted}'")
                cleaned = dequoted
                is_obfuscated = True
                evasion_type = evasion_type or "Quoted Concatenation"

        # 3. Hex String Decoding (e.g. \x72\x6d \x2d\x72\x66 -> rm -rf)
        if self.HEX_DECODE_PATTERN.search(cleaned):
            try:
                def hex_replacer(match):
                    hex_val = match.group(0)[2:]
                    return bytes.fromhex(hex_val).decode('utf-8', errors='ignore')
                
                dehexed = self.HEX_DECODE_PATTERN.sub(hex_replacer, cleaned)
                if dehexed != cleaned:
                    logger.warning(f"Detected Hex String Obfuscation: '{cleaned}' -> '{dehexed}'")
                    cleaned = dehexed
                    is_obfuscated = True
                    evasion_type = evasion_type or "Hex Escape Sequence"
            except Exception as e:
                logger.error(f"Error decoding hex string: {e}")

        # 4. Backslash Escaping Obfuscation (e.g. \r\m -\r\f -> rm -rf)
        if re.search(r'\\[a-zA-Z]', cleaned):
            deslashed = re.sub(r'\\([a-zA-Z])', r'\1', cleaned)
            if deslashed != cleaned:
                logger.warning(f"Detected Backslash Escaping Obfuscation: '{cleaned}' -> '{deslashed}'")
                cleaned = deslashed
                is_obfuscated = True
                evasion_type = evasion_type or "Backslash Character Escaping"

        return cleaned, is_obfuscated, evasion_type

anti_evasion_engine = AntiEvasionEngine()
