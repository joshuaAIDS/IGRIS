import { IGRIS_MODEL_CATALOG } from '../../config/models';
import { detectLanguage } from '../../utils/languageDetector';
import {
  CANDIDATE_A_METADATA,
  estimateCandidateATokens,
  TokenizerMetadata,
} from '../tokenizer/candidateA';
import { IInferenceAdapter } from './adapter.interface';
import {
  BackendHealthStatus,
  InferenceChunk,
  InferenceRequest,
  InferenceResponse,
  TokenUsage,
} from './types';

export class DemoSimulationAdapter implements IInferenceAdapter {
  readonly id = 'demo-adapter';
  readonly name = 'IGRIS Demo Simulation Adapter';
  readonly isDemo = true;
  private currentAbortController: AbortController | null = null;

  async sendMessage(
    request: InferenceRequest,
    onChunk?: (chunk: InferenceChunk) => void,
    signal?: AbortSignal,
  ): Promise<InferenceResponse> {
    this.currentAbortController = new AbortController();

    const effectiveSignal = signal || this.currentAbortController.signal;
    const model = IGRIS_MODEL_CATALOG[request.modelId] || IGRIS_MODEL_CATALOG['IGRIS-50M-BASELINE'];
    const detectedLang = request.language || detectLanguage(request.prompt);

    const startTime = performance.now();
    const promptTokens = estimateCandidateATokens(request.prompt, detectedLang);

    // Build a linguistically sound demo response tailored to Tamil, English, or Tanglish
    const generatedContent = this.generateTrilingualDemoText(request.prompt, detectedLang, model.name);

    if (effectiveSignal.aborted) {
      const err = new Error('Generation aborted by user');
      err.name = 'AbortError';
      throw err;
    }

    const completionTokens = estimateCandidateATokens(generatedContent, detectedLang);
    const latencyMs = Math.round(performance.now() - startTime + 85);
    const usage: TokenUsage = {
      promptTokens,
      completionTokens,
      totalTokens: promptTokens + completionTokens,
      latencyMs,
    };

    // If streaming is not requested, return immediately
    if (!request.config.streaming || !onChunk) {
      return {
        text: generatedContent,
        usage,
        isDemo: true,
        modelId: model.id,
        finishReason: 'stop',
      };
    }

    // Stream chunks word by word
    const words = generatedContent.split(' ');
    let emittedText = '';
    const delayPerChunk = 24; // Smooth conversational stream pacing

    for (let i = 0; i < words.length; i++) {
      if (effectiveSignal.aborted) {
        const abortedUsage: TokenUsage = {
          promptTokens,
          completionTokens: estimateCandidateATokens(emittedText, detectedLang),
          totalTokens: promptTokens + estimateCandidateATokens(emittedText, detectedLang),
          latencyMs: Math.round(performance.now() - startTime),
        };
        return {
          text: emittedText,
          usage: abortedUsage,
          isDemo: true,
          modelId: model.id,
          finishReason: 'abort',
        };
      }

      const nextWord = i === 0 ? words[i] : ' ' + words[i];
      emittedText += nextWord;

      onChunk({
        deltaText: nextWord,
        isFinal: i === words.length - 1,
        isDemo: true,
      });

      // Non-blocking async sleep
      await new Promise((resolve) => setTimeout(resolve, delayPerChunk));
    }

    return {
      text: generatedContent,
      usage: {
        ...usage,
        latencyMs: Math.round(performance.now() - startTime),
      },
      isDemo: true,
      modelId: model.id,
      finishReason: 'stop',
    };
  }

  abort(): void {
    if (this.currentAbortController) {
      this.currentAbortController.abort();
      this.currentAbortController = null;
    }
  }

  async checkHealth(_endpointUrl?: string): Promise<BackendHealthStatus> {
    return {
      isConnected: false,
      isDemo: true,
      endpoint: 'Local Memory (No Runtime Connected)',
      statusText: 'DEMO MODE · LOCAL RUNTIME STANDBY',
      modelState: 'DEMO MODE',
      latencyMs: 0,
      modelName: 'IGRIS-50M-Baseline (Demo)',
    };
  }

