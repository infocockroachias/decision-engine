// LongCat LLM Client - OpenAI-compatible API at https://api.longcat.chat/openai/v1
// Uses the LONGCAT_API_KEY environment variable for authentication.

import { LongCatMessage, LongCatResponse } from './types';

const LONGCAT_BASE_URL = 'https://api.longcat.chat/openai/v1';
const DEFAULT_MODEL = 'LongCat-Flash-Chat';

export interface LongCatClientConfig {
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  timeoutMs?: number;
}

export class LongCatClient {
  private apiKey: string;
  private baseUrl: string;
  private model: string;
  private temperature: number;
  private maxTokens: number;
  private timeoutMs: number;

  constructor(config: LongCatClientConfig = {}) {
    this.apiKey = config.apiKey || process.env.LONGCAT_API_KEY || '';
    if (!this.apiKey) {
      throw new Error('LONGCAT_API_KEY environment variable is not set');
    }
    this.baseUrl = config.baseUrl || LONGCAT_BASE_URL;
    this.model = config.model || DEFAULT_MODEL;
    this.temperature = config.temperature ?? 0.3;
    this.maxTokens = config.maxTokens ?? 4096;
    this.timeoutMs = config.timeoutMs ?? 60000;
  }

  /**
   * Send a chat completion request to the LongCat API.
   */
  async chat(
    messages: LongCatMessage[],
    options: Partial<Pick<LongCatClientConfig, 'model' | 'temperature' | 'maxTokens'>> = {}
  ): Promise<LongCatResponse> {
    const model = options.model || this.model;
    const temperature = options.temperature ?? this.temperature;
    const maxTokens = options.maxTokens ?? this.maxTokens;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify({
          model,
          messages,
          temperature,
          max_tokens: maxTokens,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `LongCat API error: ${response.status} ${response.statusText} - ${errorText}`
        );
      }

      const data: LongCatResponse = await response.json();
      return data;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Simple text completion helper - returns just the assistant's response text.
   */
  async complete(
    systemPrompt: string,
    userPrompt: string,
    options: Partial<Pick<LongCatClientConfig, 'model' | 'temperature' | 'maxTokens'>> = {}
  ): Promise<string> {
    const messages: LongCatMessage[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ];

    const response = await this.chat(messages, options);
    const content = response.choices?.[0]?.message?.content;
    if (!content) {
      throw new Error('LongCat API returned empty response');
    }
    return content;
  }

  /**
   * Parse JSON from an LLM response, handling common formatting issues.
   */
  async completeJson<T>(
    systemPrompt: string,
    userPrompt: string,
    options: Partial<Pick<LongCatClientConfig, 'model' | 'temperature' | 'maxTokens'>> = {}
  ): Promise<T> {
    const content = await this.complete(systemPrompt, userPrompt, {
      temperature: 0.1, // Lower temperature for JSON
      ...options,
    });

    // Try to extract JSON from markdown code blocks
    let jsonStr = content.trim();
    const codeBlockMatch = jsonStr.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (codeBlockMatch) {
      jsonStr = codeBlockMatch[1].trim();
    }

    try {
      return JSON.parse(jsonStr) as T;
    } catch (e) {
      throw new Error(`Failed to parse LongCat JSON response: ${(e as Error).message}\nContent: ${content.substring(0, 500)}`);
    }
  }
}

// Singleton instance for reuse across the app
let defaultClient: LongCatClient | null = null;

export function getLongCatClient(): LongCatClient {
  if (!defaultClient) {
    defaultClient = new LongCatClient();
  }
  return defaultClient;
}