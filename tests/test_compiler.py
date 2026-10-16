import os
import sys
import tempfile
import unittest

# Add tools directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))
from prompt_cache_compiler import (
    CACHE_STATIC_START,
    CACHE_STATIC_END,
    extract_static_prefix,
    hash_prefix,
    compile_prompt,
    estimate_tokens,
)

class TestPromptCacheCompiler(unittest.TestCase):
    def setUp(self):
        self.sample_template = f"""{CACHE_STATIC_START}
You are a senior subagent engineer.
Do not modify interfaces.
Do not import new libraries.
{CACHE_STATIC_END}

# [DYNAMIC-TASK]
Old task placeholder
# [/DYNAMIC-TASK]
"""

    def test_extract_static_prefix(self):
        prefix = extract_static_prefix(self.sample_template)
        self.assertTrue(prefix.startswith(CACHE_STATIC_START))
        self.assertTrue(prefix.endswith(CACHE_STATIC_END))
        self.assertIn("Do not import new libraries.", prefix)

    def test_hash_determinism(self):
        prefix1 = extract_static_prefix(self.sample_template)
        # Even with CRLF vs LF variation, hash should be identical
        prefix2 = prefix1.replace("\n", "\r\n")
        h1 = hash_prefix(prefix1)
        h2 = hash_prefix(prefix2)
        self.assertEqual(h1, h2)

    def test_compile_prompt(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as f:
            f.write(self.sample_template)
            t_path = f.name

        try:
            compiled, meta = compile_prompt(
                template_path=t_path,
                file_paths=[],
                task_title="Fix discount",
                task_description="Solve -20% coupon bug on checkout",
                constraints="Keep function signature unchanged",
            )
            self.assertIn("[CACHE-STATIC-PREFIX", compiled)
            self.assertIn("[STABLE-CONTEXT]", compiled)
            self.assertIn("[DYNAMIC-TASK]", compiled)
            self.assertIn("Fix discount", compiled)
            self.assertIn("Keep function signature unchanged", compiled)
            self.assertIsNotNone(meta["prefix_hash"])
        finally:
            if os.path.exists(t_path):
                os.remove(t_path)

if __name__ == "__main__":
    unittest.main()
