const studentLogin  = document.getElementById('student-choose')
const adminLogin = document.getElementById('admin-choose');
const repairLogin = document.getElementById('repair-choose');

const registerButton = document.getElementById('register-button')
const submitButton = document.getElementById('submit-button');

const account = document.getElementById(`account`)
const password = document.getElementById(`password`)
const loginForm = document.getElementById('login-form')
const passwordToggle = document.getElementById('password-toggle')
const registerDialog = document.getElementById('register-dialog')
const registerForm = document.getElementById('register-form')
const registerTitle = document.getElementById('register-title')
const registerAccount = document.getElementById('register-account')
const registerPassword = document.getElementById('register-password')
const registerPasswordConfirm = document.getElementById('register-password-confirm')
const registerCodeField = document.getElementById('register-code-field')
const registerCode = document.getElementById('register-code')
const registerSubmit = document.getElementById('register-submit')
const registerClose = document.getElementById('register-close')
const registerCancel = document.getElementById('register-cancel')

let identity = 1;
let registeringIdentity = 1;

// 重置身份和样式
function resetIdentity(){
    ;[studentLogin, adminLogin, repairLogin].forEach(option => {
        option.classList.remove('is-active')
        option.setAttribute('aria-checked', 'false')
    })
}

// 完成字符 -> 身份映射
/**
 * 
 * @param {HTMLElement} target 
 * @returns 
 */
function showIdentity(target){

    if(target === studentLogin){
        return 1;
    }
    else if(target === adminLogin){
        return 2;
    }
    else if(target === repairLogin){
        return 3;
    }
}

// 选择身份和样式
/**
 * 
 * @param {HTMLElement} target 
 */
function chooseIdentity(target){
    resetIdentity();
    target.classList.add('is-active');
    target.setAttribute('aria-checked', 'true')
    identity = showIdentity(target);
}

function identityName(identityValue){
    return {1: '学生', 2: '管理员', 3: '维修人员'}[identityValue]
}

function identityApi(identityValue){
    return {1: 'user', 2: 'admin', 3: 'repair'}[identityValue]
}

function openRegisterDialog(){
    registeringIdentity = identity
    const isAdmin = registeringIdentity === 2
    registerForm.reset()
    registerTitle.textContent = `注册${identityName(registeringIdentity)}账号`
    registerCodeField.hidden = !isAdmin
    registerCode.required = isAdmin
    registerDialog.showModal()
    registerAccount.focus()
}

function closeRegisterDialog(){
    registerDialog.close()
}

// 注册
async function register(){
    const checkedAccount = checkAccount(registerAccount)
    const checkedPassword = checkPassword(registerPassword)

    if(checkedAccount !== false && checkedPassword !== false){
        if(checkedPassword !== registerPasswordConfirm.value){
            alert('两次输入的密码不一致')
            registerPasswordConfirm.focus()
            return false
        }
        if(registeringIdentity === 2 && !registerCode.value.trim()){
            alert('请输入管理员注册码')
            registerCode.focus()
            return false
        }
        return await sendRegister(
            checkedAccount,
            checkedPassword,
            identityApi(registeringIdentity),
            registerCode.value.trim()
        )
    }else{
        return false;
    }

}

//登录
async function submit(){
    return await sendSubmit(account.value,password.value,apiChoose())
}



studentLogin.addEventListener('click',async () => chooseIdentity(studentLogin))
repairLogin.addEventListener('click',async () => chooseIdentity(repairLogin))
adminLogin.addEventListener('click',async () => chooseIdentity(adminLogin))

registerButton.addEventListener('click', openRegisterDialog)
registerClose.addEventListener('click', closeRegisterDialog)
registerCancel.addEventListener('click', closeRegisterDialog)
registerDialog.addEventListener('click', event => {
    if(event.target === registerDialog) closeRegisterDialog()
})
registerForm.addEventListener('submit', async event => {
    event.preventDefault()
    registerSubmit.disabled = true
    registerSubmit.textContent = '注册中...'
    if(await register() === true){
        alert("注册成功")
        closeRegisterDialog()
    }
    registerSubmit.disabled = false
    registerSubmit.textContent = '确认注册'
})
loginForm.addEventListener('submit', async event => {
    event.preventDefault()
    if(await submit() === true){
        alert("登录成功")
        window.location.replace(`/campus-equipment-mgr/frontend/pages/${apiChoose()}.html`)
    }
})

passwordToggle.addEventListener('click', () => {
    const shouldShow = password.type === 'password'
    password.type = shouldShow ? 'text' : 'password'
    passwordToggle.textContent = shouldShow ? '隐藏' : '显示'
    passwordToggle.setAttribute('aria-label', shouldShow ? '隐藏密码' : '显示密码')
})
