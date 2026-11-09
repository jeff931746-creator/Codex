let stopRequested=false;
let running=false;

const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function backgroundCall(type,payload={}){
  const result=await chrome.runtime.sendMessage({target:'background',type,...payload});
  if(result?.__error)throw Error(result.__error);
  return result;
}
async function saveState(patch){
  const current=await backgroundCall('collector-state-get');
  const next={...current,...patch,updatedAt:new Date().toISOString()};
  await backgroundCall('collector-state-set',{state:next});
  return next;
}

function readCurrentListingPage(){
  const config=globalThis.CBG_GAME_CONFIG||{};
  const server=globalThis.ServerInfo||{};
  const login=globalThis.LoginInfo||{};
  const pageUrl=new URL(location.href);
  const serverId=String(pageUrl.searchParams.get('s')||server.server_id||login.serverid||'');
  const sameLoginServer=String(login.serverid||'')===serverId;
  const serverName=(sameLoginServer?login.server_name:'')||server.server_name||login.server_name||'';
  const areaName=(sameLoginServer?login.area_name:'')||server.area_name||login.area_name||null;
  const queryRows=Array.isArray(globalThis.QueryResult)?globalThis.QueryResult:[];
  const found=new Map();
  const serverById=ident=>{
    const all=globalThis.server_data||{};
    for(const entry of Object.values(all)){
      const area=Array.isArray(entry?.[0])?entry[0][0]:'';
      const servers=Array.isArray(entry?.[1])?entry[1]:Object.values(entry?.[1]||{});
      const match=servers.find(item=>String(item?.[0])===String(ident));
      if(match)return {server_name:match[1]||'',area_name:area||null};
    }
    return {server_name:'',area_name:null};
  };
  const addInline=(order,equipDesc,node,row={})=>{
    if(!order||!equipDesc)return;
    let normalized=equipDesc;
    try{
      const decoded=typeof globalThis.parse_role_info==='function'
        ?globalThis.parse_role_info(equipDesc)
        :globalThis.js_eval(globalThis.lpc_2_js(globalThis.decode_desc(equipDesc)));
      if(decoded&&typeof decoded==='object')normalized=JSON.stringify(decoded);
    }catch(error){console.warn('角色内嵌字段解码失败',order,error)}
    const dataNode=node||document.querySelector(`[data_game_ordersn="${CSS.escape(order)}"],[data_ordersn="${CSS.escape(order)}"]`);
    const anchor=dataNode?.closest('a[href]')||dataNode?.closest('tr')?.querySelector('a[href]')||node?.closest('tr')?.querySelector('a[href]');
    let cursor=dataNode||node,rowText='';
    for(let depth=0;cursor&&depth<8;depth++,cursor=cursor.parentElement){rowText=cursor.innerText||rowText;if(/[¥￥]\s*[\d,.]+/.test(rowText))break}
    const displayPrice=Number((rowText.match(/[¥￥]\s*([\d,.]+)/)?.[1]||'').replaceAll(',',''))||null;
    const attrPrice=Number(dataNode?.getAttribute('data_price')||0);
    const rowPrice=Number(row.price||0)/100;
    const id=String(row.game_ordersn||dataNode?.getAttribute('data_whole_game_ordersn')||order);
    const itemServerId=String(dataNode?.getAttribute('data_serverid')||row.serverid||row.server_id||'');
    const mapped=serverById(itemServerId);
    const areaServer=rowText.match(/([^\s￥¥]+区)\s*[-—]\s*([^\s￥¥]+)/);
    const url=new URL(anchor?.href||`https://xyq.cbg.163.com/equip?s=${encodeURIComponent(itemServerId)}&eid=${encodeURIComponent(id)}`,location.href);
    found.set(id,{listing_id:id,url:url.href,equip_desc:normalized,price:displayPrice||attrPrice||rowPrice||null,
      server_id:itemServerId,server_name:row.server_name||row.servername||mapped.server_name||areaServer?.[2]||'',
      area_name:row.area_name||row.areaname||mapped.area_name||areaServer?.[1]||null});
  };
  document.querySelectorAll('[id^="other_info_"]').forEach(hidden=>{
    const order=hidden.id.slice('other_info_'.length);
    const row=queryRows.find(item=>String(item.game_ordersn||item.eid||'')===order)||{};
    addInline(order,(hidden.value||hidden.textContent||hidden.getAttribute('value')||'').trim(),hidden,row);
  });
  return {items:[...found.values()].slice(0,20),server_id:serverId,server_name:serverName,area_name:areaName,
    official_catalog:{school_skill:config.school_skill||{},life_skill:config.life_skill||{},
      ju_qing_skill:config.ju_qing_skill||{},ju_qing_skill_desc:config.ju_qing_skill_desc||{},
      equip_info:config.equip_info||{},pet_info:config.pet_info||{},rider_info:config.rider_info||{},
      clothes_info:config.clothes_info||{},xiangrui_info:config.xiangrui_info||{},
      pet_skill_desc:config.pet_skill_desc||{},zuoqi_skill_desc:config.zuoqi_skill_desc||{},
      pet_neidans:config.pet_neidans||{},neidan_desc:config.neidan_desc||{},
      pet_shipin_info:config.pet_shipin_info||{},xiangrui_skill:config.xiangrui_skill||{}}};
}

