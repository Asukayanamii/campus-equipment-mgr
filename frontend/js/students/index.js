const dataShowing = document.getElementById(`data-showing`)

const defaultQueryData = new QueryData({});
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

renderData()



