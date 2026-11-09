import {renderSkills} from './profile-sections.js';
const q=s=>document.querySelector(s);
export function clearProfile(){q('#role-form').reset();q('#extra-features').value='';q('#assets').value='';q('#role-skills')?.replaceChildren();q('#profile-source').textContent='';window.dispatchEvent(new CustomEvent('profile-cleared'));}
export function applyProfile(profile){
 clearProfile();const f=q('#role-form');
 for(const [key,value] of Object.entries({name:profile.name,server:profile.server,...profile.features})){
  const field=f.elements.namedItem(key);if(!field)continue;
  if(field.tagName==='SELECT'&&![...field.options].some(o=>o.value===String(value)))field.add(new Option(String(value),String(value)));
  field.value=value;
 }
 const simple=['level','school','realm','cultivation','pet_cultivation','qianyuan','strong','speed'];
 const features={...profile.features};if(profile.description)features.sample_scope='full_role';
 q('#extra-features').value=JSON.stringify(Object.fromEntries(Object.entries(features).filter(([k])=>!simple.includes(k))),null,2);
 if(profile.source_url)q('#role-link').value=profile.source_url;
 const time=profile.response_time||'未知';
 q('#link-status').textContent=`已载入本机保存的离线资料：${profile.server} · ${profile.features.level}级${profile.features.school} · ${profile.status_desc||'状态未知'}。响应时间 ${time}；未联网更新。`;
 q('#profile-source').textContent=`商品 ${profile.listing_id||'未提供'} · 保存在本机数据库，刷新后可恢复；不属于当前在售行情。`;
 renderSkills(profile);
 f.querySelectorAll('input,textarea,select').forEach(field=>{
  if(field.id==='include-appearance')return;
  field.setAttribute('aria-readonly','true');field.tabIndex=-1;
  if(field.tagName==='SELECT')field.classList.add('readonly-control');
  else field.readOnly=true;
 });
 window.dispatchEvent(new CustomEvent('profile-applied',{detail:profile}));
}
export async function restoreLatest(){
 let edited=false;const mark=()=>{edited=true};document.addEventListener('input',mark,{once:true});
 try{const ident=new URLSearchParams(location.search).get('listing_id');const path=ident?'/api/profile?listing_id='+encodeURIComponent(ident):'/api/profile';const r=await fetch(path,{cache:'no-store'});if(!r.ok)return;const data=await r.json();if(!edited&&data.profile)applyProfile(data.profile)}finally{document.removeEventListener('input',mark)}
}
