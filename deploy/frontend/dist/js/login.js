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
const registerCodeLabel = document.getElementById('register-code-label')
const registerCode = document.getElementById('register-code')
const registerSubmit = document.getElementById('register-submit')
const registerClose = document.getElementById('register-close')
const registerCancel = document.getElementById('register-cancel')
const emailLoginPanel = document.getElementById('email-login-panel')
const emailLoginToggle = document.getElementById('email-login-toggle')
const sendCodeButton = document.getElementById('send-code-button')
let emailLoginMode = false

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
    if(identity !== 1){
        emailLoginMode = false
        emailLoginPanel.hidden = true
        emailLoginToggle.hidden = true
        document.querySelector('.input-data').hidden = false
        account.disabled = false
        password.disabled = false
    } else {
        emailLoginToggle.hidden = false
    }
    prepareRoleLogin(identityApi(identity))
}

function identityName(identityValue){
    return {1: '学生', 2: '管理员', 3: '维修人员'}[identityValue]
}

function identityApi(identityValue){
    return {1: 'user', 2: 'admin', 3: 'repair'}[identityValue]
}

function openRegisterDialog(){
    registeringIdentity = identity
    const requiresRegistrationCode = registeringIdentity === 2 || registeringIdentity === 3
    registerForm.reset()
    registerTitle.textContent = `注册${identityName(registeringIdentity)}账号`
    registerCodeField.hidden = !requiresRegistrationCode
    registerCode.required = requiresRegistrationCode
    registerCodeLabel.textContent = registeringIdentity === 3 ? '维修员注册码' : '管理员注册码'
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
            Toast.warning('两次输入的密码不一致')
            registerPasswordConfirm.focus()
            return false
        }
        if((registeringIdentity === 2 || registeringIdentity === 3) && !registerCode.value.trim()){
            Toast.warning(`请输入${registerCodeLabel.textContent}`)
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
    if(emailLoginMode) return await submitEmailLogin(document.getElementById('login-email').value.trim(), document.getElementById('login-code').value.trim())
    return await sendSubmit(account.value,password.value,apiChoose())
}

emailLoginToggle.addEventListener('click', () => {
    if(identity !== 1) return
    emailLoginMode = !emailLoginMode
    emailLoginPanel.hidden = !emailLoginMode
    document.querySelector('.input-data').hidden = emailLoginMode
    // 邮箱登录时禁用隐藏的必填输入框，避免浏览器原生校验阻止表单提交。
    account.disabled = emailLoginMode
    password.disabled = emailLoginMode
    emailLoginToggle.textContent = emailLoginMode ? '使用账号密码登录' : '使用邮箱验证码登录'
})

sendCodeButton.addEventListener('click', async () => {
    const email = document.getElementById('login-email').value.trim()
    if(!email) { Toast.warning('请输入邮箱'); return }
    sendCodeButton.disabled = true
    if(await sendEmailVerificationCode(email)){
        let remaining = 60
        sendCodeButton.textContent = `${remaining}s后重发`
        const timer = setInterval(() => { remaining -= 1; sendCodeButton.textContent = remaining ? `${remaining}s后重发` : '发送验证码'; if(!remaining){clearInterval(timer); sendCodeButton.disabled = false} }, 1000)
    } else sendCodeButton.disabled = false
})



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
        Toast.success("注册成功")
        closeRegisterDialog()
    }
    registerSubmit.disabled = false
    registerSubmit.textContent = '确认注册'
})
loginForm.addEventListener('submit', async event => {
    event.preventDefault()
    const button = document.getElementById('submit-button')
    if(button.disabled) return
    button.disabled = true
    button.textContent = '登录中...'
    try {
        if(await submit() === true){
            Toast.nextPage("登录成功")
            const targetPage = `./pages/${apiChoose()}.html`
            window.location.replace(targetPage)
        }
    } finally {
        button.disabled = false
        button.textContent = '登录'
    }
})

passwordToggle.addEventListener('click', () => {
    const shouldShow = password.type === 'password'
    password.type = shouldShow ? 'text' : 'password'
    passwordToggle.textContent = shouldShow ? '隐藏' : '显示'
    passwordToggle.setAttribute('aria-label', shouldShow ? '隐藏密码' : '显示密码')
})
