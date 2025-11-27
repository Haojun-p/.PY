# -*- coding:utf-8 -*-
# KEDA.py 测试脚本

print("=" * 50)
print("KEDA.py 模块诊断测试")
print("=" * 50)

# 1. 检查依赖库
print("\n1. 检查依赖库...")
dependencies = {
    'websocket': 'websocket-client',
    'pygame': 'pygame',
}

missing = []
for module, package in dependencies.items():
    try:
        __import__(module)
        print(f"  ✓ {module} 已安装")
    except ImportError:
        print(f"  ✗ {module} 未安装 (需要安装: pip install {package})")
        missing.append(package)

# 2. 检查 KEDA 模块导入
print("\n2. 检查 KEDA 模块...")
try:
    from KEDA import text_to_speech
    print("  ✓ KEDA 模块导入成功")
    print("  ✓ text_to_speech 函数可用")
except ImportError as e:
    print(f"  ✗ KEDA 模块导入失败: {e}")
    if missing:
        print(f"\n  请先安装缺失的依赖库:")
        print(f"  pip install {' '.join(missing)}")
    exit(1)
except Exception as e:
    print(f"  ✗ 导入时出错: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 3. 检查配置
print("\n3. 检查配置...")
try:
    from KEDA import APPID, APIKEY, APISECRET, REQURL
    if APPID and APIKEY and APISECRET:
        print(f"  ✓ APPID: {APPID[:8]}...")
        print(f"  ✓ APIKEY: {APIKEY[:8]}...")
        print(f"  ✓ APISECRET: {APISECRET[:8]}...")
        print(f"  ✓ REQURL: {REQURL}")
    else:
        print("  ✗ 配置信息不完整")
except Exception as e:
    print(f"  ✗ 检查配置时出错: {e}")

# 4. 测试 TTS 功能（可选）
print("\n4. 测试 TTS 功能...")
print("  输入 'y' 进行实际测试，或按回车跳过")
choice = input("  是否测试? (y/n): ").strip().lower()

if choice == 'y':
    test_text = "这是一个测试"
    print(f"  正在测试: '{test_text}'...")
    try:
        text_to_speech(test_text)
        print("  ✓ TTS 测试完成")
    except Exception as e:
        print(f"  ✗ TTS 测试失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("  跳过测试")

print("\n" + "=" * 50)
print("诊断完成")
print("=" * 50)

if missing:
    print(f"\n⚠️  请安装缺失的依赖库:")
    print(f"   pip install {' '.join(missing)}")

