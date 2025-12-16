using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using ChatdollKit.Model;
using ChatdollKit.Dialog;
using ChatdollKit.SpeechSynthesizer;
using System.Threading;

// 对应 JSONBin 的数据结构
[System.Serializable]
public class JsonBinResponse
{
    public JsonBinRecord record;
}

[System.Serializable]
public class JsonBinRecord
{
    public string text;
    public string timestamp;
    public bool read;
}

public class JsonBinListener : MonoBehaviour
{
    // 配置（在 Inspector 面板填入）
    [Header("JSONBin Configuration")]
    [Tooltip("在 JSONBin.io 控制台获取你的 Bin ID")]
    public string binId = "";
    [Tooltip("在 JSONBin.io 控制台的 API Keys 页面获取 Access Key")]
    public string accessKey = "";
    public float interval = 2.0f; // 轮询间隔
    [Tooltip("首次运行也说话（用于测试，否则会跳过首次消息）")]
    public bool speakOnFirstRun = false;

    [Header("Components")]
    public ModelController modelController;

    private string lastTimestamp = "";
    private CancellationTokenSource tokenSource;

    void Start()
    {
        // 自动获取 ModelController（如果在同一个物体上）
        if (modelController == null)
        {
            modelController = GetComponent<ModelController>();
        }

        if (modelController == null)
        {
            Debug.LogWarning("JsonBinListener: No ModelController found! Character will not speak.");
            return;
        }

        // 自动设置 TTS 函数（优先查找 FishAudioSpeechSynthesizer）
        if (modelController.SpeechSynthesizerFunc == null)
        {
            // 优先使用 FishAudioSpeechSynthesizer
            var fishTTS = GetComponent<FishAudioSpeechSynthesizer>();
            if (fishTTS != null && fishTTS.IsEnabled)
            {
                modelController.SpeechSynthesizerFunc = fishTTS.GetAudioClipAsync;
                Debug.Log("[JsonBinListener] 已自动设置 FishAudioSpeechSynthesizer");
            }
            else
            {
                // 尝试查找其他 SpeechSynthesizer
                var synthesizers = GetComponents<ISpeechSynthesizer>();
                foreach (var synth in synthesizers)
                {
                    if (synth.IsEnabled)
                    {
                        modelController.SpeechSynthesizerFunc = synth.GetAudioClipAsync;
                        Debug.Log($"[JsonBinListener] 已自动设置 {synth.GetType().Name}");
                        break;
                    }
                }
            }

            if (modelController.SpeechSynthesizerFunc == null)
            {
                Debug.LogError("[JsonBinListener] 未找到启用的 SpeechSynthesizer！请添加 FishAudioSpeechSynthesizer 组件并启用。");
            }
        }

        // 开始轮询协程
        StartCoroutine(PollJsonBin());
    }

    private void OnDestroy()
    {
        tokenSource?.Cancel();
    }

    IEnumerator PollJsonBin()
    {
        if (string.IsNullOrEmpty(binId) || string.IsNullOrEmpty(accessKey))
        {
            Debug.LogWarning("[JsonBinListener] Bin ID 或 Access Key 未配置！请在 Inspector 中填入配置。");
            yield break;
        }
        
        string url = $"https://api.jsonbin.io/v3/b/{binId}/latest";
        Debug.Log($"[JsonBinListener] Started polling: {url}");

        while (true)
        {
            using (UnityWebRequest www = UnityWebRequest.Get(url))
            {
                www.SetRequestHeader("X-Access-Key", accessKey);
                yield return www.SendWebRequest();

                if (www.result == UnityWebRequest.Result.Success)
                {
                    string json = www.downloadHandler.text;
                    HandleResponse(json);
                }
                else
                {
                    // 显示详细的错误信息
                    string errorDetail = www.downloadHandler?.text ?? "";
                    int statusCode = (int)www.responseCode;
                    Debug.LogError($"[JsonBinListener] HTTP {statusCode}: {www.error}\nResponse: {errorDetail}\n\n请检查:\n1. Bin ID 是否正确: {binId}\n2. Access Key 是否有 READ 权限\n3. 在 JSONBin 控制台确认 Bin 的权限设置");
                }
            }

            // 等待下一次轮询
            yield return new WaitForSeconds(interval);
        }
    }

    private async void HandleResponse(string json)
    {
        try
        {
            JsonBinResponse response = JsonUtility.FromJson<JsonBinResponse>(json);

            if (response == null || response.record == null)
            {
                Debug.LogError($"[JsonBinListener] JSON 解析失败：response 或 record 为 null\nJSON: {json}");
                return;
            }

            string text = response.record.text;
            string timestamp = response.record.timestamp;

            if (string.IsNullOrEmpty(text))
            {
                return;
            }

            // 如果是第一次运行
            bool isFirstRun = string.IsNullOrEmpty(lastTimestamp);
            
            if (isFirstRun && !speakOnFirstRun)
            {
                // 首次运行，跳过旧消息
                lastTimestamp = timestamp;
                return;
            }

            // 检查是否是新消息
            if (isFirstRun || timestamp != lastTimestamp)
            {
                lastTimestamp = timestamp;
                
                Debug.Log($"[New Message] {text}");

                // 让模型说话
                if (modelController == null || modelController.SpeechSynthesizerFunc == null)
                {
                    Debug.LogError("[JsonBinListener] TTS 未配置！");
                    return;
                }

                // 取消上一次的说话（如果有）
                tokenSource?.Cancel();
                tokenSource = new CancellationTokenSource();

                // 构建说话请求
                var voiceRequest = new AnimatedVoiceRequest();
                voiceRequest.AddVoice(text, 0.0f, 0.0f, null);

                // 异步执行说话
                try
                {
                    await modelController.AnimatedSay(voiceRequest, tokenSource.Token);
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[JsonBinListener] 说话失败: {e.Message}");
                }
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[JsonBinListener] Parse Error: {e.Message}\n{e.StackTrace}\nJSON: {json}");
        }
    }
}

