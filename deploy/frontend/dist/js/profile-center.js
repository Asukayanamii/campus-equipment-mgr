(function(){
    const role = protectedPageRole()
    if(role !== 'admin' && role !== 'repair') return
    const trigger = document.getElementById('profile-picture-box')
    if(!trigger) return

    // 替换节点可解除旧 index.js 已绑定的个人中心监听，避免新旧弹窗同时打开。
    const cleanTrigger = trigger.cloneNode(true)
    trigger.replaceWith(cleanTrigger)
    cleanTrigger.addEventListener('click', open)
    refreshNavigationProfile()

    async function refreshNavigationProfile(){
        const data = await getPersonalData(role)
        if(!data) return
        cleanTrigger.querySelector('img').src = data.image || '../assets/images/all-icon..png'
        document.getElementById('profile-name').textContent = data.name || data.username
    }

    async function open(){
        if(document.querySelector('.role-profile-dialog')) return
        const dialog=document.createElement('dialog');dialog.className='role-profile-dialog';dialog.innerHTML='<form><header><div><p>个人中心</p><h2>账号资料</h2></div><button class="profile-close" type="button">×</button></header><p class="profile-loading">加载中...</p><div class="profile-content" hidden><section class="profile-avatar"><img alt="当前头像"><div><label>选择头像<input type="file" accept="image/*"></label><p>选择后立即上传</p></div></section><dl><div><dt>用户 ID</dt><dd data-field="id"></dd></div><div><dt>账号</dt><dd data-field="username"></dd></div></dl><label class="profile-input">姓名<input name="name" minlength="2" maxlength="12" required></label><label class="profile-input">原密码<input name="password" type="password" minlength="6" maxlength="24" autocomplete="current-password" placeholder="不修改密码时留空"></label><label class="profile-input">新密码<input name="newPassword" type="password" minlength="6" maxlength="24" autocomplete="new-password" placeholder="不修改密码时留空"></label><label class="profile-input">确认新密码<input name="confirmNewPassword" type="password" minlength="6" maxlength="24" autocomplete="new-password" placeholder="不修改密码时留空"></label><footer><button class="profile-logout" type="button">退出登录</button><button class="profile-save" type="submit">保存资料</button></footer></div></form>'
        document.body.appendChild(dialog);dialog.querySelector('.profile-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>dialog.remove());dialog.showModal()
        const data=await getPersonalData(role);if(!data){dialog.close();return}initialize(dialog,data)
    }
    function initialize(dialog,data){
        const form=dialog.querySelector('form'),avatar=dialog.querySelector('.profile-avatar img'),fileInput=dialog.querySelector('[type=file]');let image=data.image||null,uploading=false
        avatar.src=image||'../assets/images/all-icon..png';form.elements.name.value=data.name||'';dialog.querySelector('[data-field=id]').textContent=data.id;dialog.querySelector('[data-field=username]').textContent=data.username
        fileInput.addEventListener('change',async()=>{const file=fileInput.files[0];if(!file)return;uploading=true;fileInput.disabled=true;const url=await uploadImage(file);if(url){image=url;avatar.src=url}uploading=false;fileInput.disabled=false;fileInput.value=''})
        form.addEventListener('submit',async e=>{e.preventDefault();if(uploading){Toast.warning('头像仍在上传');return}const currentPassword=form.elements.password.value,newPassword=form.elements.newPassword.value,confirmNewPassword=form.elements.confirmNewPassword.value,updateData={name:form.elements.name.value.trim(),image};if(currentPassword||newPassword||confirmNewPassword){if(!currentPassword){Toast.warning('修改密码时请输入原密码');return}if(!newPassword){Toast.warning('请输入新密码');return}if(!checkPassword(form.elements.newPassword))return;if(newPassword!==confirmNewPassword){Toast.warning('两次输入的新密码不一致');return}updateData.password=currentPassword;updateData.newPassword=newPassword}const button=form.querySelector('.profile-save');button.disabled=true;const ok=await changePersonalData(updateData,role);if(ok){Toast.success('个人资料已更新');sessionStorage.setItem('name',form.elements.name.value.trim());document.getElementById('profile-name').textContent=form.elements.name.value.trim();document.getElementById('profile-picture').src=image||'../assets/images/all-icon..png';dialog.close()}else button.disabled=false})
        dialog.querySelector('.profile-logout').addEventListener('click',()=>{if(!confirm('确认退出当前账号吗？'))return;clearAuthSession();location.replace('../login.html')});dialog.querySelector('.profile-loading').hidden=true;dialog.querySelector('.profile-content').hidden=false
    }
})()