  getTokenizerInfo(): TokenizerMetadata {
    return CANDIDATE_A_METADATA;
  }

  private generateTrilingualDemoText(
    prompt: string,
    lang: 'en' | 'ta' | 'tanglish',
    modelName: string,
  ): string {
    const demoNotice = `> **[IGRIS DEMO MODE]** *This is a demonstration response. The actual IGRIS model runtime backend is not yet connected.*`;
    const cleanPrompt = prompt.trim();

    if (lang === 'ta') {
      return [
        demoNotice,
        `வணக்கம்! நான் **இக்ரிஸ் (IGRIS)** — தமிழ், ஆங்கிலம் மற்றும் தங்கிலிஷ் (Tanglish) மொழிகளுக்கான சுயாட்சி கொண்ட சிறிய மொழி மாதிரி (SLM).`,
        `உங்கள் கேள்வி: *"${cleanPrompt}"*`,
        `**தமிழ் செயலாக்க சிறப்பம்சங்கள்:**`,
        `1. **Candidate A டோக்கனைசர்**: தமிழ் எழுத்துக்களுக்கான 32,768 சொல்லகராதி (vocabulary) மற்றும் பைட்-ஃபால்பேக் (byte fallback) அமைப்புடன் வடிவமைக்கப்பட்டுள்ளது.`,
        `2. **உள்ளூர் கட்டமைப்பு**: 50M அளவுருக்கள் கொண்ட இந்த மாதிரி, தனியுரிமையைப் பாதுகாத்து நுகர்வோர் வன்பொருளில் (Consumer GPU) நேரடியாக இயங்கும் திறன் கொண்டது.`,
        `3. **அடுத்த கட்டம்**: உண்மையான IGRIS பைடார்ச்/சி++ ரன்டைம் இணைக்கப்பட்டவுடன், நேரடி மாதிரி கணிப்புகள் இங்கு தோன்றும்.`,
      ].join('\n\n');
    }

    if (lang === 'tanglish') {
      return [
        demoNotice,
        `Vanakkam! Naan **IGRIS** — Tamil, English, and Tanglish native-aa handle panna koodiya autonomous Small Language Model (SLM).`,
        `Unga input: *"${cleanPrompt}"*`,
        `**Tanglish Processing Architecture:**`,
        `1. **Phonetic Normalization**: Tanglish digraphs ("zh", "dh", "th") Candidate A tokenizer moolamaaga accurately compress aagum.`,
        `2. **Edge Performance**: Consumer GPU-la (RTX 3050 6GB) ultra-low latency-oda execute panna 50M parameter baseline optimize panni irukkom.`,
        `3. **Demo Status**: Real IGRIS weights innum runtime-la load aagala. Runtime daemon start panni Settings-la connect pannina live inference activate aagidum.`,
      ].join('\n\n');
    }

    // Default: English response
    return [
      demoNotice,
      `Hello! I am **IGRIS** — a Voice-First Autonomous Small Language Model (SLM) engineered from first principles in PyTorch and C++.`,
      `Your prompt: *"${cleanPrompt}"*`,
      `**Key Architectural Highlights:**`,
      `- **50M Parameter Baseline**: Decoder-only Transformer with Pre-LayerNorm RMSNorm, SwiGLU activation, RoPE embeddings, and GQA (8:4 heads) for consumer-grade GPU execution.`,
      `- **Trilingual Candidate A Tokenizer**: Unified 32,768 vocabulary covering English, Tamil Unicode, and phonetic Tanglish with zero out-of-vocabulary fallback.`,
      `- **Three-Tier Desktop Safety**: Sandboxed execution preserving strict human-in-the-loop permission gating for OS commands.`,
      `To stream live tokens from the neural network, connect the local IGRIS inference runtime daemon in Settings.`,
    ].join('\n\n');
  }
}
