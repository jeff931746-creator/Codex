import {readCurrentListingPage,clickNextListingPage,clickFirstListingPage,inspectLoginState} from './collector-page.js';

const AUTOMATION_ALARM='cbg-collector-schedule';
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));

async function getAutomation(){
  return (await chrome.storage.local.get('collectorAutomation')).collectorAutomation||{enabled:false,intervalMinutes:360,maxPages:5};
}

async function saveAutomation(patch){
  const next={...(await getAutomation()),...patch,updatedAt:new Date().toISOString()};
  await chrome.storage.local.set({collectorAutomation:next});return next;
}

async function findSearchTab(config){
  if(config.tabId){
    try{const tab=await chrome.tabs.get(config.tabId);if(/^https:\/\/xyq\.cbg\.163\.com\/cgi-bin\/xyq_overall_search\.py/.test(tab.url||''))return tab}catch{}
  }
  const tabs=await chrome.tabs.query({url:'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py*'});
  return tabs.find(tab=>tab.id)||null;
}

async function clearLoginWarning(){
  await chrome.action.setBadgeText({text:''});
  await saveAutomation({loginRequired:false});
}

async function markLoginRequired(tabId,reason='藏宝阁登录已失效，请重新登录后重试'){
  const now=new Date().toISOString();
  await saveAutomation({loginRequired:true,lastError:reason,lastRunAt:now});
  await chrome.storage.local.set({collectorState:{status:'waiting_login',message:`等待登录：${reason}`,reasons:[reason],updatedAt:now}});
  await chrome.action.setBadgeBackgroundColor({color:'#c83b32'});
  await chrome.action.setBadgeText({text:'登录'});
  const iconUrl='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><rect width="128" height="128" rx="28" fill="#c83b32"/><text x="64" y="84" text-anchor="middle" font-size="64" font-family="sans-serif" fill="white">登</text></svg>');
  await chrome.notifications.create('cbg-login-required',{type:'basic',iconUrl,title:'藏宝阁采集等待登录',message:'请在绑定的藏宝阁标签页重新登录，然后点扩展里的“立即执行一次”。',priority:2}).catch(()=>{});
  return {ok:false,loginRequired:true,error:reason,tabId};
}

async function runScheduledCollection(){
  const config=await getAutomation();if(!config.enabled)return {ok:false,error:'定时采集未启用'};
  const tab=await findSearchTab(config);
  if(!tab?.id){
    await saveAutomation({lastRunAt:new Date().toISOString(),lastError:'未找到保持搜索条件的藏宝阁全服搜索标签页'});
    await chrome.storage.local.set({collectorState:{status:'waiting',message:'定时采集等待：请打开已设置条件的藏宝阁全服搜索结果页。',updatedAt:new Date().toISOString()}});
    return {ok:false,error:'未找到藏宝阁全服搜索结果页'};
  }
  const [loginCheck]=await chrome.scripting.executeScript({target:{tabId:tab.id},world:'MAIN',func:inspectLoginState});
  if(loginCheck?.result?.state==='logged_out')return markLoginRequired(tab.id,'藏宝阁页面显示未登录');
  if(loginCheck?.result?.state==='logged_in')await clearLoginWarning();
  const [first]=await chrome.scripting.executeScript({target:{tabId:tab.id},world:'MAIN',func:clickFirstListingPage});
  if(first?.result?.clicked)await pause(1600);
  await ensureCollectorDocument();
  const result=await chrome.runtime.sendMessage({type:'collector-start',target:'offscreen',tabId:tab.id,sourceUrl:tab.url,maxPages:config.maxPages,scheduled:true});
  const alarm=await chrome.alarms.get(AUTOMATION_ALARM);
  await saveAutomation({tabId:tab.id,sourceUrl:tab.url,lastRunAt:new Date().toISOString(),lastError:result?.ok?'':result?.error||'后台采集启动失败',nextRunAt:alarm?.scheduledTime?new Date(alarm.scheduledTime).toISOString():null});
  return result;
}

async function ensureAutomationAlarm(){
  const config=await getAutomation();
  if(!config.enabled)return;
  let alarm=await chrome.alarms.get(AUTOMATION_ALARM);
  if(!alarm){
    await chrome.alarms.create(AUTOMATION_ALARM,{delayInMinutes:config.intervalMinutes,periodInMinutes:config.intervalMinutes});
    alarm=await chrome.alarms.get(AUTOMATION_ALARM);
  }
  await saveAutomation({nextRunAt:alarm?.scheduledTime?new Date(alarm.scheduledTime).toISOString():null});
}

