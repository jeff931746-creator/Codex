const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const readonlyStyle=document.createElement('style');
readonlyStyle.textContent='.inline-number[readonly],.compact-form input[readonly],.compact-form textarea[readonly],.compact-form .readonly-control{cursor:default;pointer-events:none;user-select:none;background:#f7f3ed;color:var(--ink);opacity:1;border-color:#e5ddd2;box-shadow:none}';
document.head.append(readonlyStyle);
export function renderSkills(profile){
 let container=document.getElementById('role-skills');
 if(!container){container=document.createElement('div');container.id='role-skills';document.getElementById('role-form').after(container)}
 const groups=profile.skills?.groups;
 if(!groups){container.innerHTML='';return}
 const officialPlotIds=new Set([151,152,153,154,155,156,157,158,159,160,161,170,197]);
 const visibleGroups={...groups,plot:(groups.plot||[]).filter(skill=>officialPlotIds.has(Number(skill.id)))};
 const features=profile.features||{};
 const raw=profile.description?.raw||{};
 const roleTraining=[['攻击修炼','iExptSki1','iMaxExpt1'],['防御修炼','iExptSki2','iMaxExpt2'],['法术修炼','iExptSki3','iMaxExpt3'],['抗法修炼','iExptSki4','iMaxExpt4'],['猎术修炼','iExptSki5',null]];
 const petTraining=[['攻击控制力','iBeastSki1'],['防御控制力','iBeastSki2'],['法术控制力','iBeastSki3'],['抗法控制力','iBeastSki4']];
 const numberInput=(key,value,max=999)=>`<input form="role-form" class="inline-number" data-feature-key="${escape(key)}" type="number" min="0" max="${max}" value="${value==null?'':escape(value)}" aria-label="${escape(key)}" readonly tabindex="-1">`;
 const skillIcon=id=>/^\d{1,12}$/.test(String(id))?`/api/icon?kind=role_skill&id=${encodeURIComponent(id)}`:'';
 const valueFor=(key,rawKey=key)=>features[key]??raw[rawKey];
 const statusFields=[['气血上限','hp_max','iHp_Max'],['魔法上限','mp_max','iMp_Max'],['命中','hit','iAtt_All'],['伤害','damage','iDamage_All'],['防御','defense','iDef_All'],['速度','character_speed','iDex_All'],['法伤','spell_damage','iTotalMagDam_all'],['法防','spell_defense','iTotalMagDef_all'],['体质','constitution','iCor_All'],['魔力','magic','iMag_All'],['力量','strength','iStr_All'],['耐力','endurance','iRes_All'],['敏捷','agility','iSpe_All'],['潜力','potential_points','iPoint']];
 const pointFields=[['成就点','achievement','AchPointTotal'],['比武积分','hero_score','HeroScore'],['剑会积分','sword_score','sword_score'],['副本积分','dungeon_score','dup_score'],['神器积分','artifact_score','shenqi_score'],['门贡','school_offer','iSchOffer'],['帮贡','guild_offer','iOrgOffer'],['人气','popularity','iPride'],['潜能果','potential','iNutsNum'],['乾元丹','qianyuan','TA_iAllNewPoint'],['月饼粽子机缘','seasonal_points','addPoint'],['打造熟练度','smith_skill','iSmithski'],['裁缝熟练度','sew_skill','iSewski']];
 const editableStat=([label,key,rawKey])=>`<label><span>${escape(label)}</span>${numberInput(key,valueFor(key,rawKey),999999999)}</label>`;
 const trainingItem=([label,key,maxKey])=>`<label><span>${label}</span><span class="training-values">${numberInput(key,features[key],100)}${maxKey?`<i>/</i>${numberInput(maxKey,features[maxKey],100)}`:''}</span></label>`;
 const skillItem=(s,kind)=>`<label class="skill-icon-item ${kind}"><span class="skill-icon"><em>${escape(s.name.slice(0,1))}</em>${kind!=='unknown'&&skillIcon(s.id)?`<img src="${skillIcon(s.id)}" alt="${escape(s.name)}">`:''}</span><span class="skill-level">${numberInput(`skill_${s.id}`,s.level,999)}</span><b>${escape(s.name)}</b></label>`;
 const skillSection=(key,label)=>`<section class="cbg-skill-section ${key}"><header><h2>${label}</h2><span>${visibleGroups[key].length} 项</span></header>${visibleGroups[key].length?`<div class="cbg-skill-grid">${visibleGroups[key].map(s=>skillItem(s,key)).join('')}</div>`:'<p class="hint">未识别到该分类。</p>'}</section>`;
 const unknown=groups.unknown?.length?`<details class="unknown-skills"><summary>未公开名称的内部技能 · ${groups.unknown.length} 项</summary><div class="cbg-skill-grid">${groups.unknown.map(s=>skillItem(s,'unknown')).join('')}</div></details>`:'';
 container.innerHTML=`<div class="role-character-board"><section class="character-status"><header><h2>人物状态</h2><span>同步资料 · 只读</span></header><div class="character-stat-grid">${statusFields.map(editableStat).join('')}</div></section><div class="character-side"><div class="training-dashboard"><section><header><h2>人物修炼</h2>${features.cultivation!=null?`<span>合计 ${escape(features.cultivation)}</span>`:''}</header><div class="training-grid">${roleTraining.map(trainingItem).join('')}</div></section><section><header><h2>召唤兽控制力</h2>${features.pet_cultivation!=null?`<span>合计 ${escape(features.pet_cultivation)}</span>`:''}</header><div class="training-grid">${petTraining.map(trainingItem).join('')}</div></section></div><section class="character-points"><header><h2>积分与其他</h2></header><div class="point-grid">${pointFields.map(editableStat).join('')}</div></section></div></div><div class="role-skill-board"><div class="cbg-skill-layout">${skillSection('school','师门技能')}<div class="cbg-skill-right">${skillSection('life','生活技能')}${skillSection('plot','剧情技能')}</div></div>${unknown}</div>`;
 container.querySelectorAll('.skill-icon img').forEach(img=>img.addEventListener('error',()=>img.remove(),{once:true}));
}
window.addEventListener('role-profile-parsed',event=>renderSkills(event.detail));
window.addEventListener('offline-profile-loaded',event=>{if(event.detail)renderSkills(event.detail)});
