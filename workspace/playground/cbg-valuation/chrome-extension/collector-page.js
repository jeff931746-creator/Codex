export function readCurrentListingPage(){
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

export function clickNextListingPage(){
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

export function clickFirstListingPage(){
  const roots=[...document.querySelectorAll('nav,[class*="page"],[id*="page"],[class*="pager"],[id*="pager"]')];
  for(const root of roots){
    const controls=[...root.querySelectorAll('a,button,input[type="button"]')];
    const first=controls.find(node=>Number((node.textContent||node.value||'').trim())===1);
    const current=root.querySelector('.current,.active,[aria-current="page"],.page_on,.on,em,strong');
    const currentNumber=Number((current?.textContent||'').trim());
    if(first&&Number.isFinite(currentNumber)){
      if(currentNumber===1)return {clicked:false,current:1};
      first.click();return {clicked:true,current:currentNumber};
    }
  }
  return {clicked:false,current:null};
}

export function inspectLoginState(){
  const login=globalThis.LoginInfo||{};
  const text=(document.body?.innerText||'').slice(0,8000);
  const hasIdentity=Boolean(login.userid||login.user_id||login.username||login.nickname||login.serverid);
  const hasLogout=/(?:退出|注销)/.test(text);
  const hasLoginPrompt=/(?:请登录|立即登录|登录藏宝阁|登录网易通行证)/.test(text);
  return {state:hasIdentity||hasLogout?'logged_in':hasLoginPrompt?'logged_out':'unknown',hasIdentity,hasLogout,title:document.title,url:location.href};
}
