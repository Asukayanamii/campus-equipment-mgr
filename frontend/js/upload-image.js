function createImageUploadController({ input, preview, maxCount = 9 }){
    const state = { urls: [], uploading: false }

    function render(){
        preview.replaceChildren()
        state.urls.forEach((url, index) => {
            const item = document.createElement('div')
            item.className = 'image-upload-preview-item'
            const image = document.createElement('img')
            image.src = url
            image.alt = `已上传图片 ${index + 1}`
            const removeButton = document.createElement('button')
            removeButton.type = 'button'
            removeButton.textContent = '×'
            removeButton.setAttribute('aria-label', `删除第 ${index + 1} 张图片`)
            removeButton.addEventListener('click', () => {
                state.urls.splice(index, 1)
                render()
            })
            item.append(image, removeButton)
            preview.appendChild(item)
        })
    }

    input.addEventListener('change', async () => {
        const files = Array.from(input.files)
        if(files.some(file => !file.type.startsWith('image/'))){
            Toast.warning('只能上传图片文件')
            input.value = ''
            return
        }
        if(state.urls.length + files.length > maxCount){
            Toast.warning(`最多上传 ${maxCount} 张图片`)
            input.value = ''
            return
        }

        state.uploading = true
        input.disabled = true
        try {
            // 逐张上传，确保预览顺序与用户选择顺序一致。
            for(const file of files){
                const url = await uploadImage(file)
                if(!url) break
                state.urls.push(url)
                render()
            }
        } finally {
            state.uploading = false
            input.disabled = false
            input.value = ''
        }
    })

    return {
        getUrls: () => [...state.urls],
        isUploading: () => state.uploading,
        clear: () => {
            state.urls.length = 0
            render()
        }
    }
}
