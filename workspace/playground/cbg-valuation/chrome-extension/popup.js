const status=document.querySelector('#status');
const sync=document.querySelector('#sync');
const collect=document.querySelector('#collect');
const stop=document.querySelector('#stop');
const roleSelect=document.querySelector('#role-select');
const fillSearch=document.querySelector('#fill-search');
const pageCount=document.querySelector('#page-count');
const automationInterval=document.querySelector('#automation-interval');
const automationToggle=document.querySelector('#automation-toggle');
const automationRun=document.querySelector('#automation-run');
const automationStatus=document.querySelector('#automation-status');
let workbenchUrl='http://127.0.0.1:8765/#estimate';
let stopRequested=false;

function fillRoleSearch(profile){
  const features=profile.features||{};
  const changed=[];
  const set=(id,value)=>{
    const node=document.getElementById(id);
    if(!node||value==null||value==='')return;
    node.value=String(value);
    node.dispatchEvent(new Event('input',{bubbles:true}));
    node.dispatchEvent(new Event('change',{bubbles:true}));
    changed.push(id);
  };
  const clickText=(containerId,text)=>{
    const root=document.getElementById(containerId);
    const target=[...(root?.querySelectorAll('li')||[])].find(li=>li.textContent.trim()===String(text).trim());
    if(target){target.click();changed.push(containerId)}
  };
  set('level_min',features.level);set('level_max',features.level);
  clickText('school_list',features.school);
  const realm=String(features.realm||'');
  let realmRadio;
  if(realm.includes('化圣'))realmRadio=document.getElementById('zhuang_zhi_hua_sheng');
  else if(realm.includes('渡劫'))realmRadio=document.querySelector('input[name="zhuang_zhi"][value="2"]');
  else if(realm.includes('飞升')&&!realm.includes('未'))realmRadio=document.querySelector('input[name="zhuang_zhi"][value="1"]');
  else realmRadio=document.querySelector('input[name="zhuang_zhi"][value=""]');
  realmRadio?.click();
  if(realm.includes('化圣')){
    const numerals={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9};
    const rank=Object.entries(numerals).find(([key])=>realm.includes(key))?.[1];
    const select=document.getElementById('zhuang_zhi_hua_sheng_select');
    if(select&&rank){select.disabled=false;select.selectedIndex=rank;select.dispatchEvent(new Event('change',{bubbles:true}))}
  }
  const fields={
    expt_gongji:'iExptSki1',expt_fangyu:'iExptSki2',expt_fashu:'iExptSki3',expt_kangfa:'iExptSki4',expt_lieshu:'iExptSki5',
    max_expt_gongji:'iMaxExpt1',max_expt_fangyu:'iMaxExpt2',max_expt_fashu:'iMaxExpt3',max_expt_kangfa:'iMaxExpt4',
    bb_expt_gongji:'iBeastSki1',bb_expt_fangyu:'iBeastSki2',bb_expt_fashu:'iBeastSki3',bb_expt_kangfa:'iBeastSki4',cheng_jiu:'achievement'
  };
  Object.entries(fields).forEach(([id,key])=>set(id,features[key]));
  const sum=keys=>keys.reduce((total,key)=>total+(Number(features[key])||0),0);
  set('expt_total',sum(['iExptSki1','iExptSki2','iExptSki3','iExptSki4']));
  set('bb_expt_total',sum(['iBeastSki1','iBeastSki2','iBeastSki3','iBeastSki4']));
  const schoolSkills=(profile.skills?.groups?.school||[]).map(item=>Number(item.level)).filter(Number.isFinite);
  if(schoolSkills.length){set('school_skill_num',schoolSkills.length);set('school_skill_level',Math.min(...schoolSkills))}
  document.getElementById('role_basic_panel')?.scrollIntoView({behavior:'smooth',block:'start'});
  return {changed:changed.length,role:profile.name||`${features.level||''}级${features.school||''}`};
}

