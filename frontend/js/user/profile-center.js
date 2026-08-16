(function(){
    const FALLBACK_AVATAR = '../assets/images/all-icon..png'

    function createProfileDialog(){
        const dialog = document.createElement('dialog')
        dialog.className = 'profile-center-dialog'
        dialog.innerHTML = `
            <form class="profile-center-form">
                <header class="profile-center-heading">
                    <div><p>个人中心</p><h2>账号资料</h2></div>
                    <button class="profile-center-close" type="button" aria-label="关闭">×</button>
                </header>
                <div class="profile-center-loading" role="status">正在加载个人资料...</div>
                <div class="profile-center-content" hidden>
                    <section class="profile-avatar-section">
                        <img class="profile-avatar-preview" alt="当前头像">
                        <div>
                            <label class="profile-avatar-picker">选择头像
                                <input class="profile-avatar-input" type="file" accept="image/*">
                            </label>
                            <p class="profile-avatar-status">选择后将立即上传</p>
                        </div>
                    </section>
                    <dl class="profile-account-info">
                        <div><dt>用户 ID</dt><dd data-field="id"></dd></div>
                        <div><dt>账号</dt><dd data-field="username"></dd></div>
                        <div><dt>创建时间</dt><dd data-field="createTime"></dd></div>
                        <div><dt>更新时间</dt><dd data-field="updateTime"></dd></div>
                    </dl>
                    <label class="profile-field">姓名
                        <input name="name" type="text" minlength="2" maxlength="12" required>
                    </label>
                    <label class="profile-field">密码
                        <input name="password" type="password" minlength="6" maxlength="24" autocomplete="new-password" placeholder="请输入当前密码或新密码" required>
                    </label>
                    <div class="profile-center-actions">
                        <button class="profile-logout-button" type="button">退出登录</button>
                        <button class="profile-save-button" type="submit">保存资料</button>
                    </div>
                </div>
            </form>
        `
        document.body.appendChild(dialog)
        return dialog
    }

    async function openProfileCenter(){
        if(document.querySelector('.profile-center-dialog')) return
        const dialog = createProfileDialog()
        dialog.showModal()

        const close = () => dialog.close()
        dialog.querySelector('.profile-center-close').addEventListener('click', close)
        dialog.addEventListener('click', event => {
            if(event.target === dialog) close()
        })
        dialog.addEventListener('close', () => dialog.remove())

        const profile = await getPersonalData('user')
        if(!profile){
            close()
            return
        }
        initializeProfileForm(dialog, profile)
    }

    function initializeProfileForm(dialog, profile){
        const form = dialog.querySelector('form')
        const avatar = dialog.querySelector('.profile-avatar-preview')
        const avatarInput = dialog.querySelector('.profile-avatar-input')
        const avatarStatus = dialog.querySelector('.profile-avatar-status')
        let avatarUrl = profile.image || null
        let avatarUploading = false

        avatar.src = avatarUrl || FALLBACK_AVATAR
        form.elements.name.value = profile.name || ''
        ;['id', 'username', 'createTime', 'updateTime'].forEach(field => {
            dialog.querySelector(`[data-field="${field}"]`).textContent = profile[field] || '暂无'
        })

        avatarInput.addEventListener('change', async () => {
            const file = avatarInput.files[0]
            if(!file) return
            avatarUploading = true
            avatarInput.disabled = true
            avatarStatus.textContent = '上传中...'
            const url = await uploadImage(file)
            if(url){
                avatarUrl = url
                avatar.src = url
                avatarStatus.textContent = '头像已上传，保存资料后生效'
            }else{
                avatarStatus.textContent = '上传失败，请重新选择'
            }
            avatarUploading = false
            avatarInput.disabled = false
            avatarInput.value = ''
        })

        form.addEventListener('submit', async event => {
            event.preventDefault()
            if(avatarUploading){
                Toast.warning('头像仍在上传，请稍候')
                return
            }
            if(!checkPassword(form.elements.password)) return

            const saveButton = form.querySelector('.profile-save-button')
            saveButton.disabled = true
            saveButton.textContent = '保存中...'
            const saved = await changePersonalData({
                name: form.elements.name.value.trim(),
                password: form.elements.password.value,
                image: avatarUrl
            }, 'user')
            saveButton.disabled = false
            saveButton.textContent = '保存资料'
            if(!saved) return

            Toast.success('个人资料已更新')
            dialog.close()
            document.dispatchEvent(new CustomEvent('profile-updated'))
        })

        dialog.querySelector('.profile-logout-button').addEventListener('click', () => {
            if(!window.confirm('确认退出当前账号吗？')) return
            clearAuthSession()
            window.location.replace('../login.html')
        })
        dialog.querySelector('.profile-center-loading').hidden = true
        dialog.querySelector('.profile-center-content').hidden = false
    }

    document.getElementById('profile-picture-box').addEventListener('click', openProfileCenter)
})()
