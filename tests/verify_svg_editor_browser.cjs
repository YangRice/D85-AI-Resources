// Optional browser regression: NODE_PATH must provide playwright; SVG_EDITOR_BROWSER selects an installed Chromium.
// SVG_EDITOR_POSTER optionally adds the original bilingual poster integration fixture.
const {chromium}=require('playwright');
const {spawn}=require('child_process');const sharp=require('sharp');const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..');
const reportDir=path.join(root,'output/svg-editor-qa/browser');fs.mkdirSync(reportDir,{recursive:true});
async function start(input,out){return await new Promise((resolve,reject)=>{
 const p=spawn('python3',[process.env.SVG_EDITOR_SCRIPT || path.join(root,'skills/edit-svg-canvas/scripts/edit_svg.py'),'launch',input,'--output-dir',out,'--cache-dir',process.env.SVG_EDITOR_CACHE || path.join(root,'.cache/method-draw')]);let stdout='',stderr='';
 const timer=setTimeout(()=>{p.kill();reject(new Error('Launcher timeout '+stderr))},60000);
 p.stderr.on('data',d=>stderr+=d);p.on('exit',code=>{if(!stdout.includes('\n'))reject(new Error('Launcher exit '+code+':'+stderr))});
 p.stdout.on('data',d=>{stdout+=d;if(stdout.includes('\n')){clearTimeout(timer);resolve({process:p,session:JSON.parse(stdout.split('\n')[0])})}});
});}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.SVG_EDITOR_BROWSER || undefined,args:['--disable-background-networking']});const results=[];
 try{
 // Numeric letter-spacing is normalized to editable tspan dx values before
 // Method Draw's sanitizer sees it. Verify both supported spellings survive
 // import and save without leaving the unsupported property behind.
 for (const [kind,markup] of [
  ['inline-spacing','<text x="20" y="70" style="letter-spacing:12px">SCAN TO JOIN US</text>'],
  ['attribute-spacing','<text x="20" y="70" letter-spacing="12">SCAN TO JOIN US</text>'],
 ]) {
  const input=path.join(reportDir,kind+'.svg');
  const original='<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">'+markup+'</svg>';
  fs.writeFileSync(input,original);
  console.log('Checking',kind);
  const run=await start(input,path.join(reportDir,kind));const page=await browser.newPage();
  try {
   await page.goto(run.session.editor_url);
   await page.waitForSelector('body[data-svg-editor-ready="true"]',{timeout:30000});
   if(await page.locator('body').getAttribute('data-svg-editor-error'))throw Error(kind+': safe spacing import failed');
   if((await page.locator('#svgcontent text').innerText())!=='SCAN TO JOIN US')throw Error(kind+': text content changed');
   await page.locator('#save-and-finish').click();
   await page.waitForSelector('body[data-svg-editor-finished="true"]',{timeout:30000});
   const completed=JSON.parse(fs.readFileSync(run.session.session_json,'utf8'));
   const saved=fs.readFileSync(completed.saved_path,'utf8');
   if(saved.includes('letter-spacing'))throw Error(kind+': unsupported property leaked into saved SVG');
   if(!saved.includes('dx="12"'))throw Error(kind+': spacing offsets missing from saved SVG');
   if(!saved.includes('xml:space="preserve"'))throw Error(kind+': literal spaces were not marked for preservation');
   if(crypto.createHash('sha256').update(saved).digest('hex')!==completed.saved_sha256)throw Error(kind+': hash mismatch');
   results.push({kind,passed:true,saved_path:completed.saved_path,sha256:completed.saved_sha256});
  }catch(error){const importError=await page.locator('body').getAttribute('data-svg-editor-error');throw new Error(error.message+(importError?' · Import error: '+importError:''));}finally{await page.close();run.process.kill('SIGINT')}
 }
 // Unsupported styling must fail before the canvas is enabled or a revision
 // can be saved. Stylesheet cascade and unsafe inline syntax remain rejected.
 for (const [kind,markup,property] of [
  ['stylesheet','<style>text {letter-spacing:12px}</style><text x="20" y="70">Spaced</text>','stylesheet'],
  ['css-transform','<text x="20" y="70" style="transform:translate(10px,20px)">Moved</text>','transform'],
  ['css-comments','<text x="20" y="70" style="fill:r/**/ed">Styled</text>','CSS comments'],
  ['important','<text x="20" y="70" style="fill:red!important">Styled</text>','inline CSS'],
  ['text-decoration','<text x="20" y="70" text-decoration="underline">Underlined</text>','text-decoration'],
 ]) {
  const input=path.join(reportDir,kind+'.svg');
  const original='<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">'+markup+'</svg>';
  fs.writeFileSync(input,original);
  console.log('Checking',kind);
  const run=await start(input,path.join(reportDir,kind));const page=await browser.newPage();
  try {
   await page.goto(run.session.editor_url);
   await page.waitForSelector('body[data-svg-editor-error]',{timeout:30000});
   const error=await page.locator('body').getAttribute('data-svg-editor-error');
   if(!error.includes(property))throw Error(kind+': wrong error '+error);
   if(await page.locator('#save-and-finish').isEnabled())throw Error(kind+': unsafe save enabled');
   if(await page.locator('body').getAttribute('data-svg-editor-ready'))throw Error(kind+': unsafe canvas marked ready');
   if(fs.readFileSync(input,'utf8')!==original)throw Error('Rejected source changed');
   if(JSON.parse(fs.readFileSync(run.session.session_json,'utf8')).state!=='editing')throw Error('Rejected import finished');
   results.push({kind,passed:true,rejected:true,error});
  } finally {await page.close();run.process.kill('SIGINT')}
 }
 const common=path.join(reportDir,'common.svg');
 fs.writeFileSync(common,`<svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520"><defs><linearGradient id="grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#114488"/><stop offset="1" stop-color="#e7b84b"/></linearGradient><clipPath id="clip"><circle cx="675" cy="125" r="70"/></clipPath></defs><rect width="800" height="520" fill="#f6f2e9"/><g transform="translate(75 70) rotate(-5 170 80)" opacity="0.92"><rect width="340" height="160" rx="18" fill="url(#grad)" stroke="#114488" stroke-width="6"/><text x="24" y="70" font-family="sans-serif" font-size="36" font-weight="700" fill="#fff">TRANSFORM</text></g><path d="M80 310 C180 245 280 375 380 310" fill="none" stroke="#bb3254" stroke-width="12" stroke-linecap="round" stroke-dasharray="18 10"/><circle cx="675" cy="125" r="98" fill="#bb3254" clip-path="url(#clip)"/><text x="470" y="300" font-family="sans-serif" font-size="30" fill="#114488"><tspan x="470" dy="0">LINE ONE</tspan><tspan x="470" dy="38">LINE TWO</tspan></text><rect x="470" y="350" width="220" height="90" fill="#e7b84b" fill-opacity="0.45" stroke="#114488" stroke-opacity="0.7" stroke-width="4"/><image x="720" y="360" width="50" height="50" href="data:image/png;base64,YWJj"/></svg>`);
 console.log('Checking common');
 const commonRun=await start(common,path.join(reportDir,'common'));const commonPage=await browser.newPage();
 try {
  await commonPage.goto(commonRun.session.editor_url);await commonPage.waitForSelector('body[data-svg-editor-ready="true"]',{timeout:30000});
  await commonPage.locator('#save-and-finish').click();await commonPage.waitForSelector('body[data-svg-editor-finished="true"]',{timeout:30000});
  const completed=JSON.parse(fs.readFileSync(commonRun.session.session_json,'utf8'));const saved=fs.readFileSync(completed.saved_path,'utf8');
  for (const marker of ['transform="matrix(', 'linearGradient', 'clip-path="url(#clip)"', 'stroke-dasharray', 'fill-opacity', 'stroke-opacity', '<tspan', '<image']) if(!saved.includes(marker)) throw Error('common: missing '+marker);
  if(crypto.createHash('sha256').update(saved).digest('hex')!==completed.saved_sha256)throw Error('common: hash mismatch');
  results.push({kind:'common',passed:true,saved_path:completed.saved_path,sha256:completed.saved_sha256});
 } finally {await commonPage.close();commonRun.process.kill('SIGINT')}
 const fixture=path.join(root,'output/svg-editor-qa/simple.svg');
 fs.mkdirSync(path.dirname(fixture),{recursive:true});
 fs.writeFileSync(fixture,'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="#e7eef5"/><text id="headline" x="30" y="80" font-family="sans-serif" font-size="32" style="fill:#114488;font-weight:700">Hello design</text><g fill-opacity="0.3" stroke-width="10"><rect id="explicit-default" x="250" y="140" width="100" height="90" fill="#ffcc00" style="fill-opacity:1;stroke-width:1"/></g><rect id="material" x="80" y="140" width="100" height="90" fill="#bb3254"/></svg>');
 const cases=[['simple',fixture]];if(process.env.SVG_EDITOR_POSTER)cases.push(['poster',process.env.SVG_EDITOR_POSTER]);
 for(const [kind,input] of cases){
  console.log('Checking',kind);
  const run=await start(input,path.join(reportDir,kind));const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('response',r=>{if(r.status()>=400)console.log('HTTP',r.status(),r.url())});page.on('requestfailed',r=>console.log('REQUEST FAILED',r.failure(),r.url()));page.on('pageerror',e=>errors.push(e.stack));
  try{
   await page.goto(run.session.editor_url);await page.waitForSelector('body[data-svg-editor-ready="true"]',{timeout:30000});
   if(kind==='poster'){
    await page.locator('#tm-layer-title-zh').dblclick();await page.getByText('AI 实战：',{exact:true}).click();
    await page.locator('#text').fill('AI 實戰：');await page.locator('#text').press('Enter');await page.keyboard.press('Escape');await page.keyboard.press('Escape');
    await page.locator('#tm-layer-title-en').dblclick();await page.getByText('DESIGN POSTERS',{exact:true}).click();
    await page.locator('#text').fill('DESIGN TOGETHER');await page.locator('#text').press('Enter');await page.keyboard.press('Escape');await page.keyboard.press('Escape');
    await page.locator('#tm-layer-portrait').click();const b=await page.locator('#tm-layer-portrait').boundingBox();
    await page.mouse.move(b.x+b.width/2,b.y+b.height/2);await page.mouse.down();await page.mouse.move(b.x+b.width/2-5,b.y+b.height/2+5,{steps:5});await page.mouse.up();
   }else{
    await page.locator('#headline').click();await page.locator('#text').fill('你好 Design');
    const ime=await page.locator('#text').evaluate(el=>{el.focus();const e=new KeyboardEvent('keydown',{key:'Enter',isComposing:true,bubbles:true,cancelable:true});el.dispatchEvent(e);return {prevented:e.defaultPrevented,focused:document.activeElement===el}});
    if(ime.prevented||!ime.focused)throw Error('IME candidate confirmation was intercepted');
    await page.locator('#text').press('Enter');
    await page.locator('#material').click();const b=await page.locator('#material').boundingBox();await page.mouse.move(b.x+40,b.y+40);await page.mouse.down();await page.mouse.move(b.x+55,b.y+50,{steps:5});await page.mouse.up();
   }
   await page.screenshot({path:path.join(reportDir,kind+'-editing.png')});await page.locator('#save-and-finish').click();
   await page.waitForSelector('body[data-svg-editor-finished="true"]',{timeout:30000});await page.screenshot({path:path.join(reportDir,kind+'-finished.png')});
   const completed=JSON.parse(fs.readFileSync(run.session.session_json,'utf8'));if(completed.state!=='complete')throw Error('Not complete');
   const saved=fs.readFileSync(completed.saved_path,'utf8');
   if(!saved.includes(kind==='poster'?'AI 實戰：':'你好 Design'))throw Error('Text edit missing');
   if(kind==='simple'){
    const style=await page.evaluate(()=>{const n=document.querySelector('#svgcontent #headline');return {fill:getComputedStyle(n).fill,weight:getComputedStyle(n).fontWeight}});
    const defaults=await page.evaluate(()=>{const n=document.querySelector('#svgcontent #explicit-default');return {opacity:getComputedStyle(n).fillOpacity,width:getComputedStyle(n).strokeWidth}});
    if(defaults.opacity!=='1'||defaults.width!=='1px')throw Error('Explicit inherited override lost '+JSON.stringify(defaults));
    if(style.fill!=='rgb(17, 68, 136)'||style.weight!=='700')throw Error('Supported inline style lost '+JSON.stringify(style));
    if(!saved.includes('fill="#114488"')||!saved.includes('font-weight="700"'))throw Error('Supported style missing from saved SVG');
   }
   if(crypto.createHash('sha256').update(saved).digest('hex')!==completed.saved_sha256)throw Error('Hash mismatch');
   const svgPage=await browser.newPage({viewport:kind==='poster'?{width:1600,height:2400}:{width:600,height:400}});
   for(const [label,svg] of [['source',fs.readFileSync(input,'utf8')],['edited',saved]]){
    await svgPage.setContent('<style>body{margin:0}svg{display:block}</style>'+svg.replace(/<\?xml[^>]*\?>/,''));
    await svgPage.evaluate(()=>document.fonts.ready);await svgPage.screenshot({path:path.join(reportDir,kind+'-'+label+'-render.png'),fullPage:true});
   }
   if(kind==='poster'){
    const sourcePNG=path.join(reportDir,'poster-source-render.png'),editedPNG=path.join(reportDir,'poster-edited-render.png');
    for(const region of [{left:785,top:1818,width:380,height:364},{left:1213,top:1849,width:320,height:320}]){
     const a=await sharp(sourcePNG).extract(region).raw().toBuffer();const b=await sharp(editedPNG).extract(region).raw().toBuffer();
     if(!a.equals(b))throw Error('Untouched QR pixels changed during import/save');
    }
   }
   await svgPage.close();await page.reload();await page.getByRole('status').filter({hasText:'Saved'}).waitFor();
   results.push({kind,passed:true,saved_path:completed.saved_path,sha256:completed.saved_sha256,errors});
   if(errors.length)throw Error('Browser errors '+errors.join(';'));
  }catch(error){const importError=await page.locator('body').getAttribute('data-svg-editor-error');throw new Error(error.message+(importError?' · Import error: '+importError:''));}finally{await page.close();run.process.kill('SIGINT')}
 }
 }finally{await browser.close();fs.writeFileSync(path.join(reportDir,'browser-results.json'),JSON.stringify(results,null,2))}
 console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e.stack);process.exit(1)});
