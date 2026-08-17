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
                        <div><dt>邮箱</dt><dd data-field="email"></dd></div>
                        <div><dt>创建时间</dt><dd data-field="createTime"></dd></div>
                        <div><dt>更新时间</dt><dd data-field="updateTime"></dd></div>
                    </dl>
                    <label class="profile-field">姓名
                        <input name="name" type="text" minlength="2" maxlength="12" required>
                    </label>
                    <label class="profile-field">原密码
                        <input name="password" type="password" minlength="6" maxlength="24" autocomplete="current-password" placeholder="不修改密码时留空">
                    </label>
                    <label class="profile-field">新密码
                        <input name="newPassword" type="password" minlength="6" maxlength="24" autocomplete="new-password" placeholder="不修改密码时留空">
                    </label>
                    <label class="profile-field">确认新密码
                        <input name="confirmNewPassword" type="password" minlength="6" maxlength="24" autocomplete="new-password" placeholder="不修改密码时留空">
                    </label>
                    <section class="profile-email-binding">
                        <h3>邮箱绑定</h3>
                        <p class="profile-email-status">绑定后可使用邮箱验证码登录。</p>
                        <label class="profile-field">邮箱
                            <input name="bindingEmail" type="email" maxlength="64" autocomplete="email" placeholder="请输入要绑定的邮箱">
                        </label>
                        <label class="profile-field">验证码
                            <span class="profile-email-code"><input name="bindingCode" type="text" inputmode="numeric" maxlength="6" placeholder="请输入六位验证码"><button class="profile-send-code" type="button">发送验证码</button></span>
                        </label>
                        <button class="profile-bind-email" type="button">确认绑定邮箱</button>
                    </section>
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
        ;['id', 'username', 'email', 'createTime', 'updateTime'].forEach(field => {
            dialog.querySelector(`[data-field="${field}"]`).textContent = profile[field] || '暂无'
        })
        const emailBindingSection = dialog.querySelector('.profile-email-binding')
        if(profile.email) emailBindingSection.remove()

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
            const currentPassword = form.elements.password.value
            const newPassword = form.elements.newPassword.value
            const confirmNewPassword = form.elements.confirmNewPassword.value
            const updateData = {
                name: form.elements.name.value.trim(),
                image: avatarUrl
            }
            if(currentPassword || newPassword || confirmNewPassword){
                if(!currentPassword){
                    Toast.warning('修改密码时请输入原密码')
                    return
                }
                if(!newPassword){
                    Toast.warning('请输入新密码')
                    return
                }
                if(!checkPassword(form.elements.newPassword)) return
                if(newPassword !== confirmNewPassword){
                    Toast.warning('两次输入的新密码不一致')
                    return
                }
                // 未修改密码时不发送密码字段，后端不会触发原密码校验。
                updateData.password = currentPassword
                updateData.newPassword = newPassword
            }

            const saveButton = form.querySelector('.profile-save-button')
            saveButton.disabled = true
            saveButton.textContent = '保存中...'
            const saved = await changePersonalData(updateData, 'user')
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
        if(!profile.email){
            const bindingEmail = form.elements.bindingEmail
            const bindingCode = form.elements.bindingCode
            const bindingStatus = dialog.querySelector('.profile-email-status')
            const sendCodeButton = dialog.querySelector('.profile-send-code')
            const bindEmailButton = dialog.querySelector('.profile-bind-email')
            let codeCountdownTimer = null
            const startCodeCountdown = () => {
                let remaining = 60
                sendCodeButton.textContent = `${remaining}s 后重发`
                codeCountdownTimer = window.setInterval(() => {
                    remaining -= 1
                    sendCodeButton.textContent = remaining ? `${remaining}s 后重发` : '发送验证码'
                    if(remaining > 0) return
                    window.clearInterval(codeCountdownTimer)
                    codeCountdownTimer = null
                    sendCodeButton.disabled = false
                }, 1000)
            }
            dialog.addEventListener('close', () => {
                if(codeCountdownTimer) window.clearInterval(codeCountdownTimer)
            })
            sendCodeButton.addEventListener('click', async () => {
                const email = bindingEmail.value.trim()
                if(!email || !bindingEmail.checkValidity()){
                    Toast.warning('请输入合法邮箱')
                    return
                }
                sendCodeButton.disabled = true
                sendCodeButton.textContent = '发送中...'
                const sent = await sendEmailBindingVerificationCode(email)
                if(sent){
                    bindingStatus.textContent = '验证码已发送，请在有效期内完成绑定。'
                    startCodeCountdown()
                }else{
                    sendCodeButton.disabled = false
                    sendCodeButton.textContent = '发送验证码'
                }
            })
            bindEmailButton.addEventListener('click', async () => {
                const email = bindingEmail.value.trim()
                const verificationCode = bindingCode.value.trim()
                if(!email || !bindingEmail.checkValidity()){
                    Toast.warning('请输入合法邮箱')
                    return
                }
                if(!/^\d{6}$/.test(verificationCode)){
                    Toast.warning('请输入六位数字验证码')
                    return
                }
                bindEmailButton.disabled = true
                bindEmailButton.textContent = '绑定中...'
                const bound = await bindEmail(email, verificationCode)
                bindEmailButton.disabled = false
                bindEmailButton.textContent = '确认绑定邮箱'
                if(!bound) return
                profile.email = email
                dialog.querySelector('[data-field="email"]').textContent = email
                if(codeCountdownTimer) window.clearInterval(codeCountdownTimer)
                // 邮箱已绑定，移除绑定组件以避免重复绑定。
                emailBindingSection.remove()
                Toast.success('邮箱绑定成功')
            })
        }
        dialog.querySelector('.profile-center-loading').hidden = true
        dialog.querySelector('.profile-center-content').hidden = false
    }

    document.getElementById('profile-picture-box').addEventListener('click', openProfileCenter)
})()
