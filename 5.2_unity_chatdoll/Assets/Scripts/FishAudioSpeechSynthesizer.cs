using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;
using UnityEngine.Networking;
using Cysharp.Threading.Tasks;
using ChatdollKit.SpeechSynthesizer;
using System.Text;
using Newtonsoft.Json;

// Fish Audio TTS - HTTP API，简单稳定
public class FishAudioSpeechSynthesizer : SpeechSynthesizerBase
{
    [Header("Fish Audio 配置")]
    [Tooltip("API Key（从 fishspeech.net 获取）")]
    public string ApiKey = "";
    
    [Tooltip("声音模型 ID（reference_id）")]
    public string ReferenceId = "";
    
    [Tooltip("语速，范围：0.5-2.0")]
    [Range(0.5f, 2.0f)]
    public float Speed = 1.0f;
    
    [Tooltip("音量，范围：-20 到 20")]
    [Range(-20f, 20f)]
    public float Volume = 0f;
    
    [Tooltip("TTS 版本：v1/v2/s1（传统版本）或 v3-turbo/v3-hd（V3版本，支持情绪控制）")]
    public string Version = "s1";
    
    [Tooltip("音频格式：mp3/wav/pcm")]
    public string Format = "mp3";
    
    [Tooltip("情绪控制（仅V3版本支持）：happy/sad/angry/fearful/disgusted/surprised/calm/fluent/auto")]
    public string Emotion = "auto";
    
    [Tooltip("语言增强（仅V3版本支持）：auto/zh/en 等")]
    public string Language = "auto";

    public bool _IsEnabled = true;
    public override bool IsEnabled
    {
        get { return _IsEnabled; }
        set { _IsEnabled = value; }
    }

    private void Start()
    {
        // TTS 生成可能需要较长时间，默认设置为 60 秒
        if (Timeout == 10)
        {
            Timeout = 60;
        }
    }

