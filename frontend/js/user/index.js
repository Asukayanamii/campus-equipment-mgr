const dataShowing = document.getElementById(`data-showing`)

const profileName = document.getElementById('profileName')
const profilePicture = document.getElementById('profile-picture')
let pageNow = 1;
const identity = 1
const defaultQueryData = new QueryData({
    page : pageNow,
});
function renderData(){
    getData().then(res => {
        const list = res.data.items;
        list.forEach(i => {
            dataShowing.innerHTML += `
                <div class="data-card">
                    <h1>${i.equipmentName}</h1>
                    <p>${i.location}</p>
                </div>
            `
        });
    })
}

function renderPersonalData(){
    const personalData = getPersonalData(apiChoose())

    profileName.innerText = personalData.name
    profilePicture.src = personalData.image
    
}
renderData()





