using System.Threading;
using UnityEngine;
using Cysharp.Threading.Tasks;
using ChatdollKit.Model;

#if USE_VRM10
using UniVRM10;
#endif

/// <summary>
/// VRM10 专用的眨眼组件，通过 VRM Expression API 控制眨眼
/// </summary>
public class VRM10Blink : MonoBehaviour, IBlink
{
    [Header("Blink Settings")]
    [SerializeField] private float minBlinkInterval = 3.0f;
    [SerializeField] private float maxBlinkInterval = 5.0f;
    [SerializeField] private float blinkDuration = 0.1f;
    [SerializeField] private float blinkTransition = 0.05f;

#if USE_VRM10
    private Vrm10Instance vrm10Instance;
#endif
    
    private bool isBlinkEnabled = false;
    private bool blinkLoopStarted = false;
    private CancellationTokenSource blinkCts;
    private float currentBlinkWeight = 0f;
    private float targetBlinkWeight = 0f;

    public bool IsBlinkEnabled => isBlinkEnabled;

    private void Update()
    {
        // 平滑过渡眨眼权重
        if (Mathf.Abs(currentBlinkWeight - targetBlinkWeight) > 0.01f)
        {
            currentBlinkWeight = Mathf.Lerp(currentBlinkWeight, targetBlinkWeight, Time.deltaTime / blinkTransition);
            ApplyBlinkWeight(currentBlinkWeight);
        }
        else if (currentBlinkWeight != targetBlinkWeight)
        {
            currentBlinkWeight = targetBlinkWeight;
            ApplyBlinkWeight(currentBlinkWeight);
        }
    }

    private void OnDestroy()
    {
        blinkCts?.Cancel();
    }

    public void Setup(GameObject avatarObject)
    {
#if USE_VRM10
        // 查找 VRM10 Instance
        vrm10Instance = avatarObject.GetComponent<Vrm10Instance>();
        if (vrm10Instance == null)
        {
            vrm10Instance = avatarObject.GetComponentInChildren<Vrm10Instance>();
        }

        if (vrm10Instance == null)
        {
            Debug.LogWarning("[VRM10Blink] Vrm10Instance not found on avatar");
        }
        else
        {
            Debug.Log("[VRM10Blink] Setup completed");
        }
#else
        Debug.LogWarning("[VRM10Blink] USE_VRM10 is not defined. Please add USE_VRM10 to Scripting Define Symbols.");
#endif

        blinkCts = new CancellationTokenSource();
    }

    public string GetBlinkShapeName()
    {
        return "Blink (VRM Expression)";
    }

    public async UniTask StartBlinkAsync()
    {
        if (isBlinkEnabled && blinkLoopStarted)
        {
            return;
        }

        isBlinkEnabled = true;

        if (blinkLoopStarted)
        {
            return;
        }

        blinkLoopStarted = true;
        Debug.Log("[VRM10Blink] Blink started");

        while (isBlinkEnabled && !blinkCts.Token.IsCancellationRequested)
        {
            try
            {
                // 等待随机间隔
                float interval = Random.Range(minBlinkInterval, maxBlinkInterval);
                await UniTask.Delay((int)(interval * 1000), cancellationToken: blinkCts.Token);

                if (!isBlinkEnabled) break;

                // 闭眼
                targetBlinkWeight = 1f;
                await UniTask.Delay((int)(blinkDuration * 1000), cancellationToken: blinkCts.Token);

                // 开眼
                targetBlinkWeight = 0f;
            }
            catch (System.OperationCanceledException)
            {
                break;
            }
        }
    }

    public void StopBlink()
    {
        isBlinkEnabled = false;
        targetBlinkWeight = 0f;
        currentBlinkWeight = 0f;
        ApplyBlinkWeight(0f);
    }

    private void ApplyBlinkWeight(float weight)
    {
#if USE_VRM10
        if (vrm10Instance != null && vrm10Instance.Runtime != null)
        {
            var blinkKey = ExpressionKey.Blink;
            vrm10Instance.Runtime.Expression.SetWeight(blinkKey, weight);
        }
#endif
    }
}

