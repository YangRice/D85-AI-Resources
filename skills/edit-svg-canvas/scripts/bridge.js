/* Method Draw adapter. Upstream source remains in the verified cache. */
(async function () {
  'use strict';
  const bar = document.createElement('div');
  bar.id = 'svg-edit-handoff';
  bar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:100000;min-height:42px;background:#16354b;color:white;display:flex;align-items:center;justify-content:flex-end;gap:16px;padding:6px 18px;font:14px system-ui';
  const message = document.createElement('span');
  message.setAttribute('role', 'status');
  message.textContent = 'Opening your design… / 正在開啟設計…';
  const finish = document.createElement('button');
  finish.id = 'save-and-finish';
  finish.textContent = 'Save and finish / 儲存並完成';
  finish.disabled = true;
  finish.style.cssText = 'padding:9px 16px;background:#fff;color:#16354b;border:0;border-radius:5px;font:600 14px system-ui;cursor:pointer';
  bar.append(message, finish);
  document.body.append(bar);
  const spacing = document.createElement('style');
  spacing.textContent = '#menu_bar{top:54px!important} #workarea{top:100px!important} #tools_left{top:102px!important} #panels{top:102px!important} #rulers{top:90px!important}';
  document.head.append(spacing);
  let baseline;
  let finished = false;
  let embeddedFonts = '';
  const imageAttributes = new Map();
  const fingerprint = doc => {
    const images = [...doc.querySelectorAll('image')].map(n => n.getAttribute('href') || n.getAttributeNS('http://www.w3.org/1999/xlink', 'href')).sort();
    // Method Draw re-serializes multi-line <text> children with its own
    // indentation, and the source may join <tspan> lines without any space.
    // Compare the actual characters so indentation alone is not a mismatch.
    const textValue = node => {
      const children = [...node.childNodes];
      const hasElements = children.some(child => child.nodeType === 1);
      return (hasElements
        ? children.map(child => child.nodeType === 3 && !child.nodeValue.trim() ? '' : child.textContent).join('')
        : node.textContent
      ).replace(/\u00a0/g, ' ');
    };
    // Method Draw may flatten line tspans and add indentation whitespace;
    // compare glyph content here. Literal spaces are separately marked with
    // xml:space in the normalized text runs and covered by the browser regression.
    const texts = [...doc.querySelectorAll('text')].map(n => textValue(n).replace(/\s+/g, '')).sort();
    return JSON.stringify({images, texts});
  };
  const parse = text => new DOMParser().parseFromString(text, 'image/svg+xml');
  // Method Draw's sanitizer whitelist rejects `letter-spacing` on <text>, so the
  // import fails closed even though the appearance is reproducible. <tspan>
  // accepts `dx`, therefore letter-spacing is converted to one dx per glyph,
  // keeping the line editable as text (each glyph stays a real character).
  // A middle-anchored chunk is centred on its advance width; since dx extends
  // that advance, the pen x moves left by half of the total added tracking and
  // the anchor switches to start. End/start anchors need no correction.
  const normalizeLetterSpacing = doc => {
    let converted = 0;
    for (const node of doc.querySelectorAll('text')) {
      const styleAttr = node.getAttribute('style') || '';
      let raw = node.getAttribute('letter-spacing');
      if (raw == null) {
        const m = styleAttr.match(/(?:^|;)\s*letter-spacing\s*:\s*([-+0-9.]+)\s*(?:px)?\s*(?:;|$)/i);
        if (m) raw = m[1];
      }
      if (raw == null) continue;
      const value = String(raw).trim();
      const valueMatch = value.match(/^([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*(?:px)?$/i);
      if (!valueMatch) throw new Error('Unsupported letter-spacing value; use a unitless or px value');
      const amount = Number(valueMatch[1]);
      node.removeAttribute('letter-spacing');
      if (styleAttr) {
        const cleaned = styleAttr.replace(/(?:^|;)\s*letter-spacing\s*:[^;]*/gi, '').replace(/^;+|;+$/g, '');
        if (cleaned) node.setAttribute('style', cleaned); else node.removeAttribute('style');
      }
      if (!isFinite(amount) || amount === 0) continue;

      const anchor = () => (node.getAttribute('text-anchor') || 'start').toLowerCase();
      const shiftFor = text => (anchor() === 'middle' && text.length > 1 ? -(text.length - 1) * amount / 2 : 0);
      const wrap = (run, text) => {
        run.textContent = '';
        [...text].forEach((ch, i) => {
          const tspan = doc.createElementNS('http://www.w3.org/2000/svg', 'tspan');
          if (i) tspan.setAttribute('dx', String(amount));
          if (/\s/.test(ch)) tspan.setAttribute('xml:space', 'preserve');
          // Mark whitespace explicitly. Method Draw may normalize the
          // whitespace-only text during export, but retains this preservation
          // marker while the text remains editable in the canvas.
          tspan.textContent = ch === ' ' ? '\u00a0' : ch;
          run.append(tspan);
        });
      };
      const shiftX = (target, shift) => {
        if (!shift) return;
        const base = parseFloat(target.getAttribute('x') ?? node.getAttribute('x') ?? '0') || 0;
        target.setAttribute('x', String(Math.round((base + shift) * 10) / 10));
      };

      const lines = [...node.querySelectorAll('tspan')].filter(t => !t.querySelector('tspan'));
      if (lines.length) {
        for (const line of lines) {
          const text = line.textContent;
          if (!text) continue;
          shiftX(line, shiftFor(text));
          wrap(line, text);
        }
      } else {
        const text = node.textContent;
        if (text) {
          shiftX(node, shiftFor(text));
          wrap(node, text);
        }
      }
      if (anchor() === 'middle') node.setAttribute('text-anchor', 'start');
      converted++;
    }
    return converted;
  };
  const current = () => {
    const doc = parse(svgCanvas.getSvgString());
    for (const image of doc.querySelectorAll('image')) {
      for (const [name, value] of imageAttributes.get(image.id) || []) image.setAttribute(name, value);
    }
    if (embeddedFonts) {
      const style = doc.createElementNS('http://www.w3.org/2000/svg', 'style');
      style.textContent = embeddedFonts;
      doc.documentElement.prepend(style);
    }
    return new XMLSerializer().serializeToString(doc);
  };
  try {
    const existing = await (await fetch('session')).json();
    if (existing.state === 'complete') {
      message.textContent = 'Saved / 已儲存：' + existing.saved_path + ' · Return to your assistant / 請返回對話繼續';
      finished = true;
      return;
    }
    const response = await fetch('input.svg');
    if (!response.ok) throw new Error('Cannot read the design');
    const original = await response.text();
    const originalDoc = parse(original);
    const workingDoc = parse(original);
    // Unsupported-but-lossless styling is normalized before the whitelist check
    // below (which stays fail-closed for everything else).
    const letterSpacingConverted = normalizeLetterSpacing(workingDoc);
    if (letterSpacingConverted) {
      console.info(`bridge: letter-spacing normalized to tspan dx on ${letterSpacingConverted} text node(s)`);
    }
    // Fail closed before upstream sanitization can discard styling. Use the
    // pinned editor's own per-element attribute support rather than maintaining
    // a second list. Inline CSS is normalized to presentation attributes only
    // for simple, supported declarations. Stylesheets other than @font-face
    // are rejected below: their cascade cannot be flattened reliably here.
    const supported = svgedit.sanitize.svgWhiteList();
    // CSS geometry/transform grammars differ from SVG attributes (px/deg,
    // transform-origin, percentages). Do not treat attribute support alone as
    // permission to flatten them.
    const presentationCSS = new Set(('fill fill-opacity fill-rule clip-rule opacity stroke stroke-width stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity font-family font-size font-style font-weight text-anchor stop-color stop-opacity image-rendering clip-path mask filter display shape-rendering').split(' '));
    for (const node of [workingDoc.documentElement, ...workingDoc.querySelectorAll('*')].filter((n, i, all) => all.indexOf(n) === i)) {
      if (!Object.hasOwn(supported, node.localName)) throw new Error(`Unsupported SVG element ${node.localName}`);
      const allowed = supported[node.localName];
      for (const attr of [...node.attributes]) {
        if (attr.name.startsWith('aria-') || attr.name === 'role' || attr.name === 'style' || attr.namespaceURI === 'http://www.w3.org/2000/xmlns/' ||
            (node.localName === 'image' && ['image-rendering', 'preserveAspectRatio'].includes(attr.name))) continue;
        if (!allowed.includes(attr.name)) {
          throw new Error(`Unsupported SVG attribute ${attr.name} on ${node.localName}; import stopped to preserve appearance`);
        }
      }
      if (!node.hasAttribute('style')) continue;
      const css = node.getAttribute('style');
      if (css.includes('/*') || css.includes('*/')) throw new Error('Unsupported inline CSS comments; import stopped to preserve appearance');
      for (const declaration of css.split(';')) {
        if (!declaration.trim()) continue;
        const match = declaration.match(/^\s*([a-zA-Z-]+)\s*:\s*([^{};]+?)\s*$/);
        if (!match || /!|var\s*\(|(?:inherit|initial|unset|revert)\b/i.test(match[2])) {
          throw new Error('Unsupported inline CSS syntax; import stopped to preserve appearance');
        }
        const property = match[1].toLowerCase(), value = match[2];
        if (!presentationCSS.has(property) || (!allowed.includes(property) && !(node.localName === 'image' && property === 'image-rendering'))) {
          throw new Error(`Unsupported inline CSS property ${property} on ${node.localName}; import stopped to preserve appearance`);
        }
        // Reject declarations the browser itself cannot interpret as CSS.
        if (!CSS.supports(property, value)) throw new Error(`Unsupported CSS value for ${property}`);
        node.setAttribute(property, value);
      }
      node.removeAttribute('style');
    }
    // Keep image-only presentation attributes upstream does not retain. IDs
    // distinguish repeated copies of the same image with different rendering.
    const usedIds = new Set([...workingDoc.querySelectorAll('[id]')].map(n => n.id));
    let imageIndex = 0;
    for (const image of workingDoc.querySelectorAll('image')) {
      if (!image.id) {
        let id;
        do { id = `svg-edit-image-${++imageIndex}`; } while (usedIds.has(id));
        image.id = id;
        usedIds.add(id);
      }
      imageAttributes.set(image.id, ['image-rendering', 'preserveAspectRatio']
        .filter(name => image.hasAttribute(name)).map(name => [name, image.getAttribute(name)]));
    }
    // Upstream's transform normalizer can drop chained translate/scale lists.
    // Consolidate them with the browser's native SVG implementation first.
    for (const node of workingDoc.querySelectorAll('[transform]')) {
      if (node.transform?.baseVal.numberOfItems) {
        const matrix = node.transform.baseVal.consolidate().matrix;
        node.setAttribute('transform', `matrix(${matrix.a} ${matrix.b} ${matrix.c} ${matrix.d} ${matrix.e} ${matrix.f})`);
      }
    }
    // Upstream styleToAttr treats @font-face as a selector and throws. Keep
    // font declarations in the adapter, apply them to the editor, and restore
    // them verbatim into every exported SVG.
    for (const style of workingDoc.querySelectorAll('style')) {
      style.textContent = style.textContent.replace(/@font-face\s*\{[^}]*\}/gi, rule => {
        embeddedFonts += rule + '\n';
        return '';
      });
      if (style.textContent.trim()) throw new Error('Unsupported SVG stylesheet rules; use supported presentation attributes or a different canvas');
      style.remove();
    }
    if (svgCanvas.setSvgString(new XMLSerializer().serializeToString(workingDoc)) === false) throw new Error('Method Draw cannot open this SVG');
    for (const image of document.querySelectorAll('#svgcontent image')) {
      for (const [name, value] of imageAttributes.get(image.id) || []) {
        image.setAttribute(name, value);
        if (name === 'image-rendering') image.style.imageRendering = value;
      }
    }
    editor.canvas.update(true);
    // Preserve embedded @font-face declarations for both the canvas and export.
    const liveStyle = document.createElement('style');
    liveStyle.textContent = embeddedFonts;
    document.head.append(liveStyle);
    await document.fonts.ready;
    const area = document.getElementById('workarea').getBoundingClientRect();
    const resolution = svgCanvas.getResolution();
    svgCanvas.setZoom(Math.min(area.width / resolution.w, area.height / resolution.h) * 0.85);
    editor.canvas.update(true);
    const imported = parse(current());
    if (fingerprint(originalDoc) !== fingerprint(imported)) {
      throw new Error('Import changed text or image content; keep the original and report this incompatibility');
    }
    baseline = current();
    // Upstream only listens to keyup, missing paste/IME/input changes, and its
    // Enter handler assumes an active inline cursor even for sidebar editing.
    const textInput = document.getElementById('text');
    $(textInput).off('keydown keyup');
    textInput.addEventListener('input', () => {
      const selected = svgCanvas.getSelectedElems().filter(Boolean);
      if (selected.length === 1 && selected[0].tagName === 'text') {
        const target = selected[0].querySelector('textPath') || selected[0];
        svgCanvas.changeSelectedAttribute('#text', textInput.value, [target]);
        svgCanvas.selectorManager.requestSelector(selected[0]).resize();
      }
    });
    textInput.addEventListener('keydown', event => {
      event.stopPropagation();
      if (event.isComposing || event.keyCode === 229) return;
      if (event.key === 'Enter' || event.key === 'Escape') {
        event.preventDefault();
        if (svgCanvas.getMode() === 'textedit') svgCanvas.textActions.toSelectMode();
        textInput.blur();
      }
    });
    textInput.addEventListener('keyup', event => event.stopPropagation());
    finish.disabled = false;
    message.textContent = 'Edit text or drag items. / 點選文字修改，拖動素材調整位置。';
    document.body.dataset.svgEditorReady = 'true';
  } catch (error) {
    message.textContent = 'Unable to edit / 無法編輯：' + error.message;
    document.body.dataset.svgEditorError = error.message;
  }
  finish.addEventListener('click', async () => {
    finish.disabled = true;
    document.getElementById('method-draw').inert = true;
    message.textContent = 'Saving… / 正在儲存…';
    try {
      document.activeElement?.blur();
      svgCanvas.clearSelection();
      const svg = current();
      const response = await fetch('finish', {method: 'POST', headers: {'Content-Type': 'image/svg+xml'}, body: svg});
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Save failed');
      finished = true;
      message.textContent = 'Saved / 已儲存：' + result.saved_path + ' · Return to your assistant and say continue / 請返回對話說「繼續」';
      document.body.dataset.svgEditorFinished = 'true';
      document.getElementById('method-draw').style.pointerEvents = 'none';
      document.getElementById('method-draw').inert = true;
    } catch (error) {
      message.textContent = 'Not saved / 未儲存：' + error.message + ' · Retry / 請重試';
      document.getElementById('method-draw').inert = false;
      finish.disabled = false;
    }
  });
  window.addEventListener('beforeunload', event => {
    if (!finished && baseline && current() !== baseline) {
      event.preventDefault();
      event.returnValue = '';
    }
  });
})();
