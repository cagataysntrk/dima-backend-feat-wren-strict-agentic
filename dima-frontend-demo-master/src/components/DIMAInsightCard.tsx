import React, { useState } from 'react';
import { ShieldCheck, Terminal, ChevronDown, Activity, ArrowRight } from 'lucide-react';

export function DIMAInsightCard({ responseData, onFollowUpClick }: { responseData: any, onFollowUpClick?: (q: string) => void }) {
    const [showProof, setShowProof] = useState(false);

    if (!responseData) return null;

    return (
        <div className="w-full bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-2xl font-sans">
            {/* Üst Başlık & Rozet */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
                <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-emerald-400" />
                    <h3 className="text-lg font-bold text-white">{responseData.question}</h3>
                </div>

                {responseData.badge === "GOLD_TRUST_BADGE" && (
                    <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full text-emerald-400 text-xs font-semibold">
                        <ShieldCheck className="w-4 h-4" />
                        <span>GOLD TRUST BADGE (%100 Deterministik)</span>
                    </div>
                )}
            </div>

            {/* Rapor & Ana Veri Kartı */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {responseData.data?.map((item: any, idx: number) => (
                    <div key={idx} className="bg-slate-800/60 border border-slate-700/50 p-4 rounded-lg">
                        <span className="text-xs text-slate-400 font-medium block mb-1">
                            {item.islem_tarihi || item.makine_adi || `Kayıt #${idx + 1}`}
                        </span>
                        <span className="text-2xl font-black text-emerald-400">
                            {item.toplam_kayip_tl
                                ? `${item.toplam_kayip_tl.toLocaleString('tr-TR')} TL`
                                : JSON.stringify(item)}
                        </span>
                    </div>
                ))}
            </div>

            {/* Şeffaf Kanıt Paneli (Accordion) */}
            <div className="border-t border-slate-800 pt-4">
                <button
                    onClick={() => setShowProof(!showProof)}
                    className="flex items-center gap-2 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                    <Terminal className="w-4 h-4 text-cyan-400" />
                    <span>Matematiksel Kanıt Zinciri & QueryContract (SHA-256)</span>
                    <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showProof ? 'rotate-180' : ''}`} />
                </button>

                {showProof && (
                    <div className="mt-3 p-4 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 space-y-2">
                        <div>
                            <span className="text-slate-500 block">Çalıştırılan Wren SQL:</span>
                            <code className="text-cyan-400 break-all">{responseData.proof?.executed_wren_sql}</code>
                        </div>
                        <div>
                            <span className="text-slate-500 block">SHA-256 Kriptografik Mühür Hash'i:</span>
                            <code className="text-emerald-400 break-all">{responseData.proof?.query_contract_hash}</code>
                        </div>
                    </div>
                )}
            </div>

            {/* Takip Eden Akıllı Sorular */}
            {responseData.suggested_follow_up_questions && (
                <div className="mt-6 border-t border-slate-800/60 pt-4">
                    <span className="text-xs text-slate-400 font-semibold block mb-2 uppercase tracking-wider">
                        Önerilen Sonraki Adımlar:
                    </span>
                    <div className="flex flex-wrap gap-2">
                        {responseData.suggested_follow_up_questions.map((q: string, i: number) => (
                            <button
                                key={i}
                                onClick={() => onFollowUpClick && onFollowUpClick(q)}
                                className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-lg border border-slate-700/60 transition-all hover:border-emerald-500/50"
                            >
                                <span>{q}</span>
                                <ArrowRight className="w-3 h-3 text-slate-500" />
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
