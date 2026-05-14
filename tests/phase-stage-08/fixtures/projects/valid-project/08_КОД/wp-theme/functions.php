<?php
add_action('lzb/init', function () {
    lazyblocks()->add_block([
        'slug'  => 'lazyblock/hero',
        'title' => 'Hero',
    ]);
});
