document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('editor-textarea');
    if (!textarea) return;

    const easyMDE = new EasyMDE({
        element: textarea,
        spellChecker: false,
        autosave: { enabled: false },
        placeholder: '开始写作...使用 [[slug]] 创建链接',
        toolbar: ['bold', 'italic', 'heading', '|', 'quote', 'unordered-list', 'ordered-list', '|', 'link', 'image', '|', 'preview', 'side-by-side', 'fullscreen', '|', 'guide'],
    });

    document.getElementById('save-btn').addEventListener('click', () => {
        const form = document.getElementById('note-form');
        const formData = new FormData(form);
        formData.set('content', easyMDE.value());

        fetch('/api/notes', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.slug) {
                    window.location.href = '/note/' + data.slug;
                }
            });
    });
});