function clickNextListingPage(){
  const disabled=node=>node.matches?.('[disabled],.disabled,.disable,.off')||node.closest?.('.disabled,.disable,.off')||node.getAttribute?.('aria-disabled')==='true';
  const roots=[...document.querySelectorAll('nav,[class*="page"],[id*="page"],[class*="pager"],[id*="pager"]')];
  const pagers=roots.map(root=>{
    const controls=[...root.querySelectorAll('a,button,input[type="button"]')];
    const numbers=controls.map(node=>Number((node.textContent||node.value||'').trim())).filter(Number.isFinite);
    const current=root.querySelector('.current,.active,[aria-current="page"],.page_on,.on,em,strong');
    return {controls,numbers,currentNumber:Number((current?.textContent||'').trim())};
  }).filter(item=>item.numbers.length>=2&&Number.isFinite(item.currentNumber));
  const pager=pagers.sort((a,b)=>b.numbers.length-a.numbers.length)[0];
  if(!pager)return {clicked:false,reason:'未识别到带当前页码的分页栏'};
  let next=pager.controls.find(node=>!disabled(node)&&Number((node.textContent||node.value||'').trim())===pager.currentNumber+1);
  if(!next)next=pager.controls.find(node=>!disabled(node)&&/(?:下一页|下页|后页|›|»)/.test((node.textContent||node.value||node.title||'').trim()));
  if(!next)return {clicked:false,reason:`第 ${pager.currentNumber} 页后没有可用页码`};
  next.click();return {clicked:true,current:pager.currentNumber};
}