chrome.alarms.onAlarm.addListener(alarm=>{if(alarm.name===AUTOMATION_ALARM)runScheduledCollection().catch(error=>saveAutomation({lastError:error?.message||String(error)}))});
chrome.runtime.onStartup.addListener(()=>ensureAutomationAlarm().catch(()=>{}));
chrome.runtime.onInstalled.addListener(()=>ensureAutomationAlarm().catch(()=>{}));
ensureAutomationAlarm().catch(()=>{});
chrome.notifications.onClicked.addListener(async notificationId=>{
  if(notificationId!=='cbg-login-required')return;
  const tab=await findSearchTab(await getAutomation());
  if(tab?.id){await chrome.tabs.update(tab.id,{active:true});if(tab.windowId)await chrome.windows.update(tab.windowId,{focused:true})}
});

async function ensureCollectorDocument(){
  const exists=chrome.offscreen.hasDocument
    ?await chrome.offscreen.hasDocument()
    :(await chrome.runtime.getContexts({contextTypes:['OFFSCREEN_DOCUMENT'],documentUrls:[chrome.runtime.getURL('offscreen.html')]})).length>0;
  if(!exists)await chrome.offscreen.createDocument({
    url:'offscreen.html',reasons:['DOM_PARSER'],
    justification:'关闭扩展弹窗后继续解析藏宝阁列表和详情页'
  });
}

chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  if(message?.target==='background'){
    (async()=>{
      if(message.type==='collector-state-get')return (await chrome.storage.local.get('collectorState')).collectorState||{};
      if(message.type==='collector-state-set'){
        await chrome.storage.local.set({collectorState:message.state});return {ok:true};
      }
      if(message.type==='collector-page-read'){
        const [result]=await chrome.scripting.executeScript({target:{tabId:message.tabId},world:'MAIN',func:readCurrentListingPage});
        return result?.result;
      }
      if(message.type==='collector-page-next'){
        const [result]=await chrome.scripting.executeScript({target:{tabId:message.tabId},world:'MAIN',func:clickNextListingPage});
        return result?.result;
      }
      if(message.type==='collector-login-required')return markLoginRequired(message.tabId,message.reason);
      if(message.type==='collector-login-cleared'){await clearLoginWarning();return {ok:true}}
      throw Error('不支持的后台采集操作');
    })().then(sendResponse).catch(error=>sendResponse({__error:error?.message||String(error)}));
    return true;
  }
  if(message?.target==='offscreen')return;
  if(!['collector-start','collector-stop','collector-automation-get','collector-automation-set','collector-automation-run'].includes(message?.type))return;
  (async()=>{
    if(message.type==='collector-automation-get')return getAutomation();
    if(message.type==='collector-automation-set'){
      if(!message.enabled){await chrome.alarms.clear(AUTOMATION_ALARM);return saveAutomation({enabled:false,nextRunAt:null})}
      if(![60,360,720,1440].includes(message.intervalMinutes))throw Error('不支持的定时间隔');
      if(!Number.isInteger(message.maxPages)||message.maxPages<1||message.maxPages>20)throw Error('采集页数必须为1至20');
      const tab=await chrome.tabs.get(message.tabId);
      if(!/^https:\/\/xyq\.cbg\.163\.com\/cgi-bin\/xyq_overall_search\.py/.test(tab.url||''))throw Error('请在藏宝阁全服搜索结果页启用定时采集');
      await chrome.alarms.create(AUTOMATION_ALARM,{delayInMinutes:message.intervalMinutes,periodInMinutes:message.intervalMinutes});
      const alarm=await chrome.alarms.get(AUTOMATION_ALARM);
      await clearLoginWarning();
      return saveAutomation({enabled:true,intervalMinutes:message.intervalMinutes,maxPages:message.maxPages,tabId:tab.id,sourceUrl:tab.url,lastError:'',nextRunAt:new Date(alarm.scheduledTime).toISOString()});
    }
    if(message.type==='collector-automation-run')return runScheduledCollection();
    await ensureCollectorDocument();
    if(message.type==='collector-start'){
      const automation=await getAutomation();
      if(automation.enabled)await saveAutomation({tabId:message.tabId,sourceUrl:message.sourceUrl,maxPages:message.maxPages});
    }
    const response=await chrome.runtime.sendMessage({...message,target:'offscreen'});
    sendResponse(response||{ok:true});
  })().catch(error=>sendResponse({ok:false,error:error?.message||String(error)}));
  return true;
});
