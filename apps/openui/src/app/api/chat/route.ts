import { NextRequest } from "next/server";
import OpenAI from "openai";

import { systemPrompt } from "@/generated/system-prompt";

/**
 * Pano üretim ucu — PLAYGROUND.
 *
 * Üretimde bu iş `dima-backend`'e ait: sağlayıcı anahtarı Next sürecinde
 * durmamalı. Burası yalnız vokabüleri ve istemi denemek için.
 *
 * İSTEM RUNTIME'DA ÜRETİLMEZ. `generateSystemPrompt()` çağrılsaydı OpenUI'ın
 * yerleşik "veri istendiğinde gerçekçi/makul veri üret" kuralı geri gelirdi —
 * dima'nın deterministik-önce vaadinin tam tersi. Onun yerine
 * `scripts/genui-prompt.mjs`'in ürettiği YAMALI sabit okunuyor.
 *
 * İstemciden gelen `catalog` yalnız ŞEKİL taşır (bkz. lib/catalog.ts):
 * sonuç kimlikleri, boyut/ölçü ADLARI, satır SAYILARI. Gerçek satırlar,
 * müşteri adları ve rakamlar sağlayıcıya HİÇ gitmez.
 *
 * İstemci modül seviyesinde DEĞİL, istek başına kuruluyor: SDK anahtar yokken
 * kurulum anında fırlatır ve `next build` "page data" toplarken patlardı. CI ve
 * on-prem imaj üretiminde sır bulunmaz; build sırdan bağımsız olmalı.
 *
 * Sağlayıcı env'den: `OPENAI_BASE_URL` verilirse OpenAI-uyumlu herhangi bir uç
 * (Azure OpenAI, vLLM, Ollama) kullanılabilir — kurumsal müşteri "model
 * binamdan çıkmayacak" dediğinde değişen tek şey bu.
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
    const { messages, catalog } = (await req.json()) as {
      messages: { role: "user" | "assistant"; content: string }[];
      catalog?: string;
    };

    const client = new OpenAI({
      apiKey,
      // undefined bırakılırsa SDK kendi varsayılan uç noktasını kullanır.
      baseURL: process.env.OPENAI_BASE_URL,
    });

    const response = await client.chat.completions.create({
      model: process.env.OPENAI_MODEL ?? DEFAULT_MODEL,
      messages: [
        { role: "system", content: systemPrompt },
        ...(catalog
          ? ([
              {
                role: "system" as const,
                content:
                  `KATALOG — kullanabileceğin sonuçlar. Yalnız bu kimliklere atıf yap:\n\n${catalog}`,
              },
            ] as const)
          : []),
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
    return Response.json({ error: "Pano üretilemedi." }, { status: 502 });
  }
}
