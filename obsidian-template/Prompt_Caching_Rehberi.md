---
title: Prompt Caching & Token Optimizasyon Rehberi
tags: [guide, token-optimization, prompt-caching, claude, gemini, ai-architecture]
created: 2026-10-16
updated: 2026-10-16
---

# 🧠 Prompt Caching & Token Optimizasyon Rehberi

Bu rehber, LLM tabanlı yazılım geliştirme süreçlerinde (Antigravity, Claude Code, Cursor, Codex vb.) token tüketimini **%80-%90 oranında düşüren** Prefix Caching ve Orchestrator-Worker mimarisini detaylandırır.

---

## 1. Problem: Token Limitleri Neden Çabuk Bitiyor?

Geleneksel kullanımda yapılan en yaygın hatalar:
1. **Devasa Sohbet Geçmişi (Context Bloat):** 20 mesajlık bir oturumda her yeni mesaj, önceki 19 mesajın tüm metnini, tool çıktılarını ve kod parçalarını modelin context penceresine tekrar gönderir.
2. **Belirsiz Promptlar:** *"Şu koda bir bak hata var"* dendiğinde model projedeki tüm dosyaları tarar, arama tool'ları çalıştırır, ekran görüntüleri alır ve binlerce gereksiz token tüketir.
3. **Rastgele Prompt Yapısı:** Kuralların, kodların ve görevlerin her mesajda farklı sırada veya farklı kelimelerle verilmesi LLM sağlayıcısının cache'ini geçersiz kılar.

---

## 2. Çözüm: Prefix Caching Mekanizması

Büyük Dil Modelleri (Claude 3.5 Sonnet, GPT-4o, Gemini 2.5/3.8), context caching için **Prefix Caching** kullanır. Bu sistem metni baştan sona (soldan sağa) hash'ler:

```
[Statik Kurallar & Roller] -> Hash: 0xA1B2 (CACHED ✅)
      │
[Proje Mimarisi & Hedef Kod] -> Hash: 0xC3D4 (CACHED ✅)
      │
[Dinamik Görev & Buton Rengi] -> Hash: 0xE5F6 (Yeni İşlem ⚙️)
```

Eğer ilk iki bloğa tek bir harf dahi eklenmez/silinmezse:
* **Girdi (Input) Maliyeti:** %80 - %90 daha ucuz (Cache Read tarifesi).
* **Yanıt Hızı (Latency):** 2 ila 4 kat daha hızlı.

### Fiyat Farkı Tablosu (Örnek: Claude 3.5 Sonnet)

| İşlem Türü | Normal Input | Cache Write (İlk Sefer) | Cache Read (Tekrar Eden) | Tasarruf |
| :--- | :--- | :--- | :--- | :--- |
| **1M Token Başına** | \$3.00 | \$3.75 | **\$0.30** | **%90 İndirim** |

---

## 3. Orchestrator - SubAgent Mimarisi

Kullanıcı olarak her iş için uzun optimize promptlar yazmak zahmetlidir. Çözüm: **Orchestrator Ajan** yaklaşımıdır:

1. **Sen:** Orchestrator'a kısa, doğal bir istek yazarsın (*"Sepetteki kupon çakışmasını düzelt"*).
2. **Orchestrator:**
   - İlgili dosyayı (`checkout.js`) bulur.
   - Obsidian'daki `SubAgent_Cache_Template.md` şablonunu alır.
   - Statik prefix'i tepeye, dosyayı ortaya, isteğini kısıtlarla birlikte en alta koyar.
3. **Sub-Agent:** İzole bir oturumda çalışır, işi yapar, çıktıyı döner ve sonlanır.
   - Ana sohbetin context'i şişmez.
   - Alt ajanların tümü aynı cache havuzunu kullanır.

---

## 4. Altın Kurallar (Best Practices)

1. **Byte-level Determinizm:** Statik bloktaki boşlukları, satır sonlarını (CRLF vs LF) veya virgülleri asla değiştirmeyin.
2. **Token Barajı:** Cache'in tetiklenmesi için statik ön ekin genellikle en az **1024 token** (modellerine göre 2048) olması gerekir. Statik bloğunuzu zengin kurallar ve prensiplerle doldurun.
3. **Değişkenler En Alta:** Tarih, saat, dinamik değişken veya kullanıcı girdilerini asla statik bloğun arasına sokmayın. Her zaman en son satıra ekleyin.
