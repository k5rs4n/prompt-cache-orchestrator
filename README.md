# ⚡ Prompt Cache Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Antigravity](https://img.shields.io/badge/Antigravity-Custom%20Skill-blue.svg)](https://github.com/k5rs4n/prompt-cache-orchestrator)
[![Prompt Cache](https://img.shields.io/badge/Token%20Savings-%7E90%25-brightgreen.svg)](https://github.com/k5rs4n/prompt-cache-orchestrator)

> **LLM token maliyetlerini ve limitlerini %80-%90 oranında düşüren, Prefix Caching ve Sub-Agent (Orchestrator-Worker) optimizasyon sistemi.**
> Antigravity, Obsidian ve tüm LLM iş akışlarıyla (Claude Code, Cursor, Codex) tam uyumludur.

---

## 🎯 Bu Proje Neyi Çözüyor?

Büyük dil modellerinde (Claude 3.5 Sonnet, GPT-4o, Gemini 2.5/3.8) uzun sohbetler uzadıkça:
1. **Context Bloat:** Her yeni soruda önceki tüm mesaj geçmişi tekrar tekrar modele gönderilir ve token limitleri hızla tükenir.
2. **Düzensiz Promptlar:** *"Şu koda bir bak hata var"* dendiğinde model tüm repoyu tarar, gereksiz tool çağrıları yapar.
3. **Cache Miss:** Prompt yapısı her mesajda değiştiği için model sağlayıcılarının sunduğu indirimli **Prompt Cache** devreye giremez.

### 💡 Çözüm: 3 Katmanlı Prefix Cache & Orchestrator Mimarisi

LLM'lerin context cache mekanizması **soldan sağa (prefix)** çalışır. Bu sistem ile:
* Sen Orchestrator'a **düz, kısa ve informal** bir prompt yazarsın (`"Sepetteki kupon çakışmasını düzelt"`).
* Orchestrator, Obsidian'daki veya projedeki **değişmeyen şablonu** en başa koyar, hedef dosyaları bağlam olarak ekler ve senin isteğini en sona yerleştirerek alt ajanı (Sub-Agent) çalıştırır.
* Alt ajan izole bir oturumda çalışır, işi bitirir ve döner. Sohbet geçmişi şişmez; token maliyeti **10'da 1'e** iner!

```mermaid
graph TD
    User["👤 Kullanıcı (Düz Prompt)"] -->|'Kupon hatasını çöz'| Orchestrator["🤖 Orchestrator Ajan"]
    Orchestrator -->|1. Statik Şablonu Çeker| Obsidian["📓 Obsidian / Kural Şablonu"]
    Orchestrator -->|2. İlgili Dosyaları Belirler| Files["📁 Hedef Dosyalar (checkout.js)"]
    Orchestrator -->|3. 3-Tier Cache Prompt Derler| Compiler["⚡ Prompt Cache Compiler"]
    Compiler --> Worker["👷 Sub-Agent (Worker)"]
    
    subgraph "Sub-Agent Prompt Yapısı"
        P1["1. [CACHE-STATIC-PREFIX] (Roller, Kurallar) -> %90 İndirimli Cache Hit"]
        P2["2. [STABLE-CONTEXT] (checkout.js İçeriği) -> Cache Hit"]
        P3["3. [DYNAMIC-TASK] (Kupon Hatası Düzeltimi) -> Yalnızca Bu Kısım Ücretli"]
    end
    
    Worker --> Sub-Agent Prompt Yapısı
    Worker -->|Temiz Diff / Çözüm| Orchestrator
    Orchestrator -->|Nihai Sonuç| User
```

---

## 💰 Rakamlarla Tasarruf (Örnek: Claude 3.5 Sonnet)

| Kullanım Şekli | 1M Token Maliyeti | 20 Mesaj Sonrası Context | Hız (Latency) |
| :--- | :--- | :--- | :--- |
| **Geleneksel Sohbet (Tek Session)** | \$3.00 / 1M | ~150.000 Token (Şişmiş) | Gittikçe yavaşlar |
| **Prompt Cache Orchestrator** | **\$0.30 / 1M** (Cache Hit) | **~3.000 Token** (İzole) | **2-4 kat daha hızlı** |

---

## 🚀 Kurulum

### 1. Antigravity İçine Kurulum (Global)

Windows PowerShell'de projeyi klonlayıp installer'ı çalıştırın:

```powershell
git clone https://github.com/k5rs4n/prompt-cache-orchestrator.git
cd prompt-cache-orchestrator
.\install.ps1
```

*(macOS / Linux için: `chmod +x install.sh && ./install.sh`)*

Bu komut, Antigravity global yetenek klasörüne (`~/.gemini/config/skills/prompt-cache-orchestrator`) yeteneği otomatik olarak yükler. Artık Antigravity'ye *"bu işi alt ajanla cache optimizasyonu yaparak çöz"* demeniz yeterlidir!

---

### 2. Obsidian Entegrasyonu

Depodaki `obsidian-template/` klasörünü Obsidian kasanıza kopyalayın:

```
Obsidian_Kasaniz/
├── 📄 SubAgent_Cache_Template.md      <-- Değişmeyen ana prompt şablonu
├── 📄 Proje_Mimarisi_Sablonu.md       <-- Projenizin mimari kuralları
└── 📄 Prompt_Caching_Rehberi.md       <-- Mantık ve optimizasyon rehberi
```

#### Örnek Şablon Mantığı:
```markdown
# [CACHE-STATIC-PREFIX: DO NOT MODIFY]
Sen kıdemli bir alt ajansın.
1. Sadece hedef dosyalarda çalış.
2. Dışarıdan rastgele paket ekleme.
3. Fonksiyon imzalarını bozma.
# [/CACHE-STATIC-PREFIX]

# [STABLE-CONTEXT]
{{TARGET_FILES}}
# [/STABLE-CONTEXT]

# [DYNAMIC-TASK]
{{USER_REQUEST}}
# [/DYNAMIC-TASK]
```

---

### 3. Python CLI ile Prompt Derleme ve Doğrulama

Sistem içinde bağımsız çalışan bir prompt derleyici araç (`tools/prompt_cache_compiler.py`) mevcuttur:

```bash
# Prefix determinizmini ve token sayısını test etme
python tools/prompt_cache_compiler.py hash -t obsidian-template/SubAgent_Cache_Template.md

# 3-Tier Cache uyumlu prompt derleme
python tools/prompt_cache_compiler.py compile \
  -t obsidian-template/SubAgent_Cache_Template.md \
  -f src/checkout.js \
  --title "Kupon Hatası" \
  --task "%20 kupon ve kampanya çakışmasını düzelt" \
  -o compiled_prompt.txt
```

---

## 🤖 Otomatik Devreye Alma Protokolü

Antigravity'nin global kural dosyasına (`~/.gemini/GEMINI.md`) otomatik sorgu protokolü entegre edilmiştir. 

Artık siz herhangi bir kodlama veya teknik görev verdiğinizde, Antigravity göreve doğrudan başlamak yerine size sorar:
> *"Bu görevi token tasarrufu ve context optimizasyonu için **Prompt Cache Orchestrator** ve alt ajan (sub-agent) ile yürüteyim mi?"*

* **Evet / Devreye Al:** İlgili dosyaları context olarak alır, `[CACHE-STATIC-PREFIX]` ile promptu derler ve izole alt ajan başlatır.
* **Hayır / Gerek Yok:** Görevi standart şekilde mevcut oturumda tamamlar.

## 🛠️ Antigravity İçinde Kullanım Örneği

Sohbet esnasında Antigravity'ye doğrudan şöyle diyebilirsiniz:

> *"Sepetteki indirim hesaplama hatasını alt ajan çalıştırarak ve prompt-cache-orchestrator şablonuyla çöz."*

Antigravity otomatik olarak:
1. İlgili dosyayı (`checkout.js`) tespit eder.
2. `[CACHE-STATIC-PREFIX]` bloğunu tek bir karakter dahi değiştirmeden en tepeye koyar.
3. Dosya içeriğini ortaya, görevi en alta ekler.
4. `invoke_subagent` ile izole bir alt ajan başlatıp sıfır context şişmesiyle görevi tamamlar.

---

## 📁 Proje Yapısı

```
prompt-cache-orchestrator/
├── skills/
│   └── prompt-cache-orchestrator/
│       └── SKILL.md                  # Antigravity Skill tanımı
├── obsidian-template/
│   ├── SubAgent_Cache_Template.md    # Obsidian için dokunulmaz statik şablon
│   ├── Proje_Mimarisi_Sablonu.md     # Proje kuralları şablonu
│   └── Prompt_Caching_Rehberi.md     # Kapsamlı optimizasyon kılavuzu
├── tools/
│   └── prompt_cache_compiler.py      # Deterministik CLI derleyici & token sayacı
├── tests/
│   └── test_compiler.py              # Birim testleri
├── install.ps1                       # Windows tek tıkla kurulum
├── install.sh                        # Unix/macOS kurulum
├── LICENSE                           # MIT Lisansı
└── README.md
```

---

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Dilediğiniz gibi kullanabilir, projelerinize entegre edebilir ve paylaşabilirsiniz.
