(function(){
    function displayValue(value){
        return value === null || value === undefined || value === '' ? '暂无' : String(value)
    }

    function addDetail(list, label, value){
        const item = document.createElement('div')
        const term = document.createElement('dt')
        const description = document.createElement('dd')
        term.textContent = label
        description.textContent = displayValue(value)
        item.append(term, description)
        list.appendChild(item)
    }

    function createSection(title){
        const section = document.createElement('section')
        section.className = 'report-detail-section'
        const heading = document.createElement('h2')
        heading.textContent = title
        const list = document.createElement('dl')
        list.className = 'report-detail-list'
        section.append(heading, list)
        return { section, list }
    }

    function appendImageGallery(section, title, urls){
        if(!Array.isArray(urls) || urls.length === 0) return
        const heading = document.createElement('h3')
        heading.textContent = title
        const gallery = document.createElement('div')
        gallery.className = 'report-image-gallery'

        urls.forEach((url, index) => {
            const button = document.createElement('button')
            button.type = 'button'
            button.className = 'image-preview-trigger'
            button.dataset.imagePreviewSrc = url
            button.setAttribute('aria-label', `放大查看${title}第 ${index + 1} 张`)
            const image = document.createElement('img')
            image.src = url
            image.alt = `${title} ${index + 1}`
            image.loading = 'lazy'
            button.appendChild(image)
            gallery.appendChild(button)
        })
        section.append(heading, gallery)
    }

    function renderEquipmentSection(container, report){
        const { section, list } = createSection('设备与损坏信息')
        addDetail(list, '报修记录 ID', report.id)
        addDetail(list, '设备名称', report.equipmentName)
        addDetail(list, '设备编号', report.equipmentNo)
        addDetail(list, '分类', report.categoryName)
        addDetail(list, '规格型号', report.spec)
        addDetail(list, '品牌', report.brand)
        addDetail(list, '存放位置', report.location)
        addDetail(list, '设备状态', statusToChinese(EQUIPMENT_STATUS_MAP, report.equipmentStatus))
        addDetail(list, '报修状态', statusToChinese(REPAIR_REPORT_STATUS_MAP, report.status))
        addDetail(list, '损坏说明', report.damageDescription)
        addDetail(list, '报修时间', report.createTime)
        appendImageGallery(section, '损坏图片', report.damageImages)
        container.appendChild(section)
    }

    function renderOrderSection(container, report){
        if(!report.repairOrderId) return
        const { section, list } = createSection('维修工单与派单')
        addDetail(list, '维修工单 ID', report.repairOrderId)
        addDetail(list, '工单状态', statusToChinese(REPAIR_ORDER_STATUS_MAP, report.repairStatus))
        addDetail(list, '维修人员 ID', report.repairUserId)
        addDetail(list, '派单备注', report.assignRemark)
        addDetail(list, '派单时间', report.assignTime)
        container.appendChild(section)
    }

    function hasRepairResult(report){
        return Boolean(
            report.faultCause || report.repairProcess || report.repairResult ||
            report.completionTime || report.beforeImages?.length || report.afterImages?.length
        )
    }

    function renderResultSection(container, report){
        if(!hasRepairResult(report)) return
        const { section, list } = createSection('维修结果')
        addDetail(list, '故障原因', report.faultCause)
        addDetail(list, '维修过程', report.repairProcess)
        addDetail(list, '维修结果', report.repairResult)
        addDetail(list, '提交完成时间', report.completionTime)
        appendImageGallery(section, '维修前图片', report.beforeImages)
        appendImageGallery(section, '维修后图片', report.afterImages)
        container.appendChild(section)
    }

    function renderReportDetail(report){
        const detailWindow = document.querySelector('.record-detail-window')
        const content = detailWindow?.querySelector('.record-detail-content')
        if(!detailWindow || !content) return

        detailWindow.classList.add('report-detail-window')
        content.replaceChildren()
        renderEquipmentSection(content, report)
        renderOrderSection(content, report)
        renderResultSection(content, report)
    }

    document.addEventListener('record-detail-opened', event => {
        if(event.detail.recordType === 'repair'){
            renderReportDetail(event.detail.record)
        }
    })
})()