async function loadRoles(){
  try{
    const response=await fetch('http://127.0.0.1:8765/api/profiles',{cache:'no-store'});
    const data=await response.json();
    if(!response.ok)throw Error(data.error||'读取角色失败');
    roleSelect.replaceChildren(new Option(data.profiles.length?'请选择角色':'暂无已录入角色',''));
    data.profiles.forEach(item=>roleSelect.add(new Option(`${item.name} · ${item.server} · ${item.level||'?'}级${item.school||''}`,item.listing_id)));
    fillSearch.disabled=!data.profiles.length;
  }catch(error){
    roleSelect.replaceChildren(new Option('估价工作台未启动',''));
    fillSearch.disabled=true;
  }
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
  const found=new Map();
  const add=(href,node,extra={})=>{
    let url;try{url=new URL(href,location.href)}catch{return}
    if(url.protocol!=='https:'||url.hostname!=='xyq.cbg.163.com')return;
    const eid=extra.listing_id||url.searchParams.get('eid')||url.pathname.match(/\/equip\/(?:\d+\/)?([\w-]+)/)?.[1];
    if(!eid)return;
    let text='',cursor=node;
    for(let depth=0;cursor&&depth<5;depth++,cursor=cursor.parentElement){
      text=cursor.innerText||text;
      if(/[¥￥]\s*[\d,.]+|价格\s*[:：]?\s*[\d,.]+/.test(text))break;
    }
    const match=text.match(/[¥￥]\s*([\d,.]+)|价格\s*[:：]?\s*([\d,.]+)/);
    const price=Number((match?.[1]||match?.[2]||'').replaceAll(',',''))||null;
    found.set(eid,{...(found.get(eid)||{}),listing_id:eid,url:url.href,price:extra.price||price,...extra});
  };
  document.querySelectorAll('a[href*="eid="],a[href*="/equip/"]').forEach(a=>add(a.href,a));
  const queryRows=Array.isArray(globalThis.QueryResult)?globalThis.QueryResult:[];
  const serverById=ident=>{
    const all=globalThis.server_data||{};
    for(const config of Object.values(all)){
      const areaName=Array.isArray(config?.[0])?config[0][0]:'';
      const servers=Array.isArray(config?.[1])?config[1]:Object.values(config?.[1]||{});
      const match=servers.find(item=>String(item?.[0])===String(ident));
      if(match)return {server_name:match[1]||'',area_name:areaName||null};
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
    }catch(error){console.warn('全服角色内嵌字段解码失败',order,error)}
    const dataNode=node||document.querySelector(`[data_game_ordersn="${CSS.escape(order)}"],[data_ordersn="${CSS.escape(order)}"]`);
    const anchor=dataNode?.closest('a[href]')||dataNode?.closest('tr')?.querySelector('a[href]')||node?.closest('tr')?.querySelector('a[href]');
    let cursor=dataNode||node,rowText='';
    for(let depth=0;cursor&&depth<8;depth++,cursor=cursor.parentElement){rowText=cursor.innerText||rowText;if(/[¥￥]\s*[\d,.]+/.test(rowText)&&/区\s*[-—]/.test(rowText))break}
    const displayPrice=Number((rowText.match(/[¥￥]\s*([\d,.]+)/)?.[1]||'').replaceAll(',',''))||null;
    const attrPrice=Number(dataNode?.getAttribute('data_price')||0);
    const rowPrice=Number(row.price||0)/100;
    const id=String(row.game_ordersn||dataNode?.getAttribute('data_whole_game_ordersn')||order);
    const serverId=String(dataNode?.getAttribute('data_serverid')||row.serverid||row.server_id||'');
    const mappedServer=serverById(serverId);
    const areaServer=rowText.match(/([^\s￥¥]+区)\s*[-—]\s*([^\s￥¥]+)/);
    add(anchor?.href||`https://xyq.cbg.163.com/equip?s=${encodeURIComponent(serverId)}&eid=${encodeURIComponent(id)}`,dataNode||node,{
      listing_id:id,equip_desc:normalized,price:displayPrice||attrPrice||rowPrice||null,server_id:serverId,
      server_name:row.server_name||row.servername||mappedServer.server_name||areaServer?.[2]||'',
      area_name:row.area_name||row.areaname||mappedServer.area_name||areaServer?.[1]||null
    });
  };
  document.querySelectorAll('[data_game_ordersn],[data_ordersn]').forEach(node=>{
    const order=String(node.getAttribute('data_game_ordersn')||node.getAttribute('data_ordersn')||'');
    if(!order)return;
    const row=queryRows.find(item=>String(item.game_ordersn||item.eid||'')===order)||{};
    const hidden=document.getElementById(`other_info_${order}`);
    const equipDesc=(hidden?.value||hidden?.textContent||row.desc||'').trim();
    if(!equipDesc)return;
    addInline(order,equipDesc,node,row);
  });
  document.querySelectorAll('[id^="other_info_"]').forEach(hidden=>{
    const order=hidden.id.slice('other_info_'.length);
    const row=queryRows.find(item=>String(item.game_ordersn||item.eid||'')===order)||{};
    addInline(order,(hidden.value||hidden.textContent||'').trim(),null,row);
  });
  if(pageUrl.searchParams.get('eid'))add(pageUrl.href,document.body);
  const next=[...document.querySelectorAll('a[href]')].find(a=>/(?:下一页|下页|后页|›|»)/.test(a.textContent.trim())&&!a.closest('.disabled'));
  const allItems=[...found.values()];
  // Search results expose inline role data; unrelated recommendations do not.
  // When role markers exist, never fill the queue with generic page links.
  const roleItems=allItems.filter(item=>item.equip_desc);
  return {items:(roleItems.length?roleItems:allItems).slice(0,20),next_url:next?.href||null,server_id:serverId,server_name:serverName,
    area_name:areaName,official_catalog:{
      school_skill:config.school_skill||{},life_skill:config.life_skill||{},
      ju_qing_skill:config.ju_qing_skill||{},ju_qing_skill_desc:config.ju_qing_skill_desc||{},
      equip_info:config.equip_info||{},pet_info:config.pet_info||{},rider_info:config.rider_info||{},
      clothes_info:config.clothes_info||{},xiangrui_info:config.xiangrui_info||{},
      pet_skill_desc:config.pet_skill_desc||{},zuoqi_skill_desc:config.zuoqi_skill_desc||{},
      pet_neidans:config.pet_neidans||{},neidan_desc:config.neidan_desc||{},
      pet_shipin_info:config.pet_shipin_info||{},xiangrui_skill:config.xiangrui_skill||{}
    }};
}

