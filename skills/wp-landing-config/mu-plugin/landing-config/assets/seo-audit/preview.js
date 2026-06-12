/* Live preview updater for Head & SEO admin */
(function () {
    'use strict';
    var $desc = document.getElementById('lp-input-description');
    var $ogImage = document.getElementById('lp-input-og-image');
    var $ogTitleOut = document.getElementById('lp-preview-og-title');
    var $ogDescOut = document.getElementById('lp-preview-og-desc');
    var $ogImageOut = document.getElementById('lp-preview-og-image-area');
    var $serpTitleOut = document.getElementById('lp-preview-serp-title');
    var $serpDescOut = document.getElementById('lp-preview-serp-desc');
    var $charCount = document.getElementById('lp-char-count');
    var $pickBtn = document.getElementById('lp-pick-og-image');

    function update() {
        var descText = $desc ? $desc.value : '';
        if ($ogDescOut) $ogDescOut.textContent = descText.slice(0, 200);
        if ($serpDescOut) $serpDescOut.textContent = descText.slice(0, 200);
        if ($charCount) $charCount.textContent = String(descText.length);

        var imgUrl = $ogImage ? $ogImage.value : '';
        if ($ogImageOut) {
            if (imgUrl) {
                $ogImageOut.style.backgroundImage = "url('" + imgUrl.replace(/'/g, "%27") + "')";
            } else {
                $ogImageOut.style.backgroundImage = '';
            }
        }
    }

    if ($desc) $desc.addEventListener('input', update);
    if ($ogImage) $ogImage.addEventListener('input', update);

    // Media picker — uses wp.media (loaded via wp_enqueue_media)
    if ($pickBtn && window.wp && window.wp.media) {
        $pickBtn.addEventListener('click', function (e) {
            e.preventDefault();
            var frame = wp.media({
                title: 'Выбрать OG-image',
                button: { text: 'Использовать это изображение' },
                multiple: false,
                library: { type: 'image' },
            });
            frame.on('select', function () {
                var att = frame.state().get('selection').first().toJSON();
                if ($ogImage) {
                    $ogImage.value = att.url;
                    update();
                }
            });
            frame.open();
        });
    }

    update();
})();
