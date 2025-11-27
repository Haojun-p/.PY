# -*- coding:utf-8 -*-
import sys
import traceback

print("Testing KEDA module import...")
print("=" * 50)

try:
    print("1. Trying to import websocket...")
    import websocket
    print("   [OK] websocket imported successfully")
except Exception as e:
    print(f"   [FAIL] websocket import failed: {e}")
    traceback.print_exc()

try:
    print("\n2. Trying to import KEDA module...")
    from KEDA import text_to_speech
    print("   [OK] KEDA module imported successfully")
    print(f"   [OK] text_to_speech function: {text_to_speech}")
except ImportError as e:
    print(f"   [FAIL] ImportError: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"   [FAIL] Other error: {type(e).__name__}: {e}")
    traceback.print_exc()

try:
    print("\n3. Testing gim2.py import logic...")
    # Simulate gim2.py import
    try:
        from KEDA import text_to_speech
        TTS_AVAILABLE = True
        print(f"   [OK] TTS_AVAILABLE = {TTS_AVAILABLE}")
    except ImportError as e:
        TTS_AVAILABLE = False
        print(f"   [FAIL] TTS_AVAILABLE = {TTS_AVAILABLE}")
        print(f"   [FAIL] ImportError: {e}")
except Exception as e:
    print(f"   [FAIL] Test failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 50)

