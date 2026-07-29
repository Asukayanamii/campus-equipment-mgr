// 默认颜色
const DEFAULT_COLOR = ''
// 点击后颜色
const DEFAULT_TARGET_COLOR = 'green'
const ACCOUNT_RULE = /^[a-zA-Z0-9_]{6,24}$/
const ACCOUNR_RULE_DECRIPTION = "字母或数字或下划线 ，长度在6-24"
const PASSWORD_RULE = /^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9_\!@#\$%\^&\*\(\)\-=]{6,24}$/
const PASSWORD_RULE_DECRIPTION = "6-24 位，至少 1 个字母、至少 1 个数字，支持常用符号"

const studentLogin  = document.getElementById('student-choose')
const managerLogin = document.getElementById('manager-choose');
const maintainerLogin = document.getElementById('maintainer-choose');

const registerButton = document.getElementById('register-button')
const submitButton = document.getElementById('submit-button');

const account = document.getElementById(`account`)
const password = document.getElementById(`password`)

let identity = 1;
studentLogin.style.backgroundColor = `${DEFAULT_TARGET_COLOR}`;

// 重置身份和样式
function resetIdentity(){
    studentLogin.style.backgroundColor = `${DEFAULT_COLOR}`
    managerLogin.style.backgroundColor = `${DEFAULT_COLOR}`
    submitButton.style.backgroundColor = `${DEFAULT_COLOR}`
}

// 完成字符 -> 身份映射
/**
 * 
 * @param {HTMLElement} target 
 * @returns 
 */
function showIdentity(target){

    if(target.innerText === `我是学生`){
        return 1;
    }
    else if(target.innerText === `我是管理`){
        return 2;
    }
    else if(target.innerText === `我是维修`){
        return 3;
    }
}

// 选择身份和样式
function chooseIdentity(target){
    resetIdentity();
    target.style.backgroundColor = `${DEFAULT_TARGET_COLOR}`;
    identity = showIdentity(target);
}

// 身份映射到接口
function apiChoose(){
    if(identity === 1){
        return `/user`
    }else if(identity === 2){
        return `/repair`
    }else if(identity ===3){
        return `/admin`
    }
}

// 注册
function register(){

    if(checkAccount !==false && checkPassword() !== false){
        sendRegister(checkAccount(),checkPassword(),apiChoose());
    }else{
        return;
    }

}

//验证账号是否合规
function checkAccount(){
    const stringAccount = account.value;
    if(ACCOUNT_RULE.test(stringAccount) === false){
        alert(`您提交的账号不符合要求，必须满足${ACCOUNR_RULE_DECRIPTION}`);
        return false;
    }
    return stringAccount;
}

//验证密码是否合规
function checkPassword(){
    const stringPassword = password.value;
    if(PASSWORD_RULE.test(stringPassword) === false){
        alert(`您提交的密码不符合要求，必须满足${PASSWORD_RULE_DECRIPTION}`);
        return false;
    }
    return stringPassword;
}



