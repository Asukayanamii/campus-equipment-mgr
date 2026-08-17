(function(){
    const RETURNABLE_STATUSES = new Set(['borrowed', '已借出', '借用中'])

    function canReturn(status){
        return RETURNABLE_STATUSES.has(status)
    }

    function addReturnAction(record){
        const detailWindow = document.querySelector('.record-detail-window')
        if(!detailWindow || !canReturn(record.status)) return

        const button = document.createElement('button')
        button.type = 'button'
        button.className = 'open-return-dialog-button'
        button.textContent = '归还设备'
        button.addEventListener('click', () => openReturnDialog(record))
        detailWindow.appendChild(button)
    }

    function openReturnDialog(record){
        const dialog = document.createElement('dialog')
        dialog.className = 'borrow-return-dialog'
        dialog.innerHTML = `
            <form class="borrow-return-form">
                <div class="return-dialog-heading">
                    <div>
                        <p>设备归还</p>
                        <h2 class="return-equipment-name"></h2>
                    </div>
                    <button class="return-dialog-close" type="button" aria-label="关闭">×</button>
                </div>
                <fieldset class="return-status-field">
                    <legend>归还状态</legend>
                    <label><input type="radio" name="returnStatus" value="normal" checked><span>正常</span></label>
                    <label><input type="radio" name="returnStatus" value="damaged"><span>损坏</span></label>
                </fieldset>
                <label class="return-field">归还说明
                    <textarea name="returnRemark" maxlength="1000" rows="3" placeholder="可填写归还说明"></textarea>
                </label>
                <section class="damage-return-fields" hidden>
                    <label class="return-field">损坏说明
                        <textarea name="damageDescription" maxlength="2000" rows="4" placeholder="请描述设备损坏情况"></textarea>
                    </label>
                    <label class="return-field">损坏图片（最多 9 张）
                        <input class="damage-image-input" type="file" accept="image/*" multiple>
                    </label>
                    <div class="image-upload-preview" aria-live="polite"></div>
                </section>
                <div class="return-dialog-actions">
                    <button class="return-cancel-button" type="button">取消</button>
                    <button class="return-submit-button" type="submit">确认归还</button>
                </div>
            </form>
        `
        document.body.appendChild(dialog)
        dialog.querySelector('.return-equipment-name').textContent = record.equipmentName || '当前设备'

        const form = dialog.querySelector('form')
        const damageFields = dialog.querySelector('.damage-return-fields')
        const uploader = createImageUploadController({
            input: dialog.querySelector('.damage-image-input'),
            preview: dialog.querySelector('.image-upload-preview'),
            maxCount: 9
        })

        function close(){ dialog.close() }
        dialog.querySelector('.return-dialog-close').addEventListener('click', close)
        dialog.querySelector('.return-cancel-button').addEventListener('click', close)
        dialog.addEventListener('click', event => {
            if(event.target === dialog) close()
        })
        dialog.addEventListener('close', () => dialog.remove())
        form.addEventListener('change', event => {
            if(event.target.name !== 'returnStatus') return
            const damaged = event.target.value === 'damaged'
            damageFields.hidden = !damaged
            if(!damaged){
                form.elements.damageDescription.value = ''
                uploader.clear()
            }
        })
        form.addEventListener('submit', event => submitReturn(event, record, uploader))
        dialog.showModal()
    }

    async function submitReturn(event, record, uploader){
        event.preventDefault()
        const form = event.currentTarget
        const returnStatus = form.elements.returnStatus.value
        const damaged = returnStatus === 'damaged'
        const damageDescription = form.elements.damageDescription.value.trim()
        const damageImages = uploader.getUrls()

        if(uploader.isUploading()){
            Toast.warning('图片仍在上传，请稍候')
            return
        }
        if(damaged && !damageDescription){
            Toast.warning('请填写损坏说明')
            form.elements.damageDescription.focus()
            return
        }
        if(damaged && damageImages.length === 0){
            Toast.warning('损坏归还至少需要一张图片')
            return
        }
        if(!window.confirm(damaged
            ? '损坏归还会自动创建报修记录，确认提交吗？'
            : '确认设备已正常归还吗？')) return

        const submitButton = form.querySelector('.return-submit-button')
        submitButton.disabled = true
        submitButton.textContent = '提交中...'
        const result = await submitBorrowReturn(record.id, {
            returnStatus,
            returnRemark: form.elements.returnRemark.value.trim() || null,
            ...(damaged ? { damageDescription, damageImages } : {})
        })
        submitButton.disabled = false
        submitButton.textContent = '确认归还'
        if(!result) return

        Toast.success(damaged ? '归还成功，已生成报修记录' : '设备归还成功')
        form.closest('dialog').close()
        document.querySelector('.record-detail-window')?.remove()
        document.querySelector('.dim-overlay')?.remove()
        document.dispatchEvent(new CustomEvent('borrow-returned', { detail: { damaged } }))
    }

    document.addEventListener('record-detail-opened', event => {
        if(event.detail.recordType === 'borrow') addReturnAction(event.detail.record)
    })
})()
