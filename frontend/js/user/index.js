const PAGE_SIZE = 18;
const DEFAULT_NAME = '代文秋'
const OFF_SETX = 15
const OFF_SETY = 15
const dataShowing = document.getElementById(`data-showing`)

const profileName = document.getElementById('profileName')
const profilePicture = document.getElementById('profile-picture')

const start = document.getElementById('start')
const pre2 = document.getElementById('pre-2')
const pre1 = document.getElementById('pre-1')
const cur = document.getElementById('cur')
const aft1 = document.getElementById('aft-1')
const aft2 = document.getElementById('aft-2')
const end = document.getElementById('end')

const dataDetailShowing = document.getElementById('data-detail-showing')
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

    switch (cur.innerHTML){
        case 1 :
            start.style.display = 'none'
            pre2.style.display = 'none'
            pre1.style.display = 'none'
        case 2 :
            pre2.style.display = 'none'
            pre1.style.display = 'none'
        case 3 :
            pre1.style.display = 'none'
    }

    switch(cur.innerText){
        case pageAll - 2:
            end.style.display = 'none'
        case pageAll - 1:
            end.style.display = 'none'
            aft2.style.display = 'none'
        case pageAll :
            end.style.display = 'none'
            aft2.style.display = 'none'
            aft1.style.display = 'none'
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
}

// 渲染数据
function renderData(QueryData = {}){
    getData(QueryData).then(res => {
        const list = res.data.items;
        list.forEach(i => {
            dataShowing.insertAdjacentHTML('beforeend',`
                <div class="data-card">
                    <h1>${i.equipmentName}</h1>
                    <p>${i.location}</p>
                    <div class="data-detail-showing">
                        <p>6</p>
                    </div>
                </div>
            `)
            pageAll = res.data.pages;
            
            renderButton()
            checkButton()
        });
        
    })
}

// 渲染个人信息
function renderPersonalData(){
    const personalData = getPersonalData(apiChoose())

    if(!profileName.innerText){
        profileName.innerText = `${DEFAULT_NAME}`
    }else{
        profileName.innerText = personalData.name
    }
    
    profilePicture.src = personalData.image
    
}




start.addEventListener('click', () =>{
     defaultQueryData.page = 1;
     renderData(defaultQueryData)
})

end.addEventListener('click',() => {
    defaultQueryData.page = pageAll
    renderData(defaultQueryData)
})

pre2.addEventListener('click' ,() => {
    defaultQueryData.page = pre2.innerText
    renderData(defaultQueryData)
})

pre1.addEventListener('click' ,() => {
    defaultQueryData.page = pre1.innerText
    renderData(defaultQueryData)
})

cur.addEventListener('click' ,() => {
    defaultQueryData.page = cur.innerText
    renderData(defaultQueryData)
})

aft1.addEventListener('click' ,() => {
    defaultQueryData.page = aft1.innerText
    renderData(defaultQueryData)
})

aft2.addEventListener('click' ,() => {
    defaultQueryData.page = aft2.innerText
    renderData(defaultQueryData)
})

// dataCard.addEventListener('mousemove', (e) => {
//     dataDetailShowing.style.left = (e.clientX + OFF_SETX) +'px'
//     dataDetailShowing.style.top = (e.clientY + OFF_SETY) +'px'
// })

dataCard.addEventListener('mousemove', (e) => {
      const card = e.target.closest('.data-card')
      if (!card) return
      const detail = card.querySelector('.data-detail-showing')
      if (!detail) return
      detail.style.left = (e.clientX  + OFF_SETX) + 'px'
      detail.style.top = (e.clientY + OFF_SETY) + 'px'
  })

renderData(defaultQueryData)