    protected override async UniTask<AudioClip> DownloadAudioClipAsync(string text, Dictionary<string, object> parameters, CancellationToken token)
    {
        if (token.IsCancellationRequested) { return null; }

        if (string.IsNullOrEmpty(text.Trim()))
        {
            Debug.LogWarning("[FishAudio] 文本为空，跳过 TTS 生成");
            return null;
        }

        Debug.Log($"[FishAudio] 开始生成 TTS: {text.Substring(0, Math.Min(50, text.Length))}...");

        if (string.IsNullOrEmpty(ApiKey))
        {
            Debug.LogError("[FishAudio] API Key 未配置！请在 Inspector 中填入 API Key。");
            return null;
        }

        // 去除 API Key 前后的空格
        string cleanApiKey = ApiKey.Trim();
        if (string.IsNullOrEmpty(cleanApiKey))
        {
            Debug.LogError("[FishAudio] API Key 为空（可能只有空格）！请检查 Inspector 中的配置。");
            return null;
        }

        if (string.IsNullOrEmpty(ReferenceId))
        {
            Debug.LogError("[FishAudio] Reference ID（声音模型ID）未配置！请在 Inspector 中填入 Reference ID。");
            return null;
        }

        // 去除 Reference ID 前后的空格
        string cleanReferenceId = ReferenceId.Trim();
        if (string.IsNullOrEmpty(cleanReferenceId))
        {
            Debug.LogError("[FishAudio] Reference ID 为空（可能只有空格）！请检查 Inspector 中的配置。");
            return null;
        }

        try
        {
            // 构建请求数据
            var requestData = new Dictionary<string, object>
            {
                { "reference_id", cleanReferenceId },
                { "text", text },
                { "speed", Speed },
                { "volume", Volume },
                { "version", Version },
                { "format", Format }
                // 注意：不设置 cache 参数，让API使用默认值
            };

            // V3 版本支持情绪控制和语言增强
            if (Version.StartsWith("v3"))
            {
                requestData["emotion"] = Emotion;
                requestData["language"] = Language;
            }

            string json = JsonConvert.SerializeObject(requestData);
            byte[] jsonBytes = Encoding.UTF8.GetBytes(json);

            // 发送 POST 请求到 Fish Audio API
            string apiUrl = "https://fishspeech.net/api/open/tts";
            
            using (UnityWebRequest www = new UnityWebRequest(apiUrl, "POST"))
            {
                www.uploadHandler = new UploadHandlerRaw(jsonBytes);
                www.downloadHandler = new DownloadHandlerBuffer();
                www.SetRequestHeader("Content-Type", "application/json");
                
                // 使用清理后的 API Key
                string authHeader = $"Bearer {cleanApiKey}";
                www.SetRequestHeader("Authorization", authHeader);
                www.timeout = Timeout;

                Debug.Log($"[FishAudio] 发送请求到: {apiUrl}");
                Debug.Log($"[FishAudio] API Key 长度: {cleanApiKey.Length} 字符");
                Debug.Log($"[FishAudio] Reference ID: {cleanReferenceId}");

                try
                {
                    await www.SendWebRequest().ToUniTask(cancellationToken: token);
                    Debug.Log($"[FishAudio] 请求完成，状态: {www.result}");
                }
                catch (Exception e)
                {
                    if (e.Message.Contains("timeout") || e.Message.Contains("Timeout"))
                    {
                        Debug.LogError($"[FishAudio] 请求超时（{Timeout}秒）。TTS 生成可能需要更长时间，请:\n1. 在 Inspector 中增加 Timeout 值（当前: {Timeout}秒）\n2. 检查网络连接\n3. 检查 API 服务是否正常");
                    }
                    else
                    {
                        Debug.LogError($"[FishAudio] 请求异常: {e.Message}");
                    }
                    return null;
                }

                // 检查 HTTP 状态码
                int statusCode = (int)www.responseCode;
                if (statusCode == 402)
                {
                    // 配额不足错误
                    string errorResponse = www.downloadHandler?.text ?? "";
                    try
                    {
                        var errorData = JsonConvert.DeserializeObject<Dictionary<string, object>>(errorResponse);
                        if (errorData != null && errorData.ContainsKey("error"))
                        {
                            string errorMsg = errorData["error"].ToString();
                            string remainingQuota = errorData.ContainsKey("remaining_quota") ? errorData["remaining_quota"].ToString() : "未知";
                            string requiredQuota = errorData.ContainsKey("required_quota") ? errorData["required_quota"].ToString() : "未知";
                            
                            Debug.LogError($"[FishAudio] ❌ API 配额不足！\n" +
                                         $"错误: {errorMsg}\n" +
                                         $"剩余配额: {remainingQuota}\n" +
                                         $"需要配额: {requiredQuota}\n\n" +
                                         $"解决方案:\n" +
                                         $"1. 登录 https://fishspeech.net 充值或升级账户\n" +
                                         $"2. 等待配额重置（如果有免费额度）\n" +
                                         $"3. 使用其他 TTS 服务");
                        }
                        else
                        {
                            Debug.LogError($"[FishAudio] HTTP 402 支付 required: {errorResponse}");
                        }
                    }
                    catch
                    {
                        Debug.LogError($"[FishAudio] HTTP 402 支付 required: {errorResponse}");
                    }
                    return null;
                }
                else if (statusCode == 401)
                {
                    // 401 Unauthorized - API Key 认证失败
                    string errorResponse = www.downloadHandler?.text ?? "";
                    Debug.LogError($"[FishAudio] ❌ HTTP 401 Unauthorized - API Key 认证失败\n" +
                                 $"错误响应: {errorResponse}\n\n" +
                                 $"请检查:\n" +
                                 $"1. API Key 是否正确（当前长度: {cleanApiKey.Length} 字符）\n" +
                                 $"2. API Key 是否包含多余的空格或换行符\n" +
                                 $"3. 是否在 https://fishspeech.net 正确获取了 API Key\n" +
                                 $"4. API Key 是否已过期或被撤销");
                    return null;
                }
                else if (statusCode >= 400)
                {
                    // 其他 HTTP 错误
                    string errorResponse = www.downloadHandler?.text ?? "";
                    Debug.LogError($"[FishAudio] HTTP 错误 {statusCode}: {www.error}\n响应: {errorResponse}");
                    return null;
                }

                if (www.result == UnityWebRequest.Result.Success)
                {
                    // 检查响应类型
                    string contentType = www.GetResponseHeader("Content-Type");
                    Debug.Log($"[FishAudio] 响应 Content-Type: {contentType}");
                    
                    if (contentType != null && contentType.Contains("audio"))
                    {
                        // 直接返回音频数据
                        byte[] audioData = www.downloadHandler.data;
                        
                        if (audioData == null || audioData.Length == 0)
                        {
                            Debug.LogError("[FishAudio] 音频数据为空");
                            return null;
                        }
                        
                        Debug.Log($"[FishAudio] 收到音频数据: {audioData.Length} bytes");
                        
                        // 保存为临时文件并加载
                        string tempPath = System.IO.Path.Combine(Application.temporaryCachePath, $"fish_tts_{DateTime.Now.Ticks}.{Format}");
                        System.IO.File.WriteAllBytes(tempPath, audioData);
                        Debug.Log($"[FishAudio] 保存临时文件: {tempPath}");

                        // 加载音频
                        AudioType audioType = Format == "mp3" ? AudioType.MPEG : 
                                            Format == "wav" ? AudioType.WAV : AudioType.UNKNOWN;
                        
                        Debug.Log($"[FishAudio] 开始加载音频文件，格式: {audioType}");
                        
                        using (UnityWebRequest audioRequest = UnityWebRequestMultimedia.GetAudioClip($"file://{tempPath}", audioType))
                        {
                            await audioRequest.SendWebRequest().ToUniTask(cancellationToken: token);

                            if (audioRequest.result == UnityWebRequest.Result.Success)
                            {
                                AudioClip clip = DownloadHandlerAudioClip.GetContent(audioRequest);

                                if (clip == null)
                                {
                                    Debug.LogError("[FishAudio] AudioClip 为 null，加载失败");
                                }
                                else
                                {
                                    Debug.Log($"[FishAudio] 成功生成 AudioClip: {clip.length}秒, {clip.frequency}Hz, {clip.channels}声道");
                                }

                                // 清理临时文件
                                try { System.IO.File.Delete(tempPath); } catch { }

                                return clip;
                            }
                            else
                            {
                                Debug.LogError($"[FishAudio] 加载音频失败: {audioRequest.error}");
                            }
                        }
                    }
                    else
                    {
                        // 可能是 JSON 错误响应
                        string responseText = www.downloadHandler.text;
                        Debug.LogError($"[FishAudio] API 返回非音频响应 (Content-Type: {contentType}): {responseText}");
                    }
                }
                else
                {
                    // www.result != Success 但 statusCode < 400 的情况（如网络错误）
                    string errorResponse = www.downloadHandler?.text ?? "";
                    Debug.LogError($"[FishAudio] 请求失败: {www.error}\n状态码: {statusCode}\n响应: {errorResponse}\n\n请检查:\n1. API Key 是否正确\n2. Reference ID 是否正确\n3. 网络连接是否正常");
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[FishAudio] 错误: {e.Message}\n{e.StackTrace}");
        }

        return null;
    }
}

