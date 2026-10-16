---
title: Proje Mimarisi & Statik Kurallar Şablonu
tags: [template, architecture, project-rules, prompt-cache]
created: 2026-10-16
updated: 2026-10-16
---

# 🏗️ Proje Mimarisi & Statik Kurallar

Bu dosya, çalıştığınız projenin değişmeyen mimari standartlarını ve teknik kurallarını tanımlar. Orchestrator ajan, alt ajanlara bağlam verirken bu dosyayı `[CACHE-STATIC-PREFIX]` veya `[STABLE-CONTEXT]` katmanına dahil eder.

---

## 1. Proje Özeti
- **Proje Adı:** {{PROJECT_NAME}}
- **Amaç:** {{PROJECT_GOAL}}
- **Ana Teknolojiler:** {{TECH_STACK}} (Örn: TypeScript, Next.js 15, TailwindCSS v4, PostgreSQL)

## 2. Dizin Yapısı & Modüller
- `/src/components`: Tekrar kullanılabilir UI bileşenleri
- `/src/lib`: Yardımcı fonksiyonlar ve API istemcileri
- `/src/server`: Backend işlemleri, veritabanı sorguları ve API rotaları

## 3. Kodlama Standartları & Kurallar
- **State Yönetimi:** Zustand veya React Context (Redux eklemeyin).
- **Stil:** Yalnızca Tailwind utility class'ları kullanın. Inline CSS veya harici CSS modülleri eklemeyin.
- **Tip Güvenliği:** `any` kullanımı yasaktır, tüm tipler açıkça tanımlanmalıdır.
- **Paketler:** Projeye yeni npm/pip paketi eklenmeden önce mutlaka kullanıcı onayı alınmalıdır.

## 4. Test & Doğrulama
- Her yeni fonksiyon için ilgili test dosyası (`*.test.ts`) güncellenmelidir.
- Test komutu: `npm test` veya `pytest`
