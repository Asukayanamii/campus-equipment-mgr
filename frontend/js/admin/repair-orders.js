(function(){
    const state = { page: 1, pages: 1, status: '', equipmentName: '', loading: false }
    const view = document.createElement('section')
    view.className = 'admin-operation-view'
    view.innerHTML = `
        <header class="operation-heading"><div><p>维修管理</p><h1>维修工单</h1></div><button class="operation-refresh" type="button">刷新</button></header>
        <form class="operation-filters">
            <label>状态<select name="status"><option value="">全部</option>${Object.entries(REPAIR_ORDER_STATUS_MAP).map(([value,label]) => `<option value="${value}">${label}</option>`).join('')}</select></label>
            <label>设备名称<input name="equipmentName" maxlength="100"></label>
            <button type="submit">查询</button><button class="operation-reset" type="button">重置</button>
        </form>
        <div class="operation-result"></div>
        <nav class="operation-pagination"><button class="previous" type="button">上一页</button><span></span><button class="next" type="button">下一页</button></nav>`
    document.body.appendChild(view)
    AdminViewManager.register(view)

    const form = view.querySelector('form')
    form.addEventListener('submit', event => { event.preventDefault(); state.page=1; state.status=form.elements.status.value; state.equipmentName=form.elements.equipmentName.value.trim(); load() })
    view.querySelector('.operation-reset').addEventListener('click', () => { form.reset(); Object.assign(state,{page:1,status:'',equipmentName:''}); load() })
    view.querySelector('.operation-refresh').addEventListener('click', load)
    view.querySelector('.previous').addEventListener('click', () => changePage(state.page-1))
    view.querySelector('.next').addEventListener('click', () => changePage(state.page+1))
    document.getElementById('repair-orders-button').addEventListener('click', () => { AdminViewManager.show(view); load() })

    function changePage(page){ if(page>=1 && page<=state.pages && page!==state.page){state.page=page;load()} }
    async function load(){
        if(state.loading)return
        state.loading=true
        view.querySelector('.operation-result').innerHTML='<p class="operation-message">加载中...</p>'
        const data=await adminBusinessRequest('/admin/repair-orders/page',{query:{page:state.page,size:10,status:state.status,equipmentName:state.equipmentName}})
        state.loading=false
        if(!data)return
        render(data)
    }
    function render(data){
        const result=view.querySelector('.operation-result')
        if(!data.items.length){result.innerHTML='<p class="operation-message">暂无维修工单</p>'}
        else{
            const table=document.createElement('table');table.className='operation-table';table.innerHTML='<thead><tr><th>工单号</th><th>设备</th><th>维修员</th><th>状态</th><th>创建时间</th></tr></thead><tbody></tbody>'
            data.items.forEach(item=>{const row=document.createElement('tr');row.tabIndex=0;row.innerHTML='<td></td><td></td><td></td><td></td><td></td>';[item.id,item.equipmentName||item.equipmentId,item.repairUserName||'未派单',statusToChinese(REPAIR_ORDER_STATUS_MAP,item.status),item.createTime].forEach((v,i)=>row.children[i].textContent=v);row.addEventListener('click',()=>openDetail(item.id));table.tBodies[0].appendChild(row)})
            result.replaceChildren(table)
        }
        state.page=data.page||1;state.pages=Math.max(1,data.pages||1);view.querySelector('.operation-pagination span').textContent=`第 ${state.page} / ${state.pages} 页，共 ${data.total} 条`;view.querySelector('.previous').disabled=state.page<=1;view.querySelector('.next').disabled=state.page>=state.pages
    }
    function addField(list,label,value){if(value===null||value===undefined||value==='')return;const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=String(value);row.append(dt,dd);list.appendChild(row)}
    async function openDetail(id){
        const detail=await adminBusinessRequest(`/admin/repair-orders/${id}`);if(!detail)return
        const dialog=document.createElement('dialog');dialog.className='operation-dialog';dialog.innerHTML='<header><div><p>维修工单</p><h2></h2></div><button type="button" aria-label="关闭">×</button></header><dl></dl><div class="operation-actions"></div>'
        dialog.querySelector('h2').textContent=detail.equipmentName||`工单 #${id}`;const list=dialog.querySelector('dl');[['工单状态',statusToChinese(REPAIR_ORDER_STATUS_MAP,detail.status)],['设备编号',detail.equipmentNo],['设备状态',statusToChinese(EQUIPMENT_STATUS_MAP,detail.equipmentStatus)],['损坏说明',detail.damageDescription],['维修人员',detail.repairUserName],['派单备注',detail.assignRemark],['故障原因',detail.faultCause],['维修过程',detail.repairProcess],['维修结果',detail.repairResult]].forEach(([l,v])=>addField(list,l,v))
        const actions=dialog.querySelector('.operation-actions')
        const orderStatus=chineseToStatus(REPAIR_ORDER_STATUS_MAP,detail.status)
        if(orderStatus==='pending_assign'){const button=document.createElement('button');button.textContent='派单';button.addEventListener('click',()=>openAssign(dialog,detail));actions.appendChild(button)}
        if(orderStatus==='pending_confirm')actions.appendChild(actionButton('确认完成',`确认工单 #${id} 已维修完成吗？`,()=>adminBusinessRequest(`/admin/repair-orders/${id}/confirm`,{method:'POST'}),dialog))
        if(orderStatus==='unrepairable')actions.appendChild(actionButton('报废设备',`报废操作不可逆，确认报废工单 #${id} 对应设备吗？`,()=>adminBusinessRequest(`/admin/repair-orders/${id}/scrap`,{method:'POST'}),dialog,'danger'))
        document.body.appendChild(dialog);dialog.querySelector('header button').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>dialog.remove());dialog.showModal()
    }
    function actionButton(text,confirmation,request,dialog,className=''){const button=document.createElement('button');button.textContent=text;button.className=className;button.addEventListener('click',async()=>{if(!confirm(confirmation))return;button.disabled=true;const ok=await request();if(ok){Toast.success(`${text}成功`);dialog.close();load()}else button.disabled=false});return button}
    async function openAssign(parent,detail){
        const users=await adminBusinessRequest('/admin/repair-users/page',{query:{page:1,size:100}});if(!users)return
        const dialog=document.createElement('dialog');dialog.className='operation-dialog operation-small-dialog';dialog.innerHTML='<header><div><p>工单派发</p><h2>选择维修员</h2></div><button type="button">×</button></header><form><label>维修员<select name="repairUserId" required></select></label><label>派单备注<textarea name="assignRemark" maxlength="1000" rows="4"></textarea></label><button type="submit">确认派单</button></form>'
        users.items.forEach(user=>{const option=document.createElement('option');option.value=user.id;option.textContent=`${user.name||user.username}（${user.username}）`;dialog.querySelector('select').appendChild(option)})
        dialog.querySelector('form').addEventListener('submit',async event=>{event.preventDefault();if(!confirm('确认将此工单派发给所选维修员吗？'))return;const button=event.currentTarget.querySelector('button[type=submit]');button.disabled=true;const ok=await adminBusinessRequest(`/admin/repair-orders/${detail.id}/assign`,{method:'POST',body:{repairUserId:Number(event.currentTarget.elements.repairUserId.value),assignRemark:event.currentTarget.elements.assignRemark.value.trim()||null}});if(ok){Toast.success('派单成功');dialog.close();parent.close();load()}else button.disabled=false})
        document.body.appendChild(dialog);dialog.querySelector('header button').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>dialog.remove());dialog.showModal()
    }
})()
