(function(){
    const state = {
        page: 1,
        size: 10,
        pages: 1,
        status: '',
        equipmentName: '',
        loading: false
    }
    const PENDING_STATUSES = new Set(['pending', '待处理'])

    function createPage(){
        const rightSide = document.querySelector('#right-side')
        rightSide.innerHTML = `
            <section class="admin-repair-page" aria-labelledby="admin-repair-title">
                <header class="admin-repair-header">
                    <div>
                        <h1 id="admin-repair-title">报修处理</h1>
                    </div>
                    <button class="repair-refresh-button" type="button" title="刷新列表" aria-label="刷新列表">↻</button>
                </header>
                <form class="repair-filter-form">
                    <label>设备名称<input name="equipmentName" type="search" placeholder="输入设备名称"></label>
                    <label>报修状态
                        <select name="status">
                            <option value="">全部状态</option>
                            <option value="pending">待处理</option>
                            <option value="confirmed">已确认</option>
                        </select>
                    </label>
                    <button type="submit">查询</button>
                    <button class="repair-filter-reset" type="button">重置</button>
                </form>
                <div class="repair-table-wrap">
                    <table class="admin-repair-table">
                        <thead><tr><th>记录 ID</th><th>设备名称</th><th>报修用户</th><th>状态</th><th>工单状态</th><th>创建时间</th><th>操作</th></tr></thead>
                        <tbody></tbody>
                    </table>
                    <p class="repair-list-message" role="status">正在加载...</p>
                </div>
                <footer class="repair-pagination">
                    <span class="repair-page-summary"></span>
                    <button class="repair-page-previous" type="button">上一页</button>
                    <button class="repair-page-next" type="button">下一页</button>
                </footer>
            </section>
        `
        bindPageEvents(rightSide)
        loadReports()
    }

    function bindPageEvents(root){
        const form = root.querySelector('.repair-filter-form')
        form.addEventListener('submit', event => {
            event.preventDefault()
            state.equipmentName = form.elements.equipmentName.value.trim()
            state.status = form.elements.status.value
            state.page = 1
            loadReports()
        })
        root.querySelector('.repair-filter-reset').addEventListener('click', () => {
            form.reset()
            state.equipmentName = ''
            state.status = ''
            state.page = 1
            loadReports()
        })
        root.querySelector('.repair-refresh-button').addEventListener('click', loadReports)
        root.querySelector('.repair-page-previous').addEventListener('click', () => {
            if(state.page <= 1) return
            state.page -= 1
            loadReports()
        })
        root.querySelector('.repair-page-next').addEventListener('click', () => {
            if(state.page >= state.pages) return
            state.page += 1
            loadReports()
        })
    }

    function addCell(row, value){
        const cell = document.createElement('td')
        cell.textContent = value === null || value === undefined || value === '' ? '暂无' : String(value)
        row.appendChild(cell)
    }

    function renderRows(items){
        const tbody = document.querySelector('.admin-repair-table tbody')
        const message = document.querySelector('.repair-list-message')
        tbody.replaceChildren()
        message.hidden = items.length > 0
        message.textContent = items.length ? '' : '暂无符合条件的报修记录'

        items.forEach(report => {
            const row = document.createElement('tr')
            addCell(row, report.id)
            addCell(row, report.equipmentName)
            addCell(row, report.userName)
            addCell(row, statusToChinese(REPAIR_REPORT_STATUS_MAP, report.status))
            addCell(row, statusToChinese(REPAIR_ORDER_STATUS_MAP, report.repairOrderStatus))
            addCell(row, report.createTime)
            const actionCell = document.createElement('td')
            const detailButton = document.createElement('button')
            detailButton.type = 'button'
            detailButton.className = 'repair-detail-button'
            detailButton.textContent = '查看'
            detailButton.addEventListener('click', () => openDetail(report.id))
            actionCell.appendChild(detailButton)
            row.appendChild(actionCell)
            tbody.appendChild(row)
        })
    }

    function renderPagination(total){
        const page = document.querySelector('.admin-repair-page')
        page.querySelector('.repair-page-summary').textContent = `共 ${total} 条，第 ${state.page} / ${state.pages} 页`
        page.querySelector('.repair-page-previous').disabled = state.page <= 1
        page.querySelector('.repair-page-next').disabled = state.page >= state.pages
    }

    async function loadReports(){
        if(state.loading || !document.querySelector('.admin-repair-page')) return
        state.loading = true
        const message = document.querySelector('.repair-list-message')
        message.hidden = false
        message.textContent = '正在加载...'
        const data = await AdminRepairReportApi.getPage({
            page: state.page,
            size: state.size,
            status: state.status,
            equipmentName: state.equipmentName,
            sort: 'id',
            order: 'desc'
        })
        state.loading = false
        // 请求返回时管理员可能已切换到其他导航页，不再写入旧页面。
        if(!data || !document.querySelector('.admin-repair-page')) return
        state.pages = Math.max(1, data.pages || 1)
        renderRows(data.items || [])
        renderPagination(data.total || 0)
    }

    function addDetail(list, label, value){
        const wrapper = document.createElement('div')
        const term = document.createElement('dt')
        const description = document.createElement('dd')
        term.textContent = label
        description.textContent = value === null || value === undefined || value === '' ? '暂无' : String(value)
        wrapper.append(term, description)
        list.appendChild(wrapper)
    }

    function addDamageImages(dialog, urls){
        if(!Array.isArray(urls) || urls.length === 0) return
        const gallery = dialog.querySelector('.admin-damage-gallery')
        urls.forEach((url, index) => {
            const button = document.createElement('button')
            button.type = 'button'
            button.className = 'image-preview-trigger'
            button.dataset.imagePreviewSrc = url
            button.setAttribute('aria-label', `放大查看损坏图片 ${index + 1}`)
            const image = document.createElement('img')
            image.src = url
            image.alt = `损坏图片 ${index + 1}`
            button.appendChild(image)
            gallery.appendChild(button)
        })
    }

    async function openDetail(repairReportId){
        const report = await AdminRepairReportApi.getDetail(repairReportId)
        if(!report) return
        const dialog = document.createElement('dialog')
        dialog.className = 'admin-repair-dialog'
        dialog.setAttribute('aria-labelledby', 'admin-repair-dialog-title')
        dialog.innerHTML = `
            <header><div><p>报修管理</p><h2 id="admin-repair-dialog-title">报修记录详情</h2></div><button class="repair-dialog-close" type="button" aria-label="关闭">×</button></header>
            <div class="admin-repair-dialog-body">
                <dl class="admin-repair-detail-list"></dl>
                <section class="admin-damage-section"><h3>损坏图片</h3><div class="admin-damage-gallery"></div></section>
            </div>
            <footer class="admin-repair-dialog-actions"></footer>
        `
        const list = dialog.querySelector('.admin-repair-detail-list')
        addDetail(list, '记录 ID', report.id)
        addDetail(list, '设备名称', report.equipmentName)
        addDetail(list, '设备编号', report.equipmentNo)
        addDetail(list, '报修用户', report.userName || report.username)
        addDetail(list, '损坏说明', report.damageDescription)
        addDetail(list, '报修状态', statusToChinese(REPAIR_REPORT_STATUS_MAP, report.status))
        addDetail(list, '维修工单 ID', report.repairOrderId)
        addDetail(list, '工单状态', statusToChinese(REPAIR_ORDER_STATUS_MAP, report.repairOrderStatus))
        addDetail(list, '创建时间', report.createTime)
        addDetail(list, '更新时间', report.updateTime)
        addDamageImages(dialog, report.damageImages)
        dialog.querySelector('.admin-damage-section').hidden = !report.damageImages?.length

        if(PENDING_STATUSES.has(report.status)){
            const confirmButton = document.createElement('button')
            confirmButton.type = 'button'
            confirmButton.className = 'repair-confirm-button'
            confirmButton.textContent = '确认报修'
            confirmButton.addEventListener('click', () => confirmReport(dialog, report.id, confirmButton))
            dialog.querySelector('.admin-repair-dialog-actions').appendChild(confirmButton)
        }
        dialog.querySelector('.repair-dialog-close').addEventListener('click', () => dialog.close())
        dialog.addEventListener('click', event => { if(event.target === dialog) dialog.close() })
        dialog.addEventListener('close', () => dialog.remove())
        document.body.appendChild(dialog)
        dialog.showModal()
    }

    async function confirmReport(dialog, repairReportId, button){
        button.disabled = true
        button.textContent = '确认中...'
        const result = await AdminRepairReportApi.confirmReport(repairReportId)
        if(!result){
            button.disabled = false
            button.textContent = '确认报修'
            return
        }
        Toast.success('报修状态已更新为已确认')
        dialog.close()
        loadReports()
    }

    document.querySelector('#repair-reports-button').addEventListener('click', createPage)
})()
