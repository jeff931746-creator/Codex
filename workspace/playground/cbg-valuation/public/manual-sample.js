const q=s=>document.querySelector(s);
const panel=document.createElement('article');panel.className='panel';
panel.innerHTML=`<h2>手动录入一条行情</h2><p class="hint">价格单位为人民币元。仅录入实际核对过的商品；角色整号价不能作为空号价。</p>
<form id="manual-sample"><div class="fields">
<label>类别<select name="category"><option value="role">空号</option><option value="equipment">装备 / 灵饰</option><option value="pet">召唤兽</option><option value="item">物品</option><option value="appearance">锦衣祥瑞</option></select></label>
<label>商品编号<input name="listing_id" required></label><label>名称<input name="name" required></label><label>服务器<input name="server" required></label>
<label>挂牌价（元）<input name="price" type="number" min="0.01" step="0.01" required></label><label>观察时间（本机时区）<input name="observed_at" type="datetime-local" required></label>
<label>商品来源链接<input name="source_url" type="url" required></label><label>状态<select name="status"><option value="listed">在售</option><option value="removed">下架</option><option value="sold">显示已售</option><option value="unknown">未知</option></select></label></div>
<div class="fields" id="sample-role-fields"><label>等级<input name="level" type="number" min="1" max="175" required></label><label>门派<input name="school" required></label><label>境界<input name="realm" required placeholder="例如：渡劫"></label></div>
<label class="check" id="sample-empty-label"><input name="empty_verified" type="checkbox">已核对为不含装备、宝宝等资产的空号价格</label>
<label>补充匹配属性 JSON（可留空）<textarea name="extra" rows="3" placeholder='{"cultivation":76,"strong":40}'></textarea></label>
<p class="hint">等级、门派、境界由上方填写；其他属性需与估价目标采用相同字段。资产按名称匹配，还应补充等级、伤害或技能等关键属性。</p>
<button class="primary" type="submit">校验并保存这条行情</button><p id="manual-result" class="hint" role="status"></p></form>`;
q('#market .import-panel').before(panel);
const form=q('#manual-sample');
function resetTime(){const now=new Date();form.elements.observed_at.value=new Date(now-now.getTimezoneOffset()*60000).toISOString().slice(0,16)}
resetTime();
form.elements.category.onchange=()=>{const role=form.elements.category.value==='role';q('#sample-role-fields').hidden=!role;q('#sample-empty-label').hidden=!role;for(const key of ['level','school','realm']){form.elements[key].disabled=!role;form.elements[key].required=role}};
form.onsubmit=async event=>{event.preventDefault();const button=form.querySelector('button[type=submit]');const result=q('#manual-result');try{
 button.disabled=true;result.textContent='正在校验…';const data=Object.fromEntries(new FormData(form));
 const extra=data.extra.trim()?JSON.parse(data.extra):{};
 if(!extra||typeof extra!=='object'||Array.isArray(extra))throw Error('补充属性必须是 JSON 对象');
 const features=data.category==='role'?{...extra,level:Number(data.level),school:data.school.trim(),realm:data.realm.trim()}:{...extra,name:data.name.trim()};
 const sample={listing_id:data.listing_id.trim(),category:data.category,name:data.name.trim(),server:data.server.trim(),price:Number(data.price),observed_at:new Date(data.observed_at).toISOString(),source_url:data.source_url.trim(),status:data.status,features};
 if(data.category==='role')sample.empty_verified=form.elements.empty_verified.checked;
 const response=await fetch('/api/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify([sample])});const body=await response.json();if(!response.ok)throw Error(body.error||'保存失败');
 result.textContent=`新增 ${body.inserted} · 重复 ${body.duplicates} · 冲突 ${body.conflicts} · 拒收 ${body.rejected}`+(body.errors?.length?'：'+body.errors.map(e=>e.reason).join('；'):'')+(data.category==='role'&&!sample.empty_verified?'。未核验空号的记录不会参与空号估价。':'');
 window.dispatchEvent(new Event('market-updated'));
}catch(error){result.textContent='未保存：'+error.message}finally{button.disabled=false}};
