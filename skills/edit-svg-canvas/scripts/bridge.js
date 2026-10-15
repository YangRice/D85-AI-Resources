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
    const texts = [...doc.querySelectorAll('text')].map(n => n.textContent).sort();
    return JSON.stringify({images, texts});
  };
  const parse = text => new DOMParser().parseFromString(text, 'image/svg+xml');
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
