const $ = id => document.getElementById(id);
let files = [], config, downloadUrl, busy = false;
function clearResult() { $('result').hidden = true; $('empty').hidden = false; if(downloadUrl) URL.revokeObjectURL(downloadUrl); downloadUrl = null; }
function status(message, type = '') { $('status').textContent = message; $('status').className = type ? `status-${type}` : ''; }
function setFiles(next) {
  if(busy) return;
  files = Array.from(next); clearResult(); status(''); $('file-list').replaceChildren();
  files.forEach(file => { const line=document.createElement('div'); line.textContent=`${file.name} · ${(file.size/1024).toFixed(1)} KB`; $('file-list').append(line); });
  $('convert').disabled = !files.length || !config;
}
function downloadBlob(blob, name) { const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); }
function encode(file) { return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve({name:file.name,data:reader.result.split(',')[1]});reader.onerror=reject;reader.readAsDataURL(file);}); }
function invalidate() {clearResult();status('模板已修改，请重新转换。');try{const t=JSON.parse($('template').value);$('template-name').textContent=t.name||'自定义模板';document.querySelector('.template-summary p').textContent=(t.columns||[]).map(c=>c.name).join(' · ');}catch{}}
$('pdfs').addEventListener('change', event=>setFiles(event.target.files));
['dragenter','dragover'].forEach(name=>$('dropzone').addEventListener(name,event=>{event.preventDefault();$('dropzone').classList.add('drag');}));
['dragleave','drop'].forEach(name=>$('dropzone').addEventListener(name,event=>{event.preventDefault();$('dropzone').classList.remove('drag');}));
$('dropzone').addEventListener('drop',event=>setFiles(event.dataTransfer.files));
$('demo').onclick=async()=>{try{const r=await fetch('/sample.pdf');if(!r.ok)throw Error('示例加载失败');setFiles([new File([await r.blob()],'demo-quotation.pdf',{type:'application/pdf'})]);}catch(e){status(e.message,'error');}};
$('reset').onclick=()=>{$('template').value=JSON.stringify(config.template,null,2);invalidate();};
$('template').addEventListener('input',invalidate);
$('save-template').onclick=()=>{try{const data=JSON.parse($('template').value);downloadBlob(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),'tablebridge-template.json');}catch(e){status('模板 JSON 格式错误：'+e.message,'error');}};
$('template-file').onchange=async event=>{if(event.target.files[0]){$('template').value=await event.target.files[0].text();invalidate();}};
$('convert').onclick=async()=>{
  clearResult();busy=true;['convert','demo','pdfs','template','reset','template-file'].forEach(id=>$(id).disabled=true);status('正在读取、校验和生成 Excel…','loading');
  try {
    if(files.length>10||files.some(f=>f.size>10*1024*1024)||files.reduce((n,f)=>n+f.size,0)>20*1024*1024)throw Error('最多10个文件，单个不超过10 MB，合计不超过20 MB。');
    const template=JSON.parse($('template').value);
    const r=await fetch('/api/convert',{method:'POST',headers:{'Content-Type':'application/json','X-TableBridge-Token':config.token},body:JSON.stringify({template,files:await Promise.all(files.map(encode))})});
    const data=await r.json();if(!r.ok)throw Error(data.error||'转换失败');
    $('row-count').textContent=data.row_count;$('page-count').textContent=data.pages;$('file-count').textContent=data.files;
    $('thead').replaceChildren();$('tbody').replaceChildren();$('warnings').replaceChildren();
    const head=document.createElement('tr');data.headers.forEach(h=>{const th=document.createElement('th');th.textContent=h;head.append(th);});$('thead').append(head);
    data.rows.forEach(row=>{const tr=document.createElement('tr');data.headers.forEach(h=>{const td=document.createElement('td');td.textContent=row[h]??'';tr.append(td);});$('tbody').append(tr);});
    data.warnings.forEach(w=>{const p=document.createElement('p');p.className='warning';p.textContent=w;$('warnings').append(p);});
    $('preview-note').textContent=`预览前 ${Math.min(100,data.row_count)} 行，Excel 包含全部 ${data.row_count} 行。`;
    const bytes=Uint8Array.from(atob(data.xlsx),c=>c.charCodeAt(0));downloadUrl=URL.createObjectURL(new Blob([bytes],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));$('download').href=downloadUrl;
    $('empty').hidden=true;$('result').hidden=false;status(data.warnings.length?'已转换，请核对下方金额差异。':'版式检查通过。请核对预览与原始 PDF。','ok');
  } catch(e) {status(e.message,'error');}
  finally {busy=false;['demo','pdfs','template','reset','template-file'].forEach(id=>$(id).disabled=false);$('convert').disabled=!files.length||!config;}
};
fetch('/api/config').then(r=>r.json()).then(data=>{config=data;$('template').value=JSON.stringify(data.template,null,2);$('template-name').textContent=data.template.name;$('convert').disabled=!files.length;}).catch(()=>status('无法连接本机程序。请重新启动 app.py。','error'));
