const fontSizeBtn = document.getElementById('fontSize');
const wysiwygContainerDiv = document.getElementById('wysiwygContainer');
const uploadMediaButton = document.getElementById('uploadMediaButton');


if (fontSizeBtn) {
    fontSizeBtn.addEventListener('change', function() {
        formatText('fontSize', this.value);
    });
}

if (wysiwygContainerDiv) {
    wysiwygContainerDiv.addEventListener('paste', function(e) {
        e.preventDefault();
        var text = (e.originalEvent || e).clipboardData.getData('text/plain');
        document.execCommand('insertText', false, text);
    });
}

if (uploadMediaButton) {
    uploadMediaButton.addEventListener('click', function() {
        const mediaInput = document.getElementById('mediaInput');
        mediaInput.click();
    });
}

function formatText(command) {
    if (command === 'fontSize') {
        document.execCommand('fontSize', false, arguments[1]);
    } else {
        document.execCommand(command, false, null);
        const buttonId = command + 'ToggleButton';
        const button = document.getElementById(buttonId);
        button.classList.toggle('toggle-active');
    }
    document.getElementById('content').focus();
}

uploadAndPasteImage = async (e) => {
    const file = e.files[0];
    const reader = new FileReader();
    reader.readAsDataURL(file);
    var paths = await uploadFile(file)

    var compressedImage = paths['compressedImage'];
    var originalImage = paths['originalImage'];

    document.execCommand('insertImage', false, originalImage);
}
