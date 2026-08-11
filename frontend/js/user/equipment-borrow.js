(function(){
    const AVAILABLE_STATUSES = new Set(['available', '可借用', '可用'])
    let activeEquipmentId = null

    function isAvailable(status){
        return AVAILABLE_STATUSES.has(status)
    }

    function formatLocalDateTime(value){
        return value && value.length === 16 ? `${value}:00` : value
    }

    function createDetailDialog(){
        const dialog = document.createElement('dialog')
        dialog.className = 'equipment-borrow-dialog'
        dialog.innerHTML = `
            <div class="equipment-dialog-heading">
                <div>
                    <p class="equipment-dialog-eyebrow">设备详情</p>
                    <h2 id="equipment-dialog-title">正在加载...</h2>
                </div>
                <button class="equipment-dialog-close" type="button" aria-label="关闭">×</button>
            </div>
            <div class="equipment-dialog-loading" role="status">正在加载设备信息...</div>
            <div class="equipment-dialog-content" hidden>
                <img class="equipment-dialog-cover" alt="设备封面">
                <dl class="equipment-detail-list"></dl>
                <form class="borrow-application-form" hidden>
                    <h3>借用申请</h3>
                    <div class="borrow-time-fields">
                        <label>开始时间<input name="borrowStartTime" type="datetime-local" required></label>
                        <label>结束时间<input name="borrowEndTime" type="datetime-local" required></label>
                    </div>
                    <label>借用用途<textarea name="purpose" maxlength="500" rows="4" placeholder="请填写借用用途（选填）"></textarea></label>
                    <div class="borrow-form-actions">
                        <button class="borrow-cancel-button" type="button">取消</button>
                        <button class="borrow-submit-button" type="submit">提交申请</button>
                    </div>
                </form>
                <p class="equipment-unavailable-message" hidden>该设备当前不可借用。</p>
            </div>
        `
        document.body.appendChild(dialog)

        dialog.querySelector('.equipment-dialog-close').addEventListener('click', () => dialog.close())
        dialog.querySelector('.borrow-cancel-button').addEventListener('click', () => dialog.close())
        dialog.addEventListener('click', event => {
            if(event.target === dialog) dialog.close()
        })
        dialog.addEventListener('close', () => {
            activeEquipmentId = null
            dialog.remove()
        })
        dialog.querySelector('.borrow-application-form').addEventListener('submit', submitBorrowApplication)
        return dialog
    }

    function appendDetail(list, label, value){
        const wrapper = document.createElement('div')
        const term = document.createElement('dt')
        const description = document.createElement('dd')
        term.textContent = label
        description.textContent = value || '未填写'
        wrapper.append(term, description)
        list.appendChild(wrapper)
    }

    function renderEquipmentDetail(dialog, equipment){
        dialog.querySelector('#equipment-dialog-title').textContent = equipment.equipmentName
        const cover = dialog.querySelector('.equipment-dialog-cover')
        if(equipment.coverImg){
            cover.src = equipment.coverImg
            cover.hidden = false
        }else{
            cover.hidden = true
        }

        const list = dialog.querySelector('.equipment-detail-list')
        appendDetail(list, '设备编号', equipment.equipmentNo)
        appendDetail(list, '分类', equipment.categoryName)
        appendDetail(list, '规格型号', equipment.spec)
        appendDetail(list, '品牌', equipment.brand)
        appendDetail(list, '存放位置', equipment.location)
        appendDetail(list, '设备状态', statusToChinese(EQUIPMENT_STATUS_MAP, equipment.status))
        appendDetail(list, '备注', equipment.remark)

        const canBorrow = isAvailable(equipment.status)
        dialog.querySelector('.borrow-application-form').hidden = !canBorrow
        dialog.querySelector('.equipment-unavailable-message').hidden = canBorrow
        dialog.querySelector('.equipment-dialog-loading').hidden = true
        dialog.querySelector('.equipment-dialog-content').hidden = false
    }

    async function openEquipmentDetail(equipmentId){
        if(activeEquipmentId !== null) return
        activeEquipmentId = equipmentId
        const dialog = createDetailDialog()
        dialog.showModal()

        const equipment = await getDataById(equipmentId, 'user')
        if(!equipment){
            dialog.close()
            return
        }
        renderEquipmentDetail(dialog, equipment)
    }

    async function submitBorrowApplication(event){
        event.preventDefault()
        const form = event.currentTarget
        const startTime = form.elements.borrowStartTime.value
        const endTime = form.elements.borrowEndTime.value

        // datetime-local 可以直接按字符串比较，格式固定且精度相同。
        if(endTime <= startTime){
            Toast.warning('结束时间必须晚于开始时间')
            form.elements.borrowEndTime.focus()
            return
        }

        const submitButton = form.querySelector('.borrow-submit-button')
        submitButton.disabled = true
        submitButton.textContent = '提交中...'
        const result = await createBorrowRecord({
            equipmentId: activeEquipmentId,
            borrowStartTime: formatLocalDateTime(startTime),
            borrowEndTime: formatLocalDateTime(endTime),
            purpose: form.elements.purpose.value.trim() || null
        })
        submitButton.disabled = false
        submitButton.textContent = '提交申请'

        if(!result) return
        Toast.success('借用申请已提交')
        form.closest('dialog').close()
        const recordViewAlreadyMounted = Boolean(document.querySelector('#record-view'))
        document.querySelector('#my-record-button').click()
        if(recordViewAlreadyMounted){
            document.dispatchEvent(new CustomEvent('borrow-record-created'))
        }
    }

    function handleCardActivation(event){
        const card = event.target.closest('.data-card[data-equipment-id]')
        if(!card) return
        openEquipmentDetail(Number(card.dataset.equipmentId))
    }

    document.addEventListener('click', handleCardActivation)
    document.addEventListener('keydown', event => {
        if(event.key !== 'Enter' && event.key !== ' ') return
        const card = event.target.closest('.data-card[data-equipment-id]')
        if(!card) return
        event.preventDefault()
        openEquipmentDetail(Number(card.dataset.equipmentId))
    })
})()
