import {applyProfile} from './profile-state.js';

const q=s=>document.querySelector(s);
const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let currentId=null;

function timeLabel(value){
  const d=new Date(value);
  return Number.isNaN(d.getTime())?'未知时间':new Intl.DateTimeFormat('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(d);
}

async function openProfile(id){
  const response=await fetch('/api/profile?listing_id='+encodeURIComponent(id),{cache:'no-store'});
  const data=await response.json();
  if(!response.ok||!data.profile)throw Error(data.error||'角色资料不存在');
  currentId=id;
  applyProfile(data.profile);
  document.querySelectorAll('.profile-history-item').forEach(x=>x.classList.toggle('active',x.dataset.id===id));
}

export async function loadProfileHistory(){
  const container=q('#profile-history');
  try{
    const response=await fetch('/api/profiles',{cache:'no-store'}),data=await response.json();
    if(!response.ok)throw Error(data.error||'读取失败');
    container.innerHTML=data.profiles.length?data.profiles.map(profile=>`<button class="profile-history-item${profile.listing_id===currentId?' active':''}" data-id="${escape(profile.listing_id)}"><strong>${escape(profile.name)}</strong><span>${escape(profile.server)} · ${escape(profile.level??'?')}级${escape(profile.school||'')}</span><small>${escape(timeLabel(profile.saved_at))}</small></button>`).join(''):'<p class="hint">还没有同步记录。</p>';
    container.querySelectorAll('button').forEach(button=>button.onclick=()=>openProfile(button.dataset.id).catch(console.error));
  }catch(error){container.innerHTML=`<p class="hint">历史读取失败：${escape(error.message)}</p>`}
}

q('#refresh-profiles').onclick=loadProfileHistory;
document.querySelectorAll('[data-profile-tab]').forEach(button=>button.onclick=()=>{
  document.querySelectorAll('[data-profile-tab]').forEach(x=>x.classList.toggle('active',x===button));
  document.querySelectorAll('[data-profile-pane]').forEach(x=>x.classList.toggle('active',x.dataset.profilePane===button.dataset.profileTab));
});

window.addEventListener('profile-applied',event=>{
  const profile=event.detail,features=profile.features||{};
  currentId=profile.listing_id||null;
  q('#profile-title').textContent=profile.name||`${features.level||'?'}级${features.school||'角色'}`;
  q('#profile-meta').textContent=[profile.server,features.realm,profile.status_desc,profile.listing_id&&`商品 ${profile.listing_id}`].filter(Boolean).join(' · ');
  loadProfileHistory();
});
window.addEventListener('profile-cleared',()=>{
  q('#profile-title').textContent='尚未选择角色';
  q('#profile-meta').textContent='从左侧历史记录选择，或使用扩展同步新角色。';
});

loadProfileHistory();
