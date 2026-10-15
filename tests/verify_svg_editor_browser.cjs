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
 const fixture=path.join(root,'output/svg-editor-qa/simple.svg');
 fs.mkdirSync(path.dirname(fixture),{recursive:true});
 fs.writeFileSync(fixture,'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="#e7eef5"/><text id="headline" x="30" y="80" font-family="sans-serif" font-size="32">Hello design</text><rect id="material" x="80" y="140" width="100" height="90" fill="#bb3254"/></svg>');
 const cases=[['simple',fixture]];if(process.env.SVG_EDITOR_POSTER)cases.push(['poster',process.env.SVG_EDITOR_POSTER]);
 for(const [kind,input] of cases){
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
  }finally{await page.close();run.process.kill('SIGINT')}
 }
 }finally{await browser.close();fs.writeFileSync(path.join(reportDir,'browser-results.json'),JSON.stringify(results,null,2))}
 console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e.stack);process.exit(1)});
