// 默认颜色
const DEFAULT_COLOR = ''
const DEFAULT_TARGET_COLOR = 'green'

const studentLogin  = document.getElementById('student-choose')
const managerLogin = document.getElementById('manager-choose');
const maintainerLogin = document.getElementById('maintainer-choose');
const submitButton = document.getElementById('submit-button');

let identity = '';
studentLogin.style.backgroundColor = `${DEFAULT_TARGET_COLOR}`;

function resetIdentity(){
    studentLogin.style.backgroundColor = `${DEFAULT_COLOR}`
    managerLogin.style.backgroundColor = `${DEFAULT_COLOR}`
    submitButton.style.backgroundColor = `${DEFAULT_COLOR}`
}

function chooseIdentity(target){
    resetIdentity();
    target.style.backgroundColor = `${DEFAULT_TARGET_COLOR}`;

}




