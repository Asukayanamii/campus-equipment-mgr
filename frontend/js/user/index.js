const PAGE_SIZE = 24;
const DEFAULT_NAME = '代文秋'
const OFF_SETX = 0
const OFF_SETY = 0
const dataShowing = document.getElementById(`data-showing`)

const profilePictureBox = document.getElementById('profile-picture-box')

const profileName = document.getElementById('profile-name')
const profilePicture = document.getElementById('profile-picture')

const start = document.getElementById('start')
const pre2 = document.getElementById('pre-2')
const pre1 = document.getElementById('pre-1')
const cur = document.getElementById('cur')
const aft1 = document.getElementById('aft-1')
const aft2 = document.getElementById('aft-2')
const end = document.getElementById('end')

const dataCard = document.getElementById('data-showing') 

let pageNow = 1;
let pageAll = 1;
const identity = 1
const defaultQueryData = new QueryData({
    page : pageNow,
    size : PAGE_SIZE
});

// 检查按钮重复，务必在pageAll有数值的时候使用
function checkButton(){
    start.style.display = 'block'
    pre2.style.display = 'block'
    pre1.style.display = 'block'
    end.style.display = 'block'
    aft2.style.display = 'block'
    aft1.style.display = 'block'
    switch (Number(cur.innerHTML)){
        case 1 :
            start.style.display = 'none'
            pre2.style.display = 'none'
            pre1.style.display = 'none'
            break
        case 2 :
            pre2.style.display = 'none'
            pre1.style.display = 'none'
            break
        case 3 :
            pre2.style.display = 'none'
            break
    }

    switch(Number(cur.innerText)){
        case pageAll -2:
            end.style.display = 'none'
            break
        case pageAll - 1:
            end.style.display = 'none'
            aft2.style.display = 'none'
            break
        case pageAll :
            end.style.display = 'none'
            aft2.style.display = 'none'
            aft1.style.display = 'none'
            break
    }
    

}

// 给按钮赋值，务必在pageAll有数值的时候使用
function renderButton(){
    start.innerText = 1
    pre2.innerText = pageNow - 2
    pre1.innerText = pageNow - 1
    cur.innerText = pageNow
    aft1.innerText = pageNow + 1
    aft2.innerText = pageNow + 2
    end.innerText = pageAll
    cur.style.backgroundColor = 'red'
}

// 渲染数据
function renderData(QueryData = {}){
    getData(QueryData).then(res => {
        const list = res.data.items;
        dataShowing.innerHTML = ''
        list.forEach(i => {
            dataShowing.insertAdjacentHTML('beforeend',`
                <div class="data-card" style = " background-image: url(${i.coverImg})">
                    <h1>${i.equipmentName}</h1>
                    <p>${i.location}</p>
                    <div class="data-detail-showing">
                        <p>设备 ID${i.id}</p>
                        <p>设备编号${i.equipmentNo}</p>
                        <p>设备分类名称${i.categoryName}</p>
                        <p>设备规格型号 ID${i.spec}</p>
                        <p>设备品牌${i.brand}</p>
                        <p>计量单位${i.unit}</p>
                        <p>采购日期${i.purchaseDate}</p>
                        <p>采购价格${i.price}</p>
                        <p>设备状态${i.status}</p>
                        <p>备注${i.remark}</p>
                        <p>创建时间${i.creatTime}</p>
                        <p>更新时间${i.updateTime}</p>
                        <p> ${i.coverImg}</p>
                    </div>
                </div>
            `)
            
            
            
        });
        pageAll = res.data.pages;
        renderButton()
        checkButton()
    })
}

// 渲染个人信息
async function renderPersonalData(){
    const personalData = await getPersonalData(apiChoose())



    if(!personalData.name){
        profileName.innerText = `${DEFAULT_NAME}`
    }else{
        profileName.innerText = personalData.name
    }
    
    if(!personalData.image){
        profilePicture.src = '../assets/images/all-icon..png'
    }else{
        profilePicture.src = personalData.image
    }
}

// 渲染详情和修改面板
async function renderChangePanel(){
    const personalData = await getPersonalData(apiChoose())
    document.body.insertAdjacentHTML('beforeend',`
        <div class="change-panel">
        <div class="profile-detail-showing">
            <img src="${personalData.image}" alt="你的头像">
            <p>你的id:${personalData.id}</p>
            <p>你的昵称:${personalData.name}</p>
            <p>你的账号:${personalData.username}</p>
            <p>你的邮箱:${personalData.email}</p>
            <p>上传更新时间:${personalData.updateTime}</p>
            <p>账号创建时间:${personalData.createTime}</p>
        </div>
    </div>
        `)
}


start.addEventListener('click', () =>{
     defaultQueryData.page = 1;
     pageNow = 1
     renderData(defaultQueryData)
})

end.addEventListener('click',() => {
    defaultQueryData.page = pageAll
    pageNow = pageAll
    renderData(defaultQueryData)
})

pre2.addEventListener('click' ,() => {
    defaultQueryData.page = pre2.innerText
    pageNow = pageNow - 2
    renderData(defaultQueryData)
})

pre1.addEventListener('click' ,() => {
    defaultQueryData.page = pre1.innerText
    pageNow = pageNow - 1
    renderData(defaultQueryData)
})

cur.addEventListener('click' ,() => {
    defaultQueryData.page = cur.innerText
    pageNow = pageNow
    renderData(defaultQueryData)
})

aft1.addEventListener('click' ,() => {
    defaultQueryData.page = aft1.innerText
    pageNow = pageNow + 1
    renderData(defaultQueryData)
})

aft2.addEventListener('click' ,() => {
    defaultQueryData.page = aft2.innerText
    pageNow = pageNow + 2
    renderData(defaultQueryData)
})

dataCard.addEventListener('mousemove', (e) => {
    const card = e.target.closest('.data-card')
    if (!card) return 
    const dataDetailShowing = card.querySelector('.data-detail-showing')
    // TODO:硬编码问题，有时间我就来修
    const maxWidth = window.innerWidth
    const maxHeigt = window.innerHeight
    if(e.clientX + OFF_SETX +100> maxWidth){
        dataDetailShowing.style.left = ( e.clientX + OFF_SETX -100) + 'px'
    }else{
        dataDetailShowing.style.left = (e.clientX + OFF_SETX ) +'px'
    }
    if(e.clientY + OFF_SETY +500> maxHeigt){
        dataDetailShowing.style.top = (e.clientY + OFF_SETY -500) + 'px'
    }else{
        dataDetailShowing.style.top = (e.clientY + OFF_SETY ) +'px'
    }
    
    
})

profilePictureBox.addEventListener('click',() => {
    renderChangePanel().then(() => {
        document.body.insertAdjacentHTML('beforeend',`
            <div class="dim-overlay"></div>
            `)
    })

})

renderData(defaultQueryData)
renderPersonalData()