function readFetchedListingPage(html,pageUrl,basePage){
  const doc=new DOMParser().parseFromString(html,'text/html');
  const found=new Map();
  const serverByText=text=>{
    const match=text.match(/([\u4e00-\u9fffA-Za-z0-9]+区)\s*[-—－]\s*([^\s￥¥]+)/);
    return {area_name:match?.[1]||null,server_name:match?.[2]||''};
  };
  const add=(id,url,node,equipDesc)=>{
    if(!id||found.has(id))return;
    let cursor=node,text='';
    for(let depth=0;cursor&&depth<9;depth++,cursor=cursor.parentElement){text=cursor.innerText||cursor.textContent||text;if(/[¥￥]\s*[\d,.]+/.test(text))break}
    const price=Number((text.match(/[¥￥]\s*([\d,.]+)/)?.[1]||node?.getAttribute('data_price')||'').replaceAll(',',''))||null;
    const server=serverByText(text);
    const dataNode=node?.closest('[data_serverid]')||node?.closest('tr')?.querySelector('[data_serverid]')||node?.parentElement?.querySelector?.('[data_serverid]');
    const serverId=String(node?.getAttribute('data_serverid')||dataNode?.getAttribute('data_serverid')||new URL(url,pageUrl).searchParams.get('s')||'');
    found.set(id,{listing_id:id,url:new URL(url,pageUrl).href,equip_desc:equipDesc||null,price,server_id:serverId,...server});
  };
  doc.querySelectorAll('[id^="other_info_"]').forEach(hidden=>{
    const id=hidden.id.slice('other_info_'.length);
    const row=hidden.closest('tr')||hidden.parentElement;
    const anchor=row?.querySelector('a[href*="eid="],a[href*="/equip/"]');
    add(id,anchor?.getAttribute('href')||`https://xyq.cbg.163.com/equip?eid=${encodeURIComponent(id)}`,hidden,(hidden.value||hidden.textContent||hidden.getAttribute('value')||'').trim());
  });
  doc.querySelectorAll('a[href*="eid="],a[href*="/equip/"]').forEach(anchor=>{
    const url=new URL(anchor.getAttribute('href'),pageUrl);const id=url.searchParams.get('eid')||url.pathname.match(/\/equip\/(?:\d+\/)?([\w-]+)/)?.[1];
    add(id,url.href,anchor,null);
  });
  const next=[...doc.querySelectorAll('a[href]')].find(a=>/(?:下一页|下页|后页|›|»)/.test(a.textContent.trim())&&!a.closest('.disabled'));
  return {items:[...found.values()].slice(0,20),next_url:next?new URL(next.getAttribute('href'),pageUrl).href:null,
          official_catalog:basePage.official_catalog,server_id:'',server_name:'',area_name:null};
}

