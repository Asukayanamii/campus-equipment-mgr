(function(){
    const state = { page: 1, pages: 1, loading: false }
    const view = document.createElement('section')
    view.className = 'admin-operation-view'
    view.innerHTML = `
        <header class="operation-heading"><div><p>审计管理</p><h1>操作日志</h1></div><button class="operation-refresh" type="button">刷新</button></header>
        <form class="operation-filters">
            <label>业务类型<select name="businessType"><option value="">全部</option><option value="borrow_record">借用记录</option><option value="repair_report">报修记录</option><option value="repair_order">维修工单</option><option value="equipment">设备</option></select></label>
            <label>操作动作<select name="action"><option value="">全部</option><option value="borrow_apply">提交借用申请</option><option value="borrow_approve">审核借用通过</option><option value="borrow_reject">审核借用驳回</option><option value="borrow_return_normal">正常归还设备</option><option value="borrow_return_damaged">损坏归还设备</option><option value="repair_report_create">创建报修记录</option><option value="repair_report_confirm">确认报修记录</option><option value="repair_order_create">创建维修工单</option><option value="repair_order_assign">派发维修工单</option><option value="repair_order_accept">接收维修工单</option><option value="repair_order_start">开始维修</option><option value="repair_order_complete">提交维修完成</option><option value="repair_order_unrepairable">提交无法维修结果</option><option value="repair_order_confirm">确认维修完成</option><option value="repair_order_scrap">报废设备</option><option value="equipment_create">新增设备</option><option value="equipment_status_change">变更设备状态</option><option value="equipment_delete">下架设备</option></select></label>
            <label>操作者<select name="operatorRole"><option value="">全部</option><option value="user">学生</option><option value="admin">管理员</option><option value="repair_user">维修人员</option><option value="system">系统</option></select></label>
            <label>业务记录 ID<input name="businessId" type="number" min="1"></label>
            <label>设备 ID<input name="equipmentId" type="number" min="1"></label>
            <button type="submit">查询</button><button class="operation-reset" type="button">重置</button>
        </form>
        <div class="operation-result" aria-live="polite"></div>
        <nav class="operation-pagination" aria-label="操作日志分页"><button class="previous" type="button">上一页</button><span></span><button class="next" type="button">下一页</button></nav>`
    document.body.appendChild(view)
    AdminViewManager.register(view)

    const form = view.querySelector('form')
    form.addEventListener('submit', event => { event.preventDefault(); state.page = 1; load() })
    view.querySelector('.operation-reset').addEventListener('click', () => { form.reset(); state.page = 1; load() })
    view.querySelector('.operation-refresh').addEventListener('click', load)
    view.querySelector('.previous').addEventListener('click', () => changePage(state.page - 1))
    view.querySelector('.next').addEventListener('click', () => changePage(state.page + 1))
    document.getElementById('operation-logs-button').addEventListener('click', () => { AdminViewManager.show(view); load() })

    function changePage(page){
        if(page < 1 || page > state.pages || page === state.page) return
        state.page = page
        load()
    }

    function getQuery(){
        return {
            page: state.page,
            size: 10,
            businessType: form.elements.businessType.value,
            action: form.elements.action.value,
            operatorRole: form.elements.operatorRole.value,
            businessId: form.elements.businessId.value,
            equipmentId: form.elements.equipmentId.value
        }
    }

    async function load(){
        if(state.loading) return
        state.loading = true
        view.querySelector('.operation-result').innerHTML = '<p class="operation-message">正在加载操作日志...</p>'
        const data = await adminBusinessRequest('/admin/operation-logs/page', { query: getQuery() })
        state.loading = false
        if(!data) return
        render(data)
    }

    function formatStatus(log){
        if(!log.fromStatus && !log.toStatus) return '无'
        return `${log.fromStatus || '无'} -> ${log.toStatus || '无'}`
    }

    function render(data){
        const result = view.querySelector('.operation-result')
        if(data.items.length === 0){
            result.innerHTML = '<p class="operation-message">暂无符合条件的操作日志</p>'
        }else{
            const table = document.createElement('table')
            table.className = 'operation-table operation-log-table'
            table.innerHTML = '<thead><tr><th>时间</th><th>业务</th><th>动作</th><th>状态变更</th><th>操作者</th><th>备注</th></tr></thead><tbody></tbody>'
            data.items.forEach(log => {
                const row = document.createElement('tr')
                row.innerHTML = '<td></td><td></td><td></td><td></td><td></td><td></td>'
                const business = `${log.businessType} #${log.businessId}${log.equipmentId ? `（设备 #${log.equipmentId}）` : ''}`
                const operator = `${log.operatorRole}${log.operatorId ? ` #${log.operatorId}` : ''}`
                ;[log.createTime, business, log.action, formatStatus(log), operator, log.remark || '无'].forEach((value, index) => { row.children[index].textContent = value })
                table.tBodies[0].appendChild(row)
            })
            result.replaceChildren(table)
        }
        state.page = data.page || 1
        state.pages = Math.max(1, data.pages || 1)
        view.querySelector('.operation-pagination span').textContent = `第 ${state.page} / ${state.pages} 页，共 ${data.total || 0} 条`
        view.querySelector('.previous').disabled = state.page <= 1
        view.querySelector('.next').disabled = state.page >= state.pages
    }
})()
