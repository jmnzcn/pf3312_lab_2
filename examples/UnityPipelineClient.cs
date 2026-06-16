// Ejemplo conceptual — pipeline STT → LLM → TTS en cliente Unity (C#).
// No es un proyecto Unity completo; ilustra el flujo descrito en docs/pipeline.puml
// y respaldado por benchmarks/pipeline/ en Python.

using System;
using System.Collections;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

public class VirtualAgentPipeline : MonoBehaviour
{
    [SerializeField] private AudioSource agentVoice;
    [SerializeField] private int sampleRate = 16000;

    // 1) Captura audio del micrófono (simplificado).
    public byte[] CaptureUserUtterance(float seconds = 3f)
    {
        var clip = Microphone.Start(null, false, (int)seconds, sampleRate);
        while (Microphone.GetPosition(null) <= 0) { }
        return WavEncoder.FromAudioClip(clip); // utilidad local del proyecto
    }

    // 2) STT → 3) LLM → 4) TTS (REST; Azure/OpenAI como referencia).
    public IEnumerator RunTurn(byte[] wavBytes)
    {
        string transcript = null;
        string llmReply = null;
        byte[] ttsAudio = null;

        yield return PostJson(
            "https://api.openai.com/v1/audio/transcriptions",
            wavBytes,
            r => transcript = r);

        yield return PostSseOrJson(
            "https://api.openai.com/v1/chat/completions",
            $"{{\"model\":\"gpt-4o\",\"messages\":[{{\"role\":\"user\",\"content\":\"{Escape(transcript)}\"}}]}}",
            r => llmReply = r);

        yield return PostJson(
            "https://api.openai.com/v1/audio/speech",
            Encoding.UTF8.GetBytes($"{{\"model\":\"gpt-4o-mini-tts\",\"input\":\"{Escape(llmReply)}\"}}"),
            r => ttsAudio = r);

        // 5) Propagación al usuario en Unity.
        var clip = WavEncoder.ToAudioClip(ttsAudio, sampleRate);
        agentVoice.clip = clip;
        agentVoice.Play();
    }

    private IEnumerator PostJson(string url, byte[] body, Action<string> onText)
    {
        using var req = new UnityWebRequest(url, "POST");
        req.uploadHandler = new UploadHandlerRaw(body);
        req.downloadHandler = new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type", "application/json");
        yield return req.SendWebRequest();
        onText?.Invoke(req.downloadHandler.text);
    }

    private IEnumerator PostSseOrJson(string url, string json, Action<string> onText)
    {
        using var client = new HttpClient();
        var task = client.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
        while (!task.IsCompleted) yield return null;
        onText?.Invoke(task.Result.Content.ReadAsStringAsync().Result);
    }

    private static string Escape(string s) => (s ?? "").Replace("\"", "\\\"");
}

// Placeholder: en un proyecto real conviene usar Azure Speech SDK .NET
// (SpeechRecognizer + SpeechSynthesizer) o el SDK oficial de cada proveedor.
