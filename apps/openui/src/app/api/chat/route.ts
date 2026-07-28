import librarySpec from "@/generated/spec.json";
import { promptOptions } from "@/lib/prompt-options";
import { generateSystemPrompt } from "@openuidev/lang-core";
import { NextRequest } from "next/server";
import OpenAI from "openai";

/**
 * Generative UI üretim ucu — PLAYGROUND.
 *
 * Üretimde bu iş `dima-backend`'e ait: sağlayıcı anahtarı Next sürecinde
 * durmamalı. Burası yalnız bileşen kütüphanesini ve istemi denemek için.
 *
 * İstemci modül seviyesinde DEĞİL, istek başına kuruluyor. Scaffold bunu
 * `const client = new OpenAI()` ile yapıyordu; SDK anahtar yoksa kurulum
 * anında fırlattığı için `next build` sırasında "page data" toplanırken
 * patlıyordu — yani build, çalıştırma sırrı olmadan hiç geçmiyordu. CI'da
 * ve on-prem imaj üretiminde sır bulunmaz; build sırdan bağımsız olmalı.
 *
 * Sağlayıcı env'den geliyor: `OPENAI_BASE_URL` verilirse OpenAI-uyumlu
 * herhangi bir uç (Azure OpenAI, vLLM, Ollama) kullanılabilir — kurumsal
 * müşteri "model binamdan çıkmayacak" dediğinde değişen tek şey bu.
 */

const DEFAULT_MODEL = "gpt-5.2";

export async function POST(req: NextRequest) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return Response.json(
      { error: "Sağlayıcı anahtarı tanımlı değil (OPENAI_API_KEY)." },
      { status: 503 },
    );
  }

  try {
    const { messages } = await req.json();

    const client = new OpenAI({
      apiKey,
      // undefined bırakılırsa SDK kendi varsayılan uç noktasını kullanır.
      baseURL: process.env.OPENAI_BASE_URL,
    });

    const response = await client.chat.completions.create({
      model: process.env.OPENAI_MODEL ?? DEFAULT_MODEL,
      messages: [
        {
          role: "system",
          content: generateSystemPrompt({
            library: librarySpec,
            promptOptions,
          }),
        },
        ...messages,
      ],
      stream: true,
    });

    return new Response(response.toReadableStream(), {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
      },
    });
  } catch (err) {
    // Sağlayıcı hata metni istemciye AKTARILMAZ: uç nokta, model adı ve
    // kota bilgisi sızdırabilir. Ayrıntı sunucu log'unda kalır.
    console.error("[genui] üretim başarısız:", err);
    return Response.json({ error: "Arayüz üretilemedi." }, { status: 502 });
  }
}
