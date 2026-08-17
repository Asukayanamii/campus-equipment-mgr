(function(){
    const IMAGE_SELECTOR = 'img'
    const EXCLUDED_SELECTOR = '#profile-picture-box, .image-preview-dialog'
    let lastTrigger = null

    function isPreviewableImage(image){
        return image instanceof HTMLImageElement && !image.closest(EXCLUDED_SELECTOR)
    }

    function prepareImage(image){
        if(!isPreviewableImage(image)) return
        image.classList.add('image-previewable')
        image.draggable = false
        if(!image.closest('button, a, label')){
            if(!image.hasAttribute('tabindex')) image.tabIndex = 0
            if(!image.hasAttribute('role')) image.setAttribute('role', 'button')
            if(!image.hasAttribute('title')) image.title = '点击查看大图'
        }
    }

    function prepareImages(root){
        if(root instanceof HTMLImageElement) prepareImage(root)
        root.querySelectorAll?.(IMAGE_SELECTOR).forEach(prepareImage)
    }

    function createDialog(){
        const dialog = document.createElement('dialog')
        dialog.className = 'image-preview-dialog'
        dialog.setAttribute('aria-label', '图片大图预览')

        const closeButton = document.createElement('button')
        closeButton.type = 'button'
        closeButton.className = 'image-preview-close'
        closeButton.setAttribute('aria-label', '关闭大图预览')
        closeButton.title = '关闭'
        closeButton.textContent = '×'

        const image = document.createElement('img')
        image.className = 'image-preview-full'
        image.alt = '图片大图预览'
        image.draggable = false

        dialog.append(closeButton, image)
        closeButton.addEventListener('click', () => dialog.close())
        dialog.addEventListener('click', event => {
            if(event.target === dialog) dialog.close()
        })
        dialog.addEventListener('close', () => {
            image.removeAttribute('src')
            lastTrigger?.focus?.()
            lastTrigger = null
        })
        document.body.appendChild(dialog)
        return dialog
    }

    function openImagePreview(src, alt, trigger){
        if(!src) return
        const dialog = document.querySelector('.image-preview-dialog') || createDialog()
        const image = dialog.querySelector('.image-preview-full')
        lastTrigger = trigger
        image.src = src
        image.alt = alt || '图片大图预览'
        if(!dialog.open) dialog.showModal()
    }

    function findPreviewTarget(target){
        const explicit = target.closest?.('[data-image-preview-src]')
        if(explicit && !explicit.closest('.image-preview-dialog')){
            const nestedImage = explicit.querySelector('img')
            return {
                trigger: explicit,
                src: explicit.dataset.imagePreviewSrc,
                alt: nestedImage?.alt || explicit.getAttribute('aria-label')
            }
        }

        const image = target.closest?.('img')
        if(!isPreviewableImage(image)) return null
        return {
            trigger: image,
            src: image.currentSrc || image.src,
            alt: image.alt
        }
    }

    document.addEventListener('click', event => {
        const preview = findPreviewTarget(event.target)
        if(!preview) return
        event.preventDefault()
        event.stopPropagation()
        openImagePreview(preview.src, preview.alt, preview.trigger)
    }, true)

    document.addEventListener('keydown', event => {
        if(event.key !== 'Enter' && event.key !== ' ') return
        if(!(event.target instanceof HTMLImageElement) || !isPreviewableImage(event.target)) return
        event.preventDefault()
        event.stopPropagation()
        openImagePreview(event.target.currentSrc || event.target.src, event.target.alt, event.target)
    }, true)

    const initialize = () => {
        prepareImages(document)
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
                if(node instanceof Element) prepareImages(node)
            }))
        })
        observer.observe(document.body, { childList: true, subtree: true })
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initialize, { once: true })
    }else{
        initialize()
    }
})()