function clickNextListingPage(){
  const disabled=node=>node.matches?.('[disabled],.disabled,.disable,.off')||
    node.closest?.('.disabled,.disable,.off')||node.getAttribute?.('aria-disabled')==='true';
  const roots=[...document.querySelectorAll('nav,[class*="page"],[id*="page"],[class*="pager"],[id*="pager"]')];
  const pagers=roots.map(root=>{
    const controls=[...root.querySelectorAll('a,button,input[type="button"]')];
    const numbers=controls.map(node=>Number((node.textContent||node.value||'').trim())).filter(Number.isFinite);
    const current=root.querySelector('.current,.active,[aria-current="page"],.page_on,.on,em,strong');
    const currentNumber=Number((current?.textContent||'').trim());
    return {root,controls,numbers,currentNumber};
  }).filter(item=>item.numbers.length>=2&&Number.isFinite(item.currentNumber));
  const pager=pagers.sort((a,b)=>b.numbers.length-a.numbers.length)[0];
  if(!pager)return {clicked:false,reason:'未识别到带当前页码的分页栏'};
  let next=pager.controls.find(node=>!disabled(node)&&Number((node.textContent||node.value||'').trim())===pager.currentNumber+1);
  if(!next)next=pager.controls.find(node=>{
    const text=(node.textContent||node.value||node.title||node.getAttribute?.('aria-label')||'').trim();
    return !disabled(node)&&/(?:下一页|下页|后页|›|»)/.test(text);
  });
  if(!next)return {clicked:false,reason:`第 ${pager.currentNumber} 页后没有可用页码`};
  next.scrollIntoView({block:'center'});
  next.click();
  return {clicked:true,from:location.href,current:pager.currentNumber,
          label:(next.textContent||next.value||next.title||'下一页').trim()};
}

async function gatherListingPages(firstPage,firstUrl,maxPages,tabId){
  const pages=[firstPage],seenItems=new Set(firstPage.items.map(item=>item.listing_id));
  while(pages.length<maxPages&&!stopRequested){
    status.textContent=`正在翻到列表第 ${pages.length+1}/${maxPages} 页…`;
    const [{result:turn}]=await chrome.scripting.executeScript({target:{tabId},world:'MAIN',func:clickNextListingPage});
    if(!turn?.clicked){status.textContent=`连续采集停在第 ${pages.length} 页：${turn?.reason||'没有下一页'}`;break}
    let page=null;
    for(let retry=0;retry<5;retry++){
      await pause(retry?800:1400);
      try{
        const [{result}]=await chrome.scripting.executeScript({target:{tabId},world:'MAIN',func:readCurrentListingPage});
        const fresh=result.items.filter(item=>!seenItems.has(item.listing_id));
        if(fresh.length){page={...result,items:fresh};break}
      }catch(error){if(retry===4)throw error}
    }
    if(!page){status.textContent=`连续采集停在第 ${pages.length} 页：翻页后列表没有变化`;break}
    page.items.forEach(item=>seenItems.add(item.listing_id));
    pages.push(page);
  }
  return pages.flatMap(page=>page.items.map(item=>({item,page})));
}