async function decodedHtml(response){
  const bytes=new Uint8Array(await response.arrayBuffer());
  const head=new TextDecoder('windows-1252').decode(bytes.slice(0,8192));
  const charset=(response.headers.get('content-type')?.match(/charset=([^;\s]+)/i)?.[1]||head.match(/charset\s*=\s*["']?([^\s"'/>;]+)/i)?.[1]||'utf-8').toLowerCase();
  return new TextDecoder(/^(?:gb2312|gbk|gb18030)$/.test(charset)?'gb18030':'utf-8').decode(bytes);
}

function detailBundle(html,item,page){
  const doc=new DOMParser().parseFromString(html,'text/html');
  const field=doc.querySelector('#equip_desc_value');
  const encoded=(field?.value||field?.textContent||field?.getAttribute('value')||'').trim();
  if(!encoded)throw Error('详情页未包含角色属性，可能需要重新登录或完成验证');
  if(!item.price)throw Error('列表卡片未识别到挂牌价');
  const url=new URL(item.url);let detailServer={};
  const serverMatch=html.match(/var\s+ServerInfo\s*=\s*(\{[\s\S]*?\})\s*;/);
  if(serverMatch){try{detailServer=JSON.parse(serverMatch[1])}catch{detailServer={}}}
  const decodeJsString=value=>{if(!value)return '';try{return JSON.parse(`"${value.replaceAll('"','\\"')}"`)}catch{return value}};
  if(!detailServer.server_id)detailServer.server_id=serverMatch?.[1]?.match(/["']?server_id["']?\s*:\s*["']?([^,"'}\s]+)/)?.[1];
  if(!detailServer.server_name)detailServer.server_name=decodeJsString(serverMatch?.[1]?.match(/["']?server_name["']?\s*:\s*["']([^"']*)["']/)?.[1]);
  if(!detailServer.area_name)detailServer.area_name=decodeJsString(serverMatch?.[1]?.match(/["']?area_name["']?\s*:\s*["']([^"']*)["']/)?.[1]);
  const visible=doc.body?.textContent?.match(/([\u4e00-\u9fffA-Za-z0-9]+区)\s*(?:[-—－]|->|→)\s*([^\s￥¥]+)/);
  const detailServerId=String(detailServer.server_id||item.server_id||url.searchParams.get('s')||page.server_id||'');
  const samePageServer=detailServerId===String(page.server_id||'');
  return {equip_desc:encoded,official_catalog:page.official_catalog,metadata:{listing_id:item.listing_id,
    server_id:detailServerId,server_name:item.server_name||(samePageServer?page.server_name:'')||detailServer.server_name||visible?.[2],
    area_name:item.area_name||(samePageServer?page.area_name:'')||detailServer.area_name||visible?.[1]||null,
    price:item.price,status_desc:'在售',source_url:item.url,response_time:new Date().toISOString()}};
}

async function api(path,body){
  const response=await fetch(`http://127.0.0.1:8765${path}`,{method:'POST',headers:{'Content-Type':'application/json','X-CBG-Extension':'sync-v1'},body:JSON.stringify(body)});
  const result=await response.json();if(!response.ok)throw Error(result.error||`本机接口失败：${response.status}`);return result;
}

async function gatherPages(tabId,maxPages){
  const first=await backgroundCall('collector-page-read',{tabId});
  if(!first?.items?.length)throw Error('当前页面没有发现角色搜索结果');
  const pages=[first],seen=new Set(first.items.map(item=>item.listing_id));
  while(pages.length<maxPages&&!stopRequested){
    await saveState({message:`正在读取列表第 ${pages.length+1}/${maxPages} 页…`});
    const turn=await backgroundCall('collector-page-next',{tabId});
    if(!turn?.clicked)break;
    let page=null;
    for(let retry=0;retry<5;retry++){
      await pause(retry?800:1400);
      const result=await backgroundCall('collector-page-read',{tabId});
      const items=result.items.filter(item=>!seen.has(item.listing_id));
      if(items.length){page={...result,items};break}
    }
    if(!page)break;
    page.items.forEach(item=>seen.add(item.listing_id));pages.push(page);
  }
  return pages.flatMap(page=>page.items.map(item=>({item,page})));
}

async function runCollection({tabId,maxPages,sourceUrl}){
  if(running)throw Error('已有采集任务正在运行');
  running=true;stopRequested=false;let succeeded=0,failed=0,inserted=0,overwritten=0,duplicates=0,sessionId=null,loginRequired=false,consecutiveAuthFailures=0;const reasons=[];
  try{
    await saveState({status:'gathering',total:0,completed:0,failed:0,message:'正在读取分页列表…',startedAt:new Date().toISOString(),reasons:[]});
    const queue=await gatherPages(tabId,maxPages);
    sessionId=(await api('/api/collection-session',{action:'start',total:queue.length,source_url:sourceUrl})).id;
    await saveState({status:'running',sessionId,total:queue.length,message:`发现 ${queue.length} 个角色，开始读取详情…`});
    for(let index=0;index<queue.length&&!stopRequested;index++){
      const {item,page}=queue[index];
      try{
        const detail=await fetch(item.url,{credentials:'include',cache:'no-store'});
        if(!detail.ok)throw Error(`详情请求 ${detail.status}`);
        const bundle=detailBundle(await decodedHtml(detail),item,page);
        const collected=await api('/api/collect-desktop-bundle',bundle);succeeded++;
        consecutiveAuthFailures=0;
        inserted+=Number(collected.ingestion?.inserted||0);
        overwritten+=Number(collected.ingestion?.overwritten||0);
        duplicates+=Number(collected.ingestion?.duplicates||0);
      }catch(error){
        failed++;const reason=error?.message||String(error);if(!reasons.includes(reason))reasons.push(reason);
        const authFailure=/未包含角色属性|重新登录|完成验证|登录|403|401/.test(reason);
        consecutiveAuthFailures=authFailure?consecutiveAuthFailures+1:0;
        if(consecutiveAuthFailures>=2){loginRequired=true;await backgroundCall('collector-login-required',{tabId,reason:'连续两次无法读取角色详情，登录可能已失效或需要完成验证'});break}
      }
      await api('/api/collection-session',{action:'update',id:sessionId,status:'running',completed:succeeded,failed,inserted,overwritten,duplicates,errors:reasons});
      await saveState({completed:succeeded,failed,inserted,overwritten,duplicates,reasons:reasons.slice(0,5),message:`正在采集 ${index+1}/${queue.length} · 成功 ${succeeded} · 失败 ${failed}`});
      if(index<queue.length-1&&!stopRequested)await pause(1200);
    }
    const finalStatus=loginRequired?'waiting_login':stopRequested?'stopped':'completed';
    await api('/api/collection-session',{action:'update',id:sessionId,status:finalStatus,completed:succeeded,failed,inserted,overwritten,duplicates,errors:reasons});
    await saveState({status:finalStatus,completed:succeeded,failed,inserted,overwritten,duplicates,reasons:reasons.slice(0,5),
      message:`${loginRequired?'等待重新登录':stopRequested?'已停止':'采集完成'}：成功 ${succeeded}，失败 ${failed}${reasons.length?` · ${reasons.slice(0,2).join('；')}`:''}`});
    if(!loginRequired&&succeeded)await backgroundCall('collector-login-cleared');
  }catch(error){
    if(sessionId){try{await api('/api/collection-session',{action:'update',id:sessionId,status:'failed',completed:succeeded,failed,inserted,overwritten,duplicates,errors:reasons})}catch{}}
    await saveState({status:'failed',completed:succeeded,failed,message:`采集失败：${error?.message||String(error)}`});
  }finally{running=false}
}

chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  if(message?.target!=='offscreen')return;
  if(message.type==='collector-stop'){stopRequested=true;saveState({message:'正在完成当前商品后停止…'});sendResponse({ok:true});return}
  if(message.type==='collector-start'){
    if(running){sendResponse({ok:false,error:'已有采集任务正在运行'});return}
    runCollection(message).catch(console.error);sendResponse({ok:true});return;
  }
});
