(function(){
    const PAGE_SIZE = 10
    const state = {
        page: 1,
        pages: 1,
        status: '',
        equipmentName: '',
        loading: false
    }
    let ordersView = null

    function createOrdersView(){
        const view = document.createElement('section')
        view.id = 'repair-orders-view'
        view.className = 'repair-orders-view'
        view.hidden = true
        view.style.display = 'none'
        view.innerHTML = `
            <header class="repair-orders-heading">
                <div><p>维修任务</p><h1>我的工单</h1></div>
                <button class="repair-orders-refresh" type="button">刷新</button>
            </header>
            <form class="repair-orders-filters">
                <label>工单状态
                    <select name="status">
                        <option value="">全部状态</option>
                        <option value="pending_accept">待接单</option>
                        <option value="pending_repair">待维修</option>
                        <option value="repairing">维修中</option>
                        <option value="pending_confirm">待确认</option>
                        <option value="completed">已完成</option>
                        <option value="unrepairable">无法维修</option>
                        <option value="scrapped">已报废</option>
                    </select>
                </label>
                <label>设备名称
                    <input name="equipmentName" type="search" maxlength="100" placeholder="输入设备名称">
                </label>
                <button type="submit">查询</button>
                <button class="repair-orders-reset" type="button">重置</button>
            </form>
            <div class="repair-orders-result" aria-live="polite"></div>
            <nav class="repair-orders-pagination" aria-label="工单分页">
                <button class="orders-previous" type="button">上一页</button>
                <span class="orders-page-info">第 1 / 1 页</span>
                <button class="orders-next" type="button">下一页</button>
            </nav>
        `
        document.querySelector('.right-side').insertAdjacentElement('afterend', view)
        bindViewEvents(view)
        return view
    }

    function bindViewEvents(view){
        const form = view.querySelector('.repair-orders-filters')
        form.addEventListener('submit', event => {
            event.preventDefault()
            state.status = form.elements.status.value
            state.equipmentName = form.elements.equipmentName.value.trim()
            state.page = 1
            loadOrders()
        })
        view.querySelector('.repair-orders-reset').addEventListener('click', () => {
            form.reset()
            Object.assign(state, { page: 1, status: '', equipmentName: '' })
            loadOrders()
        })
        view.querySelector('.repair-orders-refresh').addEventListener('click', loadOrders)
        view.querySelector('.orders-previous').addEventListener('click', () => changePage(state.page - 1))
        view.querySelector('.orders-next').addEventListener('click', () => changePage(state.page + 1))
    }

    function changePage(page){
        if(page < 1 || page > state.pages || page === state.page) return
        state.page = page
        loadOrders()
    }

    function renderOrders(data){
        const result = ordersView.querySelector('.repair-orders-result')
        if(data.items.length === 0){
            result.innerHTML = '<p class="repair-orders-empty">暂无符合条件的维修工单</p>'
        }else{
            const table = document.createElement('table')
            table.className = 'repair-orders-table'
            table.innerHTML = '<thead><tr><th>工单号</th><th>设备名称</th><th>状态</th><th>派单时间</th><th>完成时间</th></tr></thead><tbody></tbody>'
            const body = table.querySelector('tbody')
            data.items.forEach(order => {
                const row = document.createElement('tr')
                row.tabIndex = 0
                row.innerHTML = '<td></td><td></td><td></td><td></td><td></td>'
                const cells = row.children
                cells[0].textContent = order.id
                cells[1].textContent = order.equipmentName || `设备 #${order.equipmentId}`
                cells[2].textContent = statusToChinese(REPAIR_ORDER_STATUS_MAP, order.status)
                cells[3].textContent = order.assignTime || '暂无'
                cells[4].textContent = order.completionTime || '暂无'
                row.addEventListener('click', () => openOrderDetail(order.id))
                row.addEventListener('keydown', event => {
                    if(event.key === 'Enter') openOrderDetail(order.id)
                })
                body.appendChild(row)
            })
            result.replaceChildren(table)
        }

        state.pages = Math.max(1, data.pages || 1)
        state.page = data.page || state.page
        ordersView.querySelector('.orders-page-info').textContent = `第 ${state.page} / ${state.pages} 页，共 ${data.total || 0} 条`
        ordersView.querySelector('.orders-previous').disabled = state.page <= 1
        ordersView.querySelector('.orders-next').disabled = state.page >= state.pages
    }

    async function loadOrders(){
        if(state.loading) return
        state.loading = true
        const result = ordersView.querySelector('.repair-orders-result')
        result.innerHTML = '<p class="repair-orders-loading">正在加载工单...</p>'
        const data = await getMyRepairOrders({
            page: state.page,
            size: PAGE_SIZE,
            status: state.status,
            equipmentName: state.equipmentName
        })
        state.loading = false
        if(!data){
            result.innerHTML = '<p class="repair-orders-empty">工单加载失败，请稍后重试</p>'
            return
        }
        renderOrders(data)
    }

    function appendDetail(list, label, value){
        if(value === null || value === undefined || value === '') return
        const row = document.createElement('div')
        const term = document.createElement('dt')
        const description = document.createElement('dd')
        term.textContent = label
        description.textContent = String(value)
        row.append(term, description)
        list.appendChild(row)
    }

    function appendGallery(container, title, urls){
        if(!Array.isArray(urls) || urls.length === 0) return
        const heading = document.createElement('h3')
        const gallery = document.createElement('div')
        heading.textContent = title
        gallery.className = 'repair-order-gallery'
        urls.forEach((url, index) => {
            const link = document.createElement('a')
            const image = document.createElement('img')
            link.href = url
            link.target = '_blank'
            link.rel = 'noopener noreferrer'
            image.src = url
            image.alt = `${title} ${index + 1}`
            link.appendChild(image)
            gallery.appendChild(link)
        })
        container.append(heading, gallery)
    }

    async function openOrderDetail(orderId){
        const detail = await getMyRepairOrderDetail(orderId)
        if(!detail) return
        const dialog = document.createElement('dialog')
        dialog.className = 'repair-order-dialog'
        dialog.innerHTML = `
            <header><div><p>工单 #${detail.id}</p><h2></h2></div><button type="button" aria-label="关闭">×</button></header>
            <dl class="repair-order-detail-list"></dl>
            <section class="repair-order-images"></section>
        `
        dialog.querySelector('h2').textContent = detail.equipmentName || `设备 #${detail.equipmentId}`
        const list = dialog.querySelector('dl')
        appendDetail(list, '工单状态', statusToChinese(REPAIR_ORDER_STATUS_MAP, detail.status))
        appendDetail(list, '设备编号', detail.equipmentNo)
        appendDetail(list, '设备状态', statusToChinese(EQUIPMENT_STATUS_MAP, detail.equipmentStatus))
        appendDetail(list, '报修用户', detail.userName || detail.userId)
        appendDetail(list, '损坏说明', detail.damageDescription)
        appendDetail(list, '派单备注', detail.assignRemark)
        appendDetail(list, '派单时间', detail.assignTime)
        appendDetail(list, '故障原因', detail.faultCause)
        appendDetail(list, '维修过程', detail.repairProcess)
        appendDetail(list, '维修结果', detail.repairResult)
        appendDetail(list, '完成时间', detail.completionTime)
        const images = dialog.querySelector('.repair-order-images')
        appendGallery(images, '损坏图片', detail.damageImages)
        appendGallery(images, '维修前图片', detail.beforeImages)
        appendGallery(images, '维修后图片', detail.afterImages)
        document.body.appendChild(dialog)
        dialog.querySelector('header button').addEventListener('click', () => dialog.close())
        dialog.addEventListener('click', event => {
            if(event.target === dialog) dialog.close()
        })
        dialog.addEventListener('close', () => dialog.remove())
        dialog.showModal()
    }

    function showOrders(){
        const equipmentView = document.querySelector('.right-side')
        equipmentView.hidden = true
        equipmentView.style.display = 'none'
        ordersView.hidden = false
        ordersView.style.display = 'flex'
        loadOrders()
    }

    function showEquipment(){
        ordersView.hidden = true
        ordersView.style.display = 'none'
        const equipmentView = document.querySelector('.right-side')
        equipmentView.hidden = false
        equipmentView.style.display = 'flex'
    }

    ordersView = createOrdersView()
    document.getElementById('repair-orders-button').addEventListener('click', showOrders)
    document.getElementById('repair-equipment-button').addEventListener('click', showEquipment)
})()