async function decodedHtml(response){
  const bytes=new Uint8Array(await response.arrayBuffer());
  const head=new TextDecoder('windows-1252').decode(bytes.slice(0,8192));
  const charset=(response.headers.get('content-type')?.match(/charset=([^;\s]+)/i)?.[1]||
    head.match(/charset\s*=\s*["']?([^\s"'/>;]+)/i)?.[1]||'utf-8').toLowerCase();
  const encoding=/^(?:gb2312|gbk|gb18030)$/.test(charset)?'gb18030':'utf-8';
  return new TextDecoder(encoding).decode(bytes);
}

function detailBundle(html,item,page){
  const doc=new DOMParser().parseFromString(html,'text/html');
  const field=doc.querySelector('#equip_desc_value');
  const encoded=(field?.value||field?.textContent||field?.getAttribute('value')||'').trim();
  if(!encoded)throw Error('详情页未包含角色属性，可能需要重新登录或完成验证');
  if(!item.price)throw Error('列表卡片未识别到挂牌价');
  const url=new URL(item.url);
  let detailServer={};
  const serverMatch=html.match(/var\s+ServerInfo\s*=\s*(\{[\s\S]*?\})\s*;/);
  if(serverMatch){try{detailServer=JSON.parse(serverMatch[1])}catch{detailServer={}}}
  const decodeJsString=value=>{
    if(!value)return '';
    try{return JSON.parse(`"${value.replaceAll('"','\\"')}"`)}catch{return value}
  };
  if(!detailServer.server_id)detailServer.server_id=serverMatch?.[1]?.match(/["']?server_id["']?\s*:\s*["']?([^,"'}\s]+)/)?.[1];
  if(!detailServer.server_name)detailServer.server_name=decodeJsString(serverMatch?.[1]?.match(/["']?server_name["']?\s*:\s*["']([^"']*)["']/)?.[1]);
  if(!detailServer.area_name)detailServer.area_name=decodeJsString(serverMatch?.[1]?.match(/["']?area_name["']?\s*:\s*["']([^"']*)["']/)?.[1]);
  const visibleServer=doc.body?.textContent?.match(/([\u4e00-\u9fffA-Za-z0-9]+区)\s*(?:[-—－]|->|→)\s*([^\s￥¥]+)/);
  const detailServerId=String(detailServer.server_id||item.server_id||url.searchParams.get('s')||page.server_id||'');
  const samePageServer=detailServerId===String(page.server_id||'');
  return {equip_desc:encoded,official_catalog:page.official_catalog,metadata:{
    listing_id:item.listing_id,server_id:detailServerId,
    server_name:item.server_name||(samePageServer?page.server_name:'')||detailServer.server_name||visibleServer?.[2],
    area_name:item.area_name||(samePageServer?page.area_name:'')||detailServer.area_name||visibleServer?.[1]||null,price:item.price,
    status_desc:'在售',source_url:item.url,response_time:new Date().toISOString()
  }};
}

function inlineBundle(item,page){
  if(!item.equip_desc)throw Error('搜索结果没有内嵌角色属性');
  if(!item.price)throw Error('搜索结果未识别到挂牌价');
  if(!item.server_name)throw Error('搜索结果未识别到服务器');
  return {equip_desc:item.equip_desc,official_catalog:page.official_catalog,metadata:{
    listing_id:item.listing_id,server_id:item.server_id||page.server_id,server_name:item.server_name,
    area_name:item.area_name,price:item.price,status_desc:'在售',source_url:item.url,response_time:new Date().toISOString()
  }};
}

const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function sessionUpdate(body){
  const response=await fetch('http://127.0.0.1:8765/api/collection-session',{method:'POST',headers:{'Content-Type':'application/json','X-CBG-Extension':'sync-v1'},body:JSON.stringify(body)});
  const result=await response.json();if(!response.ok)throw Error(result.error||'采集任务状态写入失败');return result;
}

function readCurrentRole(){
  const encoded=document.querySelector('#equip_desc_value')?.value?.trim()||document.querySelector('#equip_desc_value')?.textContent?.trim();
  if(!encoded)throw Error('当前页面没有角色完整属性，请打开藏宝阁角色详情页');
  const url=new URL(location.href);
  const server=globalThis.ServerInfo||{};
  const login=globalThis.LoginInfo||{};
  const item=globalThis.equip||{};
  const config=globalThis.CBG_GAME_CONFIG||{};
  const serverId=url.searchParams.get('s')||String(server.server_id||item.serverid||'');
  const sameLoginServer=String(login.serverid||'')===String(serverId);
  const serverName=(sameLoginServer?login.server_name:'')||server.server_name||item.server_name;
  const areaName=(sameLoginServer?login.area_name:'')||server.area_name||item.area_name;
  if(!serverName)throw Error('页面中缺少区服名称，请确认页面已完全加载');
  return {equip_desc:encoded,official_catalog:{
    school_skill:config.school_skill||{},life_skill:config.life_skill||{},
    ju_qing_skill:config.ju_qing_skill||{},ju_qing_skill_desc:config.ju_qing_skill_desc||{},
    equip_info:config.equip_info||{},pet_info:config.pet_info||{},rider_info:config.rider_info||{},
    clothes_info:config.clothes_info||{},xiangrui_info:config.xiangrui_info||{},
    pet_skill_desc:config.pet_skill_desc||{},zuoqi_skill_desc:config.zuoqi_skill_desc||{},
    pet_neidans:config.pet_neidans||{},neidan_desc:config.neidan_desc||{},pet_shipin_info:config.pet_shipin_info||{},
    xiangrui_skill:config.xiangrui_skill||{}
  },metadata:{
    listing_id:url.searchParams.get('eid')||item.eid||'',
    server_id:serverId,server_name:serverName,area_name:areaName||null,
    price:item.price||null,status_desc:item.status_desc||null,
    source_url:`${url.origin}${url.pathname}`,response_time:new Date().toISOString()
  }};
}

sync.addEventListener('click',async()=>{
  try{
    sync.disabled=true;status.textContent='正在读取当前详情页…';
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!tab?.id||!/^https:\/\/xyq\.cbg\.163\.com\//.test(tab.url||''))throw Error('请先打开 xyq.cbg.163.com 的角色详情页');
    const [{result}]=await chrome.scripting.executeScript({target:{tabId:tab.id},world:'MAIN',func:readCurrentRole});
    status.textContent='已读取页面，正在发送到本机工作台…';
    const response=await fetch('http://127.0.0.1:8765/api/parse-desktop-bundle',{method:'POST',headers:{'Content-Type':'application/json','X-CBG-Extension':'sync-v1'},body:JSON.stringify(result)});
    const profile=await response.json();
    if(!response.ok)throw Error(profile.error||'本机解析失败');
    workbenchUrl=`http://127.0.0.1:8765/?listing_id=${encodeURIComponent(profile.listing_id)}#estimate`;
    const workbenchTabs=await chrome.tabs.query({url:'http://127.0.0.1:8765/*'});
    await Promise.all(workbenchTabs.map(item=>chrome.tabs.update(item.id,{url:workbenchUrl})));
    status.textContent=`同步成功：${profile.server} ${profile.features.level}级${profile.features.school}${profile.features.realm?` · ${profile.features.realm}`:''}`;
  }catch(error){
    status.textContent='同步失败：'+(error?.message||String(error));
  }finally{sync.disabled=false}
});

collect.addEventListener('click',async()=>{
  try{
    collect.disabled=true;sync.disabled=true;stop.disabled=false;status.dataset.state='';
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!tab?.id||!/^https:\/\/xyq\.cbg\.163\.com\//.test(tab.url||''))throw Error('请先打开 xyq.cbg.163.com 的角色搜索或推荐列表页');
    const result=await chrome.runtime.sendMessage({type:'collector-start',tabId:tab.id,sourceUrl:tab.url,maxPages:Number(pageCount.value)});
    if(!result?.ok)throw Error(result?.error||'后台采集任务启动失败');
    status.textContent='后台采集已启动，关闭本弹窗不会中断。';
    workbenchUrl='http://127.0.0.1:8765/#collector';
  }catch(error){
    const message=error?.message||String(error);
    const noReceiver=/Receiving end does not exist|Could not establish connection/i.test(message);
    status.dataset.state='error';status.textContent=noReceiver
      ?'采集后台尚未启动，请到 chrome://extensions 重载“藏宝阁资料同步”后再试。'
      :'采集失败：'+message;
    collect.disabled=false;sync.disabled=false;stop.disabled=true;
  }
});

stop.addEventListener('click',async()=>{
  stop.disabled=true;status.textContent='正在完成当前商品后停止…';
  await chrome.runtime.sendMessage({type:'collector-stop'}).catch(()=>{});
});

async function refreshCollectorState(){
  const state=(await chrome.storage.local.get('collectorState')).collectorState;
  if(!state)return;
  status.textContent=state.message||'等待采集。';
  const active=['gathering','running'].includes(state.status);
  collect.disabled=active;sync.disabled=active;stop.disabled=!active;
  status.dataset.state=state.status==='failed'?'error':state.status==='completed'?'ok':'';
}

async function refreshAutomation(){
  try{
    const config=await chrome.runtime.sendMessage({type:'collector-automation-get'});
    if(!config)return;
    automationInterval.value=String(config.intervalMinutes||360);
    automationInterval.disabled=Boolean(config.enabled);
    automationToggle.textContent=config.enabled?'停用定时采集':'启用定时采集';
    automationToggle.dataset.enabled=config.enabled?'true':'false';
    automationRun.disabled=!config.enabled;
    const next=config.nextRunAt?new Date(config.nextRunAt).toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'';
    automationStatus.textContent=config.enabled
      ?`${config.loginRequired?'等待重新登录':next?`下次 ${next}`:'定时采集已启用'} · 每次 ${config.maxPages||pageCount.value} 页${config.lastError?` · 上次异常：${config.lastError}`:''}`
      :'尚未启用。启用后复用当前搜索页和上方页数。';
  }catch(error){automationStatus.textContent='定时状态读取失败，请重新加载扩展。'}
}

automationToggle.addEventListener('click',async()=>{
  try{
    automationToggle.disabled=true;
    const enabled=automationToggle.dataset.enabled==='true';
    if(enabled){
      await chrome.runtime.sendMessage({type:'collector-automation-set',enabled:false});
      status.textContent='已停用定时采集。';
    }else{
      const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
      if(!tab?.id||!/^https:\/\/xyq\.cbg\.163\.com\/cgi-bin\/xyq_overall_search\.py/.test(tab.url||''))throw Error('请先打开已设置条件的藏宝阁全服搜索结果页');
      const result=await chrome.runtime.sendMessage({type:'collector-automation-set',enabled:true,intervalMinutes:Number(automationInterval.value),maxPages:Number(pageCount.value),tabId:tab.id});
      if(result?.ok===false)throw Error(result.error||'启用失败');
      status.dataset.state='ok';status.textContent='定时采集已启用；请保留当前搜索标签页和登录状态。';
    }
    await refreshAutomation();
  }catch(error){status.dataset.state='error';status.textContent='定时设置失败：'+(error?.message||String(error))}
  finally{automationToggle.disabled=false}
});

automationRun.addEventListener('click',async()=>{
  try{
    automationRun.disabled=true;status.textContent='正在启动定时任务…';
    const result=await chrome.runtime.sendMessage({type:'collector-automation-run'});
    if(!result?.ok)throw Error(result?.error||'启动失败');
    status.dataset.state='ok';status.textContent='定时任务已启动，关闭弹窗后仍会继续。';
    await refreshCollectorState();await refreshAutomation();
  }catch(error){status.dataset.state='error';status.textContent='立即执行失败：'+(error?.message||String(error))}
  finally{automationRun.disabled=false}
});

document.querySelector('#open').addEventListener('click',()=>chrome.tabs.create({url:workbenchUrl}));
document.querySelector('#open-search').addEventListener('click',()=>chrome.tabs.create({url:'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py?act=show_search_role_form'}));
fillSearch.addEventListener('click',async()=>{
  try{
    if(!roleSelect.value)throw Error('请先选择一个已录入角色');
    fillSearch.disabled=true;status.textContent='正在填写全服搜索条件…';
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!tab?.id||!/^https:\/\/xyq\.cbg\.163\.com\/cgi-bin\/xyq_overall_search\.py/.test(tab.url||''))throw Error('请先打开藏宝阁“全服搜索”的角色搜索页');
    const response=await fetch(`http://127.0.0.1:8765/api/profile?listing_id=${encodeURIComponent(roleSelect.value)}`,{cache:'no-store'});
    const data=await response.json();
    if(!response.ok||!data.profile)throw Error(data.error||'角色资料不存在');
    const [{result}]=await chrome.scripting.executeScript({target:{tabId:tab.id},world:'MAIN',func:fillRoleSearch,args:[data.profile]});
    status.dataset.state='ok';status.textContent=`已填入 ${result.role} 的 ${result.changed} 组条件，请在网页检查后点击“全服搜索”。`;
  }catch(error){status.dataset.state='error';status.textContent='填写失败：'+(error?.message||String(error))}
  finally{fillSearch.disabled=!roleSelect.options.length||roleSelect.options.length===1}
});
loadRoles();
refreshCollectorState();
refreshAutomation();
const collectorStateTimer=setInterval(refreshCollectorState,1000);
const automationTimer=setInterval(refreshAutomation,5000);
window.addEventListener('unload',()=>clearInterval(collectorStateTimer));
window.addEventListener('unload',()=>clearInterval(automationTimer));
