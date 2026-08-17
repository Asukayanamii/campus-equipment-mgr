(function(){
    const REGISTRATION_CODE_TYPE_MAP = {admin: '管理员', repair: '维修员'}
    const state = {page: 1, pages: 1, isUsed: '', codeType: ''}
    const view = document.createElement('section')
    view.className = 'admin-operation-view'
    view.innerHTML = `
        <header class="operation-heading"><div><p>超级管理员</p><h1>注册码管理</h1></div><button class="create-code" type="button">新增注册码</button></header>
        <form class="operation-filters">
            <label>账号类型<select name="codeType"><option value="">全部</option><option value="admin">管理员</option><option value="repair">维修员</option></select></label>
            <label>使用状态<select name="isUsed"><option value="">全部</option><option value="false">未使用</option><option value="true">已使用</option></select></label>
            <button type="submit">查询</button>
        </form>
        <div class="operation-result"></div>
        <nav class="operation-pagination"><button class="previous" type="button">上一页</button><span></span><button class="next" type="button">下一页</button></nav>`
    document.body.appendChild(view)
    AdminViewManager.register(view)

    const form = view.querySelector('form')
    document.getElementById('registration-codes-button').addEventListener('click', () => { AdminViewManager.show(view); load() })
    form.addEventListener('submit', event => {
        event.preventDefault()
        state.page = 1
        state.isUsed = form.elements.isUsed.value
        state.codeType = form.elements.codeType.value
        load()
    })
    view.querySelector('.create-code').addEventListener('click', () => openEditor())
    view.querySelector('.previous').addEventListener('click', () => change(state.page - 1))
    view.querySelector('.next').addEventListener('click', () => change(state.page + 1))

    function change(page){
        if(page >= 1 && page <= state.pages){
            state.page = page
            load()
        }
    }

    async function load(){
        const data = await adminBusinessRequest('/admin/registration-codes/page', {
            query: {page: state.page, size: 20, isUsed: state.isUsed, codeType: state.codeType}
        })
        if(!data){
            view.querySelector('.operation-result').innerHTML = '<p class="operation-message">无权访问或加载失败</p>'
            return
        }
        render(data)
    }

    function render(data){
        const result = view.querySelector('.operation-result')
        if(!data.items.length){
            result.innerHTML = '<p class="operation-message">暂无注册码</p>'
        }else{
            const table = document.createElement('table')
            table.className = 'operation-table'
            table.innerHTML = '<thead><tr><th>注册码</th><th>账号类型</th><th>状态</th><th>创建时间</th><th>操作</th></tr></thead><tbody></tbody>'
            data.items.forEach(item => {
                const row = document.createElement('tr')
                row.innerHTML = '<td></td><td></td><td></td><td></td><td class="table-actions"></td>'
                const codeButton = document.createElement('button')
                codeButton.className = 'registration-code-link'
                codeButton.type = 'button'
                codeButton.textContent = item.code
                codeButton.addEventListener('click', () => openEditor(item))
                row.children[0].appendChild(codeButton)
                row.children[1].textContent = REGISTRATION_CODE_TYPE_MAP[item.codeType] || item.codeType
                row.children[2].textContent = item.isUsed ? '已使用' : '未使用'
                row.children[3].textContent = item.createTime
                const editButton = document.createElement('button')
                editButton.textContent = '更新'
                // 已使用的注册码仍可进入更新选单，便于手动重置使用状态。
                editButton.addEventListener('click', () => openEditor(item))
                const removeButton = document.createElement('button')
                removeButton.textContent = '删除'
                removeButton.className = 'danger'
                removeButton.addEventListener('click', () => remove(item))
                row.children[4].append(editButton, removeButton)
                table.tBodies[0].appendChild(row)
            })
            result.replaceChildren(table)
        }
        state.page = data.page
        state.pages = Math.max(1, data.pages || 1)
        view.querySelector('.operation-pagination span').textContent = `第 ${state.page} / ${state.pages} 页，共 ${data.total} 条`
    }

    function openEditor(item = null){
        const editing = Boolean(item)
        const dialog = document.createElement('dialog')
        dialog.className = 'operation-dialog operation-small-dialog'
        dialog.innerHTML = `
            <header><div><p>注册码</p><h2>${editing ? '更新注册码' : '新增注册码'}</h2></div><button type="button">×</button></header>
            <form>
                <label>注册码<input name="code" maxlength="128" required ${editing ? 'readonly' : ''}></label>
                <label>账号类型<select name="codeType" required><option value="admin">管理员</option><option value="repair">维修员</option></select></label>
                ${editing && item.isUsed ? '<button class="refresh-registration-code" type="button">刷新使用状态</button>' : ''}
                <button type="submit">保存</button>
            </form>`
        dialog.querySelector('[name=code]').value = item?.code || ''
        dialog.querySelector('[name=codeType]').value = item?.codeType || 'admin'
        const refreshButton = dialog.querySelector('.refresh-registration-code')
        if(refreshButton){
            refreshButton.addEventListener('click', async () => {
                refreshButton.disabled = true
                refreshButton.textContent = '刷新中...'
                // 刷新使用状态直接复用更新接口，将 isUsed 重置为 false。
                const ok = await adminBusinessRequest(`/admin/registration-codes/${item.id}`, {
                    method: 'PUT',
                    body: {isUsed: false}
                })
                if(ok){
                    Toast.success('注册码已重置为未使用')
                    dialog.close()
                    load()
                    return
                }
                refreshButton.disabled = false
                refreshButton.textContent = '刷新使用状态'
            })
        }
        dialog.querySelector('form').addEventListener('submit', async event => {
            event.preventDefault()
            const body = editing
                ? {codeType: event.currentTarget.elements.codeType.value}
                : {code: event.currentTarget.elements.code.value.trim(), codeType: event.currentTarget.elements.codeType.value}
            const ok = await adminBusinessRequest(
                editing ? `/admin/registration-codes/${item.id}` : '/admin/registration-codes/',
                {method: editing ? 'PUT' : 'POST', body}
            )
            if(ok){
                Toast.success(editing ? '注册码已更新' : '注册码已保存')
                dialog.close()
                load()
            }
        })
        document.body.appendChild(dialog)
        dialog.querySelector('header button').addEventListener('click', () => dialog.close())
        dialog.addEventListener('close', () => dialog.remove())
        dialog.showModal()
    }

    async function remove(item){
        if(!confirm(`确认删除注册码 ${item.code} 吗？`)) return
        const ok = await adminBusinessRequest(`/admin/registration-codes/${item.id}`, {method: 'DELETE'})
        if(ok){
            Toast.success('注册码已删除')
            load()
        }
    }
})()
