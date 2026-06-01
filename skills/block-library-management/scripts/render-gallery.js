#!/usr/bin/env node
/**
 * Render a visual block gallery HTML from the block-library catalog.
 *
 * Usage:
 *   node render-gallery.js --library <path> --output <path>
 */

import fs from 'fs';
import path from 'path';
import { parse as parseYaml } from 'yaml';

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function htmlAttr(str) {
  return escapeHtml(str);
}

function getArgs() {
  const args = process.argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    if (args[i].startsWith('--')) {
      result[args[i].slice(2)] = args[i + 1];
    }
  }
  return result;
}

function main() {
  const args = getArgs();

  if (!args.library || !args.output) {
    console.error('Usage: node render-gallery.js --library <path> --output <path>');
    process.exit(1);
  }

  const libPath = path.resolve(args.library);
  const outputPath = path.resolve(args.output);
  const outputDir = path.dirname(outputPath);
  const catalogPath = path.join(libPath, 'catalog.yaml');

  if (!fs.existsSync(catalogPath)) {
    console.error(`ERROR: catalog.yaml not found at ${catalogPath}`);
    process.exit(1);
  }

  const catalogText = fs.readFileSync(catalogPath, 'utf-8');
  const catalog = parseYaml(catalogText);
  const blocks = catalog.blocks || [];

  // Gather unique categories
  const categories = [];
  const seen = new Set();
  for (const b of blocks) {
    const cat = b.category || 'unknown';
    if (!seen.has(cat)) {
      seen.add(cat);
      categories.push(cat);
    }
  }

  // Category RU labels
  const catLabelsRu = {
    'hero': 'Hero',
    'features': 'Фичи',
    'social-proof': 'Отзывы',
    'process': 'Процесс',
    'pricing': 'Цены',
    'trust': 'Доверие',
    'cta': 'CTA',
    'faq': 'FAQ',
    'quiz': 'Квиз',
    'references': 'Референсы',
  };

  // Category stats
  const catCounts = {};
  for (const b of blocks) {
    const cat = b.category || 'unknown';
    catCounts[cat] = (catCounts[cat] || 0) + 1;
  }

  // Build CSS for :checked filter rules
  const filterRules = [];
  filterRules.push('#filter-all:checked ~ .gallery-grid .gallery-card { display: flex !important; }');

  for (const cat of categories) {
    const safeCat = cat.replace(/-/g, '_');
    filterRules.push(`#filter-${safeCat}:checked ~ .gallery-grid .gallery-card { display: none; }`);
    filterRules.push(`#filter-${safeCat}:checked ~ .gallery-grid .gallery-card[data-cat="${escapeHtml(cat)}"] { display: flex; }`);
    filterRules.push(`#filter-${safeCat}:checked ~ .filter-bar label[for="filter-${safeCat}"] { background: #111; color: #fff; border-color: #111; }`);
  }

  filterRules.push('#filter-all:checked ~ .filter-bar label[for="filter-all"] { background: #111; color: #fff; border-color: #111; }');

  const LOFI_CSS = `
<style>
/* === LO-FI WIREFRAME RESET === */
*, *::before, *::after {
  color: #333 !important;
  font-family: system-ui, sans-serif !important;
  text-shadow: none !important;
  -webkit-text-fill-color: unset !important;
}
/* Backgrounds: all sections/wrappers → light grey */
html, body, section, header, footer, main, article, aside, nav,
div, figure, blockquote, form, fieldset {
  background-color: #f5f5f5 !important;
  background-image: none !important;
  box-shadow: none !important;
}
/* Cards, badges, feature boxes, step circles → slightly darker grey */
.card, .badge, .tier, .col, .feature, .step,
[class*="card"], [class*="badge"], [class*="tier"],
[class*="feature"], [class*="step"], [class*="item"],
[class*="block__col"], [class*="__card"], [class*="__item"] {
  background-color: #e8e8e8 !important;
  background-image: none !important;
}
/* Images and photo slots → grey placeholder */
img {
  background: #d0d0d0 !important;
  opacity: 0.6 !important;
  filter: grayscale(100%) !important;
}
/* SVG icons → grey */
svg, svg * {
  fill: #aaa !important;
  stroke: #aaa !important;
  color: #aaa !important;
}
/* Buttons and CTAs */
a, button, .btn, .cta,
[class*="btn"], [class*="cta"], [class*="button"], [class*="__link"] {
  background-color: #999 !important;
  background-image: none !important;
  color: #fff !important;
  border-color: #999 !important;
}
/* Borders → subtle grey */
* {
  border-color: #d0d0d0 !important;
  outline-color: #d0d0d0 !important;
}
/* Gradients and pseudo-elements */
*::before, *::after {
  background-image: none !important;
  background-color: transparent !important;
}
</style>
`;

  // Build cards HTML
  const cardsParts = [];

  for (const b of blocks) {
    const blockId = b.id;
    const cat = b.category || 'unknown';
    const blockPath = path.join(libPath, b.path || `${cat}/${blockId}/`);
    const metaPath = path.join(blockPath, 'meta.yaml');
    const templatePath = path.join(blockPath, 'assets', 'template.html');

    let meta = {};
    if (fs.existsSync(metaPath)) {
      const metaText = fs.readFileSync(metaPath, 'utf-8');
      meta = parseYaml(metaText) || {};
    }

    const displayName = htmlAttr(meta.display_name_ru || blockId);
    const layoutPattern = htmlAttr(meta.layout_pattern || b.layout_pattern || '');
    const useCases = meta.use_cases || b.use_cases || [];
    const source = meta.source || b.source || 'manual';
    const recommendedStyles = meta.recommended_styles_ru || [];

    // Read template content
    let tmplContent = '';

    if (fs.existsSync(templatePath)) {
      let raw = fs.readFileSync(templatePath, 'utf-8');
      const rawStripped = raw.trim();

      if (rawStripped.startsWith('<!--') && rawStripped.endsWith('-->')) {
        // It's just a comment
        const commentText = rawStripped.slice(4, -3).trim();
        tmplContent = `<!DOCTYPE html>
<html lang='ru'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>${htmlAttr(blockId)}</title>
<style>body{margin:0;padding:20px;font-family:system-ui,sans-serif;background:#f5f5f5}</style>
</head><body>
<section style='background:#e8e8e8;padding:40px;border-radius:8px;text-align:center;'>
<p style='color:#666;font-size:14px;'>${htmlAttr(commentText)}</p>
</section>
${LOFI_CSS}
</body></html>`;
      } else if (!rawStripped.startsWith('<!') && !rawStripped.startsWith('<html')) {
        // It's a fragment
        tmplContent = `<!DOCTYPE html>
<html lang='ru'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>${htmlAttr(blockId)}</title>
<style>body{margin:0;padding:20px;font-family:system-ui,sans-serif;background:#f5f5f5}
.lp-{margin:0}</style>
</head><body>
${raw}
${LOFI_CSS}
</body></html>`;
      } else {
        // Full HTML document
        if (raw.includes('</body>')) {
          tmplContent = raw.replace('</body>', LOFI_CSS + '</body>');
        } else if (raw.includes('</html>')) {
          tmplContent = raw.replace('</html>', LOFI_CSS + '</html>');
        } else {
          tmplContent = raw + LOFI_CSS;
        }
      }
    } else {
      tmplContent = `<!DOCTYPE html><html><head><meta charset='UTF-8'><title>${htmlAttr(blockId)}</title>
<style>body{display:flex;align-items:center;justify-content:center;height:100%;color:#999;
font-size:12px;font-family:sans-serif;}</style></head>
<body>template.html not found at ${htmlAttr(templatePath)}</body></html>`;
    }

    // Build use case badges
    const ucBadges = useCases
      .map(uc => `<span class="uc-badge">${htmlAttr(uc)}</span>`)
      .join(' ');

    // Source badge
    let sourceBadge = '';
    if (source === 'opendesign') {
      sourceBadge = '<span class="source-badge od-badge">OpenDesign</span>';
    }

    // Style tags
    let styleTags = '';
    if (recommendedStyles.length > 0) {
      styleTags = recommendedStyles.slice(0, 2)
        .map(s => `<span class="style-tag">${htmlAttr(s.slice(0, 20))}</span>`)
        .join(' ');
    }

    // Escape template content for srcdoc attribute
    const srcdocEscaped = htmlAttr(tmplContent);

    const iframeHtml = `<div class="card-thumb">
<div class="thumb-scaler">
<iframe sandbox srcdoc="${srcdocEscaped}"
title="${htmlAttr(blockId)}"
loading="lazy"></iframe>
</div>
</div>`;

    const stylesDiv = styleTags ? `<div class="card-styles">${styleTags}</div>` : '';

    // File URL for local access
    const absTemplatePath = path.resolve(templatePath);
    const fileUrl = 'file:///' + absTemplatePath.replace(/\\/g, '/');
    const openHref = htmlAttr(fileUrl);

    const layoutPatternHtml = layoutPattern
      ? `<span class="card-layout-pattern">layout: ${layoutPattern}</span>`
      : '';

    const card = `<article class="gallery-card" data-cat="${htmlAttr(cat)}" data-id="${htmlAttr(blockId)}">
${iframeHtml}
<div class="card-info">
<div class="card-name">${displayName}</div>
<div class="card-meta">
<span class="card-cat">${htmlAttr(catLabelsRu[cat] || cat)}</span>
${sourceBadge}
${layoutPatternHtml}
</div>
<div class="card-uc">${ucBadges}</div>
${stylesDiv}
<div class="card-id">${htmlAttr(blockId)}</div>
</div>
<a class="card-open-btn" href="${openHref}" target="_blank">Открыть</a>
</article>`;

    cardsParts.push(card);
  }

  // Build filter buttons
  const filterRadios = ['<input type="radio" id="filter-all" name="gallery-filter" checked hidden>'];
  const filterLabels = [`<label for="filter-all" class="filter-btn active">Все блоки <span class="filter-count">${blocks.length}</span></label>`];

  for (const cat of categories) {
    const safeCat = cat.replace(/-/g, '_');
    filterRadios.push(`<input type="radio" id="filter-${safeCat}" name="gallery-filter" hidden>`);
    filterLabels.push(
      `<label for="filter-${safeCat}" class="filter-btn">` +
      `${htmlAttr(catLabelsRu[cat] || cat)} ` +
      `<span class="filter-count">${catCounts[cat] || 0}</span>` +
      `</label>`
    );
  }

  const statsByCat = Object.entries(catCounts)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([cat, cnt]) => `${catLabelsRu[cat] || cat}: ${cnt}`)
    .join(', ');

  const htmlOut = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Block Library Gallery — ${blocks.length} блоков</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #f0f0f0; color: #111; }

  .gallery-header { background: #111; color: #fff; padding: 20px 28px; }
  .gallery-header h1 { font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }
  .gallery-stats { font-size: 13px; color: #aaa; }

  /* CSS-only filter: radios control display */
  ${filterRules.join('\n  ')}

  .filter-bar { display: flex; gap: 8px; flex-wrap: wrap; padding: 16px 24px; background: #fff; border-bottom: 1px solid #e0e0e0; position: sticky; top: 0; z-index: 10; }
  .filter-btn { padding: 7px 14px; border: 1.5px solid #ccc; border-radius: 20px; cursor: pointer; font-size: 13px; font-weight: 500; color: #444; transition: all .15s; user-select: none; }
  .filter-btn:hover { border-color: #888; color: #111; }
  .filter-count { font-size: 11px; color: #888; margin-left: 2px; }

  .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 24px; }

  .gallery-card { display: flex; flex-direction: column; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .2s, box-shadow .2s; }
  .gallery-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }

  .card-thumb { width: 100%; height: 200px; overflow: hidden; background: #e8e8e8; position: relative; }
  .thumb-scaler { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; }
  .thumb-scaler iframe {
    width: 1280px;
    height: 800px;
    border: none;
    transform: scale(0.234375);  /* 300/1280 */
    transform-origin: top left;
    pointer-events: none;
  }

  .card-info { padding: 12px 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
  .card-name { font-size: 14px; font-weight: 600; line-height: 1.3; }
  .card-meta { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
  .card-cat { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: #f0f0f0; color: #555; text-transform: uppercase; letter-spacing: .04em; }
  .source-badge { font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 10px; }
  .od-badge { background: #e8f4fd; color: #0066cc; }
  .card-uc { display: flex; gap: 4px; flex-wrap: wrap; }
  .uc-badge { font-size: 10px; padding: 2px 6px; border-radius: 6px; background: #f8f0ff; color: #7c3aed; }
  .card-styles { display: flex; gap: 4px; flex-wrap: wrap; }
  .style-tag { font-size: 10px; padding: 2px 6px; border-radius: 6px; background: #fff7ed; color: #c2410c; }
  .card-id { font-size: 10px; color: #999; font-family: monospace; margin-top: 2px; }
  .card-layout-pattern { font-size: 10px; color: #777; font-family: monospace; background: #f0f0f0; padding: 1px 6px; border-radius: 6px; }
  .card-open-btn { display: block; text-align: center; padding: 10px; background: #f5f5f5; color: #333; text-decoration: none; font-size: 13px; font-weight: 500; border-top: 1px solid #eee; transition: background .15s; }
  .card-open-btn:hover { background: #111; color: #fff; }
</style>
</head>
<body>

<header class="gallery-header">
  <h1>📚 Block Library Gallery — ${blocks.length} блоков</h1>
  <div class="gallery-stats">${statsByCat}</div>
</header>

${filterRadios.join('')}
<div class="filter-bar">
  ${filterLabels.join('')}
</div>

<div class="gallery-grid">
  ${cardsParts.join('')}
</div>

</body>
</html>`;

  // Create output directory if needed
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, htmlOut, 'utf-8');
  console.log(`OK: gallery rendered at ${outputPath} (${blocks.length} blocks)`);
}

main();
