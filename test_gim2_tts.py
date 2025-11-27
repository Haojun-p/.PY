# -*- coding:utf-8 -*-
# Test TTS import in gim2.py style

print("Testing TTS import (gim2.py style)...")
print("=" * 50)

# 可选导入TTS模块
try:
    from KEDA import text_to_speech
    TTS_AVAILABLE = True
    print("[SUCCESS] TTS module imported successfully!")
    print(f"TTS_AVAILABLE = {TTS_AVAILABLE}")
except ImportError as e:
    TTS_AVAILABLE = False
    print(f"[FAIL] ImportError: {e}")
except Exception as e:
    TTS_AVAILABLE = False
    print(f"[FAIL] Other error ({type(e).__name__}): {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
print(f"Final TTS_AVAILABLE = {TTS_AVAILABLE}")











